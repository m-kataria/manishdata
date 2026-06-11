import { callBackend } from '$lib/api';
import type { BcSalesQuote } from '$lib/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
    const q = event.url.searchParams.get('q') ?? '';
    const status = event.url.searchParams.get('status') ?? '';

    const params = new URLSearchParams();
    if (q) params.set('q', q);
    if (status) params.set('status', status);
    const qs = params.toString();
    const path = `/api/bc/sales-quotes${qs ? '?' + qs : ''}`;

    const res = await callBackend<BcSalesQuote[]>(event, path);
    return {
        quotes: res.data ?? [],
        error: res.error,
        q,
        status
    };
};
