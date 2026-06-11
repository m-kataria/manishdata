<script lang="ts">
    import { invalidateAll } from '$app/navigation';
    import type {
        BcAssemblyLine,
        BcAtoBundle,
        BcItemListing,
        BcQuoteLine,
        BcSkuRow
    } from '$lib/types';
    import type { PageData } from './$types';

    export let data: PageData;

    function fmtMoney(n: number | undefined, cur: string | undefined): string {
        if (n === null || n === undefined) return '—';
        return n.toLocaleString(undefined, {
            style: 'currency',
            currency: cur || 'CAD',
            maximumFractionDigits: 2
        });
    }

    let busy = false;
    let converting = false;

    async function convertToOrder() {
        if (!data.quote?.id) {
            alert('Quote SystemId not loaded yet — refresh and try again.');
            return;
        }
        if (!confirm(`Convert quote ${data.quoteNo} to a Sales Order?\n\nBC will release this quote and create a new SO with all lines.`)) return;
        busy = true;
        converting = true;
        try {
            const res = await fetch(`/api/bc/sales-quotes/${data.quote.id}/make-order`, {
                method: 'POST'
            });
            if (!res.ok) {
                const err = await res.text();
                alert(`Convert failed: ${err}`);
                return;
            }
            const order = await res.json();
            const orderNo = order.number || order.Number || '';
            if (orderNo && confirm(`✓ Sales Order ${orderNo} created from quote ${data.quoteNo}.\n\nOpen it now?`)) {
                window.location.href = `/orders?q=${encodeURIComponent(orderNo)}`;
            } else if (orderNo) {
                window.location.href = `/quotes`;
            } else {
                window.location.href = `/quotes`;
            }
        } finally {
            busy = false;
            converting = false;
        }
    }

    function num(e: Event): number {
        const t = e.target as HTMLInputElement;
        return parseFloat(t.value || '0') || 0;
    }

    function strVal(e: Event): string {
        const t = e.target as HTMLSelectElement | HTMLInputElement;
        return t.value;
    }

    // ── Item picker state for adding new lines ─────────────────────────────
    let pickerQuery = '';
    let pickerResults: BcItemListing[] = [];
    let pickerTimeout: ReturnType<typeof setTimeout> | null = null;
    async function searchItems() {
        if (!pickerQuery.trim()) {
            pickerResults = [];
            return;
        }
        const res = await fetch(`/api/bc/items-search?q=${encodeURIComponent(pickerQuery)}`);
        if (res.ok) pickerResults = await res.json();
    }
    function onPickerInput() {
        if (pickerTimeout) clearTimeout(pickerTimeout);
        pickerTimeout = setTimeout(searchItems, 250);
    }

    async function addLine(itemNo: string) {
        busy = true;
        try {
            const res = await fetch(`/api/bc/sales-quotes/${encodeURIComponent(data.quoteNo)}/lines`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ itemNo, quantity: 1, lineType: 'Item' })
            });
            if (!res.ok) {
                const err = await res.text();
                alert(`Add line failed: ${err}`);
                return;
            }
            pickerQuery = '';
            pickerResults = [];
            await invalidateAll();
        } finally {
            busy = false;
        }
    }

    async function patchLine(line: BcQuoteLine, patch: Record<string, unknown>) {
        busy = true;
        try {
            const res = await fetch(`/api/bc/quote-lines/${line.systemId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(patch)
            });
            if (!res.ok) {
                alert(`Update failed: ${await res.text()}`);
                return;
            }
            await invalidateAll();
        } finally {
            busy = false;
        }
    }

    async function deleteLine(line: BcQuoteLine) {
        if (!confirm(`Delete line ${line.lineNo} (${line.itemNo})?`)) return;
        busy = true;
        try {
            const res = await fetch(`/api/bc/quote-lines/${line.systemId}`, {
                method: 'DELETE'
            });
            if (!res.ok) {
                alert(`Delete failed: ${await res.text()}`);
                return;
            }
            await invalidateAll();
        } finally {
            busy = false;
        }
    }

    // ── ATO modal state ────────────────────────────────────────────────────
    let atoLine: BcQuoteLine | null = null;
    let atoBundle: BcAtoBundle | null = null;
    let atoLoading = false;
    let atoError: string | null = null;
    // Per-item variant lists cached during the modal lifetime
    const variantsCache: Record<string, { code: string; description: string }[]> = {};

    async function openAto(line: BcQuoteLine) {
        atoLine = line;
        atoBundle = null;
        atoError = null;
        atoLoading = true;
        try {
            const res = await fetch(
                `/api/bc/sales-quotes/${encodeURIComponent(data.quoteNo)}/lines/${line.lineNo}/ato-lines`
            );
            if (!res.ok) {
                atoError = await res.text();
                return;
            }
            atoBundle = await res.json();
            // Preload variants for each item in the bundle
            if (atoBundle?.lines) {
                const itemNos = Array.from(new Set(atoBundle.lines.map((l) => l.itemNo)));
                await Promise.all(itemNos.map((n) => loadVariants(n)));
            }
        } finally {
            atoLoading = false;
        }
    }

    function closeAto() {
        atoLine = null;
        atoBundle = null;
        atoError = null;
    }

    async function loadVariants(itemNo: string) {
        if (variantsCache[itemNo]) return;
        try {
            const r = await fetch(`/api/bc/sku-inventory?q=${encodeURIComponent(itemNo)}&top=200`);
            if (!r.ok) return;
            const rows: BcSkuRow[] = await r.json();
            const seen = new Set<string>();
            const out: { code: string; description: string }[] = [];
            for (const row of rows) {
                if (row.itemNo !== itemNo) continue;
                if (!row.variantCode) continue;
                if (seen.has(row.variantCode)) continue;
                seen.add(row.variantCode);
                out.push({ code: row.variantCode, description: row.variantDescription || '' });
            }
            variantsCache[itemNo] = out;
        } catch {
            variantsCache[itemNo] = [];
        }
    }

    async function patchAtoLine(line: BcAssemblyLine, patch: Record<string, unknown>) {
        const res = await fetch(`/api/bc/ato-lines/${line.systemId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(patch)
        });
        if (!res.ok) {
            alert(`ATO update failed: ${await res.text()}`);
            return;
        }
        if (atoLine) await openAto(atoLine);
    }

    async function deleteAtoLine(line: BcAssemblyLine) {
        if (!confirm(`Delete component ${line.itemNo}?`)) return;
        const res = await fetch(`/api/bc/ato-lines/${line.systemId}`, { method: 'DELETE' });
        if (!res.ok) {
            alert(`Delete failed: ${await res.text()}`);
            return;
        }
        if (atoLine) await openAto(atoLine);
    }

    let newAtoItemNo = '';
    let newAtoQty = 1;
    async function addAtoLine() {
        if (!atoBundle || !newAtoItemNo) return;
        const res = await fetch(`/api/bc/ato-lines`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                assemblyDocType: atoBundle.assemblyDocType,
                assemblyDocNo: atoBundle.assemblyDocNo,
                itemNo: newAtoItemNo,
                quantity: newAtoQty
            })
        });
        if (!res.ok) {
            alert(`Add failed: ${await res.text()}`);
            return;
        }
        newAtoItemNo = '';
        newAtoQty = 1;
        if (atoLine) await openAto(atoLine);
    }

    $: linesTotal = data.lines.reduce((s, l) => s + (l.amountIncludingTax ?? 0), 0);
</script>

<div class="px-8 py-8 max-w-[1480px]">
    <div class="mb-6 flex items-end justify-between gap-6 flex-wrap">
        <div>
            <p class="eyebrow mb-1"><a href="/quotes" class="hover:text-primary-container">Quotes</a> · Edit</p>
            <h1 class="font-h2 text-h2 text-on-surface font-semibold">
                {data.quoteNo}.
            </h1>
            {#if data.quote}
                <p class="font-body-md text-sm text-secondary mt-2">
                    {data.quote.shipToName || data.quote.customerName || '—'} ·
                    {data.quote.status}
                </p>
            {/if}
        </div>
        <div class="flex items-center gap-3 flex-wrap">
            <a href="/quotes" class="btn-outline">← Back to quotes</a>
            <button
                type="button"
                on:click={convertToOrder}
                class="btn-primary"
                disabled={busy || data.lines.length === 0}
                title={data.lines.length === 0 ? 'Add at least one line first' : 'Convert this quote to a Sales Order'}
            >
                {#if converting}
                    Converting…
                {:else}
                    Convert to Order →
                {/if}
            </button>
        </div>
    </div>

    {#if data.error}
        <div class="border-l-4 border-error bg-surface-container-low px-5 py-4 mb-6 flex gap-3 items-start">
            <span class="material-symbols-outlined text-error">error</span>
            <p class="font-body-md text-sm text-on-surface">{data.error}</p>
        </div>
    {/if}

    <!-- Add line -->
    <section class="card p-6 mb-6">
        <div class="section-heading mb-4">
            <p class="font-h3 text-base font-semibold text-on-surface">Add line</p>
            <p class="font-body-md text-secondary text-sm">
                Search an item; click a result to insert. Assembly items auto-default
                <em>Qty. to Assemble</em> = quantity.
            </p>
        </div>
        <div class="flex flex-col gap-1 mb-3">
            <label for="picker" class="field-label">Item search</label>
            <input
                id="picker"
                type="text"
                bind:value={pickerQuery}
                on:input={onPickerInput}
                placeholder="Item # or name…"
                class="field"
                disabled={busy}
            />
        </div>
        {#if pickerResults.length > 0}
            <ul class="max-h-[260px] overflow-y-auto border border-zinc-200 divide-y divide-zinc-100">
                {#each pickerResults as item}
                    <li>
                        <button
                            type="button"
                            on:click={() => addLine(item.number)}
                            disabled={busy}
                            class="w-full text-left px-4 py-2.5 hover:bg-surface-container-low transition-colors flex items-center justify-between gap-3"
                        >
                            <span>
                                <span class="font-medium text-primary-container">#{item.number}</span>
                                <span class="text-on-surface ml-2">{item.displayName}</span>
                            </span>
                            <span class="font-label-sm text-xs text-secondary">+ Add</span>
                        </button>
                    </li>
                {/each}
            </ul>
        {/if}
    </section>

    <!-- Lines table -->
    <section class="card overflow-hidden mb-6">
        <div class="flex items-center justify-between px-6 py-4 border-b border-zinc-100 flex-wrap gap-3">
            <p class="eyebrow">
                {data.lines.length} line{data.lines.length === 1 ? '' : 's'}
                · total {fmtMoney(linesTotal, data.quote?.currencyCode)}
            </p>
            <p class="font-label-sm text-xs text-secondary">
                <span class="badge-bc">BC · Live</span>
            </p>
        </div>

        {#if data.lines.length === 0}
            <p class="text-center text-secondary py-12 font-body-md text-sm">
                No lines yet. Use the search above to add one.
            </p>
        {:else}
            <div class="overflow-x-auto">
                <table class="nrv-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Item</th>
                            <th>Variant</th>
                            <th>Location</th>
                            <th>Description</th>
                            <th class="text-right">Qty</th>
                            <th class="text-right">Qty to Assemble</th>
                            <th class="text-right">Unit Price</th>
                            <th class="text-right">Amount</th>
                            <th class="text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each data.lines as line}
                            <tr>
                                <td class="muted">{line.lineNo}</td>
                                <td class="font-medium text-primary-container whitespace-nowrap">{line.itemNo}</td>
                                <td class="muted">{line.variantCode || '—'}</td>
                                <td class="muted whitespace-nowrap">{line.locationCode || '—'}</td>
                                <td>{line.description || '—'}</td>
                                <td class="text-right tabular-nums">
                                    <input
                                        type="number"
                                        min="0"
                                        step="0.01"
                                        value={line.quantity}
                                        on:change={(e) => patchLine(line, { quantity: num(e) })}
                                        disabled={busy}
                                        class="field !py-1 !px-2 w-24 text-right inline-block"
                                    />
                                </td>
                                <td class="text-right tabular-nums">
                                    <input
                                        type="number"
                                        min="0"
                                        step="0.01"
                                        value={line.qtyToAssembleToOrder}
                                        on:change={(e) =>
                                            patchLine(line, { qtyToAssembleToOrder: num(e) })}
                                        disabled={busy}
                                        class="field !py-1 !px-2 w-24 text-right inline-block"
                                    />
                                </td>
                                <td class="text-right tabular-nums">
                                    {fmtMoney(line.unitPrice, data.quote?.currencyCode)}
                                </td>
                                <td class="text-right tabular-nums font-medium">
                                    {fmtMoney(line.amountIncludingTax, data.quote?.currencyCode)}
                                </td>
                                <td class="text-right whitespace-nowrap">
                                    {#if line.qtyToAssembleToOrder > 0}
                                        <button
                                            on:click={() => openAto(line)}
                                            class="btn-outline !py-1 !px-3 !text-xs"
                                            disabled={busy}
                                        >
                                            ⚙ ATO
                                        </button>
                                    {/if}
                                    <button
                                        on:click={() => deleteLine(line)}
                                        class="btn-danger !py-1 !px-3 !text-xs"
                                        disabled={busy}
                                    >
                                        ×
                                    </button>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        {/if}
    </section>
</div>

<!-- ATO modal -->
{#if atoLine}
    <div
        class="fixed inset-0 z-40 bg-zinc-900/50 flex items-start justify-center p-6 overflow-y-auto"
        on:click={closeAto}
        role="dialog"
    >
        <div
            class="bg-white rounded-card w-full max-w-[1280px] my-6 border-t-4 border-primary-container"
            on:click|stopPropagation
            role="document"
        >
            <header class="px-6 py-5 border-b border-zinc-200 flex items-center justify-between gap-4 flex-wrap">
                <div>
                    <p class="eyebrow mb-1">Assemble-to-Order Lines</p>
                    <h2 class="font-h3 text-h3 text-on-surface font-semibold">
                        {atoLine.itemNo}
                        {#if atoBundle?.assemblyDocNo}
                            <span class="font-mono-data text-sm text-secondary ml-2">
                                ({atoBundle.assemblyDocNo})
                            </span>
                        {/if}
                    </h2>
                    <p class="font-body-md text-sm text-secondary mt-1">
                        {atoLine.description || ''}
                    </p>
                </div>
                <button on:click={closeAto} class="btn-outline">Close</button>
            </header>

            {#if atoLoading}
                <div class="px-6 py-16 text-center text-secondary font-body-md text-sm">Loading…</div>
            {:else if atoError}
                <div class="px-6 py-6 border-l-4 border-error bg-surface-container-low text-on-surface">
                    {atoError}
                </div>
            {:else if atoBundle}
                {#if atoBundle.lines.length === 0}
                    <div class="px-6 py-16 text-center">
                        <p class="font-body-md text-on-surface">No ATO components yet.</p>
                        <p class="font-body-md text-sm text-secondary mt-1">
                            BC creates components from the item's Assembly BOM when Qty. to Assemble is set on the parent line. If empty, the item may not have an Assembly BOM configured.
                        </p>
                    </div>
                {:else}
                    <div class="overflow-x-auto">
                        <table class="nrv-table">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Item</th>
                                    <th>Variant</th>
                                    <th>Description</th>
                                    <th>Location</th>
                                    <th class="text-right">Qty</th>
                                    <th class="text-right">Qty per</th>
                                    <th class="text-right">UoM</th>
                                    <th class="text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {#each atoBundle.lines as line}
                                    <tr>
                                        <td class="muted">{line.lineNo}</td>
                                        <td class="font-medium text-primary-container whitespace-nowrap">{line.itemNo}</td>
                                        <td>
                                            {#if variantsCache[line.itemNo]?.length}
                                                <select
                                                    class="field !py-1 !px-2 text-sm"
                                                    value={line.variantCode || ''}
                                                    on:change={(e) =>
                                                        patchAtoLine(line, { variantCode: strVal(e) })}
                                                >
                                                    <option value="">(base)</option>
                                                    {#each variantsCache[line.itemNo] as v}
                                                        <option value={v.code}>{v.code}</option>
                                                    {/each}
                                                </select>
                                            {:else}
                                                <span class="muted">{line.variantCode || '—'}</span>
                                            {/if}
                                        </td>
                                        <td class="muted">{line.description || '—'}</td>
                                        <td class="muted whitespace-nowrap">{line.locationCode || '—'}</td>
                                        <td class="text-right tabular-nums">
                                            <input
                                                type="number"
                                                step="0.01"
                                                value={line.quantity}
                                                on:change={(e) =>
                                                    patchAtoLine(line, { quantity: num(e) })}
                                                class="field !py-1 !px-2 w-24 text-right inline-block"
                                            />
                                        </td>
                                        <td class="text-right tabular-nums">{line.quantityPer}</td>
                                        <td class="text-right">{line.unitOfMeasureCode || '—'}</td>
                                        <td class="text-right">
                                            <button
                                                on:click={() => deleteAtoLine(line)}
                                                class="btn-danger !py-1 !px-3 !text-xs"
                                            >
                                                ×
                                            </button>
                                        </td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                {/if}

                <!-- Add component -->
                <div class="px-6 py-4 border-t border-zinc-200 bg-surface-container-low">
                    <p class="eyebrow mb-3">Add component</p>
                    <div class="flex items-end gap-3 flex-wrap">
                        <div class="flex flex-col gap-1">
                            <label for="ato-item" class="field-label">Item No.</label>
                            <input
                                id="ato-item"
                                bind:value={newAtoItemNo}
                                type="text"
                                placeholder="e.g. PIR-PANELS"
                                class="field w-[220px]"
                            />
                        </div>
                        <div class="flex flex-col gap-1">
                            <label for="ato-qty" class="field-label">Qty</label>
                            <input
                                id="ato-qty"
                                bind:value={newAtoQty}
                                type="number"
                                min="0"
                                step="0.01"
                                class="field w-[120px]"
                            />
                        </div>
                        <button on:click={addAtoLine} class="btn-primary">+ Add component</button>
                    </div>
                </div>
            {/if}
        </div>
    </div>
{/if}
