import { fail } from '@sveltejs/kit';
import { callBackend } from '$lib/api';
import type { BcCustomer, BcDimensionValue } from '$lib/types';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
    const number = event.params.id;
    const [customer, custCategory, businessType] = await Promise.all([
        callBackend<BcCustomer>(event, `/api/bc/customers/${encodeURIComponent(number)}`),
        callBackend<BcDimensionValue[]>(event, '/api/bc/dimension-values?code=CUST%20CATEGORY'),
        callBackend<BcDimensionValue[]>(event, '/api/bc/dimension-values?code=BUSINESS%20TYPE')
    ]);
    return {
        number,
        customer: customer.data ?? null,
        error: customer.error,
        custCategoryValues: custCategory.data ?? [],
        businessTypeValues: businessType.data ?? []
    };
};

export const actions: Actions = {
    save: async (event) => {
        const form = await event.request.formData();
        const systemId = String(form.get('systemId') ?? '').trim();
        if (!systemId) {
            return fail(400, { error: 'Missing customer systemId.' });
        }

        const patch: Record<string, string> = {};
        const fields: [string, string][] = [
            ['displayName', 'displayName'],
            ['contactName', 'contactName'],
            ['phoneNumber', 'phoneNumber'],
            ['email', 'email'],
            ['addressLine1', 'addressLine1'],
            ['addressLine2', 'addressLine2'],
            ['city', 'city'],
            ['state', 'state'],
            ['postalCode', 'postalCode'],
            ['countryRegionCode', 'countryRegionCode'],
            ['custCategory', 'custCategory'],
            ['businessType', 'businessType']
        ];
        for (const [formKey, bcKey] of fields) {
            const raw = form.get(formKey);
            if (raw === null) continue;
            patch[bcKey] = String(raw).trim();
        }

        const res = await callBackend<BcCustomer>(
            event,
            `/api/bc/customers/${encodeURIComponent(systemId)}`,
            { method: 'PATCH', body: JSON.stringify(patch) }
        );
        if (!res.ok) {
            return fail(res.status || 502, { error: res.error || 'Update failed', patch });
        }
        return { success: true, customer: res.data };
    }
};
