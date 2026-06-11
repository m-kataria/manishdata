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
        init.body = await request.text();
    }
    const res = await fetch(target, init);
    const body = await res.arrayBuffer();
    const respHeaders = new Headers();
    const respCt = res.headers.get('content-type');
    if (respCt) respHeaders.set('content-type', respCt);
    return new Response(body, { status: res.status, headers: respHeaders });
};

export const GET = proxy;
export const POST = proxy;
export const PATCH = proxy;
export const PUT = proxy;
export const DELETE = proxy;
