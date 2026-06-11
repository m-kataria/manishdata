import { callBackend } from '$lib/api';
import type { BcSkuRow } from '$lib/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
    const q = event.url.searchParams.get('q') ?? '';
    const location = event.url.searchParams.get('location') ?? '';

    const params = new URLSearchParams();
    if (q) params.set('q', q);
    if (location) params.set('location', location);
    // Pull a wide net so alphabetical sort doesn't cut off later items (PIR-PANELS, SHELF, etc.)
    params.set('top', '2000');
    const path = `/api/bc/sku-inventory?${params.toString()}`;

    const res = await callBackend<BcSkuRow[]>(event, path);
    const rows = res.data ?? [];

    const locations = Array.from(new Set(rows.map((r) => r.locationCode))).sort();

    return { rows, error: res.error, q, location, locations };
};
