import { fail, redirect } from '@sveltejs/kit';
import { callBackend } from '$lib/api';
import type { BcCustomer } from '$lib/types';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
    const res = await callBackend<BcCustomer[]>(event, '/api/bc/customers?top=2000');
    return { customers: res.data ?? [], error: res.error };
};

export const actions: Actions = {
    create: async (event) => {
        const form = await event.request.formData();
        const customerId = String(form.get('customerId') ?? '').trim();
        const documentDate = String(form.get('documentDate') ?? '').trim() || undefined;
        const validUntil = String(form.get('validUntil') ?? '').trim() || undefined;
        if (!customerId) return fail(400, { error: 'Pick a customer.' });

        const res = await callBackend<{ id: string; number: string }>(
            event,
            '/api/bc/sales-quotes',
            { method: 'POST', body: JSON.stringify({ customerId, documentDate, validUntil }) }
        );
        if (!res.ok || !res.data?.number) {
            return fail(res.status || 502, { error: res.error || 'Failed to create quote' });
        }
        throw redirect(303, `/quotes/${encodeURIComponent(res.data.number)}/edit`);
    }
};
