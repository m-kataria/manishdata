import { redirect } from '@sveltejs/kit';
import { callBackend } from '$lib/api';
import type { IntegrationStatus, User } from '$lib/types';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async (event) => {
    const path = event.url.pathname;
    const userRes = await callBackend<User>(event, '/api/auth/me');

    if (path === '/login') {
        if (userRes.ok && userRes.data) throw redirect(303, '/');
        return { user: null, integrations: null };
    }

    if (!userRes.ok) throw redirect(303, '/login');

    const intRes = await callBackend<IntegrationStatus>(event, '/api/integrations');

    return {
        user: userRes.data,
        integrations: intRes.data
    };
};
