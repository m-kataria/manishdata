import { callBackend } from '$lib/api';
import type { BcSalesOrder } from '$lib/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
    const q = event.url.searchParams.get('q') ?? '';
    // Default to Open when no status given — matches BC's "Open Sales Orders" view
    const status = event.url.searchParams.get('status') ?? 'Open';

    const params = new URLSearchParams();
    if (q) params.set('q', q);
    if (status) params.set('status', status);
    const qs = params.toString();
    const path = `/api/bc/sales-orders${qs ? '?' + qs : ''}`;

    const res = await callBackend<BcSalesOrder[]>(event, path);
    return {
        orders: res.data ?? [],
        error: res.error,
        q,
        status
    };
};
