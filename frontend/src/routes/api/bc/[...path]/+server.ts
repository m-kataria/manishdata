import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

const BACKEND = env.BACKEND_URL || 'http://localhost:5000';

const proxy: RequestHandler = async ({ params, request, fetch, url }) => {
    const path = params.path ?? '';
    const target = `${BACKEND}/api/bc/${path}${url.search}`;
    const headers = new Headers();
    const cookie = request.headers.get('cookie');
    if (cookie) headers.set('cookie', cookie);
    const ct = request.headers.get('content-type');
    if (ct) headers.set('content-type', ct);

    const init: RequestInit = { method: request.method, headers };
    if (request.method !== 'GET' && request.method !== 'HEAD') {
        const text = await request.text();
        if (text) init.body = text;
    }
    try {
        const res = await fetch(target, init);
        const respHeaders = new Headers();
        const respCt = res.headers.get('content-type');
        if (respCt) respHeaders.set('content-type', respCt);
        // 204/205/304 must have null body per the Fetch spec.
        const nullBodyStatus = res.status === 204 || res.status === 205 || res.status === 304;
        const body = nullBodyStatus ? null : await res.arrayBuffer();
        return new Response(body, { status: res.status, headers: respHeaders });
    } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        return new Response(
            JSON.stringify({ error: `proxy to ${target} failed: ${msg}` }),
            { status: 502, headers: { 'content-type': 'application/json' } }
        );
    }
};

export const GET = proxy;
export const POST = proxy;
export const PATCH = proxy;
export const PUT = proxy;
export const DELETE = proxy;
