<script lang="ts">
    import { onMount } from 'svelte';
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

    function fmtQty(n: number | null): string {
        if (n === null || n === undefined) return '—';
        return n.toLocaleString(undefined, { maximumFractionDigits: 0 });
    }

    // Client-side fuzzy refine: server already filtered by q on first load,
    // but typing here narrows the visible set instantly without a roundtrip.
    let liveQ = data.q;
    $: filtered = liveQ.trim()
        ? data.rows.filter((r) => {
              const t = liveQ.toLowerCase();
              return (
                  r.itemNo.toLowerCase().includes(t) ||
                  (r.itemDescription || '').toLowerCase().includes(t) ||
                  (r.variantCode || '').toLowerCase().includes(t) ||
                  (r.variantDescription || '').toLowerCase().includes(t) ||
                  (r.locationCode || '').toLowerCase().includes(t)
              );
          })
        : data.rows;

    $: distinctItems = new Set(filtered.map((r) => r.itemNo)).size;

    // Item (36%) + Variant (18%) + Location (12%) + On Hand (6%) = 72%;
    // price columns share the remaining 28%.
    $: priceColPct =
        data.priceGroups.length > 0
            ? ((100 - 72) / data.priceGroups.length).toFixed(3)
            : '0';

    // ── Synced top + bottom horizontal scrollbars ──────────────────────────
    let topScrollEl: HTMLDivElement;
    let bodyScrollEl: HTMLDivElement;
    let tableScrollWidth = 0;
    let needsHScroll = false;
    let suppressSync = false;

    function syncFromTop() {
        if (suppressSync || !bodyScrollEl || !topScrollEl) return;
        suppressSync = true;
        bodyScrollEl.scrollLeft = topScrollEl.scrollLeft;
        requestAnimationFrame(() => (suppressSync = false));
    }
    function syncFromBody() {
        if (suppressSync || !bodyScrollEl || !topScrollEl) return;
        suppressSync = true;
        topScrollEl.scrollLeft = bodyScrollEl.scrollLeft;
        requestAnimationFrame(() => (suppressSync = false));
    }

    function measure() {
        if (!bodyScrollEl) return;
        tableScrollWidth = bodyScrollEl.scrollWidth;
        needsHScroll = bodyScrollEl.scrollWidth > bodyScrollEl.clientWidth + 1;
    }

    onMount(() => {
        measure();
        const ro = new ResizeObserver(measure);
        if (bodyScrollEl) ro.observe(bodyScrollEl);
        window.addEventListener('resize', measure);
        return () => {
            ro.disconnect();
            window.removeEventListener('resize', measure);
        };
    });

    // Re-measure when the filtered set changes (column widths may shift).
    $: filtered && typeof requestAnimationFrame === 'function' && requestAnimationFrame(measure);
</script>

<div class="px-8 py-8 mx-auto max-w-[1480px]">
    <!-- Soft cyan/blue gradient hero — distinct from Customers' sky→indigo -->
    <section class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-cyan-500 via-sky-500 to-blue-600 text-white p-6 mb-6 shadow-md">
        <span class="pointer-events-none absolute -top-16 -left-16 h-64 w-64 rounded-full bg-white/15 blur-3xl"></span>
        <span class="pointer-events-none absolute -bottom-20 -right-12 h-72 w-72 rounded-full bg-cyan-200/20 blur-3xl"></span>
        <span class="pointer-events-none absolute inset-0 opacity-[0.06] bg-[radial-gradient(circle_at_1px_1px,_white_1px,_transparent_0)] [background-size:14px_14px]"></span>

        <div class="relative flex items-end justify-between gap-6 flex-wrap">
            <div class="min-w-0">
                <p class="text-[0.65rem] uppercase tracking-[0.25em] text-white/80 font-medium mb-1">Catalog · Pricing matrix</p>
                <h1 class="font-h2 text-h2 font-semibold">Pricing.</h1>
                <p class="font-body-md text-sm text-white/85 mt-2 max-w-2xl">
                    Every item × variant on one screen with prices across all customer price groups.
                    Search by item number, name, variant code, or variant description.
                </p>
            </div>
            <div class="flex items-center gap-3 flex-wrap">
                <div class="rounded-xl bg-white/15 backdrop-blur-sm px-4 py-3 border border-white/20">
                    <p class="text-[0.55rem] uppercase tracking-[0.25em] text-white/70 font-medium">SKUs</p>
                    <p class="font-h3 text-xl font-semibold tabular-nums leading-none mt-1">
                        {filtered.length.toLocaleString()}
                    </p>
                </div>
                <div class="rounded-xl bg-white/15 backdrop-blur-sm px-4 py-3 border border-white/20">
                    <p class="text-[0.55rem] uppercase tracking-[0.25em] text-white/70 font-medium">Items</p>
                    <p class="font-h3 text-xl font-semibold tabular-nums leading-none mt-1">
                        {distinctItems.toLocaleString()}
                    </p>
                </div>
                <div class="rounded-xl bg-white/15 backdrop-blur-sm px-4 py-3 border border-white/20">
                    <p class="text-[0.55rem] uppercase tracking-[0.25em] text-white/70 font-medium">Groups</p>
                    <p class="font-h3 text-xl font-semibold tabular-nums leading-none mt-1">
                        {data.priceGroups.length}
                    </p>
                </div>
            </div>
        </div>

        <div class="relative mt-5">
            <form method="GET" class="flex items-center gap-2 max-w-3xl flex-wrap">
                <div class="relative flex-1 min-w-[260px]">
                    <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-white/70" style="font-size: 18px">search</span>
                    <input
                        type="text"
                        name="q"
                        bind:value={liveQ}
                        placeholder="Item #, name, variant code/desc, location…"
                        class="w-full h-10 pl-10 pr-3 rounded-lg bg-white/20 border border-white/30 text-white placeholder-white/60 focus:bg-white/30 focus:border-white/60 focus:outline-none transition"
                    />
                </div>
                <select
                    name="location"
                    value={data.location}
                    class="h-10 px-3 rounded-lg bg-white/20 border border-white/30 text-white focus:bg-white/30 focus:border-white/60 focus:outline-none transition min-w-[140px]"
                >
                    <option value="" class="text-on-surface">All locations</option>
                    {#each data.locations as loc}
                        <option value={loc} class="text-on-surface">{loc}</option>
                    {/each}
                </select>
                <button class="h-10 px-4 rounded-lg bg-white/95 hover:bg-white text-blue-700 font-semibold text-sm transition">
                    Refresh
                </button>
            </form>
            <p class="text-[0.65rem] text-white/70 mt-2">
                Typing filters locally. Use the location filter or hit Refresh to query BC again.
            </p>
        </div>
    </section>

    {#if data.error}
        <div class="border-l-4 border-error bg-surface-container-low px-5 py-4 mb-6 flex gap-3 items-start">
            <span class="material-symbols-outlined text-error">error</span>
            <p class="font-body-md text-sm text-on-surface">{data.error}</p>
        </div>
    {/if}

    <!-- Flat pricing table -->
    <div class="card overflow-hidden">
        <div class="flex items-center justify-between px-6 py-4 border-b border-zinc-100 flex-wrap gap-3">
            <p class="eyebrow">
                {filtered.length.toLocaleString()} SKU{filtered.length === 1 ? '' : 's'} ·
                {distinctItems.toLocaleString()} item{distinctItems === 1 ? '' : 's'}
                {#if data.location}<span class="text-on-surface ml-1">· location: {data.location}</span>{/if}
                {#if liveQ}<span class="text-on-surface ml-1">· filter: "{liveQ}"</span>{/if}
            </p>
            <p class="font-label-sm text-xs text-secondary"><span class="badge-bc">BC</span></p>
        </div>

        {#if filtered.length === 0}
            <p class="text-center text-secondary py-16 font-body-md text-sm">
                {liveQ ? `No SKUs match "${liveQ}".` : 'No SKUs found.'}
            </p>
        {:else}
            <!-- Top synced horizontal scrollbar (only when overflow). -->
            {#if needsHScroll}
                <div
                    bind:this={topScrollEl}
                    on:scroll={syncFromTop}
                    class="overflow-x-auto overflow-y-hidden border-b border-zinc-100"
                    style="height: 14px"
                >
                    <div style="width: {tableScrollWidth}px; height: 1px"></div>
                </div>
            {/if}

            <!-- Body wrapper: caps vertical height so thead sticky-top has room to pin. -->
            <div
                bind:this={bodyScrollEl}
                on:scroll={syncFromBody}
                class="overflow-auto"
                style="max-height: calc(100vh - 360px)"
            >
                <table class="pricing-table">
                    <thead>
                        <tr>
                            <th class="th-corner col-item">Item</th>
                            <th class="th-corner col-variant">Variant</th>
                            <th class="th-top col-location">Location</th>
                            <th class="th-top col-onhand text-right">Avail. for Sale</th>
                            {#each data.priceGroups as g}
                                <th class="th-top col-price text-right" style="width: {priceColPct}%">
                                    {g.description ?? g.code}
                                </th>
                            {/each}
                        </tr>
                    </thead>
                    <tbody>
                        {#each filtered as r}
                            {@const available = (r.inventory ?? 0) - (r.qtyOnSalesOrder ?? 0)}
                            <tr class="row-hover">
                                <td class="td-sticky col-item">
                                    <div class="font-body-md text-sm font-medium text-on-surface truncate" title={r.itemDescription}>
                                        {r.itemDescription || '—'}
                                    </div>
                                    <div class="font-label-sm text-xs text-secondary mt-0.5">
                                        #{r.itemNo}
                                        {#if r.unitOfMeasure} · per {r.unitOfMeasure}{/if}
                                    </div>
                                </td>
                                <td class="td-sticky col-variant">
                                    <span class="font-mono-data text-[1.05rem] font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded inline-block">
                                        {r.variantCode || 'BASE'}
                                    </span>
                                    {#if r.variantDescription}
                                        <div class="font-label-sm text-xs text-secondary mt-1 truncate" title={r.variantDescription}>
                                            {r.variantDescription}
                                        </div>
                                    {/if}
                                </td>
                                <td class="col-location whitespace-nowrap">
                                    <span class="font-mono-data text-xs font-medium text-on-surface bg-zinc-100 px-1.5 py-0.5 rounded inline-block">
                                        {r.locationCode || '—'}
                                    </span>
                                </td>
                                <td class="col-onhand text-right tabular-nums whitespace-nowrap">
                                    <span
                                        class="font-body-md text-sm font-medium {available <= 0
                                            ? 'text-error'
                                            : 'text-on-surface'}"
                                    >
                                        {fmtQty(available)}
                                    </span>
                                </td>
                                {#each r.prices as p}
                                    <td class="col-price text-right tabular-nums whitespace-nowrap">
                                        <span class="font-body-md text-sm font-semibold text-on-surface">
                                            {fmtPrice(p.unitPrice, p.currency)}
                                        </span>
                                    </td>
                                {/each}
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        {/if}

        <footer class="px-6 py-4 border-t border-zinc-200 bg-surface-container-low">
            <p class="font-label-sm text-xs text-secondary">
                Prices sourced from BC Price List Lines (active sale prices, Customer Price Group source).
                Inventory aggregated across all locations. Customer's price group is applied
                automatically at quote/order time.
            </p>
        </footer>
    </div>
</div>

<style>
    .pricing-table {
        width: 100%;
        table-layout: fixed;
        border-collapse: collapse;
    }
    /* Header row */
    .pricing-table thead th {
        text-align: left;
        font-size: 0.75rem;
        line-height: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        color: rgb(82 82 91);
        padding: 0.75rem 0.75rem;
        font-weight: 500;
        background-color: white;
        position: sticky;
        top: 0;
        z-index: 20;
        box-shadow: inset 0 -1px 0 #e4e4e7;
    }
    .pricing-table thead th.text-right {
        text-align: right;
    }
    /* Sticky-top + sticky-left corner cells (Item, Variant headers) */
    .pricing-table thead th.th-corner {
        z-index: 30;
    }
    .pricing-table thead th.col-item {
        left: 0;
        box-shadow: inset 0 -1px 0 #e4e4e7, 1px 0 0 #e4e4e7;
    }
    .pricing-table thead th.col-variant {
        left: 36%;
        box-shadow: inset 0 -1px 0 #e4e4e7, 1px 0 0 #e4e4e7;
    }
    /* Body cells */
    .pricing-table tbody td {
        font-size: 0.875rem;
        line-height: 1.25rem;
        color: rgb(24 24 27);
        padding: 0.625rem 0.75rem;
        border-bottom: 1px solid #f4f4f5;
        background-color: white;
    }
    .pricing-table tbody td.td-sticky {
        position: sticky;
        z-index: 10;
        box-shadow: 1px 0 0 #f4f4f5;
    }
    .pricing-table tbody td.col-item {
        left: 0;
    }
    .pricing-table tbody td.col-variant {
        left: 36%;
    }
    /* Column widths — percentages so the table fills the wrapper exactly.
       Item (36%) + Variant (18%) + Location (12%) + On Hand (6%) = 72%;
       price columns share the remaining 28% (set inline per group count). */
    .pricing-table .col-item {
        width: 36%;
    }
    .pricing-table .col-variant {
        width: 18%;
    }
    .pricing-table .col-location {
        width: 12%;
    }
    .pricing-table .col-onhand {
        width: 6%;
    }
    .pricing-table .col-price {
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
    /* Row hover — blue tint */
    .pricing-table tbody tr.row-hover:hover td {
        background-color: #eff6ff;
    }
</style>
