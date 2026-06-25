import { callBackend } from '$lib/api';
import type { VariantPricingResponse } from '$lib/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
    const q = event.url.searchParams.get('q') ?? '';
    const location = event.url.searchParams.get('location') ?? '';

    const params = new URLSearchParams();
    if (q) params.set('q', q);
    if (location) params.set('location', location);
    const path = `/api/bc/pricing-rows${params.toString() ? `?${params}` : ''}`;

    const res = await callBackend<VariantPricingResponse>(event, path);

    const isArchive = (code: string | undefined) =>
        !!code && code.toLowerCase().includes('archive');

    const rawRows = res.data?.rows ?? [];
    const rows = rawRows.filter((r) => !isArchive(r.locationCode));

    const rawLocations = res.data?.locations ?? [];
    const locations = rawLocations.filter((l) => !isArchive(l));

    return {
        q,
        location,
        priceGroups: res.data?.priceGroups ?? [],
        rows,
        locations,
        error: res.error
    };
};
