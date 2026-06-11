import { env } from '$env/dynamic/private';
import { error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const BACKEND = env.BACKEND_URL || 'http://localhost:5000';

export const GET: RequestHandler = async ({ params, request, fetch }) => {
    const incomingCookie = request.headers.get('cookie');
    const headers: HeadersInit = {};
    if (incomingCookie) headers['cookie'] = incomingCookie;

    const res = await fetch(`${BACKEND}/api/bc/sales-orders/${params.id}/pdf`, { headers });

    if (!res.ok) {
        const text = await res.text();
        throw error(res.status, text || 'PDF download failed');
    }

    const pdfBytes = await res.arrayBuffer();
    return new Response(pdfBytes, {
        status: 200,
        headers: {
            'Content-Type': 'application/pdf',
            'Content-Disposition':
                res.headers.get('content-disposition') ?? `attachment; filename="${params.id}.pdf"`,
            'Content-Length': String(pdfBytes.byteLength)
        }
    });
};
