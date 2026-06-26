<script lang="ts">
    import { invalidateAll } from '$app/navigation';
    import { page } from '$app/stores';
    import LoadingBar from '$lib/components/LoadingBar.svelte';
    import type {
        BcAssemblyLine,
        BcAtoBundle,
        BcComponentPriceResponse,
        BcItemListing,
        BcQuoteLine,
        BcSkuRow
    } from '$lib/types';
    import type { PageData } from './$types';

    export let data: PageData;

    $: canDelete = $page.data.user?.role === 'superadmin';

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

    // ── Reusable confirmation modal ────────────────────────────────────────
    let confirmOpen = false;
    let confirmTitle = '';
    let confirmMessage = '';
    let confirmDetail = '';
    let confirmConfirmLabel = 'Confirm';
    let confirmCancelLabel = 'Cancel';
    let confirmDanger = false;
    let confirmResolver: ((value: boolean) => void) | null = null;

    function confirmAction(opts: {
        title: string;
        message: string;
        detail?: string;
        confirmLabel?: string;
        cancelLabel?: string;
        danger?: boolean;
    }): Promise<boolean> {
        confirmTitle = opts.title;
        confirmMessage = opts.message;
        confirmDetail = opts.detail ?? '';
        confirmConfirmLabel = opts.confirmLabel ?? 'Confirm';
        confirmCancelLabel = opts.cancelLabel ?? 'Cancel';
        confirmDanger = !!opts.danger;
        confirmOpen = true;
        return new Promise<boolean>((resolve) => {
            confirmResolver = resolve;
        });
    }

    function resolveConfirm(value: boolean) {
        confirmOpen = false;
        const resolver = confirmResolver;
        confirmResolver = null;
        if (resolver) resolver(value);
    }

    async function convertToOrder() {
        if (!data.quote?.id) {
            alert('Quote SystemId not loaded yet — refresh and try again.');
            return;
        }
        if (!(await confirmAction({
            title: `Convert ${data.quoteNo} to a Sales Order?`,
            message: 'BC will release this quote and create a new sales order with all lines.',
            confirmLabel: 'Convert',
        }))) return;
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
            if (orderNo && (await confirmAction({
                title: `Sales Order ${orderNo} created`,
                message: `Created from quote ${data.quoteNo}.`,
                confirmLabel: 'Open it now',
                cancelLabel: 'Back to quotes',
            }))) {
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
                // Send qtyToAssembleToOrder=0 so BC doesn't auto-create an
                // empty assembly order. User sets ATA manually; the subsequent
                // PATCH triggers BC to populate the assembly BOM defaults.
                body: JSON.stringify({ itemNo, quantity: 1, qtyToAssembleToOrder: 0, lineType: 'Item' })
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
        if (!(await confirmAction({
            title: 'Delete line?',
            message: `Line ${line.lineNo} — ${line.itemNo}`,
            confirmLabel: 'Delete',
            danger: true,
        }))) return;
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

    // ── Copy-from-quote modal ─────────────────────────────────────────────
    let copyOpen = false;
    let copyQuery = '';
    let copyResults: { number: string; customerNumber: string; customerName?: string }[] = [];
    let copySearching = false;
    let copyApplying = false;
    let copyApplyingFor = '';
    let copyTimer: ReturnType<typeof setTimeout> | null = null;

    function openCopy() {
        copyOpen = true;
        copyQuery = '';
        copyResults = [];
    }
    function closeCopy() {
        copyOpen = false;
        copyResults = [];
    }
    async function searchCopySource() {
        if (!copyQuery.trim()) {
            copyResults = [];
            return;
        }
        copySearching = true;
        try {
            const r = await fetch(`/api/bc/sales-quotes?q=${encodeURIComponent(copyQuery)}&top=20`);
            if (!r.ok) {
                copyResults = [];
                return;
            }
            const all = (await r.json()) as typeof copyResults;
            copyResults = all.filter((q) => q.number !== data.quoteNo);
        } finally {
            copySearching = false;
        }
    }
    function onCopyInput() {
        if (copyTimer) clearTimeout(copyTimer);
        copyTimer = setTimeout(searchCopySource, 250);
    }
    async function applyCopyFrom(sourceNo: string) {
        if (copyApplying) return;
        if (data.lines.length > 0 && !(await confirmAction({
            title: `Copy ${sourceNo} on top?`,
            message: `${data.quoteNo} already has ${data.lines.length} line${data.lines.length === 1 ? '' : 's'}.`,
            detail: `Lines from ${sourceNo} (including ATO components) will be appended. Existing lines are kept.`,
            confirmLabel: 'Copy',
        }))) return;
        copyApplying = true;
        copyApplyingFor = sourceNo;
        try {
            const r = await fetch(`/api/bc/sales-quotes/${encodeURIComponent(data.quoteNo)}/copy-from`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sourceQuoteNo: sourceNo })
            });
            if (!r.ok) {
                alert(`Copy failed: ${await r.text()}`);
                return;
            }
            const result = await r.json();
            const warnings: string[] = result.warnings ?? [];
            const summary =
                `Copied ${result.lines_copied} line(s) and ${result.ato_lines_copied} ATO component(s).` +
                (warnings.length ? `\n\nWarnings:\n${warnings.slice(0, 10).join('\n')}` : '');
            alert(summary);
            closeCopy();
            await invalidateAll();
        } finally {
            copyApplying = false;
            copyApplyingFor = '';
        }
    }

    // ── Multi-select / bulk delete for quote lines ─────────────────────────
    let selectedLines = new Set<string>();
    function toggleLineSelected(id: string) {
        if (selectedLines.has(id)) selectedLines.delete(id);
        else selectedLines.add(id);
        selectedLines = selectedLines;
    }
    function toggleAllLines(e: Event) {
        const checked = (e.target as HTMLInputElement).checked;
        selectedLines = new Set(checked ? data.lines.map((l) => l.systemId) : []);
    }
    async function deleteSelectedLines() {
        if (selectedLines.size === 0) return;
        if (!(await confirmAction({
            title: `Delete ${selectedLines.size} line${selectedLines.size === 1 ? '' : 's'}?`,
            message: 'This removes the selected lines from BC permanently.',
            confirmLabel: 'Delete',
            danger: true,
        }))) return;
        busy = true;
        const failures: string[] = [];
        try {
            for (const id of Array.from(selectedLines)) {
                const res = await fetch(`/api/bc/quote-lines/${id}`, { method: 'DELETE' });
                if (!res.ok) failures.push(`${id.slice(0, 8)}: ${await res.text()}`);
            }
            selectedLines = new Set();
            await invalidateAll();
            if (failures.length) alert(`Some deletes failed:\n${failures.join('\n')}`);
        } finally {
            busy = false;
        }
    }

    // ── ATO modal state ────────────────────────────────────────────────────
    let atoLine: BcQuoteLine | null = null;
    let atoBundle: BcAtoBundle | null = null;
    let atoLoading = false;
    let atoError: string | null = null;
    let atoPrices: BcComponentPriceResponse | null = null;
    // Per-item variant lists — reactive so dropdowns populate as fetches finish.
    let variantsCache: Record<string, { code: string; description: string }[]> = {};

    function atoPriceFor(line: BcAssemblyLine): number | null {
        if (!atoPrices) return null;
        const v = line.variantCode || '';
        const exact = atoPrices.prices.find((p) => p.itemNo === line.itemNo && p.variantCode === v);
        if (exact?.unitPrice != null) return exact.unitPrice;
        if (v) {
            const base = atoPrices.prices.find((p) => p.itemNo === line.itemNo && p.variantCode === '');
            if (base?.unitPrice != null) return base.unitPrice;
        }
        return null;
    }

    function atoLineTotal(line: BcAssemblyLine): number | null {
        const unit = atoPriceFor(line);
        if (unit == null) return null;
        return unit * (line.quantity ?? 0);
    }

    $: atoVisibleTotal = (atoBundle?.lines ?? [])
        .filter((l) => (l.quantity ?? 0) > 0)
        .reduce((sum, l) => sum + (atoLineTotal(l) ?? 0), 0);

    let atoPriceStatus = '';
    async function loadAtoPrices() {
        atoPriceStatus = '';
        if (!atoBundle?.lines?.length) {
            atoPrices = null;
            atoPriceStatus = 'no components';
            return;
        }
        if (!data.quote?.customerNumber) {
            atoPrices = null;
            atoPriceStatus = 'quote has no customerNumber on data.quote';
            return;
        }
        const components = atoBundle.lines.map((l) => ({
            itemNo: l.itemNo,
            variantCode: l.variantCode || ''
        }));
        try {
            atoPriceStatus = `POST /api/bc/component-prices (cust=${data.quote.customerNumber}, ${components.length} components)…`;
            const r = await fetch('/api/bc/component-prices', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    customerNumber: data.quote.customerNumber,
                    components
                })
            });
            if (!r.ok) {
                const txt = await r.text();
                atoPrices = null;
                atoPriceStatus = `HTTP ${r.status} from /component-prices: ${txt.slice(0, 200)}`;
                return;
            }
            atoPrices = await r.json();
            const priced = (atoPrices?.prices ?? []).filter((p) => p.unitPrice != null).length;
            atoPriceStatus = `group=${atoPrices?.priceGroup ?? '(none)'} — ${priced}/${atoPrices?.prices?.length ?? 0} components priced`;
        } catch (e) {
            atoPrices = null;
            atoPriceStatus = `fetch threw: ${e instanceof Error ? e.message : String(e)}`;
        }
    }

    // Progress state for the ATO modal loader
    let atoLoadPct = 0;
    let atoLoadStep = '';

    async function openAto(line: BcQuoteLine) {
        atoLine = line;
        atoBundle = null;
        atoError = null;
        atoPrices = null;
        atoLoading = true;
        atoLoadPct = 5;
        atoLoadStep = 'Connecting to Business Central…';
        try {
            atoLoadStep = 'Loading assembly lines…';
            atoLoadPct = 15;
            const res = await fetch(
                `/api/bc/sales-quotes/${encodeURIComponent(data.quoteNo)}/lines/${line.lineNo}/ato-lines`
            );
            if (!res.ok) {
                atoError = await res.text();
                return;
            }
            atoBundle = await res.json();
            atoLoadPct = 45;

            if (atoBundle?.lines) {
                const itemNos = Array.from(new Set(atoBundle.lines.map((l) => l.itemNo)));
                atoLoadStep = `Loading variants (${itemNos.length} item${itemNos.length === 1 ? '' : 's'})…`;
                atoLoadPct = 55;
                await Promise.all(itemNos.map((n) => loadVariants(n)));
                atoLoadPct = 75;
            }

            atoLoadStep = 'Loading customer group prices…';
            atoLoadPct = 85;
            await loadAtoPrices();
            atoLoadPct = 100;
        } finally {
            atoLoading = false;
            atoLoadStep = '';
            atoLoadPct = 0;
        }
    }

    function closeAto() {
        atoLine = null;
        atoBundle = null;
        atoError = null;
        atoPrices = null;
        selectedAtoLines = new Set();
    }

    // Rollup computation: sum(price × quantityPer) for priced components.
    // This gives a per-parent-unit price, which is what the parent sales-quote
    // line's unitPrice expects (BC multiplies by parent qty for the line total).
    $: rollupCalc = (() => {
        if (!atoBundle?.lines || !atoPrices) {
            return { total: 0, priced: 0, unpriced: 0 };
        }
        let total = 0;
        let priced = 0;
        let unpriced = 0;
        const parentQty = atoLine?.quantity ?? 1;
        for (const l of atoBundle.lines) {
            if ((l.quantity ?? 0) <= 0) continue;
            const v = l.variantCode || '';
            const exact = atoPrices.prices.find((p) => p.itemNo === l.itemNo && p.variantCode === v);
            let unit: number | null = null;
            if (exact?.unitPrice != null) unit = exact.unitPrice;
            else if (v) {
                const base = atoPrices.prices.find((p) => p.itemNo === l.itemNo && p.variantCode === '');
                if (base?.unitPrice != null) unit = base.unitPrice;
            }
            const qtyPer = l.quantityPer || (parentQty > 0 ? l.quantity / parentQty : l.quantity);
            if (unit == null || !qtyPer) {
                unpriced += 1;
                continue;
            }
            total += unit * qtyPer;
            priced += 1;
        }
        return { total, priced, unpriced };
    })();

    // Rollup confirmation modal state.
    let rollupPromptOpen = false;
    let rollupPromptItemNo = '';
    let rollupPromptPrice = '';
    let rollupPromptUnpriced = 0;
    let rollupApplying = false;

    function closeAtoWithRollupPrompt() {
        if (!atoLine || rollupCalc.total <= 0) {
            closeAto();
            return;
        }
        const cur = atoPrices?.currency || data.quote?.currencyCode || 'CAD';
        rollupPromptItemNo = atoLine.itemNo;
        rollupPromptPrice = rollupCalc.total.toLocaleString(undefined, {
            style: 'currency',
            currency: cur,
            maximumFractionDigits: 2
        });
        rollupPromptUnpriced = rollupCalc.unpriced;
        rollupPromptOpen = true;
    }

    function dismissRollup(applyClose: boolean) {
        rollupPromptOpen = false;
        if (applyClose) closeAto();
    }

    async function applyRollup() {
        if (!atoLine) {
            rollupPromptOpen = false;
            return;
        }
        rollupApplying = true;
        try {
            const res = await fetch(`/api/bc/quote-lines/${atoLine.systemId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ unitPrice: rollupCalc.total })
            });
            if (!res.ok) {
                alert(`Roll-up failed (HTTP ${res.status}): ${await res.text()}`);
                return;
            }
            await invalidateAll();
            rollupPromptOpen = false;
            closeAto();
        } finally {
            rollupApplying = false;
        }
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
            variantsCache = { ...variantsCache, [itemNo]: out };
        } catch {
            variantsCache = { ...variantsCache, [itemNo]: [] };
        }
    }

    // Preload variants for every line item in the quote so the variant
    // dropdown in the main table has options immediately.
    $: {
        if (data.lines) {
            const seen = new Set<string>();
            for (const l of data.lines) {
                if (!l.itemNo || seen.has(l.itemNo) || variantsCache[l.itemNo]) continue;
                seen.add(l.itemNo);
                loadVariants(l.itemNo);
            }
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

    function isAtoLineVisible(systemId: string): boolean {
        const match = (atoBundle?.lines ?? []).find((l) => l.systemId === systemId);
        return !!match && (match.quantity ?? 0) > 0;
    }

    async function deleteAtoLine(line: BcAssemblyLine) {
        if (!(await confirmAction({
            title: 'Remove component?',
            message: line.itemNo,
            confirmLabel: 'Remove',
            danger: true,
        }))) return;
        const failed = await removeAtoLineById(line.systemId, true);
        if (failed) {
            alert(
                `Couldn't remove ${line.itemNo}. Open assembly order ${
                    atoBundle?.assemblyDocNo || '(unknown)'
                } in BC to check what BC is blocking.`
            );
        }
    }

    // Returns true if the line is still visible after both attempts (i.e. failed).
    // BC's assemblyLines endpoint can return 500 even when the DELETE (or PATCH)
    // actually succeeded — a post-write trigger throws after the row is already
    // updated. Don't trust the HTTP status; instead, refetch the bundle and check
    // whether the line is really gone.
    async function removeAtoLineById(targetId: string, refetchBetween: boolean): Promise<boolean> {
        await fetch(`/api/bc/ato-lines/${targetId}`, { method: 'DELETE' });
        if (refetchBetween && atoLine) await openAto(atoLine);
        if (refetchBetween && !isAtoLineVisible(targetId)) return false;
        await fetch(`/api/bc/ato-lines/${targetId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quantity: 0 })
        });
        if (refetchBetween && atoLine) await openAto(atoLine);
        if (refetchBetween && !isAtoLineVisible(targetId)) return false;
        return refetchBetween;
    }

    // ── Multi-select / bulk delete for ATO components ──────────────────────
    let selectedAtoLines = new Set<string>();
    function toggleAtoSelected(id: string) {
        if (selectedAtoLines.has(id)) selectedAtoLines.delete(id);
        else selectedAtoLines.add(id);
        selectedAtoLines = selectedAtoLines;
    }
    function toggleAllAto(e: Event) {
        const checked = (e.target as HTMLInputElement).checked;
        const visible = (atoBundle?.lines ?? []).filter((l) => (l.quantity ?? 0) > 0);
        selectedAtoLines = new Set(checked ? visible.map((l) => l.systemId) : []);
    }
    async function deleteSelectedAtoLines() {
        if (selectedAtoLines.size === 0) return;
        if (!(await confirmAction({
            title: `Remove ${selectedAtoLines.size} component${selectedAtoLines.size === 1 ? '' : 's'}?`,
            message: 'The selected components will be removed from the assembly order.',
            confirmLabel: 'Remove',
            danger: true,
        }))) return;
        const ids = Array.from(selectedAtoLines);
        // Fire DELETEs without re-fetching between each, then refetch once.
        for (const id of ids) {
            await fetch(`/api/bc/ato-lines/${id}`, { method: 'DELETE' });
        }
        if (atoLine) await openAto(atoLine);
        // For any still-visible lines, fall back to PATCH quantity=0.
        const stillThere = ids.filter((id) => isAtoLineVisible(id));
        for (const id of stillThere) {
            await fetch(`/api/bc/ato-lines/${id}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ quantity: 0 })
            });
        }
        if (stillThere.length && atoLine) await openAto(atoLine);
        const failed = ids.filter((id) => isAtoLineVisible(id));
        selectedAtoLines = new Set();
        if (failed.length) {
            alert(
                `Couldn't remove ${failed.length} component${failed.length === 1 ? '' : 's'}. Open assembly order ${
                    atoBundle?.assemblyDocNo || '(unknown)'
                } in BC to check what BC is blocking.`
            );
        }
    }

    let newAtoItemNo = '';
    let newAtoQty = 1;
    let atoPickerQuery = '';
    let atoPickerResults: BcItemListing[] = [];
    let atoPickerTimeout: ReturnType<typeof setTimeout> | null = null;
    async function searchAtoItems() {
        if (!atoPickerQuery.trim()) {
            atoPickerResults = [];
            return;
        }
        const r = await fetch(`/api/bc/items-search?q=${encodeURIComponent(atoPickerQuery)}`);
        atoPickerResults = r.ok ? await r.json() : [];
    }
    function onAtoPickerInput() {
        if (atoPickerTimeout) clearTimeout(atoPickerTimeout);
        atoPickerTimeout = setTimeout(searchAtoItems, 250);
    }
    function pickAtoItem(item: BcItemListing) {
        newAtoItemNo = item.number;
        atoPickerQuery = `${item.number} — ${item.displayName ?? ''}`;
        atoPickerResults = [];
    }
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
        atoPickerQuery = '';
        atoPickerResults = [];
        if (atoLine) await openAto(atoLine);
    }

    $: linesTotal = data.lines.reduce((s, l) => s + (l.amountIncludingTax ?? 0), 0);
</script>

{#if busy}
    <!-- Top progress bar (mirrors $navigating bar in +layout.svelte) -->
    <div class="fixed top-0 left-0 right-0 z-50 h-1 bg-zinc-100 overflow-hidden">
        <div class="h-full w-2/5 bg-gradient-to-r from-primary-container to-primary nrv-indeterminate"></div>
    </div>
    <div
        class="fixed top-4 right-6 z-40 bg-white border-2 border-primary-container rounded-card px-4 py-2 flex items-center gap-2.5 pointer-events-none"
    >
        <span class="relative flex h-2.5 w-2.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-container opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-primary-container"></span>
        </span>
        <span class="font-label-sm text-xs uppercase tracking-[0.2em] text-primary-container font-semibold">
            Working…
        </span>
    </div>
{/if}

<div class="px-8 py-8 mx-auto max-w-[1480px]">
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
        <div class="section-heading mb-4 flex items-start justify-between gap-4 flex-wrap">
            <div>
                <p class="font-h3 text-base font-semibold text-on-surface">Add line</p>
                <p class="font-body-md text-secondary text-sm">
                    Search an item; click a result to insert. Assembly items auto-default
                    <em>Qty. to Assemble</em> = quantity.
                </p>
            </div>
            <button on:click={openCopy} class="btn-outline !py-2 !px-4 !text-xs" disabled={busy}>
                ⧉ Copy from another quote
            </button>
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
            <div class="flex items-center gap-3">
                {#if canDelete && selectedLines.size > 0}
                    <button
                        on:click={deleteSelectedLines}
                        disabled={busy}
                        class="btn-danger !py-1 !px-3 !text-xs"
                    >
                        Delete selected ({selectedLines.size})
                    </button>
                {/if}
                <p class="font-label-sm text-xs text-secondary">
                    <span class="badge-bc">BC · Live</span>
                </p>
            </div>
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
                            <th class="w-8">
                                <input
                                    type="checkbox"
                                    aria-label="Select all lines"
                                    on:change={toggleAllLines}
                                    checked={data.lines.length > 0 && selectedLines.size === data.lines.length}
                                />
                            </th>
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
                            <tr class={selectedLines.has(line.systemId) ? 'bg-primary-container/10' : ''}>
                                <td>
                                    <input
                                        type="checkbox"
                                        aria-label={`Select line ${line.lineNo}`}
                                        checked={selectedLines.has(line.systemId)}
                                        on:change={() => toggleLineSelected(line.systemId)}
                                    />
                                </td>
                                <td class="muted">{line.lineNo}</td>
                                <td class="font-medium text-primary-container whitespace-nowrap">{line.itemNo}</td>
                                <td>
                                    {#if variantsCache[line.itemNo]?.length}
                                        <select
                                            class="field !py-1 !px-2 text-sm"
                                            value={line.variantCode || ''}
                                            on:change={(e) => patchLine(line, { variantCode: strVal(e) })}
                                            disabled={busy}
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
                                    {#if canDelete}
                                        <button
                                            on:click={() => deleteLine(line)}
                                            class="btn-danger !py-1 !px-3 !text-xs"
                                            disabled={busy}
                                        >
                                            ×
                                        </button>
                                    {/if}
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
        on:click={closeAtoWithRollupPrompt}
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
                <div class="flex items-center gap-4 flex-wrap">
                    {#if rollupCalc.total > 0}
                        <div class="text-right">
                            <p class="eyebrow mb-0.5">Components total{#if atoPrices?.priceGroup} · {atoPrices.priceGroup}{/if}</p>
                            <p class="font-mono-data text-base text-on-surface">
                                {fmtMoney(rollupCalc.total, atoPrices?.currency || data.quote?.currencyCode)}
                            </p>
                            {#if rollupCalc.unpriced > 0}
                                <p class="text-[0.65rem] text-secondary">{rollupCalc.unpriced} unpriced skipped</p>
                            {/if}
                        </div>
                    {/if}
                    <button on:click|stopPropagation={closeAtoWithRollupPrompt} class="btn-outline">Close</button>
                </div>
            </header>

            {#if atoPriceStatus}
                <div class="px-6 py-2 bg-surface-container-low border-b border-zinc-200 font-mono-data text-xs text-secondary">
                    Group-price status: {atoPriceStatus}
                </div>
            {/if}

            {#if atoLoading}
                <LoadingBar label={atoLoadStep || 'Loading…'} pct={atoLoadPct} />
            {:else if atoError}
                <div class="px-6 py-6 border-l-4 border-error bg-surface-container-low text-on-surface">
                    {atoError}
                </div>
            {:else if atoBundle}
                <!-- Add component (moved to top) -->
                <div class="px-6 py-4 border-b border-zinc-200 bg-surface-container-low">
                    <p class="eyebrow mb-3">Add component</p>
                    <div class="flex items-end gap-3 flex-wrap">
                        <div class="flex flex-col gap-1 relative">
                            <label for="ato-item" class="field-label">Item search</label>
                            <input
                                id="ato-item"
                                type="text"
                                bind:value={atoPickerQuery}
                                on:input={onAtoPickerInput}
                                placeholder="Item # or name…"
                                class="field w-[360px]"
                                autocomplete="off"
                            />
                            {#if atoPickerResults.length > 0}
                                <ul class="absolute z-10 left-0 right-0 top-full mt-1 max-h-[240px] overflow-y-auto border border-zinc-200 bg-white shadow-md divide-y divide-zinc-100">
                                    {#each atoPickerResults as item}
                                        <li>
                                            <button
                                                type="button"
                                                on:click={() => pickAtoItem(item)}
                                                class="w-full text-left px-3 py-2 hover:bg-surface-container-low text-sm"
                                            >
                                                <span class="font-medium text-primary-container">#{item.number}</span>
                                                <span class="text-on-surface ml-2">{item.displayName}</span>
                                            </button>
                                        </li>
                                    {/each}
                                </ul>
                            {/if}
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
                        <button
                            on:click={addAtoLine}
                            class="btn-primary !text-base !font-bold !px-7 !py-3 shadow-md hover:shadow-lg ring-2 ring-primary-container/30 transition-all"
                            disabled={!newAtoItemNo}
                        >
                            + Add component
                        </button>
                    </div>
                    {#if newAtoItemNo}
                        <p class="text-xs text-secondary mt-2">
                            Will add: <span class="font-mono-data">{newAtoItemNo}</span> × {newAtoQty}
                        </p>
                    {/if}
                </div>
                {#if atoBundle.lines.length === 0}
                    <div class="px-6 py-16 text-center">
                        <p class="font-body-md text-on-surface">No ATO components yet.</p>
                        <p class="font-body-md text-sm text-secondary mt-1">
                            BC creates components from the item's Assembly BOM when Qty. to Assemble is set on the parent line. If empty, the item may not have an Assembly BOM configured.
                        </p>
                    </div>
                {:else}
                    {#if canDelete && selectedAtoLines.size > 0}
                        <div class="px-6 py-2 border-b border-zinc-200 bg-surface-container-low flex items-center justify-end">
                            <button
                                on:click={deleteSelectedAtoLines}
                                class="btn-danger !py-1 !px-3 !text-xs"
                            >
                                Delete selected ({selectedAtoLines.size})
                            </button>
                        </div>
                    {/if}
                    <div class="overflow-x-auto">
                        <table class="nrv-table">
                            <thead>
                                <tr>
                                    <th class="w-8">
                                        <input
                                            type="checkbox"
                                            aria-label="Select all components"
                                            on:change={toggleAllAto}
                                            checked={(() => {
                                                const v = (atoBundle?.lines ?? []).filter((l) => (l.quantity ?? 0) > 0);
                                                return v.length > 0 && selectedAtoLines.size === v.length;
                                            })()}
                                        />
                                    </th>
                                    <th>#</th>
                                    <th>Item</th>
                                    <th>Variant</th>
                                    <th>Description</th>
                                    <th>Location</th>
                                    <th class="text-right">Qty</th>
                                    <th class="text-right">Qty per</th>
                                    <th class="text-right">UoM</th>
                                    <th class="text-right whitespace-nowrap">
                                        Group Price{#if atoPrices?.priceGroup}
                                            <span class="block text-[0.65rem] muted font-normal tracking-[0.15em] uppercase">
                                                {atoPrices.priceGroup}
                                            </span>
                                        {/if}
                                    </th>
                                    <th class="text-right">Total</th>
                                    <th class="text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {#each atoBundle.lines.filter((l) => (l.quantity ?? 0) > 0) as line}
                                    <tr class={selectedAtoLines.has(line.systemId) ? 'bg-primary-container/10' : ''}>
                                        <td>
                                            <input
                                                type="checkbox"
                                                aria-label={`Select component ${line.itemNo}`}
                                                checked={selectedAtoLines.has(line.systemId)}
                                                on:change={() => toggleAtoSelected(line.systemId)}
                                            />
                                        </td>
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
                                        <td class="text-right tabular-nums">
                                            {fmtMoney(atoPriceFor(line) ?? undefined, atoPrices?.currency || data.quote?.currencyCode)}
                                        </td>
                                        <td class="text-right tabular-nums font-medium">
                                            {fmtMoney(atoLineTotal(line) ?? undefined, atoPrices?.currency || data.quote?.currencyCode)}
                                        </td>
                                        <td class="text-right">
                                            {#if canDelete}
                                                <button
                                                    on:click={() => deleteAtoLine(line)}
                                                    class="btn-danger !py-1 !px-3 !text-xs"
                                                >
                                                    ×
                                                </button>
                                            {/if}
                                        </td>
                                    </tr>
                                {/each}
                            </tbody>
                            <tfoot>
                                <tr class="bg-surface-container-low">
                                    <td colspan="9" class="text-right font-cta text-xs font-bold uppercase tracking-wider text-secondary">
                                        Components total
                                    </td>
                                    <td class="text-right tabular-nums font-semibold text-on-surface">
                                        {fmtMoney(atoVisibleTotal, atoPrices?.currency || data.quote?.currencyCode)}
                                    </td>
                                    <td></td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                {/if}
            {/if}
        </div>
    </div>
{/if}

<!-- Rollup confirmation modal -->
{#if rollupPromptOpen}
    <div
        class="fixed inset-0 z-50 bg-zinc-900/60 flex items-center justify-center p-6"
        on:click|self={() => dismissRollup(false)}
        role="dialog"
        aria-modal="true"
    >
        <div class="card max-w-md w-full overflow-hidden">
            <header class="px-6 py-4 border-b border-zinc-100">
                <p class="eyebrow mb-1">Roll up component prices</p>
                <h2 class="font-h3 text-lg font-semibold text-on-surface">
                    Apply to {rollupPromptItemNo}?
                </h2>
            </header>
            <div class="px-6 py-5 space-y-3">
                <div class="flex items-baseline justify-between">
                    <span class="font-body-md text-sm text-secondary">New unit price</span>
                    <span class="font-h3 text-2xl font-semibold text-on-surface tabular-nums">
                        {rollupPromptPrice}
                    </span>
                </div>
                {#if rollupPromptUnpriced > 0}
                    <p class="font-body-md text-xs text-secondary border-l-2 border-amber-400 pl-3">
                        {rollupPromptUnpriced} component{rollupPromptUnpriced === 1 ? '' : 's'}
                        had no group price and {rollupPromptUnpriced === 1 ? 'was' : 'were'} skipped.
                    </p>
                {/if}
            </div>
            <footer class="px-6 py-4 bg-surface-container-low border-t border-zinc-200 flex justify-end gap-3">
                <button
                    class="btn-outline !py-2 !px-4 !text-xs"
                    on:click={() => dismissRollup(true)}
                    disabled={rollupApplying}
                >
                    Keep existing
                </button>
                <button
                    class="btn-primary !py-2 !px-4 !text-xs"
                    on:click={applyRollup}
                    disabled={rollupApplying}
                >
                    {rollupApplying ? 'Applying…' : 'Apply'}
                </button>
            </footer>
        </div>
    </div>
{/if}

<!-- Copy-from-quote modal -->
{#if copyOpen}
    <div
        class="fixed inset-0 z-50 bg-zinc-900/60 flex items-center justify-center p-6"
        on:click|self={closeCopy}
        role="dialog"
        aria-modal="true"
    >
        <div class="card max-w-xl w-full overflow-hidden flex flex-col" style="max-height: 80vh">
            <header class="px-6 py-4 border-b border-zinc-100">
                <p class="eyebrow mb-1">Copy lines + assembly components</p>
                <h2 class="font-h3 text-lg font-semibold text-on-surface">
                    Pick a source quote
                </h2>
                <p class="font-body-md text-xs text-secondary mt-1">
                    Lines from the chosen quote — including their ATO components — will be appended to {data.quoteNo}.
                </p>
            </header>
            <div class="px-6 py-4">
                <label for="copy-search" class="field-label">Quote # or customer</label>
                <input
                    id="copy-search"
                    type="text"
                    bind:value={copyQuery}
                    on:input={onCopyInput}
                    placeholder="SQ1000… or customer number…"
                    class="field w-full"
                    autocomplete="off"
                    disabled={copyApplying}
                />
            </div>
            <div class="flex-1 overflow-y-auto px-6 pb-4">
                {#if copySearching}
                    <p class="text-secondary font-body-md text-sm py-4">Searching…</p>
                {:else if copyQuery.trim() && copyResults.length === 0}
                    <p class="text-secondary font-body-md text-sm py-4">No matching quotes.</p>
                {:else if copyResults.length > 0}
                    <ul class="divide-y divide-zinc-100 border border-zinc-200 rounded-card overflow-hidden">
                        {#each copyResults as q}
                            <li class="flex items-center justify-between px-4 py-3 hover:bg-surface-container-low">
                                <div>
                                    <p class="font-medium text-primary-container">{q.number}</p>
                                    <p class="font-body-md text-xs text-secondary">
                                        {q.customerNumber}{q.customerName ? ` · ${q.customerName}` : ''}
                                    </p>
                                </div>
                                <button
                                    class="btn-primary !py-1.5 !px-3 !text-xs"
                                    on:click={() => applyCopyFrom(q.number)}
                                    disabled={copyApplying}
                                >
                                    {copyApplying && copyApplyingFor === q.number ? 'Copying…' : 'Copy'}
                                </button>
                            </li>
                        {/each}
                    </ul>
                {/if}
            </div>
            <footer class="px-6 py-3 bg-surface-container-low border-t border-zinc-200 flex justify-end">
                <button class="btn-outline !py-2 !px-4 !text-xs" on:click={closeCopy} disabled={copyApplying}>
                    Close
                </button>
            </footer>
        </div>
    </div>
{/if}

<!-- Reusable confirmation modal -->
{#if confirmOpen}
    <div
        class="fixed inset-0 z-50 bg-zinc-900/60 flex items-center justify-center p-6"
        on:click|self={() => resolveConfirm(false)}
        role="dialog"
        aria-modal="true"
    >
        <div class="card max-w-md w-full overflow-hidden">
            <header class="px-6 py-4 border-b border-zinc-100">
                <h2 class="font-h3 text-lg font-semibold text-on-surface">
                    {confirmTitle}
                </h2>
            </header>
            <div class="px-6 py-5 space-y-2">
                <p class="font-body-md text-sm text-on-surface">{confirmMessage}</p>
                {#if confirmDetail}
                    <p class="font-body-md text-xs text-secondary border-l-2 border-amber-400 pl-3">
                        {confirmDetail}
                    </p>
                {/if}
            </div>
            <footer class="px-6 py-4 bg-surface-container-low border-t border-zinc-200 flex justify-end gap-3">
                <button class="btn-outline !py-2 !px-4 !text-xs" on:click={() => resolveConfirm(false)}>
                    {confirmCancelLabel}
                </button>
                <button
                    class={confirmDanger ? 'btn-danger !py-2 !px-4 !text-xs' : 'btn-primary !py-2 !px-4 !text-xs'}
                    on:click={() => resolveConfirm(true)}
                >
                    {confirmConfirmLabel}
                </button>
            </footer>
        </div>
    </div>
{/if}
