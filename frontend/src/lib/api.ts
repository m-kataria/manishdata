import { env } from '$env/dynamic/private';
import type { RequestEvent } from '@sveltejs/kit';

const BACKEND = env.BACKEND_URL || 'http://localhost:5000';

export type BackendResponse<T> = {
    ok: boolean;
    status: number;
    data: T | null;
    error: string | null;
};

type CookieOptions = {
    path: string;
    domain?: string;
    expires?: Date;
    maxAge?: number;
    sameSite?: 'lax' | 'strict' | 'none';
    secure?: boolean;
    httpOnly?: boolean;
};

function parseSetCookie(setCookie: string): { name: string; value: string; options: CookieOptions } | null {
    const parts = setCookie.split(';').map((p) => p.trim());
    if (parts.length === 0 || !parts[0]) return null;
    const eq = parts[0].indexOf('=');
    if (eq < 1) return null;
    const name = parts[0].slice(0, eq);
    const value = parts[0].slice(eq + 1);

    const options: CookieOptions = { path: '/' };
    for (let i = 1; i < parts.length; i++) {
        const seg = parts[i];
        const segEq = seg.indexOf('=');
        const key = (segEq === -1 ? seg : seg.slice(0, segEq)).toLowerCase();
        const v = segEq === -1 ? '' : seg.slice(segEq + 1);
        switch (key) {
            case 'path':
                options.path = v || '/';
                break;
            case 'domain':
                options.domain = v;
                break;
            case 'expires':
                options.expires = new Date(v);
                break;
            case 'max-age':
                options.maxAge = parseInt(v, 10);
                break;
            case 'samesite': {
                const lower = v.toLowerCase();
                if (lower === 'lax' || lower === 'strict' || lower === 'none') options.sameSite = lower;
                break;
            }
            case 'secure':
                options.secure = true;
                break;
            case 'httponly':
                options.httpOnly = true;
                break;
        }
    }
    return { name, value, options };
}

/**
 * Server-side call to the Flask backend. Forwards the user's session cookie from the
 * incoming SvelteKit request, and applies any Set-Cookie headers Flask emits via
 * `event.cookies.set()` so the browser receives them on the SvelteKit origin.
 */
export async function callBackend<T = unknown>(
    event: RequestEvent,
    path: string,
    init: RequestInit = {}
): Promise<BackendResponse<T>> {
    const url = `${BACKEND}${path}`;
    const headers = new Headers(init.headers);

    const incomingCookie = event.request.headers.get('cookie');
    if (incomingCookie) headers.set('cookie', incomingCookie);

    if (init.body && !headers.has('content-type')) {
        headers.set('content-type', 'application/json');
    }

    let res: Response;
    try {
        res = await event.fetch(url, { ...init, headers });
    } catch (e) {
        return {
            ok: false,
            status: 0,
            data: null,
            error: e instanceof Error ? e.message : 'network error'
        };
    }

    // Forward any Set-Cookie headers from Flask to the browser via SvelteKit's cookies API
    const setCookies = res.headers.getSetCookie?.() ?? [];
    for (const sc of setCookies) {
        const parsed = parseSetCookie(sc);
        if (parsed) {
            event.cookies.set(parsed.name, parsed.value, parsed.options);
        }
    }

    let data: T | null = null;
    let error: string | null = null;
    const text = await res.text();
    if (text) {
        try {
            const parsed = JSON.parse(text);
            if (res.ok) data = parsed as T;
            else error = parsed.error || text;
        } catch {
            error = text;
        }
    }

    return { ok: res.ok, status: res.status, data, error };
}
