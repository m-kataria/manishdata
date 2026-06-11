import { callBackend } from '$lib/api';
import type { BcItemListing, PricingMatrix } from '$lib/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
    const q = event.url.searchParams.get('q') ?? '';
    const item = event.url.searchParams.get('item') ?? '';

    const itemsPath = q ? `/api/bc/items-search?q=${encodeURIComponent(q)}` : '/api/bc/items-search';
    const itemsRes = await callBackend<BcItemListing[]>(event, itemsPath);

    let matrix: PricingMatrix | null = null;
    let matrixError: string | null = null;
    if (item) {
        const r = await callBackend<PricingMatrix>(
            event,
            `/api/bc/pricing-matrix?itemNo=${encodeURIComponent(item)}`
        );
        matrix = r.data;
        matrixError = r.error;
    }

    return {
        q,
        selectedItemNumber: item,
        items: itemsRes.data ?? [],
        itemsError: itemsRes.error,
        matrix,
        matrixError
    };
};
