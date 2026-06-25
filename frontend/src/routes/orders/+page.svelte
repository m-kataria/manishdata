<script lang="ts">
    import type { PageData } from './$types';

    export let data: PageData;

    function orderBadge(status: string): string {
        const s = status.toLowerCase();
        if (s === 'released') return 'badge-active';
        if (s === 'cancelled' || s === 'rejected') return 'badge-review';
        return 'badge-pending';
    }

    function fmtMoney(n: number, currency: string | undefined): string {
        return n.toLocaleString(undefined, {
            style: 'currency',
            currency: currency || 'CAD',
            maximumFractionDigits: 2
        });
    }

    function fmtDate(s: string | undefined): string {
        if (!s || s.startsWith('0001')) return '—';
        return new Date(s).toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    let downloading: Record<string, boolean> = {};

    async function downloadPdf(id: string, number: string) {
        downloading = { ...downloading, [id]: true };
        try {
            const res = await fetch(`/orders/${id}/pdf`);
            if (!res.ok) {
                alert(`Download failed: ${res.status}`);
                return;
            }
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${number}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (e) {
            alert(`Download error: ${(e as Error).message}`);
        } finally {
            downloading = { ...downloading, [id]: false };
        }
    }

    $: totalValue = data.orders.reduce((sum, o) => sum + (o.totalAmountIncludingTax || 0), 0);

    let sortDir: 'asc' | 'desc' = 'asc';
    function toggleSort() {
        sortDir = sortDir === 'asc' ? 'desc' : 'asc';
    }
    $: sortedOrders = [...data.orders].sort((a, b) => {
        const cmp = (a.number || '').localeCompare(b.number || '', undefined, { numeric: true });
        return sortDir === 'asc' ? cmp : -cmp;
    });
</script>

<div class="px-8 py-8 mx-auto max-w-[1480px]">
    <div class="mb-8 flex items-end justify-between gap-6 flex-wrap">
        <div>
            <p class="eyebrow mb-1">Fulfillment</p>
            <h1 class="font-h2 text-h2 text-on-surface font-semibold">Sales Orders.</h1>
            <p class="font-body-md text-sm text-secondary mt-2 max-w-2xl">
                Live from Business Central. Default view: <strong>Open</strong> orders. Download
                any order as the BC-rendered PDF.
            </p>
        </div>
        <form method="GET" class="flex items-end gap-3 flex-wrap">
            <div class="flex flex-col gap-1">
                <label for="so-q" class="field-label">Search</label>
                <input
                    id="so-q"
                    name="q"
                    value={data.q}
                    placeholder="Order #, customer #, or name"
                    class="field w-[280px]"
                />
            </div>
            <div class="flex flex-col gap-1">
                <label for="so-status" class="field-label">Status</label>
                <select
                    id="so-status"
                    name="status"
                    class="field w-[140px]"
                    value={data.status}
                >
                    <option value="">All</option>
                    <option value="Draft">Draft</option>
                    <option value="Open">Open</option>
                    <option value="Released">Released</option>
                    <option value="Pending Approval">Pending Approval</option>
                    <option value="Pending Prepayment">Pending Prepayment</option>
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
                {data.orders.length.toLocaleString()} order{data.orders.length === 1 ? '' : 's'}
                {#if data.orders.length > 0}
                    <span class="text-on-surface ml-2">· total {fmtMoney(totalValue, data.orders[0]?.currencyCode)}</span>
                {/if}
                {#if data.q || data.status}
                    <span class="text-on-surface ml-2">
                        ·
                        {#if data.q}filter: "{data.q}"{/if}
                        {#if data.q && data.status}<span> · </span>{/if}
                        {#if data.status}status: {data.status}{/if}
                    </span>
                {/if}
            </p>
            <p class="font-label-sm text-xs text-secondary">
                Source:
                <span class="badge-bc ml-1">BC · ICC ENERGY INC LIVE</span>
            </p>
        </div>

        {#if data.orders.length === 0}
            <p class="text-center text-secondary py-20 font-body-md text-sm">No orders match the filter.</p>
        {:else}
            <div class="overflow-x-auto">
                <table class="nrv-table">
                    <thead>
                        <tr>
                            <th class="whitespace-nowrap">
                                <button
                                    type="button"
                                    on:click={toggleSort}
                                    class="inline-flex items-center gap-1 hover:text-primary-container"
                                >
                                    Order #
                                    <span class="text-xs">{sortDir === 'asc' ? '▲' : '▼'}</span>
                                </button>
                            </th>
                            <th>Customer</th>
                            <th>Salesperson</th>
                            <th>Group</th>
                            <th>Order Date</th>
                            <th>Requested Delivery</th>
                            <th class="text-right">Total (incl. tax)</th>
                            <th class="text-right">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each sortedOrders as o}
                            <tr>
                                <td class="font-medium text-primary-container whitespace-nowrap">
                                    {o.number}
                                </td>
                                <td>
                                    <div class="font-medium">{o.shipToName || o.customerName || '—'}</div>
                                    <div class="font-label-sm text-xs text-secondary mt-0.5">#{o.customerNumber}</div>
                                </td>
                                <td class="muted whitespace-nowrap">{o.salesperson || '—'}</td>
                                <td class="whitespace-nowrap">
                                    {#if o.shortcutDimension1Code}
                                        <span class="badge-pending">{o.shortcutDimension1Code}</span>
                                    {:else}
                                        <span class="muted">—</span>
                                    {/if}
                                </td>
                                <td class="muted whitespace-nowrap">{fmtDate(o.orderDate)}</td>
                                <td class="muted whitespace-nowrap">{fmtDate(o.requestedDeliveryDate)}</td>
                                <td class="text-right tabular-nums whitespace-nowrap font-medium">
                                    {fmtMoney(o.totalAmountIncludingTax, o.currencyCode)}
                                </td>
                                <td class="text-right whitespace-nowrap">
                                    <button
                                        on:click={() => downloadPdf(o.id, o.number)}
                                        disabled={downloading[o.id]}
                                        class="btn-outline !py-1.5 !px-4 !text-xs"
                                    >
                                        {#if downloading[o.id]}
                                            Generating…
                                        {:else}
                                            ↓ PDF
                                        {/if}
                                    </button>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        {/if}
    </div>
</div>
