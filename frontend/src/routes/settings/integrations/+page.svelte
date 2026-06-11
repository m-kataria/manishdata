<script lang="ts">
    import { enhance } from '$app/forms';
    import type { ActionData, PageData } from './$types';

    export let data: PageData;
    export let form: ActionData;

    let pingingBC = false;
    let pingingSF = false;
    let syncing = false;

    function fmtTimestamp(s: string | null): string {
        if (!s) return '—';
        return new Date(s).toLocaleString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    function syncBadge(status: string): string {
        if (status === 'success') return 'badge-active';
        if (status === 'failed') return 'badge-review';
        return 'badge-pending';
    }
</script>

<div class="px-8 py-8 max-w-[1280px]">
    <div class="mb-8">
        <p class="eyebrow mb-1">External</p>
        <h1 class="font-h2 text-h2 text-on-surface font-semibold">Integrations.</h1>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mb-8">
        <!-- Business Central -->
        <section class="card overflow-hidden">
            <div class="h-1 bg-bc" />
            <div class="p-6">
                <div class="flex items-start justify-between gap-3 mb-5">
                    <div>
                        <p class="font-label-sm text-xs uppercase tracking-[0.2em] text-bc mb-1">
                            Channel · BC
                        </p>
                        <h2 class="font-h3 text-h3 text-on-surface font-semibold">
                            Business Central
                        </h2>
                        <p class="font-label-sm text-xs text-secondary mt-1">
                            OAuth 2.0 · OData v4
                        </p>
                    </div>
                    {#if data.status?.businessCentral.configured}
                        {#if data.status.businessCentral.lastSync?.status === 'failed'}
                            <span class="badge-review">Faulted</span>
                        {:else}
                            <span class="badge-bc"><span class="dot-bc" /> Online</span>
                        {/if}
                    {:else}
                        <span class="badge-pending">Offline</span>
                    {/if}
                </div>

                <dl class="grid grid-cols-2 gap-3 mb-5">
                    <div>
                        <dt class="field-label">Last sync</dt>
                        <dd class="font-body-md text-sm text-on-surface mt-1">
                            {fmtTimestamp(data.status?.businessCentral.lastSync?.completedAt ?? null)}
                        </dd>
                    </div>
                    <div>
                        <dt class="field-label">Records</dt>
                        <dd class="font-body-md text-sm text-on-surface mt-1 tabular-nums">
                            {data.status?.businessCentral.lastSync?.recordsSynced ?? 0}
                        </dd>
                    </div>
                </dl>

                <div class="flex gap-2 flex-wrap">
                    <form
                        method="POST"
                        action="?/pingBC"
                        use:enhance={() => {
                            pingingBC = true;
                            return async ({ update }) => {
                                await update();
                                pingingBC = false;
                            };
                        }}
                    >
                        <button class="btn-outline" disabled={pingingBC}>
                            {pingingBC ? 'Pinging…' : 'Ping BC'}
                        </button>
                    </form>
                    <form
                        method="POST"
                        action="?/syncInventory"
                        use:enhance={() => {
                            syncing = true;
                            return async ({ update }) => {
                                await update();
                                syncing = false;
                            };
                        }}
                    >
                        <button class="btn-outline" disabled={syncing}>
                            {syncing ? 'Syncing…' : 'Sync inventory'}
                        </button>
                    </form>
                </div>

                {#if form?.bc}
                    <div
                        class="mt-5 border-l-4 {form.bc.connected
                            ? 'border-primary-container'
                            : 'border-error'} bg-surface-container-low px-5 py-3"
                    >
                        <p class="font-body-md text-sm text-on-surface font-medium">
                            {form.bc.connected ? 'Channel ready' : 'Channel unreachable'}
                        </p>
                        {#if form.bc.message}
                            <p class="font-label-sm text-xs text-secondary mt-1">{form.bc.message}</p>
                        {/if}
                    </div>
                {/if}
                {#if form?.syncResult}
                    <div class="mt-5 border-l-4 border-primary-container bg-surface-container-low px-5 py-3">
                        <p class="font-body-md text-sm text-on-surface">
                            Synced {form.syncResult.syncedRecords} record{form.syncResult.syncedRecords === 1 ? '' : 's'}.
                        </p>
                    </div>
                {/if}
            </div>
        </section>

        <!-- Salesforce -->
        <section class="card overflow-hidden">
            <div class="h-1 bg-sf" />
            <div class="p-6">
                <div class="flex items-start justify-between gap-3 mb-5">
                    <div>
                        <p class="font-label-sm text-xs uppercase tracking-[0.2em] text-sf mb-1">
                            Channel · SF
                        </p>
                        <h2 class="font-h3 text-h3 text-on-surface font-semibold">Salesforce</h2>
                        <p class="font-label-sm text-xs text-secondary mt-1">
                            Username + Token · REST
                        </p>
                    </div>
                    {#if data.status?.salesforce.configured}
                        {#if data.status.salesforce.lastSync?.status === 'failed'}
                            <span class="badge-review">Faulted</span>
                        {:else}
                            <span class="badge-sf"><span class="dot-sf" /> Online</span>
                        {/if}
                    {:else}
                        <span class="badge-pending">Offline</span>
                    {/if}
                </div>

                <dl class="grid grid-cols-2 gap-3 mb-5">
                    <div>
                        <dt class="field-label">Last sync</dt>
                        <dd class="font-body-md text-sm text-on-surface mt-1">
                            {fmtTimestamp(data.status?.salesforce.lastSync?.completedAt ?? null)}
                        </dd>
                    </div>
                    <div>
                        <dt class="field-label">Records</dt>
                        <dd class="font-body-md text-sm text-on-surface mt-1 tabular-nums">
                            {data.status?.salesforce.lastSync?.recordsSynced ?? 0}
                        </dd>
                    </div>
                </dl>

                <div class="flex gap-2 flex-wrap">
                    <form
                        method="POST"
                        action="?/pingSF"
                        use:enhance={() => {
                            pingingSF = true;
                            return async ({ update }) => {
                                await update();
                                pingingSF = false;
                            };
                        }}
                    >
                        <button class="btn-outline" disabled={pingingSF}>
                            {pingingSF ? 'Pinging…' : 'Ping Salesforce'}
                        </button>
                    </form>
                </div>

                {#if form?.sf}
                    <div
                        class="mt-5 border-l-4 {form.sf.connected
                            ? 'border-primary-container'
                            : 'border-error'} bg-surface-container-low px-5 py-3"
                    >
                        <p class="font-body-md text-sm text-on-surface font-medium">
                            {form.sf.connected ? 'Channel ready' : 'Channel unreachable'}
                        </p>
                        {#if form.sf.message}
                            <p class="font-label-sm text-xs text-secondary mt-1">{form.sf.message}</p>
                        {/if}
                    </div>
                {/if}
            </div>
        </section>
    </div>

    <!-- Activity log -->
    <section class="card overflow-hidden">
        <div class="flex items-center justify-between px-6 py-4 border-b border-zinc-100">
            <div>
                <p class="eyebrow mb-1">Telemetry</p>
                <h2 class="font-h3 text-h3 text-on-surface font-semibold">Recent activity</h2>
            </div>
            <p class="font-label-sm text-xs text-secondary">
                Last {data.syncLog.length} events
            </p>
        </div>

        {#if data.syncLog.length === 0}
            <p class="text-center text-secondary py-16 font-body-md text-sm">
                No activity recorded yet.
            </p>
        {:else}
            <table class="nrv-table">
                <thead>
                    <tr>
                        <th>Channel</th>
                        <th>Entity</th>
                        <th>Status</th>
                        <th class="text-right">Records</th>
                        <th>Started</th>
                        <th>Completed</th>
                    </tr>
                </thead>
                <tbody>
                    {#each data.syncLog as row}
                        <tr>
                            <td>
                                {#if row.integration === 'business_central'}
                                    <span class="badge-bc">BC</span>
                                {:else}
                                    <span class="badge-sf">SF</span>
                                {/if}
                            </td>
                            <td class="muted">{row.entity}</td>
                            <td><span class={syncBadge(row.status)}>{row.status}</span></td>
                            <td class="text-right tabular-nums">{row.recordsSynced}</td>
                            <td class="muted">{fmtTimestamp(row.startedAt)}</td>
                            <td class="muted">{fmtTimestamp(row.completedAt)}</td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        {/if}
    </section>
</div>
