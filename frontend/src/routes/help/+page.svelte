<script lang="ts">
    type Video = {
        title: string;
        description: string;
        url: string;
        duration?: string;
    };

    // Edit this list to add training videos. `url` can be YouTube, Vimeo,
    // SharePoint, or any embeddable / linkable host.
    const videos: Video[] = [
        {
            title: 'Getting Started',
            description: 'Tour the dashboard, customers, quotes, and orders.',
            url: '',
            duration: '—'
        },
        {
            title: 'Creating a Sales Quote',
            description: 'Pick a customer, add lines, post to Business Central.',
            url: '',
            duration: '—'
        },
        {
            title: 'Field Service Jobs',
            description: 'Dispatch jobs and link them to opportunities.',
            url: '',
            duration: '—'
        }
    ];

    // ── Panel + Corner Profile Calculator (mirrors PANEL CALCULATOR.xlsx) ───
    type CalcTab = 'overview' | 'cooler' | 'freezer' | 'combo';
    let tab: CalcTab = 'overview';
    const tabs: { id: CalcTab; label: string; icon: string }[] = [
        { id: 'overview', label: 'Overview', icon: 'info' },
        { id: 'cooler', label: 'Cooler Room', icon: 'ac_unit' },
        { id: 'freezer', label: 'Freezer Room', icon: 'severe_cold' },
        { id: 'combo', label: 'Combo Room', icon: 'view_compact' }
    ];

    // Piece count rule from the workbook: =ROUNDUP(linear_ft / 9, 0).
    function pcs(linearFt: number): number {
        if (linearFt <= 0) return 0;
        return Math.ceil(linearFt / 9);
    }
    const fmt = (n: number, d = 1) =>
        Number.isFinite(n) ? (+n.toFixed(d)).toLocaleString() : '—';

    // ── COOLER ROOM ─────────────────────────────────────────────────────────
    // Single layer panels • 4 walls + ceiling • +10% wastage
    let coolerL = 9;
    let coolerW = 10;
    let coolerH = 13;
    let coolerLayers = 1;
    let coolerWastage = 0.10;

    $: coolerLong = coolerL * coolerH * 2;        // L × H × 2
    $: coolerShort = coolerW * coolerH * 2;       // W × H × 2
    $: coolerCeil = coolerL * coolerW;            // L × W
    $: coolerSubtotal = coolerLong + coolerShort + coolerCeil;
    $: coolerPanelArea = coolerSubtotal * coolerLayers;
    $: coolerWaste = coolerPanelArea * coolerWastage;
    $: coolerTotal = coolerPanelArea + coolerWaste;

    $: coolerPP151509_lf = 2 * (2 * coolerL + 2 * coolerW);
    $: coolerPP2409_lf = 2 * coolerL + 2 * coolerW;
    $: coolerPP2609_lf = 2 * coolerL + 2 * coolerW;
    $: coolerPP6409_lf = 4 * coolerH;
    $: coolerPP151509 = pcs(coolerPP151509_lf);
    $: coolerPP2409 = pcs(coolerPP2409_lf);
    $: coolerPP2609 = pcs(coolerPP2609_lf);
    $: coolerPP6409 = pcs(coolerPP6409_lf);
    $: coolerPiecesTotal = coolerPP151509 + coolerPP2409 + coolerPP2609 + coolerPP6409;

    // ── FREEZER ROOM ────────────────────────────────────────────────────────
    // Double layer panels • 4 walls + ceiling + floor • +10% wastage
    // Excel: panel area = (long+short+ceiling) × layers + floor
    let freezerL = 8;
    let freezerW = 10;
    let freezerH = 9;
    let freezerLayers = 2;
    let freezerWastage = 0.10;

    $: freezerLong = freezerL * freezerH * 2;
    $: freezerShort = freezerW * freezerH * 2;
    $: freezerCeil = freezerL * freezerW;
    $: freezerFloor = freezerL * freezerW;
    $: freezerSubtotal = freezerLong + freezerShort + freezerCeil + freezerFloor;
    $: freezerPanelArea =
        (freezerLong + freezerShort + freezerCeil) * freezerLayers + freezerFloor;
    $: freezerWaste = freezerPanelArea * freezerWastage;
    $: freezerTotal = freezerPanelArea + freezerWaste;

    $: freezerPP151509_lf = 2 * (2 * freezerL + 2 * freezerW);
    $: freezerPP2409_lf = 2 * freezerL + 2 * freezerW;
    $: freezerPP2609_lf = 2 * freezerL + 2 * freezerW;
    $: freezerPP6409_lf = 4 * freezerH;
    $: freezerPP151509 = pcs(freezerPP151509_lf);
    $: freezerPP2409 = pcs(freezerPP2409_lf);
    $: freezerPP2609 = pcs(freezerPP2609_lf);
    $: freezerPP6409 = pcs(freezerPP6409_lf);
    $: freezerPiecesTotal = freezerPP151509 + freezerPP2409 + freezerPP2609 + freezerPP6409;

    // ── COMBO ROOM ──────────────────────────────────────────────────────────
    // Cooler (single layer, walls + ceiling) + Freezer (double layer,
    // walls + ceiling + floor). Shared wall is single-layer only — deduct
    // freezer side at the shared wall. +10% wastage on the combined total.
    let comboSharedWall: 'Length wall' | 'Width wall' = 'Length wall';
    let comboCoolerL = 10;
    let comboCoolerW = 10;
    let comboCoolerH = 9;
    let comboFreezerL = 10;
    let comboFreezerW = 10;
    let comboFreezerH = 9;
    let comboFreezerLayers = 1;     // matches workbook default (editable)
    let comboWastage = 0.10;

    // Shared wall length: Length wall → min(coolerL, freezerL); Width wall → min(coolerW, freezerW).
    $: comboSharedLen =
        comboSharedWall === 'Length wall'
            ? Math.min(comboCoolerL, comboFreezerL)
            : Math.min(comboCoolerW, comboFreezerW);
    $: comboSharedArea = comboSharedLen * comboCoolerH;  // shared length × cooler height
    // Adjustment: if freezer layers = 1, subtract 1× shared; else 2×.
    $: comboSharedAdj = comboFreezerLayers === 1 ? -comboSharedArea : -comboSharedArea * 2;

    // Cooler side
    $: comboClLong = comboCoolerL * comboCoolerH * 2;
    $: comboClShort = comboCoolerW * comboCoolerH * 2;
    $: comboClCeil = comboCoolerL * comboCoolerW;
    $: comboCoolerSubtotal = comboClLong + comboClShort + comboClCeil;
    $: comboCoolerPanel = comboCoolerSubtotal * 1; // cooler is single layer

    // Freezer side
    $: comboFzLong = comboFreezerL * comboFreezerH * 2;
    $: comboFzShort = comboFreezerW * comboFreezerH * 2;
    $: comboFzCeil = comboFreezerL * comboFreezerW;
    $: comboFzFloor = comboFreezerL * comboFreezerW;
    $: comboFreezerSubtotal = comboFzLong + comboFzShort + comboFzCeil + comboFzFloor;
    $: comboFreezerPanel =
        (comboFzLong + comboFzShort + comboFzCeil) * comboFreezerLayers + comboFzFloor;

    $: comboPanelSubtotal = comboCoolerPanel + comboFreezerPanel + comboSharedAdj;
    $: comboWaste = comboPanelSubtotal * comboWastage;
    $: comboTotal = comboPanelSubtotal + comboWaste;

    // Combo corner profiles (workbook formulas)
    $: comboPP151509_lf =
        2 * ((2 * comboCoolerL + 2 * comboCoolerW) + (2 * comboFreezerL + 2 * comboFreezerW));
    $: comboPP2409_lf =
        (2 * comboCoolerL + 2 * comboCoolerW) +
        (2 * comboFreezerL + 2 * comboFreezerW) -
        comboSharedLen;
    $: comboPP2609_lf =
        comboSharedWall === 'Width wall'
            ? 2 * ((comboCoolerL + comboFreezerL) + Math.max(comboCoolerW, comboFreezerW))
            : 2 * (Math.max(comboCoolerL, comboFreezerL) + (comboCoolerW + comboFreezerW));
    $: comboPP6409_lf = 4 * comboCoolerH + 4 * comboFreezerH;
    $: comboPP151509 = pcs(comboPP151509_lf);
    $: comboPP2409 = pcs(comboPP2409_lf);
    $: comboPP2609 = pcs(comboPP2609_lf);
    $: comboPP6409 = pcs(comboPP6409_lf);
    $: comboPiecesTotal = comboPP151509 + comboPP2409 + comboPP2609 + comboPP6409;
</script>

<div class="px-8 py-8 mx-auto max-w-[1280px]">
    <!-- Header -->
    <div class="mb-8 flex items-start justify-between gap-6 flex-wrap">
        <div>
            <p class="eyebrow mb-1">Resources</p>
            <h1 class="font-h2 text-h2 text-on-surface font-semibold">Help.</h1>
            <p class="font-body-md text-sm text-secondary mt-2">
                Training videos and field tools.
            </p>
        </div>
        <a href="mailto:support@totalitsuite.com" class="btn-ghost">
            <span class="material-symbols-outlined mr-1" style="font-size: 18px">mail</span>
            Contact support
        </a>
    </div>

    <!-- Training Videos -->
    <section class="mb-12">
        <div class="flex items-end justify-between mb-4">
            <div>
                <p class="eyebrow mb-1">Library</p>
                <h2 class="font-h3 text-h3 text-on-surface font-semibold">Training videos</h2>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {#each videos as v}
                <a
                    href={v.url || '#'}
                    target={v.url ? '_blank' : undefined}
                    rel={v.url ? 'noopener noreferrer' : undefined}
                    class="group block bg-white border border-zinc-200 rounded-card overflow-hidden hover:shadow-md hover:-translate-y-0.5 transition-all {!v.url ? 'opacity-70 pointer-events-none' : ''}"
                >
                    <div class="relative aspect-video bg-gradient-to-br from-rose-500 via-pink-600 to-rose-700 flex items-center justify-center">
                        <span class="pointer-events-none absolute inset-0 opacity-[0.08] bg-[radial-gradient(circle_at_1px_1px,_white_1px,_transparent_0)] [background-size:14px_14px]"></span>
                        <span class="material-symbols-outlined text-white/90 group-hover:scale-110 transition-transform" style="font-size: 56px">
                            play_circle
                        </span>
                        {#if v.duration}
                            <span class="absolute bottom-2 right-2 bg-black/50 text-white text-[0.65rem] font-medium px-1.5 py-0.5 rounded">
                                {v.duration}
                            </span>
                        {/if}
                    </div>
                    <div class="p-4">
                        <p class="font-body-md text-sm font-semibold text-on-surface group-hover:text-primary-container transition-colors">
                            {v.title}
                        </p>
                        <p class="font-label-sm text-xs text-secondary mt-1">{v.description}</p>
                        {#if !v.url}
                            <p class="font-label-sm text-xs text-secondary mt-2 italic">Coming soon</p>
                        {/if}
                    </div>
                </a>
            {/each}
        </div>
    </section>

    <!-- Panel + Corner Profile Calculator -->
    <section class="mb-10">
        <div class="mb-5">
            <p class="eyebrow mb-1">Tools</p>
            <h2 class="font-h3 text-h3 text-on-surface font-semibold">
                Insulation panel &amp; corner profile calculator
            </h2>
            <p class="font-body-md text-sm text-secondary mt-2">
                Square footage of insulation panels and piece counts for corner profiles.
            </p>
        </div>

        <!-- Tabs -->
        <div class="flex flex-wrap gap-1 mb-5 border-b border-zinc-200">
            {#each tabs as t}
                <button
                    type="button"
                    on:click={() => (tab = t.id)}
                    class="inline-flex items-center gap-1.5 px-4 h-10 -mb-px border-b-2 text-sm font-semibold transition-colors
                           {tab === t.id
                               ? 'border-primary-container text-primary-container'
                               : 'border-transparent text-secondary hover:text-on-surface'}"
                >
                    <span class="material-symbols-outlined" style="font-size: 18px">{t.icon}</span>
                    {t.label}
                </button>
            {/each}
        </div>

        {#if tab === 'overview'}
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
                <div class="card p-6">
                    <p class="eyebrow mb-3">Calculation rules</p>
                    <dl class="space-y-3 text-sm">
                        <div>
                            <dt class="font-semibold text-on-surface">Cooler Room</dt>
                            <dd class="text-secondary">Single layer panels · 4 walls + ceiling · +10% wastage</dd>
                        </div>
                        <div>
                            <dt class="font-semibold text-on-surface">Freezer Room</dt>
                            <dd class="text-secondary">Double layer panels · 4 walls + ceiling + floor · +10% wastage</dd>
                        </div>
                        <div>
                            <dt class="font-semibold text-on-surface">Combo Room</dt>
                            <dd class="text-secondary">
                                Cooler side (single layer, walls + ceiling) + Freezer side (double layer, walls + ceiling + floor).
                                Shared wall is single layer only — Freezer side gets one layer deducted at the shared wall.
                                +10% wastage on the combined total.
                            </dd>
                        </div>
                    </dl>
                </div>

                <div class="card p-6">
                    <p class="eyebrow mb-3 text-orange-600">Corner profile rules</p>
                    <dl class="space-y-3 text-sm">
                        <div>
                            <dt class="font-semibold text-on-surface">PP151509</dt>
                            <dd class="text-secondary">
                                Corner plastic profile 1.5"×1.5" × 9'. Inside the room covering top and bottom joints
                                (wall↔ceiling and wall↔floor). Uses Length and Width.
                            </dd>
                        </div>
                        <div>
                            <dt class="font-semibold text-on-surface">PP2409</dt>
                            <dd class="text-secondary">
                                Track plastic profile 2"×4" × 9'. Bottom only — vertical panels seat into these tracks.
                                Uses Length and Width. Combo: 7 sides total (shared wall counted once).
                            </dd>
                        </div>
                        <div>
                            <dt class="font-semibold text-on-surface">PP2609</dt>
                            <dd class="text-secondary">
                                L plastic profile 2"×6" × 9'. Outside the room covering ceiling↔wall joint at top only.
                                Combo: outer perimeter only (combined rectangle, 4 sides).
                            </dd>
                        </div>
                        <div>
                            <dt class="font-semibold text-on-surface">PP6409</dt>
                            <dd class="text-secondary">
                                Two-way plastic corner profile × 9'. At each vertical corner of the room. Uses Height.
                                Combo: 8 vertical corners total (4 per room).
                            </dd>
                        </div>
                    </dl>
                    <p class="font-label-sm text-xs text-secondary mt-4 pt-4 border-t border-zinc-100">
                        <strong>Piece count rule:</strong> Pieces = ROUNDUP(linear ft ÷ 9). Half-length remainder triggers a full additional piece.
                    </p>
                </div>
            </div>
        {/if}

        {#if tab === 'cooler'}
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
                <!-- Inputs -->
                <div class="card p-6 lg:col-span-1">
                    <p class="eyebrow mb-1">Inputs</p>
                    <h3 class="font-h3 text-h3 text-on-surface font-semibold mb-4">Cooler Room</h3>
                    <p class="text-xs text-secondary mb-4">Single layer · walls + ceiling · +10% wastage</p>

                    <div class="space-y-3">
                        <div class="grid grid-cols-3 gap-3">
                            <label class="block">
                                <span class="font-label-sm text-xs text-secondary uppercase">L (ft)</span>
                                <input type="number" bind:value={coolerL} min="0" step="0.5" class="input-yellow" />
                            </label>
                            <label class="block">
                                <span class="font-label-sm text-xs text-secondary uppercase">W (ft)</span>
                                <input type="number" bind:value={coolerW} min="0" step="0.5" class="input-yellow" />
                            </label>
                            <label class="block">
                                <span class="font-label-sm text-xs text-secondary uppercase">H (ft)</span>
                                <input type="number" bind:value={coolerH} min="0" step="0.5" class="input-yellow" />
                            </label>
                        </div>
                        <label class="block">
                            <span class="font-label-sm text-xs text-secondary uppercase">Panel layers</span>
                            <input type="number" bind:value={coolerLayers} min="1" step="1" class="input-yellow" />
                        </label>
                        <label class="block">
                            <span class="font-label-sm text-xs text-secondary uppercase">Wastage allowance</span>
                            <input type="number" bind:value={coolerWastage} min="0" step="0.01" class="input-yellow" />
                            <span class="text-[0.65rem] text-secondary">e.g. 0.10 = 10%</span>
                        </label>
                    </div>
                </div>

                <!-- Surface + panel -->
                <div class="card p-6 lg:col-span-2">
                    <p class="eyebrow mb-3">Surface area</p>
                    <table class="w-full text-sm mb-4">
                        <thead>
                            <tr class="text-left text-xs text-secondary uppercase tracking-wide">
                                <th class="py-1">Surface</th>
                                <th class="py-1">Dimensions</th>
                                <th class="py-1 text-right">Qty</th>
                                <th class="py-1 text-right">Area (sq ft)</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-zinc-100">
                            <tr><td class="py-1.5">Long walls</td><td>{coolerL}' × {coolerH}'</td><td class="text-right">2</td><td class="text-right tabular-nums">{fmt(coolerLong, 1)}</td></tr>
                            <tr><td class="py-1.5">Short walls</td><td>{coolerW}' × {coolerH}'</td><td class="text-right">2</td><td class="text-right tabular-nums">{fmt(coolerShort, 1)}</td></tr>
                            <tr><td class="py-1.5">Ceiling</td><td>{coolerL}' × {coolerW}'</td><td class="text-right">1</td><td class="text-right tabular-nums">{fmt(coolerCeil, 1)}</td></tr>
                            <tr class="bg-amber-50/50"><td class="py-1.5 font-semibold">Subtotal</td><td></td><td></td><td class="text-right tabular-nums font-semibold">{fmt(coolerSubtotal, 1)}</td></tr>
                        </tbody>
                    </table>

                    <p class="eyebrow mb-3 mt-6">Panel calculation</p>
                    <div class="grid grid-cols-2 gap-4 text-sm">
                        <div class="bg-amber-50/50 p-3 rounded">
                            <p class="text-xs text-secondary">Panel area (before wastage)</p>
                            <p class="font-semibold tabular-nums">{fmt(coolerPanelArea, 1)} sq ft</p>
                        </div>
                        <div class="bg-amber-50/50 p-3 rounded">
                            <p class="text-xs text-secondary">Wastage area</p>
                            <p class="font-semibold tabular-nums">{fmt(coolerWaste, 1)} sq ft</p>
                        </div>
                    </div>

                    <div class="mt-4 rounded-xl bg-gradient-to-br from-emerald-700 to-emerald-900 text-white p-5 relative overflow-hidden">
                        <span class="pointer-events-none absolute -top-10 -right-10 h-32 w-32 rounded-full bg-emerald-300/20 blur-2xl"></span>
                        <p class="text-[0.65rem] uppercase tracking-[0.25em] text-emerald-200 font-medium">Output</p>
                        <p class="font-h3 text-h3 font-semibold">Total panel sq ft (with wastage)</p>
                        <p class="font-h1 text-4xl font-semibold tabular-nums mt-2">{fmt(coolerTotal, 1)}</p>
                    </div>
                </div>
            </div>

            <!-- Corner profiles -->
            <div class="card p-6 mt-5">
                <p class="eyebrow mb-3 text-orange-600">Corner profiles</p>
                <table class="w-full text-sm">
                    <thead>
                        <tr class="text-left text-xs text-secondary uppercase tracking-wide">
                            <th class="py-1">Code</th>
                            <th class="py-1">Description</th>
                            <th class="py-1 text-right">Linear ft</th>
                            <th class="py-1 text-right">÷ 9</th>
                            <th class="py-1 text-right">Pieces</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-zinc-100">
                        <tr><td class="py-1.5 font-medium">PP151509</td><td class="text-secondary">Inside corner — top &amp; bottom joints</td><td class="text-right tabular-nums">{fmt(coolerPP151509_lf, 1)}</td><td class="text-right tabular-nums">{fmt(coolerPP151509_lf / 9, 2)}</td><td class="text-right tabular-nums font-semibold bg-emerald-50 text-emerald-900">{coolerPP151509}</td></tr>
                        <tr><td class="py-1.5 font-medium">PP2409</td><td class="text-secondary">Bottom track — panels seat vertically</td><td class="text-right tabular-nums">{fmt(coolerPP2409_lf, 1)}</td><td class="text-right tabular-nums">{fmt(coolerPP2409_lf / 9, 2)}</td><td class="text-right tabular-nums font-semibold bg-emerald-50 text-emerald-900">{coolerPP2409}</td></tr>
                        <tr><td class="py-1.5 font-medium">PP2609</td><td class="text-secondary">Outside corner — top only (exterior)</td><td class="text-right tabular-nums">{fmt(coolerPP2609_lf, 1)}</td><td class="text-right tabular-nums">{fmt(coolerPP2609_lf / 9, 2)}</td><td class="text-right tabular-nums font-semibold bg-emerald-50 text-emerald-900">{coolerPP2609}</td></tr>
                        <tr><td class="py-1.5 font-medium">PP6409</td><td class="text-secondary">Vertical corner — at each upright corner</td><td class="text-right tabular-nums">{fmt(coolerPP6409_lf, 1)}</td><td class="text-right tabular-nums">{fmt(coolerPP6409_lf / 9, 2)}</td><td class="text-right tabular-nums font-semibold bg-emerald-50 text-emerald-900">{coolerPP6409}</td></tr>
                        <tr class="bg-amber-50/50"><td class="py-2 font-semibold" colspan="4">Total pieces (all profiles)</td><td class="text-right tabular-nums font-semibold">{coolerPiecesTotal}</td></tr>
                    </tbody>
                </table>
            </div>
        {/if}

        {#if tab === 'freezer'}
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
                <div class="card p-6 lg:col-span-1">
                    <p class="eyebrow mb-1">Inputs</p>
                    <h3 class="font-h3 text-h3 text-on-surface font-semibold mb-4">Freezer Room</h3>
                    <p class="text-xs text-secondary mb-4">Double layer · walls + ceiling + floor · +10% wastage</p>

                    <div class="space-y-3">
                        <div class="grid grid-cols-3 gap-3">
                            <label class="block">
                                <span class="font-label-sm text-xs text-secondary uppercase">L (ft)</span>
                                <input type="number" bind:value={freezerL} min="0" step="0.5" class="input-yellow" />
                            </label>
                            <label class="block">
                                <span class="font-label-sm text-xs text-secondary uppercase">W (ft)</span>
                                <input type="number" bind:value={freezerW} min="0" step="0.5" class="input-yellow" />
                            </label>
                            <label class="block">
                                <span class="font-label-sm text-xs text-secondary uppercase">H (ft)</span>
                                <input type="number" bind:value={freezerH} min="0" step="0.5" class="input-yellow" />
                            </label>
                        </div>
                        <label class="block">
                            <span class="font-label-sm text-xs text-secondary uppercase">Panel layers</span>
                            <input type="number" bind:value={freezerLayers} min="1" step="1" class="input-yellow" />
                        </label>
                        <label class="block">
                            <span class="font-label-sm text-xs text-secondary uppercase">Wastage allowance</span>
                            <input type="number" bind:value={freezerWastage} min="0" step="0.01" class="input-yellow" />
                            <span class="text-[0.65rem] text-secondary">e.g. 0.10 = 10%</span>
                        </label>
                    </div>
                </div>

                <div class="card p-6 lg:col-span-2">
                    <p class="eyebrow mb-3">Surface area</p>
                    <table class="w-full text-sm mb-4">
                        <thead>
                            <tr class="text-left text-xs text-secondary uppercase tracking-wide">
                                <th class="py-1">Surface</th>
                                <th class="py-1">Dimensions</th>
                                <th class="py-1 text-right">Qty</th>
                                <th class="py-1 text-right">Area (sq ft)</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-zinc-100">
                            <tr><td class="py-1.5">Long walls</td><td>{freezerL}' × {freezerH}'</td><td class="text-right">2</td><td class="text-right tabular-nums">{fmt(freezerLong, 1)}</td></tr>
                            <tr><td class="py-1.5">Short walls</td><td>{freezerW}' × {freezerH}'</td><td class="text-right">2</td><td class="text-right tabular-nums">{fmt(freezerShort, 1)}</td></tr>
                            <tr><td class="py-1.5">Ceiling</td><td>{freezerL}' × {freezerW}'</td><td class="text-right">1</td><td class="text-right tabular-nums">{fmt(freezerCeil, 1)}</td></tr>
                            <tr><td class="py-1.5">Floor</td><td>{freezerL}' × {freezerW}'</td><td class="text-right">1</td><td class="text-right tabular-nums">{fmt(freezerFloor, 1)}</td></tr>
                            <tr class="bg-amber-50/50"><td class="py-1.5 font-semibold">Subtotal</td><td></td><td></td><td class="text-right tabular-nums font-semibold">{fmt(freezerSubtotal, 1)}</td></tr>
                        </tbody>
                    </table>

                    <p class="eyebrow mb-3 mt-6">Panel calculation</p>
                    <p class="text-xs text-secondary mb-3">
                        Panels = (walls + ceiling) × layers + floor. Floor is always single layer.
                    </p>
                    <div class="grid grid-cols-2 gap-4 text-sm">
                        <div class="bg-amber-50/50 p-3 rounded">
                            <p class="text-xs text-secondary">Panel area (before wastage)</p>
                            <p class="font-semibold tabular-nums">{fmt(freezerPanelArea, 1)} sq ft</p>
                        </div>
                        <div class="bg-amber-50/50 p-3 rounded">
                            <p class="text-xs text-secondary">Wastage area</p>
                            <p class="font-semibold tabular-nums">{fmt(freezerWaste, 1)} sq ft</p>
                        </div>
                    </div>

                    <div class="mt-4 rounded-xl bg-gradient-to-br from-emerald-700 to-emerald-900 text-white p-5 relative overflow-hidden">
                        <span class="pointer-events-none absolute -top-10 -right-10 h-32 w-32 rounded-full bg-emerald-300/20 blur-2xl"></span>
                        <p class="text-[0.65rem] uppercase tracking-[0.25em] text-emerald-200 font-medium">Output</p>
                        <p class="font-h3 text-h3 font-semibold">Total panel sq ft (with wastage)</p>
                        <p class="font-h1 text-4xl font-semibold tabular-nums mt-2">{fmt(freezerTotal, 1)}</p>
                    </div>
                </div>
            </div>

            <div class="card p-6 mt-5">
                <p class="eyebrow mb-3 text-orange-600">Corner profiles</p>
                <table class="w-full text-sm">
                    <thead>
                        <tr class="text-left text-xs text-secondary uppercase tracking-wide">
                            <th class="py-1">Code</th>
                            <th class="py-1">Description</th>
                            <th class="py-1 text-right">Linear ft</th>
                            <th class="py-1 text-right">÷ 9</th>
                            <th class="py-1 text-right">Pieces</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-zinc-100">
                        <tr><td class="py-1.5 font-medium">PP151509</td><td class="text-secondary">Inside corner — top &amp; bottom joints</td><td class="text-right tabular-nums">{fmt(freezerPP151509_lf, 1)}</td><td class="text-right tabular-nums">{fmt(freezerPP151509_lf / 9, 2)}</td><td class="text-right tabular-nums font-semibold bg-emerald-50 text-emerald-900">{freezerPP151509}</td></tr>
                        <tr><td class="py-1.5 font-medium">PP2409</td><td class="text-secondary">Bottom track — panels seat vertically</td><td class="text-right tabular-nums">{fmt(freezerPP2409_lf, 1)}</td><td class="text-right tabular-nums">{fmt(freezerPP2409_lf / 9, 2)}</td><td class="text-right tabular-nums font-semibold bg-emerald-50 text-emerald-900">{freezerPP2409}</td></tr>
                        <tr><td class="py-1.5 font-medium">PP2609</td><td class="text-secondary">Outside corner — top only (exterior)</td><td class="text-right tabular-nums">{fmt(freezerPP2609_lf, 1)}</td><td class="text-right tabular-nums">{fmt(freezerPP2609_lf / 9, 2)}</td><td class="text-right tabular-nums font-semibold bg-emerald-50 text-emerald-900">{freezerPP2609}</td></tr>
                        <tr><td class="py-1.5 font-medium">PP6409</td><td class="text-secondary">Vertical corner — at each upright corner</td><td class="text-right tabular-nums">{fmt(freezerPP6409_lf, 1)}</td><td class="text-right tabular-nums">{fmt(freezerPP6409_lf / 9, 2)}</td><td class="text-right tabular-nums font-semibold bg-emerald-50 text-emerald-900">{freezerPP6409}</td></tr>
                        <tr class="bg-amber-50/50"><td class="py-2 font-semibold" colspan="4">Total pieces (all profiles)</td><td class="text-right tabular-nums font-semibold">{freezerPiecesTotal}</td></tr>
                    </tbody>
                </table>
            </div>
        {/if}

        {#if tab === 'combo'}
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
                <div class="card p-6 lg:col-span-1">
                    <p class="eyebrow mb-1">Inputs</p>
                    <h3 class="font-h3 text-h3 text-on-surface font-semibold mb-4">Combo Room</h3>
                    <p class="text-xs text-secondary mb-4">Cooler + Freezer share one single-layer wall · +10% wastage</p>

                    <label class="block mb-4">
                        <span class="font-label-sm text-xs text-secondary uppercase">Shared wall</span>
                        <select bind:value={comboSharedWall} class="input-yellow">
                            <option value="Length wall">Length wall</option>
                            <option value="Width wall">Width wall</option>
                        </select>
                        <span class="text-[0.65rem] text-secondary block mt-1">
                            Length wall = rooms side-by-side along Width. Width wall = rooms end-to-end along Length.
                        </span>
                    </label>

                    <p class="eyebrow mb-2">Cooler side (ft)</p>
                    <div class="grid grid-cols-3 gap-3 mb-4">
                        <label class="block">
                            <span class="font-label-sm text-xs text-secondary uppercase">L</span>
                            <input type="number" bind:value={comboCoolerL} min="0" step="0.5" class="input-yellow" />
                        </label>
                        <label class="block">
                            <span class="font-label-sm text-xs text-secondary uppercase">W</span>
                            <input type="number" bind:value={comboCoolerW} min="0" step="0.5" class="input-yellow" />
                        </label>
                        <label class="block">
                            <span class="font-label-sm text-xs text-secondary uppercase">H</span>
                            <input type="number" bind:value={comboCoolerH} min="0" step="0.5" class="input-yellow" />
                        </label>
                    </div>

                    <p class="eyebrow mb-2">Freezer side (ft)</p>
                    <div class="grid grid-cols-3 gap-3 mb-4">
                        <label class="block">
                            <span class="font-label-sm text-xs text-secondary uppercase">L</span>
                            <input type="number" bind:value={comboFreezerL} min="0" step="0.5" class="input-yellow" />
                        </label>
                        <label class="block">
                            <span class="font-label-sm text-xs text-secondary uppercase">W</span>
                            <input type="number" bind:value={comboFreezerW} min="0" step="0.5" class="input-yellow" />
                        </label>
                        <label class="block">
                            <span class="font-label-sm text-xs text-secondary uppercase">H</span>
                            <input type="number" bind:value={comboFreezerH} min="0" step="0.5" class="input-yellow" />
                        </label>
                    </div>

                    <label class="block mb-3">
                        <span class="font-label-sm text-xs text-secondary uppercase">Freezer panel layers</span>
                        <input type="number" bind:value={comboFreezerLayers} min="1" step="1" class="input-yellow" />
                    </label>
                    <label class="block">
                        <span class="font-label-sm text-xs text-secondary uppercase">Wastage allowance</span>
                        <input type="number" bind:value={comboWastage} min="0" step="0.01" class="input-yellow" />
                        <span class="text-[0.65rem] text-secondary">e.g. 0.10 = 10%</span>
                    </label>
                </div>

                <div class="card p-6 lg:col-span-2">
                    <p class="eyebrow mb-3">Surface area · Cooler side</p>
                    <table class="w-full text-sm mb-4">
                        <thead>
                            <tr class="text-left text-xs text-secondary uppercase tracking-wide">
                                <th class="py-1">Surface</th>
                                <th class="py-1 text-right">Qty</th>
                                <th class="py-1 text-right">Area (sq ft)</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-zinc-100">
                            <tr><td class="py-1.5">Long walls</td><td class="text-right">2</td><td class="text-right tabular-nums">{fmt(comboClLong, 1)}</td></tr>
                            <tr><td class="py-1.5">Short walls</td><td class="text-right">2</td><td class="text-right tabular-nums">{fmt(comboClShort, 1)}</td></tr>
                            <tr><td class="py-1.5">Ceiling</td><td class="text-right">1</td><td class="text-right tabular-nums">{fmt(comboClCeil, 1)}</td></tr>
                            <tr class="bg-amber-50/50"><td class="py-1.5 font-semibold">Cooler subtotal</td><td></td><td class="text-right tabular-nums font-semibold">{fmt(comboCoolerSubtotal, 1)}</td></tr>
                        </tbody>
                    </table>

                    <p class="eyebrow mb-3 mt-6">Surface area · Freezer side</p>
                    <table class="w-full text-sm mb-4">
                        <thead>
                            <tr class="text-left text-xs text-secondary uppercase tracking-wide">
                                <th class="py-1">Surface</th>
                                <th class="py-1 text-right">Qty</th>
                                <th class="py-1 text-right">Area (sq ft)</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-zinc-100">
                            <tr><td class="py-1.5">Long walls</td><td class="text-right">2</td><td class="text-right tabular-nums">{fmt(comboFzLong, 1)}</td></tr>
                            <tr><td class="py-1.5">Short walls</td><td class="text-right">2</td><td class="text-right tabular-nums">{fmt(comboFzShort, 1)}</td></tr>
                            <tr><td class="py-1.5">Ceiling</td><td class="text-right">1</td><td class="text-right tabular-nums">{fmt(comboFzCeil, 1)}</td></tr>
                            <tr><td class="py-1.5">Floor</td><td class="text-right">1</td><td class="text-right tabular-nums">{fmt(comboFzFloor, 1)}</td></tr>
                            <tr class="bg-amber-50/50"><td class="py-1.5 font-semibold">Freezer subtotal</td><td></td><td class="text-right tabular-nums font-semibold">{fmt(comboFreezerSubtotal, 1)}</td></tr>
                        </tbody>
                    </table>

                    <p class="eyebrow mb-3 mt-6">Panel calculation</p>
                    <table class="w-full text-sm mb-4">
                        <tbody class="divide-y divide-zinc-100">
                            <tr><td class="py-1.5">Cooler panel area (× 1 layer)</td><td class="text-right tabular-nums">{fmt(comboCoolerPanel, 1)}</td></tr>
                            <tr><td class="py-1.5">Freezer panel area (× {comboFreezerLayers} layer{comboFreezerLayers === 1 ? '' : 's'} on walls+ceiling, 1 on floor)</td><td class="text-right tabular-nums">{fmt(comboFreezerPanel, 1)}</td></tr>
                            <tr><td class="py-1.5">Shared wall adjustment <span class="text-xs text-secondary">(shared {fmt(comboSharedLen, 1)}' × {comboCoolerH}' = {fmt(comboSharedArea, 1)} sq ft)</span></td><td class="text-right tabular-nums">{fmt(comboSharedAdj, 1)}</td></tr>
                            <tr class="bg-amber-50/50"><td class="py-1.5 font-semibold">Subtotal panel area</td><td class="text-right tabular-nums font-semibold">{fmt(comboPanelSubtotal, 1)}</td></tr>
                            <tr><td class="py-1.5">Wastage area</td><td class="text-right tabular-nums">{fmt(comboWaste, 1)}</td></tr>
                        </tbody>
                    </table>

                    <div class="mt-4 rounded-xl bg-gradient-to-br from-emerald-700 to-emerald-900 text-white p-5 relative overflow-hidden">
                        <span class="pointer-events-none absolute -top-10 -right-10 h-32 w-32 rounded-full bg-emerald-300/20 blur-2xl"></span>
                        <p class="text-[0.65rem] uppercase tracking-[0.25em] text-emerald-200 font-medium">Output</p>
                        <p class="font-h3 text-h3 font-semibold">Total panel sq ft (with wastage)</p>
                        <p class="font-h1 text-4xl font-semibold tabular-nums mt-2">{fmt(comboTotal, 1)}</p>
                    </div>
                </div>
            </div>

            <div class="card p-6 mt-5">
                <p class="eyebrow mb-3 text-orange-600">Corner profiles — Combo</p>
                <table class="w-full text-sm">
                    <thead>
                        <tr class="text-left text-xs text-secondary uppercase tracking-wide">
                            <th class="py-1">Code</th>
                            <th class="py-1">Description</th>
                            <th class="py-1 text-right">Linear ft</th>
                            <th class="py-1 text-right">÷ 9</th>
                            <th class="py-1 text-right">Pieces</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-zinc-100">
                        <tr><td class="py-1.5 font-medium">PP151509</td><td class="text-secondary">Inside corner — top &amp; bottom joints</td><td class="text-right tabular-nums">{fmt(comboPP151509_lf, 1)}</td><td class="text-right tabular-nums">{fmt(comboPP151509_lf / 9, 2)}</td><td class="text-right tabular-nums font-semibold bg-emerald-50 text-emerald-900">{comboPP151509}</td></tr>
                        <tr><td class="py-1.5 font-medium">PP2409</td><td class="text-secondary">Bottom track — 7 sides (shared counted once)</td><td class="text-right tabular-nums">{fmt(comboPP2409_lf, 1)}</td><td class="text-right tabular-nums">{fmt(comboPP2409_lf / 9, 2)}</td><td class="text-right tabular-nums font-semibold bg-emerald-50 text-emerald-900">{comboPP2409}</td></tr>
                        <tr><td class="py-1.5 font-medium">PP2609</td><td class="text-secondary">Outside corner — outer perimeter (4 sides)</td><td class="text-right tabular-nums">{fmt(comboPP2609_lf, 1)}</td><td class="text-right tabular-nums">{fmt(comboPP2609_lf / 9, 2)}</td><td class="text-right tabular-nums font-semibold bg-emerald-50 text-emerald-900">{comboPP2609}</td></tr>
                        <tr><td class="py-1.5 font-medium">PP6409</td><td class="text-secondary">Vertical corner — 8 corners (4 per room)</td><td class="text-right tabular-nums">{fmt(comboPP6409_lf, 1)}</td><td class="text-right tabular-nums">{fmt(comboPP6409_lf / 9, 2)}</td><td class="text-right tabular-nums font-semibold bg-emerald-50 text-emerald-900">{comboPP6409}</td></tr>
                        <tr class="bg-amber-50/50"><td class="py-2 font-semibold" colspan="4">Total pieces (all profiles)</td><td class="text-right tabular-nums font-semibold">{comboPiecesTotal}</td></tr>
                    </tbody>
                </table>
            </div>
        {/if}

        <p class="text-[0.7rem] text-secondary mt-6 italic">
            Mirrors PANEL CALCULATOR.xlsx. Yellow inputs are editable. Green totals are calculated outputs.
            Piece count uses ROUNDUP(linear ft ÷ 9).
        </p>
    </section>
</div>

<style>
    /* Yellow input affordance, matching the workbook's "editable input" convention. */
    :global(.input-yellow) {
        margin-top: 0.25rem;
        width: 100%;
        border: 1px solid #e5b800;
        background-color: #fffbea;
        color: #0a213b;
        font-weight: 600;
        border-radius: 0.375rem;
        padding: 0.5rem 0.75rem;
        font-size: 0.875rem;
    }
    :global(.input-yellow:focus) {
        outline: 2px solid var(--md-sys-color-primary-container, #e5b800);
        outline-offset: 2px;
    }
</style>
