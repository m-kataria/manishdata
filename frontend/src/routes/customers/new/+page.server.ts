import { fail, redirect } from '@sveltejs/kit';
import { callBackend } from '$lib/api';
import type { BcCustomerTemplate, BcDimensionValue } from '$lib/types';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
    const [templates, custCategory, businessType] = await Promise.all([
        callBackend<BcCustomerTemplate[]>(event, '/api/bc/customer-templates'),
        callBackend<BcDimensionValue[]>(event, '/api/bc/dimension-values?code=CUST%20CATEGORY'),
        callBackend<BcDimensionValue[]>(event, '/api/bc/dimension-values?code=BUSINESS%20TYPE')
    ]);
    return {
        templates: templates.data ?? [],
        templatesError: templates.error,
        custCategoryValues: custCategory.data ?? [],
        businessTypeValues: businessType.data ?? []
    };
};

export const actions: Actions = {
    create: async (event) => {
        const form = await event.request.formData();
        const payload = {
            templateSystemId: String(form.get('templateSystemId') ?? '').trim(),
            name: String(form.get('name') ?? '').trim(),
            addressLine1: String(form.get('addressLine1') ?? '').trim(),
            addressLine2: String(form.get('addressLine2') ?? '').trim(),
            city: String(form.get('city') ?? '').trim(),
            county: String(form.get('county') ?? '').trim(),
            postCode: String(form.get('postCode') ?? '').trim(),
            countryRegionCode: String(form.get('countryRegionCode') ?? '').trim(),
            phoneNo: String(form.get('phoneNo') ?? '').trim(),
            email: String(form.get('email') ?? '').trim(),
            contactName: String(form.get('contactName') ?? '').trim(),
            custCategory: String(form.get('custCategory') ?? '').trim(),
            businessType: String(form.get('businessType') ?? '').trim()
        };

        if (!payload.templateSystemId) {
            return fail(400, { error: 'Pick a customer template.', form: payload });
        }
        if (!payload.name) {
            return fail(400, { error: 'Customer name is required.', form: payload });
        }

        const res = await callBackend<{ createdNo: string; customer: unknown }>(
            event,
            '/api/bc/customers',
            { method: 'POST', body: JSON.stringify(payload) }
        );

        if (!res.ok || !res.data?.createdNo) {
            return fail(res.status || 502, {
                error: res.error || 'Customer create failed',
                form: payload
            });
        }

        // Success — bounce to the customers list filtered to the new customer
        throw redirect(303, `/customers?q=${encodeURIComponent(res.data.createdNo)}`);
    }
};
