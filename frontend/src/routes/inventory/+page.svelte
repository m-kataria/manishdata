<script lang="ts">
    import type { PageData } from './$types';

    export let data: PageData;

    function fmtQty(n: number): string {
        if (n === Math.floor(n)) return n.toLocaleString();
        return n.toLocaleString(undefined, { maximumFractionDigits: 5 });
    }

    // Inventory column sort: cycles none → desc → asc → none
    let invSort: 'none' | 'desc' | 'asc' = 'none';
    function cycleInvSort() {
        invSort = invSort === 'none' ? 'desc' : invSort === 'desc' ? 'asc' : 'none';
    }

    $: sortedRows =
        invSort === 'none'
            ? data.rows
            : [...data.rows].sort((a, b) => {
                  const diff = a.inventory - b.inventory;
                  return invSort === 'asc' ? diff : -diff;
              });

    $: totalRows = data.rows.length;
    $: distinctItems = new Set(data.rows.map((r) => r.itemNo)).size;
</script>

<div class="px-8 py-8 max-w-[1480px]">
    <div class="mb-8 flex items-end justify-between gap-6 flex-wrap">
        <div>
            <p class="eyebrow mb-1">Stock</p>
            <h1 class="font-h2 text-h2 text-on-surface font-semibold">Inventory.</h1>
            <p class="font-body-md text-sm text-secondary mt-2 max-w-2xl">
                Stockkeeping units (item × variant × location). Sorted by inventory descending.
                Live from BC — same view as <code class="font-mono-data text-xs bg-surface-container px-1.5 py-0.5">Stockkeeping Units</code> in Business Central.
            </p>
        </div>
        <form method="GET" class="flex items-end gap-3 flex-wrap">
            <div class="flex flex-col gap-1">
                <label for="inv-q" class="field-label">Search</label>
                <input
                    id="inv-q"
                    name="q"
                    value={data.q}
                    placeholder="Item, variant, or description"
                    class="field w-[260px]"
                />
            </div>
            <div class="flex flex-col gap-1">
                <label for="inv-loc" class="field-label">Location</label>
                <select
                    id="inv-loc"
                    name="location"
                    class="field w-[160px]"
                    value={data.location}
                >
                    <option value="">All</option>
                    {#each data.locations as loc}
                        <option value={loc}>{loc}</option>
                    {/each}
                </select>
            </div>
            <button class="btn-outline">Apply</button>
        </form>
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
                {totalRows.toLocaleString()} SKU{totalRows === 1 ? '' : 's'} ·
                {distinctItems.toLocaleString()} item{distinctItems === 1 ? '' : 's'}
                {#if data.q || data.location}
                    <span class="text-on-surface ml-1">
                        · filter:
                        {#if data.q}"{data.q}"{/if}
                        {#if data.location}{data.q ? ' · ' : ''}location: {data.location}{/if}
                    </span>
                {/if}
            </p>
            <p class="font-label-sm text-xs text-secondary">
                Source:
                <span class="badge-bc ml-1">BC · ICC ENERGY INC LIVE</span>
            </p>
        </div>

        {#if totalRows === 0}
            <div class="text-center py-20">
                <p class="font-body-md text-on-surface mb-1">No SKUs match.</p>
                <p class="font-body-md text-sm text-secondary">
                    Try a different search term or clear the filter.
                </p>
            </div>
        {:else}
            <div class="overflow-x-auto">
                <table class="nrv-table">
                    <thead>
                        <tr>
                            <th>Item No.</th>
                            <th>Variant Code</th>
                            <th>Variant Description</th>
                            <th>Description</th>
                            <th>Location</th>
                            <th>Replenishment</th>
                            <th class="text-right">
                                <button
                                    type="button"
                                    on:click={cycleInvSort}
                                    class="inline-flex items-center gap-1 cursor-pointer hover:text-primary-container transition-colors font-label-sm text-xs uppercase tracking-[0.2em] {invSort !== 'none' ? 'text-primary-container' : ''}"
                                    title="Click to sort"
                                >
                                    Inventory
                                    <span class="inline-block w-3 text-base leading-none">
                                        {#if invSort === 'asc'}↑
                                        {:else if invSort === 'desc'}↓
                                        {:else}<span class="text-secondary opacity-40">⇅</span>
                                        {/if}
                                    </span>
                                </button>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each sortedRows as r}
                            <tr>
                                <td class="font-medium text-primary-container whitespace-nowrap">{r.itemNo}</td>
                                <td class="font-mono-data text-xs text-primary-container whitespace-nowrap">
                                    {r.variantCode || '—'}
                                </td>
                                <td class="muted">{r.variantDescription || '—'}</td>
                                <td class="muted">{r.itemDescription || '—'}</td>
                                <td class="whitespace-nowrap">{r.locationCode || '—'}</td>
                                <td class="muted whitespace-nowrap">{r.replenishmentSystem || '—'}</td>
                                <td class="text-right tabular-nums whitespace-nowrap">
                                    <span
                                        class={r.inventory <= 0
                                            ? 'text-error font-medium'
                                            : r.inventory < r.reorderPoint
                                              ? 'text-amber-700 font-medium'
                                              : 'text-on-surface font-medium'}
                                    >
                                        {fmtQty(r.inventory)}
                                    </span>
                                    {#if r.unitOfMeasure}
                                        <span class="text-secondary text-xs ml-1.5">{r.unitOfMeasure}</span>
                                    {/if}
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        {/if}
    </div>
</div>
