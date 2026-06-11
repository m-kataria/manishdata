import { callBackend } from '$lib/api';
import type { BcCustomer } from '$lib/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
    const q = event.url.searchParams.get('q') ?? '';
    const params = new URLSearchParams();
    if (q) params.set('q', q);
    params.set('top', '500');
    const path = `/api/bc/customers?${params.toString()}`;

    const res = await callBackend<BcCustomer[]>(event, path);
    return { customers: res.data ?? [], error: res.error, q };
};
