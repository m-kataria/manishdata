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
        // CA$2.6M / CA$487K — keeps long numbers fitting in narrow KPI cards
        return n.toLocaleString(undefined, {
            style: 'currency',
            currency: cur,
            notation: 'compact',
            maximumFractionDigits: 1
        });
    }

    function relTime(iso: string | null | undefined): string {
        if (!iso || iso.startsWith('0001')) return '—';
        const d = new Date(iso);
        const diff = Date.now() - d.getTime();
        const m = Math.floor(diff / 60000);
        if (m < 1) return 'now';
        if (m < 60) return `${m}m ago`;
        const h = Math.floor(m / 60);
        if (h < 24) return `${h}h ago`;
        return `${Math.floor(h / 24)}d ago`;
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
        if (s === 'released' || s === 'accepted') return 'badge-active';
        if (s === 'rejected' || s === 'expired' || s === 'cancelled') return 'badge-review';
        return 'badge-pending';
    }

    function orderBadge(status: string): string {
        const s = status.toLowerCase();
        if (s === 'released') return 'badge-active';
        if (s === 'cancelled') return 'badge-review';
        return 'badge-pending';
    }

    // Recent quotes & orders sorted descending by document number (newest first).
    $: recentQuotes = [...data.quotes].sort((a, b) =>
        (b.number || '').localeCompare(a.number || '', undefined, { numeric: true })
    );
    $: recentOrders = [...data.orders].sort((a, b) =>
        (b.number || '').localeCompare(a.number || '', undefined, { numeric: true })
    );

    // Active commercial value donut chart math.
    $: totalCommercial = openQuotesValue + ordersValue;
    $: quotePct = totalCommercial > 0 ? openQuotesValue / totalCommercial : 0;
    $: orderPct = totalCommercial > 0 ? ordersValue / totalCommercial : 0;
    const donutRadius = 48;
    const donutCircumference = 2 * Math.PI * donutRadius;

    // Animated arc fills + center value (run once on mount for a fill-in effect).
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
</script>

<div class="px-8 py-8 mx-auto max-w-[1480px]">
    <!-- Quick Access (POS-style large tiles) -->
    <section class="mb-10">
        <div class="mb-5">
            <p class="eyebrow mb-1">Quick Access</p>
            <h1 class="font-h2 text-h2 text-on-surface font-semibold">Operations Console.</h1>
            <p class="font-body-md text-sm text-secondary mt-2">
                Jump straight in. Scroll for the live overview.
            </p>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-4">
            {#each [
                { href: '/customers', label: 'Customers', sub: 'Accounts', icon: 'groups', grad: 'from-sky-500 via-blue-600 to-indigo-600' },
                { href: '/quotes', label: 'Sales Quotes', sub: 'Quote & price', icon: 'request_quote', grad: 'from-violet-500 via-violet-600 to-fuchsia-600' },
                { href: '/orders', label: 'Sales Orders', sub: 'Fulfillment', icon: 'receipt_long', grad: 'from-emerald-500 via-emerald-600 to-teal-600' },
                { href: '/inventory', label: 'Inventory', sub: 'Stock & SKUs', icon: 'inventory_2', grad: 'from-amber-500 via-orange-500 to-orange-600' },
                { href: '/pricing', label: 'Pricing', sub: 'Group prices', icon: 'sell', grad: 'from-cyan-500 via-sky-500 to-blue-600' },
                { href: '/jobs', label: 'Jobs', sub: 'Field service', icon: 'engineering', grad: 'from-indigo-500 via-purple-600 to-fuchsia-700' },
                { href: '/help', label: 'Help', sub: 'Training & tools', icon: 'help', grad: 'from-rose-500 via-pink-600 to-rose-700' }
            ] as tile}
                <a
                    href={tile.href}
                    class="group relative overflow-hidden rounded-2xl bg-gradient-to-br {tile.grad} text-white p-5 aspect-[5/4] flex flex-col justify-between shadow-md hover:shadow-xl hover:-translate-y-0.5 transition-all"
                >
                    <!-- AI-ish glow + grid texture -->
                    <span class="pointer-events-none absolute -top-10 -right-10 h-32 w-32 rounded-full bg-white/20 blur-2xl"></span>
                    <span class="pointer-events-none absolute inset-0 opacity-[0.08] bg-[radial-gradient(circle_at_1px_1px,_white_1px,_transparent_0)] [background-size:14px_14px]"></span>

                    <div class="relative">
                        <span
                            class="material-symbols-outlined bg-white/15 backdrop-blur-sm rounded-xl p-2 inline-flex items-center justify-center"
                            style="font-size: 32px"
                        >{tile.icon}</span>
                    </div>
                    <div class="relative">
                        <p class="font-h3 text-base font-semibold uppercase tracking-wide leading-tight">
                            {tile.label}
                        </p>
                        <p class="font-body-md text-xs text-white/80 mt-1">{tile.sub}</p>
                    </div>
                    <span
                        class="material-symbols-outlined absolute bottom-4 right-4 text-white/60 group-hover:text-white group-hover:translate-x-0.5 transition-all"
                        style="font-size: 20px"
                    >arrow_forward</span>
                </a>
            {/each}
        </div>
    </section>

    <!-- Page header -->
    <div class="mb-8">
        <p class="eyebrow mb-1">Operations</p>
        <h1 class="font-h3 text-h3 text-on-surface font-semibold">Overview.</h1>
        <p class="font-body-md text-sm text-secondary mt-2">
            Live from Business Central · {data.quotes.length} quotes, {data.orders.length} open orders loaded
        </p>
    </div>

    <!-- Active commercial value (animated AI donut, Salesforce report palette) -->
    <section class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-zinc-950 via-zinc-900 to-zinc-950 text-white p-6 mb-5 shadow-lg">
        <!-- SF blue + orange glows + AI grid -->
        <span class="pointer-events-none absolute -top-20 -left-20 h-72 w-72 rounded-full bg-[#0176D3]/25 blur-3xl"></span>
        <span class="pointer-events-none absolute -bottom-24 -right-16 h-72 w-72 rounded-full bg-[#FE9339]/25 blur-3xl"></span>
        <span class="pointer-events-none absolute inset-0 opacity-[0.06] bg-[radial-gradient(circle_at_1px_1px,_white_1px,_transparent_0)] [background-size:14px_14px]"></span>

        <div class="relative flex items-center gap-8 flex-wrap">
            <!-- Donut -->
            <div class="relative flex-shrink-0">
                <svg width="130" height="130" viewBox="0 0 130 130" class="relative -rotate-90">
                    <!-- Track -->
                    <circle cx="65" cy="65" r={donutRadius} fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="16" />
                    <!-- Quote segment -->
                    <circle
                        cx="65" cy="65" r={donutRadius}
                        fill="none"
                        stroke="url(#gradQuote)"
                        stroke-width="16"
                        stroke-dasharray="{$quoteArc * donutCircumference} {donutCircumference}"
                        stroke-linecap="butt"
                    />
                    <!-- Order segment, offset to start after quote arc -->
                    <circle
                        cx="65" cy="65" r={donutRadius}
                        fill="none"
                        stroke="url(#gradOrder)"
                        stroke-width="16"
                        stroke-dasharray="{$orderArc * donutCircumference} {donutCircumference}"
                        stroke-dashoffset="{-$quoteArc * donutCircumference}"
                        stroke-linecap="butt"
                    />
                    <defs>
                        <linearGradient id="gradQuote" x1="0" y1="0" x2="1" y2="1">
                            <stop offset="0%" stop-color="#014486" />
                            <stop offset="100%" stop-color="#1589EE" />
                        </linearGradient>
                        <linearGradient id="gradOrder" x1="0" y1="0" x2="1" y2="1">
                            <stop offset="0%" stop-color="#C25E00" />
                            <stop offset="100%" stop-color="#FE9339" />
                        </linearGradient>
                    </defs>
                </svg>

                <!-- Center label -->
                <div class="absolute inset-0 flex flex-col items-center justify-center text-center">
                    <p class="text-[0.55rem] uppercase tracking-[0.25em] text-white/50 font-medium">Total</p>
                    <p
                        class="font-h3 text-base font-semibold tabular-nums leading-none mt-0.5 bg-gradient-to-r from-[#7bb9f4] via-white to-[#ffc685] bg-clip-text text-transparent"
                        title={fmtMoney(totalCommercial, currency)}
                    >
                        {fmtMoneyCompact($totalDisplay, currency)}
                    </p>
                </div>
            </div>

            <!-- Breakdown -->
            <div class="flex-1 min-w-[260px]">
                <p class="text-[0.65rem] uppercase tracking-[0.25em] text-[#7bb9f4]/80 font-medium mb-1">Commercial</p>
                <h2 class="font-h3 text-h3 font-semibold mb-5">Active commercial value</h2>

                <div class="space-y-5">
                    <a href="/quotes" class="group block">
                        <div class="flex items-baseline justify-between gap-3">
                            <span class="flex items-center gap-2">
                                <span class="inline-block h-2.5 w-2.5 rounded-sm bg-gradient-to-br from-[#014486] to-[#1589EE]"></span>
                                <span class="font-body-md text-sm font-medium group-hover:text-[#7bb9f4] transition-colors">
                                    Open quotes
                                </span>
                                <span class="text-xs text-white/50 tabular-nums">
                                    {($quoteArc * 100).toFixed(0)}%
                                </span>
                            </span>
                            <span class="font-body-md text-sm font-semibold tabular-nums">
                                {fmtMoney(openQuotesValue, currency)}
                            </span>
                        </div>
                        <div class="h-1.5 rounded-full bg-white/10 overflow-hidden mt-2">
                            <div
                                class="h-full bg-gradient-to-r from-[#014486] to-[#1589EE]"
                                style={`width: ${$quoteArc * 100}%`}
                            ></div>
                        </div>
                    </a>

                    <a href="/orders" class="group block">
                        <div class="flex items-baseline justify-between gap-3">
                            <span class="flex items-center gap-2">
                                <span class="inline-block h-2.5 w-2.5 rounded-sm bg-gradient-to-br from-[#C25E00] to-[#FE9339]"></span>
                                <span class="font-body-md text-sm font-medium group-hover:text-[#ffc685] transition-colors">
                                    Open orders
                                </span>
                                <span class="text-xs text-white/50 tabular-nums">
                                    {($orderArc * 100).toFixed(0)}%
                                </span>
                            </span>
                            <span class="font-body-md text-sm font-semibold tabular-nums">
                                {fmtMoney(ordersValue, currency)}
                            </span>
                        </div>
                        <div class="h-1.5 rounded-full bg-white/10 overflow-hidden mt-2">
                            <div
                                class="h-full bg-gradient-to-r from-[#C25E00] to-[#FE9339]"
                                style={`width: ${$orderArc * 100}%`}
                            ></div>
                        </div>
                    </a>
                </div>
            </div>
        </div>
    </section>

    <!-- KPI stat cards (clickable: white bg + brand-red left accent + arrow on hover) -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-5">
        <a
            href="/customers"
            class="group block bg-white border border-zinc-200 border-l-4 border-l-primary-container rounded-card p-6 hover:bg-primary-container hover:border-primary-container transition-colors relative"
        >
            <p class="font-h1 text-3xl font-semibold text-primary-container group-hover:text-white mb-1 tabular-nums transition-colors">
                {data.customers.length.toLocaleString()}
            </p>
            <p class="eyebrow group-hover:text-white/80 transition-colors">Customers</p>
            <p class="font-body-md text-sm text-secondary group-hover:text-white/90 mt-2 transition-colors">
                Live from BC
            </p>
            <span
                class="material-symbols-outlined absolute top-5 right-5 text-primary-container group-hover:text-white opacity-40 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all"
                style="font-size: 20px"
            >
                arrow_forward
            </span>
        </a>
        <a
            href="/quotes"
            class="group block bg-white border border-zinc-200 border-l-4 border-l-primary-container rounded-card p-6 hover:bg-primary-container hover:border-primary-container transition-colors relative"
        >
            <p class="font-h1 text-3xl font-semibold text-primary-container group-hover:text-white mb-1 tabular-nums transition-colors">
                {openQuotes.length.toString().padStart(2, '0')}
            </p>
            <p class="eyebrow group-hover:text-white/80 transition-colors">Open Quotes</p>
            <p class="font-body-md text-sm text-secondary group-hover:text-white/90 mt-2 transition-colors">
                {fmtMoney(openQuotesValue, currency)} pipeline
            </p>
            <span
                class="material-symbols-outlined absolute top-5 right-5 text-primary-container group-hover:text-white opacity-40 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all"
                style="font-size: 20px"
            >
                arrow_forward
            </span>
        </a>
        <a
            href="/orders"
            class="group block bg-white border border-zinc-200 border-l-4 border-l-primary-container rounded-card p-6 hover:bg-primary-container hover:border-primary-container transition-colors relative"
        >
            <p class="font-h1 text-3xl font-semibold text-primary-container group-hover:text-white mb-1 tabular-nums transition-colors">
                {data.orders.length.toString().padStart(2, '0')}
            </p>
            <p class="eyebrow group-hover:text-white/80 transition-colors">Open Orders</p>
            <p class="font-body-md text-sm text-secondary group-hover:text-white/90 mt-2 transition-colors">
                {fmtMoney(ordersValue, currency)} backlog
            </p>
            <span
                class="material-symbols-outlined absolute top-5 right-5 text-primary-container group-hover:text-white opacity-40 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all"
                style="font-size: 20px"
            >
                arrow_forward
            </span>
        </a>
        <a
            href="/settings/integrations"
            class="group block bg-white border border-zinc-200 border-l-4 border-l-primary-container rounded-card p-6 hover:bg-primary-container hover:border-primary-container transition-colors relative"
        >
            <p class="font-h1 text-3xl font-semibold text-primary-container group-hover:text-white mb-1 tabular-nums transition-colors">
                {channelsOnline}<span class="text-secondary group-hover:text-white/70 text-2xl transition-colors">/2</span>
            </p>
            <p class="eyebrow group-hover:text-white/80 transition-colors">Integration Channels</p>
            <p class="font-body-md text-sm text-secondary group-hover:text-white/90 mt-2 transition-colors">
                BC · SF
            </p>
            <span
                class="material-symbols-outlined absolute top-5 right-5 text-primary-container group-hover:text-white opacity-40 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all"
                style="font-size: 20px"
            >
                arrow_forward
            </span>
        </a>
    </div>

    <!-- Two-column recent activity -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-5">
        <!-- Recent quotes -->
        <section class="card p-6">
            <div class="flex items-center justify-between mb-4 pb-3 border-b border-zinc-100">
                <div>
                    <p class="eyebrow mb-1">Commercial</p>
                    <h2 class="font-h3 text-h3 text-on-surface font-semibold">Recent quotes</h2>
                </div>
                <a href="/quotes" class="btn-ghost">All quotes →</a>
            </div>

            {#if data.quotes.length === 0}
                <p class="text-center text-secondary py-12 font-body-md text-sm">No quotes yet.</p>
            {:else}
                <ul class="divide-y divide-zinc-100 max-h-[340px] overflow-y-auto pr-1">
                    {#each recentQuotes as q}
                        <li>
                            <a
                                href="/quotes?q={encodeURIComponent(q.number)}"
                                class="group flex items-center justify-between gap-3 px-3 -mx-3 py-3 border-l-2 border-l-transparent hover:border-l-primary-container hover:bg-surface-container-low transition-colors"
                            >
                                <div class="min-w-0 flex-1">
                                    <div class="font-body-md text-sm text-on-surface font-medium truncate group-hover:text-primary-container transition-colors">
                                        {q.shipToName || q.customerName || '—'}
                                    </div>
                                    <div class="font-label-sm text-xs text-secondary mt-0.5">
                                        {q.number} · {fmtDate(q.documentDate)}
                                    </div>
                                </div>
                                <div class="text-right">
                                    <div class="font-body-md text-sm font-semibold tabular-nums">
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
        </section>

        <!-- Recent orders -->
        <section class="card p-6">
            <div class="flex items-center justify-between mb-4 pb-3 border-b border-zinc-100">
                <div>
                    <p class="eyebrow mb-1">Fulfillment</p>
                    <h2 class="font-h3 text-h3 text-on-surface font-semibold">Recent orders</h2>
                </div>
                <a href="/orders" class="btn-ghost">All orders →</a>
            </div>

            {#if data.orders.length === 0}
                <p class="text-center text-secondary py-12 font-body-md text-sm">No orders yet.</p>
            {:else}
                <ul class="divide-y divide-zinc-100 max-h-[340px] overflow-y-auto pr-1">
                    {#each recentOrders as o}
                        <li>
                            <a
                                href="/orders?q={encodeURIComponent(o.number)}"
                                class="group flex items-center justify-between gap-3 px-3 -mx-3 py-3 border-l-2 border-l-transparent hover:border-l-primary-container hover:bg-surface-container-low transition-colors"
                            >
                                <div class="min-w-0 flex-1">
                                    <div class="font-body-md text-sm text-on-surface font-medium truncate group-hover:text-primary-container transition-colors">
                                        {o.shipToName || o.customerName || '—'}
                                    </div>
                                    <div class="font-label-sm text-xs text-secondary mt-0.5">
                                        {o.number} · {fmtDate(o.orderDate)}
                                    </div>
                                </div>
                                <div class="text-right">
                                    <div class="font-body-md text-sm font-semibold tabular-nums">
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
        </section>
    </div>
</div>
