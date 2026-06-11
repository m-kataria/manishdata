import { fail } from '@sveltejs/kit';
import { callBackend } from '$lib/api';
import type { IntegrationStatus, PingResult, SyncLog } from '$lib/types';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
    const [status, log] = await Promise.all([
        callBackend<IntegrationStatus>(event, '/api/integrations'),
        callBackend<SyncLog[]>(event, '/api/integrations/sync-log')
    ]);
    return {
        status: status.data,
        syncLog: log.data ?? []
    };
};

export const actions: Actions = {
    pingBC: async (event) => {
        const res = await callBackend<PingResult>(event, '/api/integrations/bc/ping', {
            method: 'POST'
        });
        if (!res.ok) return fail(res.status || 502, { bc: res.data ?? { connected: false, message: res.error } });
        return { bc: res.data };
    },
    pingSF: async (event) => {
        const res = await callBackend<PingResult>(event, '/api/integrations/sf/ping', {
            method: 'POST'
        });
        if (!res.ok) return fail(res.status || 502, { sf: res.data ?? { connected: false, message: res.error } });
        return { sf: res.data };
    },
    syncInventory: async (event) => {
        const res = await callBackend<{ syncedRecords: number; syncLogId: number }>(
            event,
            '/api/bc/sync/inventory',
            { method: 'POST' }
        );
        if (!res.ok) return fail(res.status || 502, { syncError: res.error });
        return { syncResult: res.data };
    }
};
