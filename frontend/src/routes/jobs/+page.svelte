<script lang="ts">
    import type { PageData } from './$types';

    export let data: PageData;

    function jobBadge(status: string): string {
        if (status === 'completed') return 'badge-active';
        if (status === 'cancelled') return 'badge-review';
        return 'badge-pending';
    }
</script>

<div class="px-8 py-8 max-w-[1280px]">
    <div class="mb-8 flex items-end justify-between">
        <div>
            <p class="eyebrow mb-1">Field service</p>
            <h1 class="font-h2 text-h2 text-on-surface font-semibold">Jobs.</h1>
        </div>
        <button class="btn-primary" disabled>+ New Job</button>
    </div>

    {#if data.error}
        <div class="border-l-4 border-error bg-surface-container-low px-5 py-4 mb-6 flex gap-3 items-start">
            <span class="material-symbols-outlined text-error">error</span>
            <p class="font-body-md text-sm text-on-surface">{data.error}</p>
        </div>
    {/if}

    <div class="card overflow-hidden">
        <div class="flex items-center justify-between px-6 py-4 border-b border-zinc-100">
            <p class="eyebrow">
                {data.jobs.length} record{data.jobs.length === 1 ? '' : 's'}
            </p>
        </div>

        {#if data.jobs.length === 0}
            <p class="text-center text-secondary py-16 font-body-md text-sm">No jobs yet.</p>
        {:else}
            <table class="nrv-table">
                <thead>
                    <tr>
                        <th>Job #</th>
                        <th>Title</th>
                        <th>Customer</th>
                        <th>Status</th>
                        <th>Linked</th>
                        <th>Updated</th>
                    </tr>
                </thead>
                <tbody>
                    {#each data.jobs as job}
                        <tr>
                            <td class="font-medium">{job.jobNumber}</td>
                            <td>{job.title}</td>
                            <td class="muted">{job.customerName}</td>
                            <td><span class={jobBadge(job.status)}>{job.status.replace('_', ' ')}</span></td>
                            <td class="muted">
                                {#if job.sfOpportunityId}
                                    <span class="badge-sf mr-1">SF</span>
                                {/if}
                                {#if job.bcSalesOrderId}
                                    <span class="badge-bc">BC</span>
                                {/if}
                                {#if !job.sfOpportunityId && !job.bcSalesOrderId}—{/if}
                            </td>
                            <td class="muted">
                                {new Date(job.updatedAt).toLocaleDateString(undefined, {
                                    year: 'numeric',
                                    month: 'short',
                                    day: 'numeric'
                                })}
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        {/if}
    </div>
</div>
