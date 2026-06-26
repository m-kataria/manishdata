import { redirect } from '@sveltejs/kit';
import { callBackend } from '$lib/api';
import type { User } from '$lib/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
    const me = await event.parent();
    if (!me.user || me.user.role !== 'superadmin') {
        throw redirect(303, '/');
    }
    const res = await callBackend<User[]>(event, '/api/users');
    return { users: res.data ?? [], error: res.error };
};
