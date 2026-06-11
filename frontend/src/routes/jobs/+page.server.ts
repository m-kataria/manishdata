import { callBackend } from '$lib/api';
import type { Job } from '$lib/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
    const res = await callBackend<Job[]>(event, '/api/jobs');
    return { jobs: res.data ?? [], error: res.error };
};
