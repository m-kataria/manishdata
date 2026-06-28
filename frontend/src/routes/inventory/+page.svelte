<script lang="ts">
    import type { PageData } from './$types';
    import LoadingBar from '$lib/components/LoadingBar.svelte';

    export let data: PageData;

    function fmtQty(n: number): string {
        if (n === Math.floor(n)) return n.toLocaleString();
        return n.toLocaleString(undefined, { maximumFractionDigits: 5 });
    }

    function fmtDate(s: string | null | undefined): string {
        if (!s || s.startsWith('0001')) return '—';
        return new Date(s).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
    }

    // Open-orders modal (shown when user clicks On SO / On PO counts)
    type OrderRow = {
        orderNumber: string;
        customerNumber?: string;
        customerName?: string;
        vendorNumber?: string;
        vendorName?: string;
        status?: string;
        orderDate?: string;
        requestedDeliveryDate?: string;
        variantCode?: string;
        locationCode?: string;
        quantity: number;
        outstanding: number;
        unitOfMeasureCode?: string;
    };
    let modalOpen = false;
    let modalKind: 'so' | 'po' = 'so';
    let modalItem = '';
    let modalLoading = false;
    let modalRows: OrderRow[] = [];
    let modalError: string | null = null;

    async function openOrdersModal(kind: 'so' | 'po', itemNo: string, variant: string, location: string) {
        modalKind = kind;
        modalItem = itemNo;
        modalOpen = true;
        modalRows = [];
        modalError = null;
        modalLoading = true;
        try {
            const params = new URLSearchParams({ itemNo });
            if (variant) params.set('variant', variant);
            if (location) params.set('location', location);
            const r = await fetch(`/api/bc/item-open-orders?${params}`);
            if (!r.ok) {
                modalError = await r.text();
                return;
            }
            const payload = await r.json();
            modalRows = kind === 'so' ? payload.salesOrders : payload.purchaseOrders;
        } catch (e) {
            modalError = (e as Error).message;
        } finally {
            modalLoading = false;
        }
    }

    function closeModal() {
        modalOpen = false;
        modalRows = [];
    }

    // Column sort: cycles desc → asc → none. Only one column active at a time.
    type SortCol =
        | 'none'
        | 'itemNo'
        | 'variantCode'
        | 'variantDescription'
        | 'itemDescription'
        | 'locationCode'
        | 'replenishmentSystem'
        | 'onhand'
        | 'available'
        | 'onso'
        | 'onpo';
    let sortCol: SortCol = 'none';
    let sortDir: 'desc' | 'asc' = 'desc';
    function cycleSort(col: Exclude<SortCol, 'none'>) {
        if (sortCol !== col) {
            sortCol = col;
            sortDir = 'desc';
        } else if (sortDir === 'desc') {
            sortDir = 'asc';
        } else {
            sortCol = 'none';
        }
    }

    function sortValue(r: typeof data.rows[number], col: SortCol): string | number {
        switch (col) {
            case 'itemNo': return r.itemNo || '';
            case 'variantCode': return r.variantCode || '';
            case 'variantDescription': return r.variantDescription || '';
            case 'itemDescription': return r.itemDescription || '';
            case 'locationCode': return r.locationCode || '';
            case 'replenishmentSystem': return r.replenishmentSystem || '';
            case 'onhand': return r.inventory;
            case 'available': return r.inventory - r.qtyOnSalesOrder;
            case 'onso': return r.qtyOnSalesOrder;
            case 'onpo': return r.qtyOnPurchOrder;
            default: return '';
        }
    }

    $: sortedRows =
        sortCol === 'none'
            ? data.rows
            : [...data.rows].sort((a, b) => {
                  const aVal = sortValue(a, sortCol);
                  const bVal = sortValue(b, sortCol);
                  let diff: number;
                  if (typeof aVal === 'number' && typeof bVal === 'number') {
                      diff = aVal - bVal;
                  } else {
                      diff = String(aVal).localeCompare(String(bVal), undefined, { numeric: true });
                  }
                  return sortDir === 'asc' ? diff : -diff;
              });

    $: totalRows = data.rows.length;
    $: distinctItems = new Set(data.rows.map((r) => r.itemNo)).size;
</script>

<div class="px-8 py-8 mx-auto max-w-[1480px]">
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
                <span class="badge-bc ml-1">BC · DEMO MODE</span>
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
                            {#each [
                                { col: 'itemNo', label: 'Item No.', right: false },
                                { col: 'variantCode', label: 'Variant Code', right: false },
                                { col: 'variantDescription', label: 'Variant Description', right: false },
                                { col: 'itemDescription', label: 'Description', right: false },
                                { col: 'locationCode', label: 'Location', right: false },
                                { col: 'replenishmentSystem', label: 'Replenishment', right: false },
                                { col: 'onhand', label: 'On Hand', right: true },
                                { col: 'available', label: 'Available for Sale', right: true },
                                { col: 'onso', label: 'On SO', right: true },
                                { col: 'onpo', label: 'On PO', right: true }
                            ] as h}
                                <th class={h.right ? 'text-right' : ''}>
                                    <button
                                        type="button"
                                        on:click={() => cycleSort(h.col)}
                                        class="inline-flex items-center gap-1 cursor-pointer hover:text-primary-container transition-colors font-label-sm text-xs uppercase tracking-[0.2em] {sortCol === h.col ? 'text-primary-container' : ''}"
                                        title={`Click to sort by ${h.label}`}
                                    >
                                        {h.label}
                                        <span class="inline-block w-3 text-base leading-none">
                                            {#if sortCol === h.col && sortDir === 'asc'}↑
                                            {:else if sortCol === h.col && sortDir === 'desc'}↓
                                            {:else}<span class="text-secondary opacity-40">⇅</span>
                                            {/if}
                                        </span>
                                    </button>
                                </th>
                            {/each}
                        </tr>
                    </thead>
                    <tbody>
                        {#each sortedRows as r}
                            {@const available = r.inventory - r.qtyOnSalesOrder}
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
                                <td class="text-right tabular-nums whitespace-nowrap">
                                    <span
                                        class={available <= 0
                                            ? 'text-error font-medium'
                                            : available < r.reorderPoint
                                              ? 'text-amber-700 font-medium'
                                              : 'text-on-surface font-medium'}
                                    >
                                        {fmtQty(available)}
                                    </span>
                                </td>
                                <td class="text-right tabular-nums whitespace-nowrap">
                                    {#if r.qtyOnSalesOrder > 0}
                                        <button
                                            type="button"
                                            class="text-primary-container hover:underline"
                                            on:click={() => openOrdersModal('so', r.itemNo, r.variantCode, r.locationCode)}
                                            title="Show open sales orders for this SKU"
                                        >{fmtQty(r.qtyOnSalesOrder)}</button>
                                    {:else}
                                        <span class="text-secondary">{fmtQty(r.qtyOnSalesOrder)}</span>
                                    {/if}
                                </td>
                                <td class="text-right tabular-nums whitespace-nowrap">
                                    {#if r.qtyOnPurchOrder > 0}
                                        <button
                                            type="button"
                                            class="text-primary-container hover:underline"
                                            on:click={() => openOrdersModal('po', r.itemNo, r.variantCode, r.locationCode)}
                                            title="Show open purchase orders for this SKU"
                                        >{fmtQty(r.qtyOnPurchOrder)}</button>
                                    {:else}
                                        <span class="text-secondary">{fmtQty(r.qtyOnPurchOrder)}</span>
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

<!-- Open SO / PO modal -->
{#if modalOpen}
    <div
        class="fixed inset-0 z-50 bg-zinc-900/60 flex items-center justify-center p-6"
        on:click|self={closeModal}
        role="dialog"
        aria-modal="true"
    >
        <div class="card max-w-3xl w-full overflow-hidden flex flex-col" style="max-height: 80vh">
            <header class="px-6 py-4 border-b border-zinc-100">
                <p class="eyebrow mb-1">{modalKind === 'so' ? 'Open Sales Orders' : 'Open Purchase Orders'}</p>
                <h2 class="font-h3 text-lg font-semibold text-on-surface">{modalItem}</h2>
            </header>
            <div class="flex-1 overflow-y-auto">
                {#if modalLoading}
                    <LoadingBar label={`Loading open ${modalKind === 'so' ? 'sales' : 'purchase'} orders from BC…`} />
                {:else if modalError}
                    <p class="px-6 py-6 border-l-4 border-error bg-surface-container-low text-on-surface font-body-md text-sm">{modalError}</p>
                {:else if modalRows.length === 0}
                    <p class="text-center text-secondary py-12 font-body-md text-sm">
                        No open {modalKind === 'so' ? 'sales orders' : 'purchase orders'} for this item.
                    </p>
                {:else if modalKind === 'po'}
                    <table class="nrv-table">
                        <thead>
                            <tr>
                                <th>PO #</th>
                                <th>Item Number</th>
                                <th>Variant</th>
                                <th>Order Date</th>
                                <th class="text-right">Outstanding</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each modalRows as row}
                                <tr>
                                    <td class="font-medium text-primary-container whitespace-nowrap">{row.orderNumber}</td>
                                    <td class="whitespace-nowrap">{modalItem}</td>
                                    <td class="font-mono-data text-xs">{row.variantCode || '—'}</td>
                                    <td class="muted whitespace-nowrap">{fmtDate(row.orderDate)}</td>
                                    <td class="text-right tabular-nums whitespace-nowrap font-medium">
                                        {fmtQty(row.outstanding)}
                                        {#if row.unitOfMeasureCode}
                                            <span class="text-secondary text-xs ml-1.5">{row.unitOfMeasureCode}</span>
                                        {/if}
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                {:else}
                    <table class="nrv-table">
                        <thead>
                            <tr>
                                <th>SO #</th>
                                <th>Customer</th>
                                <th>Variant</th>
                                <th>Location</th>
                                <th>Requested</th>
                                <th class="text-right">Qty</th>
                                <th class="text-right">Outstanding</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each modalRows as row}
                                <tr>
                                    <td class="font-medium text-primary-container whitespace-nowrap">{row.orderNumber}</td>
                                    <td>
                                        <div class="font-medium">{row.customerName || '—'}</div>
                                        <div class="font-label-sm text-xs text-secondary mt-0.5">
                                            #{row.customerNumber || ''}
                                        </div>
                                    </td>
                                    <td class="font-mono-data text-xs">{row.variantCode || '—'}</td>
                                    <td class="whitespace-nowrap">{row.locationCode || '—'}</td>
                                    <td class="muted whitespace-nowrap">{fmtDate(row.requestedDeliveryDate)}</td>
                                    <td class="text-right tabular-nums whitespace-nowrap">
                                        {fmtQty(row.quantity)}
                                    </td>
                                    <td class="text-right tabular-nums whitespace-nowrap font-medium">
                                        {fmtQty(row.outstanding)}
                                        {#if row.unitOfMeasureCode}
                                            <span class="text-secondary text-xs ml-1.5">{row.unitOfMeasureCode}</span>
                                        {/if}
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                {/if}
            </div>
            <footer class="px-6 py-3 bg-surface-container-low border-t border-zinc-200 flex justify-end">
                <button class="btn-outline !py-2 !px-4 !text-xs" on:click={closeModal}>Close</button>
            </footer>
        </div>
    </div>
{/if}
