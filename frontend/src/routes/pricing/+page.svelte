<script lang="ts">
    import type { PageData } from './$types';

    export let data: PageData;

    function fmtPrice(n: number | null, currency: string): string {
        if (n === null || n === undefined) return '—';
        return n.toLocaleString(undefined, {
            style: 'currency',
            currency,
            maximumFractionDigits: 2
        });
    }

    $: hasSelection = !!data.matrix;
    $: itemHref = (number: string) =>
        `/pricing?${data.q ? `q=${encodeURIComponent(data.q)}&` : ''}item=${encodeURIComponent(number)}`;
</script>

<div class="px-8 py-8 max-w-[1280px]">
    <div class="mb-8 flex items-end justify-between gap-6 flex-wrap">
        <div>
            <p class="eyebrow mb-1">Catalog</p>
            <h1 class="font-h2 text-h2 text-on-surface font-semibold">Pricing.</h1>
            <p class="font-body-md text-sm text-secondary mt-2 max-w-2xl">
                Pick an item to see every variant's price across all customer price groups —
                Contractor, End User, Wholesale, Retail.
            </p>
        </div>
        <form method="GET" class="flex items-end gap-3 min-w-[360px]">
            <div class="flex flex-col gap-1 flex-1">
                <label for="pr-q" class="field-label">Search items</label>
                <input
                    id="pr-q"
                    name="q"
                    value={data.q}
                    placeholder="Item number or name"
                    class="field"
                />
            </div>
            <button class="btn-outline">Search</button>
        </form>
    </div>

    {#if data.itemsError}
        <div class="border-l-4 border-error bg-surface-container-low px-5 py-4 mb-6 flex gap-3 items-start">
            <span class="material-symbols-outlined text-error">error</span>
            <p class="font-body-md text-sm text-on-surface">{data.itemsError}</p>
        </div>
    {/if}

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
        <!-- Item list (left column) -->
        <aside class="card lg:col-span-4 overflow-hidden self-start">
            <div class="px-5 py-4 border-b border-zinc-100 flex items-center justify-between">
                <p class="eyebrow">
                    {data.items.length} item{data.items.length === 1 ? '' : 's'}
                </p>
                <p class="font-label-sm text-xs text-secondary">
                    <span class="badge-bc">BC</span>
                </p>
            </div>

            {#if data.items.length === 0}
                <p class="text-center text-secondary py-12 font-body-md text-sm">
                    No items match "{data.q}".
                </p>
            {:else}
                <ul class="max-h-[640px] overflow-y-auto">
                    {#each data.items as item}
                        {@const active = item.number === data.selectedItemNumber}
                        <li>
                            <a
                                href={itemHref(item.number)}
                                class="block px-5 py-3 border-b border-zinc-100 last:border-b-0 transition-colors {active
                                    ? 'bg-surface-container-high border-l-4 border-l-primary-container'
                                    : 'hover:bg-surface-container-low border-l-4 border-l-transparent'}"
                            >
                                <div class="flex items-center justify-between gap-2">
                                    <div class="min-w-0">
                                        <div
                                            class="font-body-md text-sm font-medium {active
                                                ? 'text-primary-container'
                                                : 'text-on-surface'} truncate"
                                        >
                                            {item.displayName}
                                        </div>
                                        <div class="font-label-sm text-xs text-secondary mt-0.5">
                                            #{item.number}
                                            {#if item.baseUnitOfMeasure}
                                                <span> · per {item.baseUnitOfMeasure}</span>
                                            {/if}
                                            {#if item.variantCount}
                                                <span> · {item.variantCount} variants</span>
                                            {/if}
                                        </div>
                                    </div>
                                    {#if active}
                                        <span class="material-symbols-outlined text-primary-container">chevron_right</span>
                                    {/if}
                                </div>
                            </a>
                        </li>
                    {/each}
                </ul>
            {/if}
        </aside>

        <!-- Pricing matrix (right column) -->
        <section class="lg:col-span-8">
            {#if data.matrixError}
                <div class="border-l-4 border-error bg-surface-container-low px-5 py-4 flex gap-3 items-start">
                    <span class="material-symbols-outlined text-error">error</span>
                    <p class="font-body-md text-sm text-on-surface">{data.matrixError}</p>
                </div>
            {:else if !hasSelection}
                <div class="card p-16 text-center">
                    <span class="material-symbols-outlined text-primary-container" style="font-size: 48px"
                        >arrow_back</span
                    >
                    <p class="font-h3 text-h3 text-on-surface font-semibold mt-3">
                        Pick an item
                    </p>
                    <p class="font-body-md text-sm text-secondary mt-2 max-w-md mx-auto">
                        Choose any item from the list to see its variants and prices across every
                        customer price group.
                    </p>
                </div>
            {:else if data.matrix}
                <article class="card overflow-hidden">
                    <header class="px-6 py-5 border-b border-zinc-200">
                        <p class="eyebrow mb-2">Item · #{data.matrix.item.number}</p>
                        <h2 class="font-h2 text-2xl text-on-surface font-semibold">
                            {data.matrix.item.displayName}
                        </h2>
                        <div class="flex items-center gap-3 mt-3 flex-wrap">
                            {#if data.matrix.item.baseUnitOfMeasure}
                                <span class="badge-pending">
                                    UoM · {data.matrix.item.baseUnitOfMeasure}
                                </span>
                            {/if}
                            <span class="badge-pending">
                                {data.matrix.variants.length} variant{data.matrix.variants.length === 1 ? '' : 's'}
                            </span>
                            <span class="badge-pending">
                                {data.matrix.priceGroups.length} price groups
                            </span>
                        </div>
                    </header>

                    <div class="overflow-x-auto">
                        <table class="nrv-table">
                            <thead>
                                <tr>
                                    <th class="sticky left-0 bg-white">Variant</th>
                                    {#each data.matrix.priceGroups as g}
                                        <th class="text-right whitespace-nowrap">
                                            {g.description ?? g.code}
                                        </th>
                                    {/each}
                                </tr>
                            </thead>
                            <tbody>
                                {#each data.matrix.variants as v}
                                    <tr>
                                        <td class="sticky left-0 bg-white border-r border-zinc-100">
                                            <div class="font-medium">
                                                {v.code || '(base)'}
                                            </div>
                                            <div class="font-label-sm text-xs text-secondary mt-0.5">
                                                {v.description}
                                            </div>
                                        </td>
                                        {#each v.prices as p}
                                            <td class="text-right tabular-nums whitespace-nowrap">
                                                <div class="font-body-md font-semibold text-on-surface">
                                                    {fmtPrice(p.unitPrice, p.currency)}
                                                </div>
                                                <div class="font-label-sm text-xs text-secondary">
                                                    {p.groupCode}
                                                </div>
                                            </td>
                                        {/each}
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>

                    <footer class="px-6 py-4 border-t border-zinc-200 bg-surface-container-low">
                        <p class="font-label-sm text-xs text-secondary">
                            Prices sourced from BC Price List Lines filtered to active sale prices
                            against Customer Price Group source type. Customer price group is
                            assigned on the customer card in BC — selecting a customer at the time
                            of quote/order automatically applies their group's column.
                        </p>
                    </footer>
                </article>
            {/if}
        </section>
    </div>
</div>
