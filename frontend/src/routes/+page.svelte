<script lang="ts">
    import { onMount } from 'svelte';
    import { tweened } from 'svelte/motion';
    import { cubicOut } from 'svelte/easing';
    import type { PageData } from './$types';

    export let data: PageData;

    $: openQuotes = data.quotes.filter((q) => q.status === 'Draft' || q.status === 'Open');
    $: openQuotesValue = openQuotes.reduce(
        (s, q) => s + (q.totalAmountIncludingTax ?? 0),
        0
    );
    $: ordersValue = data.orders.reduce(
        (s, o) => s + (o.totalAmountIncludingTax ?? 0),
        0
    );

    $: currency = data.quotes[0]?.currencyCode || data.orders[0]?.currencyCode || 'CAD';

    function fmtMoney(n: number, cur: string): string {
        return n.toLocaleString(undefined, {
            style: 'currency',
            currency: cur,
            maximumFractionDigits: 0
        });
    }

    function fmtMoneyCompact(n: number, cur: string): string {
        return n.toLocaleString(undefined, {
            style: 'currency',
            currency: cur,
            notation: 'compact',
            maximumFractionDigits: 1
        });
    }

    function fmtDate(s: string | undefined): string {
        if (!s || s.startsWith('0001')) return '—';
        return new Date(s).toLocaleDateString(undefined, {
            month: 'short',
            day: 'numeric'
        });
    }

    function quoteBadge(status: string): string {
        const s = status.toLowerCase();
        if (s === 'released' || s === 'accepted') return 'tis-badge tis-badge-success';
        if (s === 'rejected' || s === 'expired' || s === 'cancelled') return 'tis-badge tis-badge-muted';
        return 'tis-badge tis-badge-pending';
    }

    function orderBadge(status: string): string {
        const s = status.toLowerCase();
        if (s === 'released') return 'tis-badge tis-badge-success';
        if (s === 'cancelled') return 'tis-badge tis-badge-muted';
        return 'tis-badge tis-badge-pending';
    }

    $: recentQuotes = [...data.quotes].sort((a, b) =>
        (b.number || '').localeCompare(a.number || '', undefined, { numeric: true })
    );
    $: recentOrders = [...data.orders].sort((a, b) =>
        (b.number || '').localeCompare(a.number || '', undefined, { numeric: true })
    );

    $: totalCommercial = openQuotesValue + ordersValue;
    $: quotePct = totalCommercial > 0 ? openQuotesValue / totalCommercial : 0;
    $: orderPct = totalCommercial > 0 ? ordersValue / totalCommercial : 0;
    const donutRadius = 48;
    const donutCircumference = 2 * Math.PI * donutRadius;

    const quoteArc = tweened(0, { duration: 1400, easing: cubicOut });
    const orderArc = tweened(0, { duration: 1400, easing: cubicOut, delay: 200 });
    const totalDisplay = tweened(0, { duration: 1400, easing: cubicOut });
    onMount(() => {
        quoteArc.set(quotePct);
        orderArc.set(orderPct);
        totalDisplay.set(totalCommercial);
    });

    $: bcOk =
        !!data.integrations?.businessCentral.configured &&
        data.integrations.businessCentral.lastSync?.status !== 'failed';
    $: sfOk =
        !!data.integrations?.salesforce.configured &&
        data.integrations.salesforce.lastSync?.status !== 'failed';
    $: channelsOnline = (bcOk ? 1 : 0) + (sfOk ? 1 : 0);

    const tiles = [
        { href: '/crm', label: 'CRM', sub: 'Leads & deals', icon: 'hub', special: '' },
        { href: '/customers', label: 'Customers', sub: 'Accounts', icon: 'groups', special: '' },
        { href: '/quotes', label: 'Quotes', sub: 'Quote & price', icon: 'request_quote', special: '' },
        { href: '/orders', label: 'Orders', sub: 'Fulfillment', icon: 'receipt_long', special: '' },
        { href: '/inventory', label: 'Inventory', sub: 'Stock & SKUs', icon: 'inventory_2', special: '' },
        { href: '/pricing', label: 'Pricing', sub: 'Group prices', icon: 'sell', special: '' },
        { href: '/jobs', label: 'Jobs', sub: 'Field service', icon: 'engineering', special: '' },
        { href: '/ai-agents', label: 'AI Agents', sub: 'Live workforce', icon: 'auto_awesome', special: 'ai' },
        { href: '/help', label: 'Help', sub: 'Training & tools', icon: 'help', special: '' }
    ];
</script>

<div class="tis-dashboard">
    <!-- Animated grid + scan-line backdrop -->
    <div class="tis-grid" aria-hidden="true"></div>
    <div class="tis-scan" aria-hidden="true"></div>

    <div class="relative px-8 py-10 mx-auto max-w-[1480px]">
        <!-- Hero header with wordmark cube -->
        <section class="mb-10 tis-fade" style="--d:0ms">
            <div class="flex items-center gap-3 mb-2">
                <span class="tis-cube" aria-hidden="true"></span>
                <p class="tis-eyebrow">Client Portal · Live</p>
            </div>
            <h1 class="tis-title">
                Operations Console<span class="tis-dot">.</span>
            </h1>
            <p class="tis-sub mt-3">
                <span class="tis-prompt">$</span> tis status —
                {data.quotes.length} quotes, {data.orders.length} open orders synced
                <span class="tis-caret"></span>
            </p>
        </section>

        <!-- Quick Access tiles -->
        <section class="mb-10">
            <p class="tis-eyebrow mb-4">Quick Access</p>
            <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-7 xl:grid-cols-9 gap-3">
                {#each tiles as tile, i}
                    <a
                        href={tile.href}
                        class="tis-tile tis-fade"
                        class:tis-tile-ai={tile.special === 'ai'}
                        style="--d:{80 + i * 50}ms"
                    >
                        <span class="tis-tile-glow" aria-hidden="true"></span>
                        <span class="tis-tile-grid" aria-hidden="true"></span>

                        {#if tile.special === 'ai'}
                            <span class="tis-robot-wrap" aria-hidden="true">
                                <svg viewBox="0 0 48 48" class="tis-robot-svg">
                                    <!-- Antenna -->
                                    <line x1="24" y1="3" x2="24" y2="10" stroke="#22d3ee" stroke-width="1.8" stroke-linecap="round"/>
                                    <circle cx="24" cy="3" r="2.4" fill="#00d9ff"/>
                                    <!-- Head -->
                                    <rect x="8" y="11" width="32" height="28" rx="9" fill="#0f1530" stroke="#22d3ee" stroke-width="1.6"/>
                                    <!-- Side ears -->
                                    <rect x="3.5" y="19" width="3.5" height="11" rx="1.75" fill="#0a0e27" stroke="#22d3ee" stroke-width="1"/>
                                    <rect x="41" y="19" width="3.5" height="11" rx="1.75" fill="#0a0e27" stroke="#22d3ee" stroke-width="1"/>
                                    <!-- Eye glows -->
                                    <circle cx="17" cy="23" r="3" fill="#00d9ff"/>
                                    <circle cx="31" cy="23" r="3" fill="#00d9ff"/>
                                    <circle cx="17" cy="22" r="1" fill="#ffffff" opacity="0.85"/>
                                    <circle cx="31" cy="22" r="1" fill="#ffffff" opacity="0.85"/>
                                    <!-- Mouth -->
                                    <rect x="16" y="30" width="16" height="2.8" rx="1.4" fill="#22d3ee" opacity="0.75"/>
                                    <!-- Cheek dots -->
                                    <circle cx="12" cy="28" r="1.1" fill="#ec4899" opacity="0.65"/>
                                    <circle cx="36" cy="28" r="1.1" fill="#ec4899" opacity="0.65"/>
                                </svg>
                            </span>
                        {/if}

                        <div class="relative">
                            <span class="tis-tile-icon material-symbols-outlined">{tile.icon}</span>
                        </div>
                        <div class="relative">
                            <p class="tis-tile-label">{tile.label}</p>
                            <p class="tis-tile-sub">{tile.sub}</p>
                        </div>
                        <span
                            class="tis-tile-arrow material-symbols-outlined"
                            aria-hidden="true"
                        >arrow_forward</span>
                    </a>
                {/each}
            </div>
        </section>

        <!-- Animated commercial-value panel -->
        <section class="tis-panel tis-fade mb-5" style="--d:560ms">
            <span class="tis-panel-glow tis-panel-glow-cyan" aria-hidden="true"></span>
            <span class="tis-panel-glow tis-panel-glow-violet" aria-hidden="true"></span>
            <span class="tis-panel-grid" aria-hidden="true"></span>

            <div class="relative flex items-center gap-8 flex-wrap">
                <!-- Donut -->
                <div class="relative flex-shrink-0">
                    <svg width="140" height="140" viewBox="0 0 140 140" class="relative -rotate-90 tis-donut">
                        <circle cx="70" cy="70" r={donutRadius} fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="16" />
                        <circle
                            cx="70" cy="70" r={donutRadius}
                            fill="none"
                            stroke="url(#tisGradQuote)"
                            stroke-width="16"
                            stroke-dasharray="{$quoteArc * donutCircumference} {donutCircumference}"
                            stroke-linecap="butt"
                        />
                        <circle
                            cx="70" cy="70" r={donutRadius}
                            fill="none"
                            stroke="url(#tisGradOrder)"
                            stroke-width="16"
                            stroke-dasharray="{$orderArc * donutCircumference} {donutCircumference}"
                            stroke-dashoffset="{-$quoteArc * donutCircumference}"
                            stroke-linecap="butt"
                        />
                        <defs>
                            <linearGradient id="tisGradQuote" x1="0" y1="0" x2="1" y2="1">
                                <stop offset="0%" stop-color="#22d3ee" />
                                <stop offset="100%" stop-color="#00d9ff" />
                            </linearGradient>
                            <linearGradient id="tisGradOrder" x1="0" y1="0" x2="1" y2="1">
                                <stop offset="0%" stop-color="#a855f7" />
                                <stop offset="100%" stop-color="#ec4899" />
                            </linearGradient>
                        </defs>
                    </svg>

                    <div class="absolute inset-0 flex flex-col items-center justify-center text-center">
                        <p class="text-[0.55rem] uppercase tracking-[0.25em] text-white/40 font-medium">Total</p>
                        <p
                            class="font-h3 text-base font-semibold tabular-nums leading-none mt-1 tis-total-text"
                            title={fmtMoney(totalCommercial, currency)}
                        >
                            {fmtMoneyCompact($totalDisplay, currency)}
                        </p>
                    </div>
                </div>

                <!-- Breakdown -->
                <div class="flex-1 min-w-[260px]">
                    <p class="tis-eyebrow tis-eyebrow-cyan mb-1">Commercial</p>
                    <h2 class="text-2xl font-semibold text-white mb-5">Active commercial value</h2>

                    <div class="space-y-5">
                        <a href="/quotes" class="group block">
                            <div class="flex items-baseline justify-between gap-3">
                                <span class="flex items-center gap-2">
                                    <span class="inline-block h-2.5 w-2.5 rounded-sm bg-gradient-to-br from-[#22d3ee] to-[#00d9ff] shadow-[0_0_8px_rgba(0,217,255,0.6)]"></span>
                                    <span class="text-sm text-white/85 font-medium group-hover:text-[#22d3ee] transition-colors">
                                        Open quotes
                                    </span>
                                    <span class="text-xs text-white/40 tabular-nums">
                                        {($quoteArc * 100).toFixed(0)}%
                                    </span>
                                </span>
                                <span class="text-sm font-semibold tabular-nums text-white">
                                    {fmtMoney(openQuotesValue, currency)}
                                </span>
                            </div>
                            <div class="h-1.5 rounded-full bg-white/[0.06] overflow-hidden mt-2">
                                <div
                                    class="h-full bg-gradient-to-r from-[#22d3ee] to-[#00d9ff] tis-bar-shine"
                                    style={`width: ${$quoteArc * 100}%`}
                                ></div>
                            </div>
                        </a>

                        <a href="/orders" class="group block">
                            <div class="flex items-baseline justify-between gap-3">
                                <span class="flex items-center gap-2">
                                    <span class="inline-block h-2.5 w-2.5 rounded-sm bg-gradient-to-br from-[#a855f7] to-[#ec4899] shadow-[0_0_8px_rgba(168,85,247,0.6)]"></span>
                                    <span class="text-sm text-white/85 font-medium group-hover:text-[#c084fc] transition-colors">
                                        Open orders
                                    </span>
                                    <span class="text-xs text-white/40 tabular-nums">
                                        {($orderArc * 100).toFixed(0)}%
                                    </span>
                                </span>
                                <span class="text-sm font-semibold tabular-nums text-white">
                                    {fmtMoney(ordersValue, currency)}
                                </span>
                            </div>
                            <div class="h-1.5 rounded-full bg-white/[0.06] overflow-hidden mt-2">
                                <div
                                    class="h-full bg-gradient-to-r from-[#a855f7] to-[#ec4899] tis-bar-shine"
                                    style={`width: ${$orderArc * 100}%`}
                                ></div>
                            </div>
                        </a>
                    </div>
                </div>
            </div>
        </section>

        <!-- KPI cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-5">
            {#each [
                { href: '/customers', value: data.customers.length.toLocaleString(), label: 'Customers', sub: 'Live from BC' },
                { href: '/quotes', value: openQuotes.length.toString().padStart(2, '0'), label: 'Open Quotes', sub: `${fmtMoney(openQuotesValue, currency)} pipeline` },
                { href: '/orders', value: data.orders.length.toString().padStart(2, '0'), label: 'Open Orders', sub: `${fmtMoney(ordersValue, currency)} backlog` },
                { href: '/settings/integrations', value: `${channelsOnline}`, valueSuffix: '/2', label: 'Integration Channels', sub: 'BC · SF' }
            ] as kpi, i}
                <a href={kpi.href} class="tis-kpi tis-fade" style="--d:{640 + i * 80}ms">
                    <span class="tis-kpi-accent" aria-hidden="true"></span>
                    <p class="tis-kpi-value tabular-nums">
                        {kpi.value}{#if kpi.valueSuffix}<span class="text-white/40">{kpi.valueSuffix}</span>{/if}
                    </p>
                    <p class="tis-eyebrow tis-eyebrow-cyan mt-1">{kpi.label}</p>
                    <p class="text-xs text-white/55 mt-2">{kpi.sub}</p>
                    <span class="tis-kpi-arrow material-symbols-outlined">arrow_forward</span>
                </a>
            {/each}
        </div>

        <!-- Recent activity -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-5">
            <section class="tis-panel tis-panel-sm tis-fade" style="--d:1000ms">
                <span class="tis-panel-grid" aria-hidden="true"></span>
                <div class="relative">
                    <div class="flex items-center justify-between mb-4 pb-3 border-b border-white/[0.06]">
                        <div>
                            <p class="tis-eyebrow tis-eyebrow-cyan mb-1">Commercial</p>
                            <h2 class="text-lg font-semibold text-white">Recent quotes</h2>
                        </div>
                        <a href="/quotes" class="tis-link">All quotes →</a>
                    </div>

                    {#if data.quotes.length === 0}
                        <p class="text-center text-white/40 py-12 text-sm">No quotes yet.</p>
                    {:else}
                        <ul class="divide-y divide-white/[0.05] max-h-[340px] overflow-y-auto pr-1 tis-list">
                            {#each recentQuotes as q}
                                <li>
                                    <a
                                        href="/quotes?q={encodeURIComponent(q.number)}"
                                        class="tis-row group"
                                    >
                                        <div class="min-w-0 flex-1">
                                            <div class="text-sm text-white font-medium truncate group-hover:text-[#22d3ee] transition-colors">
                                                {q.shipToName || q.customerName || '—'}
                                            </div>
                                            <div class="text-xs text-white/45 mt-0.5 font-mono">
                                                {q.number} · {fmtDate(q.documentDate)}
                                            </div>
                                        </div>
                                        <div class="text-right">
                                            <div class="text-sm font-semibold tabular-nums text-white">
                                                {fmtMoney(q.totalAmountIncludingTax ?? 0, q.currencyCode || 'CAD')}
                                            </div>
                                            <div class="mt-0.5">
                                                <span class={quoteBadge(q.status)}>{q.status}</span>
                                            </div>
                                        </div>
                                    </a>
                                </li>
                            {/each}
                        </ul>
                    {/if}
                </div>
            </section>

            <section class="tis-panel tis-panel-sm tis-fade" style="--d:1100ms">
                <span class="tis-panel-grid" aria-hidden="true"></span>
                <div class="relative">
                    <div class="flex items-center justify-between mb-4 pb-3 border-b border-white/[0.06]">
                        <div>
                            <p class="tis-eyebrow tis-eyebrow-cyan mb-1">Fulfillment</p>
                            <h2 class="text-lg font-semibold text-white">Recent orders</h2>
                        </div>
                        <a href="/orders" class="tis-link">All orders →</a>
                    </div>

                    {#if data.orders.length === 0}
                        <p class="text-center text-white/40 py-12 text-sm">No orders yet.</p>
                    {:else}
                        <ul class="divide-y divide-white/[0.05] max-h-[340px] overflow-y-auto pr-1 tis-list">
                            {#each recentOrders as o}
                                <li>
                                    <a
                                        href="/orders?q={encodeURIComponent(o.number)}"
                                        class="tis-row group"
                                    >
                                        <div class="min-w-0 flex-1">
                                            <div class="text-sm text-white font-medium truncate group-hover:text-[#22d3ee] transition-colors">
                                                {o.shipToName || o.customerName || '—'}
                                            </div>
                                            <div class="text-xs text-white/45 mt-0.5 font-mono">
                                                {o.number} · {fmtDate(o.orderDate)}
                                            </div>
                                        </div>
                                        <div class="text-right">
                                            <div class="text-sm font-semibold tabular-nums text-white">
                                                {fmtMoney(o.totalAmountIncludingTax ?? 0, o.currencyCode || 'CAD')}
                                            </div>
                                            <div class="mt-0.5">
                                                <span class={orderBadge(o.status)}>{o.status}</span>
                                            </div>
                                        </div>
                                    </a>
                                </li>
                            {/each}
                        </ul>
                    {/if}
                </div>
            </section>
        </div>
    </div>
</div>

<style>
    .tis-dashboard {
        position: relative;
        min-height: calc(100vh - 56px);
        background:
            radial-gradient(1100px 600px at 15% 0%, rgba(0, 217, 255, 0.10), transparent 60%),
            radial-gradient(900px 500px at 95% 10%, rgba(168, 85, 247, 0.08), transparent 60%),
            linear-gradient(180deg, #050816 0%, #0a0e27 60%, #050816 100%);
        color: #ffffff;
        overflow-x: clip; /* clip horizontal noise but let the robot fly in from above */
    }

    /* Grid texture backdrop */
    .tis-grid {
        position: absolute;
        inset: 0;
        background-image:
            linear-gradient(rgba(0, 217, 255, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 217, 255, 0.05) 1px, transparent 1px);
        background-size: 64px 64px;
        mask-image: radial-gradient(ellipse at center, black 0%, transparent 80%);
        animation: tis-grid-drift 30s linear infinite;
        pointer-events: none;
    }
    @keyframes tis-grid-drift {
        from { background-position: 0 0, 0 0; }
        to { background-position: 64px 64px, 64px 64px; }
    }

    /* Scan line */
    .tis-scan {
        position: absolute;
        inset: 0;
        background: linear-gradient(180deg, transparent 0%, rgba(0, 217, 255, 0.06) 50%, transparent 100%);
        height: 200px;
        animation: tis-scan-move 8s linear infinite;
        pointer-events: none;
        mix-blend-mode: screen;
    }
    @keyframes tis-scan-move {
        0% { transform: translateY(-200px); opacity: 0; }
        20% { opacity: 1; }
        80% { opacity: 1; }
        100% { transform: translateY(100vh); opacity: 0; }
    }

    /* Fade-in stagger */
    .tis-fade {
        opacity: 0;
        transform: translateY(8px);
        animation: tis-fade-in 600ms cubic-bezier(0.22, 1, 0.36, 1) forwards;
        animation-delay: var(--d, 0ms);
    }
    @keyframes tis-fade-in {
        to { opacity: 1; transform: translateY(0); }
    }

    /* Wordmark cube */
    .tis-cube {
        display: inline-block;
        width: 14px;
        height: 14px;
        background: linear-gradient(135deg, #00d9ff 0%, #22d3ee 100%);
        transform: rotate(45deg);
        box-shadow:
            0 0 12px rgba(0, 217, 255, 0.6),
            inset 0 0 8px rgba(255, 255, 255, 0.3);
        animation: tis-cube-pulse 2.4s ease-in-out infinite;
    }
    @keyframes tis-cube-pulse {
        0%, 100% { box-shadow: 0 0 12px rgba(0, 217, 255, 0.6), inset 0 0 8px rgba(255, 255, 255, 0.3); }
        50% { box-shadow: 0 0 24px rgba(0, 217, 255, 0.9), inset 0 0 8px rgba(255, 255, 255, 0.5); }
    }

    /* Typography */
    .tis-eyebrow {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.25em;
        color: rgba(255, 255, 255, 0.5);
        font-weight: 600;
        font-family: 'Inter', system-ui, sans-serif;
    }
    .tis-eyebrow-cyan { color: rgba(34, 211, 238, 0.85); }

    .tis-title {
        font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
        font-size: clamp(1.75rem, 3vw, 2.5rem);
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #ffffff;
        line-height: 1.1;
    }
    .tis-dot {
        background: linear-gradient(135deg, #00d9ff, #22d3ee);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }
    .tis-sub {
        font-size: 0.875rem;
        color: rgba(255, 255, 255, 0.6);
        font-family: 'JetBrains Mono', 'Courier New', monospace;
    }
    .tis-prompt { color: #00d9ff; }
    .tis-caret {
        display: inline-block;
        width: 8px;
        height: 14px;
        background: #00d9ff;
        margin-left: 4px;
        vertical-align: -2px;
        animation: tis-blink 1.1s steps(2) infinite;
    }
    @keyframes tis-blink { 50% { opacity: 0; } }

    .tis-total-text {
        background: linear-gradient(90deg, #22d3ee 0%, #ffffff 50%, #a855f7 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    /* Tiles */
    .tis-tile {
        position: relative;
        overflow: visible; /* robot can spill above the tile */
        border-radius: 14px;
        background: linear-gradient(160deg, rgba(15, 21, 48, 0.95) 0%, rgba(10, 14, 39, 0.95) 100%);
        border: 1px solid rgba(0, 217, 255, 0.15);
        padding: 0.85rem;
        aspect-ratio: 5 / 4;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        color: #ffffff;
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    }
    .tis-tile:hover {
        transform: translateY(-2px);
        border-color: rgba(0, 217, 255, 0.5);
        box-shadow: 0 0 24px rgba(0, 217, 255, 0.18), inset 0 0 12px rgba(0, 217, 255, 0.05);
    }
    /* AI tile gets a stronger ambient glow so the robot reads as "perched" */
    .tis-tile-ai {
        border-color: rgba(0, 217, 255, 0.40);
        box-shadow: 0 0 18px rgba(0, 217, 255, 0.18);
    }
    .tis-tile-glow {
        position: absolute;
        top: -30px;
        right: -30px;
        width: 110px;
        height: 110px;
        border-radius: 9999px;
        background: radial-gradient(circle, rgba(0, 217, 255, 0.35), transparent 70%);
        filter: blur(18px);
        opacity: 0.55;
        transition: opacity 0.3s ease;
    }
    .tis-tile:hover .tis-tile-glow { opacity: 1; }
    .tis-tile-ai .tis-tile-glow { opacity: 0.8; }
    .tis-tile-grid {
        position: absolute;
        inset: 0;
        opacity: 0.06;
        background-image: radial-gradient(circle at 1px 1px, white 1px, transparent 0);
        background-size: 12px 12px;
        pointer-events: none;
        border-radius: 14px;
    }
    .tis-tile-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.35rem;
        border-radius: 10px;
        background: rgba(0, 217, 255, 0.10);
        border: 1px solid rgba(0, 217, 255, 0.25);
        color: #22d3ee;
        font-size: 22px !important;
        box-shadow: 0 0 14px rgba(0, 217, 255, 0.18);
    }
    .tis-tile-label {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        line-height: 1.15;
        color: #ffffff;
    }
    .tis-tile-sub {
        font-size: 0.6rem;
        color: rgba(255, 255, 255, 0.5);
        margin-top: 0.2rem;
    }
    .tis-tile-arrow {
        position: absolute;
        bottom: 0.6rem;
        right: 0.6rem;
        font-size: 14px !important;
        color: rgba(255, 255, 255, 0.35);
        transition: transform 0.25s ease, color 0.25s ease;
    }
    .tis-tile:hover .tis-tile-arrow {
        color: #00d9ff;
        transform: translateX(2px);
    }

    /* AI mascot robot — flies in on load and perches on top of the AI tile */
    .tis-robot-wrap {
        position: absolute;
        top: -30px;
        left: 50%;
        width: 52px;
        height: 52px;
        transform: translateX(-50%);
        z-index: 6;
        pointer-events: none;
    }
    .tis-robot-svg {
        width: 100%;
        height: 100%;
        opacity: 0;
        transform-origin: center bottom;
        filter: drop-shadow(0 3px 8px rgba(0, 217, 255, 0.55));
        animation:
            tis-robot-fly 1.7s cubic-bezier(0.34, 1.56, 0.64, 1) 0.45s forwards,
            tis-robot-bob 2.6s ease-in-out 2.4s infinite;
    }
    @keyframes tis-robot-fly {
        0% {
            opacity: 0;
            transform: translate(-280px, -180px) rotate(-200deg) scale(0.32);
        }
        45% {
            opacity: 1;
            transform: translate(-40px, -70px) rotate(-40deg) scale(0.8);
        }
        78% {
            opacity: 1;
            transform: translate(6px, 6px) rotate(10deg) scale(1.08);
        }
        100% {
            opacity: 1;
            transform: translate(0, 0) rotate(0deg) scale(1);
        }
    }
    @keyframes tis-robot-bob {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-3px) rotate(-2deg); }
    }

    /* Faint "landing puff" ring under the robot, fires once after landing */
    .tis-robot-wrap::after {
        content: '';
        position: absolute;
        bottom: -6px;
        left: 50%;
        width: 28px;
        height: 6px;
        border-radius: 9999px;
        transform: translateX(-50%);
        background: radial-gradient(ellipse at center, rgba(0, 217, 255, 0.55), transparent 70%);
        opacity: 0;
        animation: tis-robot-puff 0.7s ease-out 2.0s forwards;
    }
    @keyframes tis-robot-puff {
        0% { opacity: 0.9; transform: translateX(-50%) scaleX(0.4); }
        100% { opacity: 0; transform: translateX(-50%) scaleX(1.6); }
    }

    /* Panel (donut + recent lists) */
    .tis-panel {
        position: relative;
        overflow: hidden;
        border-radius: 16px;
        background: linear-gradient(160deg, rgba(15, 21, 48, 0.85) 0%, rgba(10, 14, 39, 0.85) 100%);
        border: 1px solid rgba(0, 217, 255, 0.12);
        padding: 1.5rem;
    }
    .tis-panel-sm { padding: 1.25rem; }
    .tis-panel-glow {
        position: absolute;
        border-radius: 9999px;
        filter: blur(60px);
        pointer-events: none;
    }
    .tis-panel-glow-cyan {
        top: -80px;
        left: -80px;
        width: 280px;
        height: 280px;
        background: radial-gradient(circle, rgba(0, 217, 255, 0.30), transparent 70%);
    }
    .tis-panel-glow-violet {
        bottom: -80px;
        right: -64px;
        width: 280px;
        height: 280px;
        background: radial-gradient(circle, rgba(168, 85, 247, 0.25), transparent 70%);
    }
    .tis-panel-grid {
        position: absolute;
        inset: 0;
        opacity: 0.05;
        background-image: radial-gradient(circle at 1px 1px, white 1px, transparent 0);
        background-size: 14px 14px;
        pointer-events: none;
    }

    /* Donut subtle rotation hint */
    .tis-donut { filter: drop-shadow(0 0 16px rgba(0, 217, 255, 0.18)); }

    /* Bar sheen */
    .tis-bar-shine {
        position: relative;
        overflow: hidden;
    }
    .tis-bar-shine::after {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), transparent);
        transform: translateX(-100%);
        animation: tis-shine 3.5s ease-in-out infinite;
    }
    @keyframes tis-shine {
        0% { transform: translateX(-100%); }
        60%, 100% { transform: translateX(200%); }
    }

    /* KPI cards */
    .tis-kpi {
        position: relative;
        overflow: hidden;
        display: block;
        border-radius: 14px;
        background: linear-gradient(160deg, rgba(15, 21, 48, 0.90) 0%, rgba(10, 14, 39, 0.90) 100%);
        border: 1px solid rgba(0, 217, 255, 0.15);
        padding: 1.5rem;
        color: #ffffff;
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    }
    .tis-kpi:hover {
        transform: translateY(-2px);
        border-color: rgba(0, 217, 255, 0.45);
        box-shadow: 0 0 24px rgba(0, 217, 255, 0.18);
    }
    .tis-kpi-accent {
        position: absolute;
        top: 0;
        left: 0;
        width: 3px;
        height: 100%;
        background: linear-gradient(180deg, #00d9ff, #a855f7);
        box-shadow: 0 0 12px rgba(0, 217, 255, 0.6);
    }
    .tis-kpi-value {
        font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1;
        background: linear-gradient(135deg, #ffffff 0%, #22d3ee 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }
    .tis-kpi-arrow {
        position: absolute;
        top: 1.25rem;
        right: 1.25rem;
        font-size: 18px !important;
        color: rgba(0, 217, 255, 0.4);
        transition: transform 0.25s ease, color 0.25s ease;
    }
    .tis-kpi:hover .tis-kpi-arrow {
        color: #00d9ff;
        transform: translateX(2px);
    }

    /* Lists */
    .tis-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        padding: 0.75rem 0.75rem;
        margin: 0 -0.75rem;
        border-left: 2px solid transparent;
        transition: background 0.2s ease, border-color 0.2s ease;
    }
    .tis-row:hover {
        background: rgba(0, 217, 255, 0.04);
        border-left-color: #00d9ff;
    }
    .tis-link {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: rgba(34, 211, 238, 0.85);
        font-weight: 600;
        transition: color 0.2s ease;
    }
    .tis-link:hover { color: #00d9ff; }

    /* Scrollbar for lists */
    .tis-list::-webkit-scrollbar { width: 6px; }
    .tis-list::-webkit-scrollbar-track { background: transparent; }
    .tis-list::-webkit-scrollbar-thumb { background: rgba(0, 217, 255, 0.2); border-radius: 3px; }
    .tis-list::-webkit-scrollbar-thumb:hover { background: rgba(0, 217, 255, 0.4); }

    /* Badges */
    :global(.tis-badge) {
        display: inline-flex;
        align-items: center;
        padding: 0.15rem 0.55rem;
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        border-radius: 9999px;
        border: 1px solid;
    }
    :global(.tis-badge-success) {
        color: #22d3ee;
        background: rgba(0, 217, 255, 0.10);
        border-color: rgba(0, 217, 255, 0.35);
    }
    :global(.tis-badge-pending) {
        color: #fbbf24;
        background: rgba(251, 191, 36, 0.08);
        border-color: rgba(251, 191, 36, 0.30);
    }
    :global(.tis-badge-muted) {
        color: rgba(255, 255, 255, 0.45);
        background: rgba(255, 255, 255, 0.04);
        border-color: rgba(255, 255, 255, 0.10);
    }
</style>
