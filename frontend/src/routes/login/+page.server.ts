import { fail, redirect } from '@sveltejs/kit';
import { callBackend } from '$lib/api';
import type { User } from '$lib/types';
import type { Actions } from './$types';

export const actions: Actions = {
    login: async (event) => {
        const form = await event.request.formData();
        const username = String(form.get('username') ?? '').trim();
        const password = String(form.get('password') ?? '');

        if (!username || !password) {
            return fail(400, { error: 'Username and password are required', username });
        }

        const res = await callBackend<User>(event, '/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        if (!res.ok) {
            return fail(res.status || 401, {
                error: res.error || 'Login failed',
                username
            });
        }

        // Cookies already applied by callBackend via event.cookies.set
        throw redirect(303, '/');
    },

    logout: async (event) => {
        await callBackend(event, '/api/auth/logout', { method: 'POST' });
        throw redirect(303, '/login');
    }
};
