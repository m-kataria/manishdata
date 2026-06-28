<script lang="ts">
    import type { PageData } from './$types';

    export let data: PageData;
</script>

<div class="px-8 py-8 mx-auto max-w-[1480px]">
    <div class="mb-8 flex items-end justify-between gap-6 flex-wrap">
        <div>
            <p class="eyebrow mb-1">Sales</p>
            <h1 class="font-h2 text-h2 text-on-surface font-semibold">Customers.</h1>
            <p class="font-body-md text-sm text-secondary mt-2 max-w-2xl">
                Live from Business Central. Create new customers using BC templates — most fields auto-fill from the chosen template.
            </p>
        </div>
        <div class="flex items-end gap-3 flex-wrap">
            <form method="GET" class="flex items-end gap-3">
                <div class="flex flex-col gap-1">
                    <label for="cu-q" class="field-label">Search</label>
                    <input
                        id="cu-q"
                        name="q"
                        value={data.q}
                        placeholder="Customer #, name, phone, email"
                        class="field w-[300px]"
                    />
                </div>
                <button class="btn-outline">Search</button>
            </form>
            <a href="/customers/new" class="btn-primary">+ New Customer</a>
        </div>
    </div>

    {#if data.error}
        <div class="border-l-4 border-error bg-surface-container-low px-5 py-4 mb-6 flex gap-3 items-start">
            <span class="material-symbols-outlined text-error">error</span>
            <p class="font-body-md text-sm text-on-surface">{data.error}</p>
        </div>
    {/if}

    <div class="card overflow-hidden">
        <div class="flex items-center justify-between px-6 py-4 border-b border-zinc-100 flex-wrap gap-3">
            <p class="eyebrow">
                {data.customers.length.toLocaleString()} customer{data.customers.length === 1 ? '' : 's'}
                {#if data.q}<span class="text-on-surface ml-2">· filter: "{data.q}"</span>{/if}
            </p>
            <p class="font-label-sm text-xs text-secondary">
                Source: <span class="badge-bc ml-1">BC · DEMO MODE</span>
            </p>
        </div>

        {#if data.customers.length === 0}
            <p class="text-center text-secondary py-20 font-body-md text-sm">
                No customers match the filter.
            </p>
        {:else}
            <div class="overflow-x-auto">
                <table class="nrv-table">
                    <thead>
                        <tr>
                            <th>No.</th>
                            <th>Name</th>
                            <th>City</th>
                            <th>Cust Category</th>
                            <th>Business Type</th>
                            <th>Phone</th>
                            <th>Price Group</th>
                            <th>Currency</th>
                            <th class="text-right">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each data.customers as c}
                            <tr>
                                <td class="font-medium text-primary-container whitespace-nowrap">
                                    <a
                                        href={`/customers/${encodeURIComponent(c.number)}/edit`}
                                        class="hover:underline"
                                    >
                                        {c.number}
                                    </a>
                                </td>
                                <td class="font-medium">{c.displayName || '—'}</td>
                                <td class="muted">{c.city || '—'}</td>
                                <td class="whitespace-nowrap">
                                    {#if c.custCategory}
                                        <span class="badge-active">{c.custCategory}</span>
                                    {:else}<span class="muted">—</span>{/if}
                                </td>
                                <td class="whitespace-nowrap">
                                    {#if c.businessType}
                                        <span class="badge-pending">{c.businessType}</span>
                                    {:else}<span class="muted">—</span>{/if}
                                </td>
                                <td class="muted whitespace-nowrap">{c.phoneNumber || '—'}</td>
                                <td class="muted whitespace-nowrap">
                                    {#if c.customerPriceGroup}
                                        <span class="badge-pending">{c.customerPriceGroup}</span>
                                    {:else}<span class="muted">—</span>{/if}
                                </td>
                                <td class="muted whitespace-nowrap">{c.currencyCode || '—'}</td>
                                <td class="text-right whitespace-nowrap">
                                    <a
                                        href={`/customers/${encodeURIComponent(c.number)}/edit`}
                                        class="btn-outline !py-1.5 !px-4 !text-xs"
                                    >
                                        ✎ Edit
                                    </a>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        {/if}
    </div>
</div>
