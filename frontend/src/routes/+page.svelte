<script lang="ts">
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

    $: bcOk =
        !!data.integrations?.businessCentral.configured &&
        data.integrations.businessCentral.lastSync?.status !== 'failed';
    $: sfOk =
        !!data.integrations?.salesforce.configured &&
        data.integrations.salesforce.lastSync?.status !== 'failed';
    $: channelsOnline = (bcOk ? 1 : 0) + (sfOk ? 1 : 0);
</script>

<div class="px-8 py-8 max-w-[1480px]">
    <!-- Page header -->
    <div class="mb-8">
        <p class="eyebrow mb-1">Operations</p>
        <h1 class="font-h2 text-h2 text-on-surface font-semibold">Overview.</h1>
        <p class="font-body-md text-sm text-secondary mt-2">
            Live from Business Central · {data.quotes.length} quotes, {data.orders.length} open orders loaded
        </p>
    </div>

    <!-- KPI stat cards (clickable: white bg + brand-red left accent + arrow on hover) -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-5 mb-8">
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
            href="/quotes"
            class="group block bg-white border border-zinc-200 border-l-4 border-l-primary-container rounded-card p-6 hover:bg-primary-container hover:border-primary-container transition-colors relative"
        >
            <p
                class="font-h1 text-3xl font-semibold text-primary-container group-hover:text-white mb-1 tabular-nums transition-colors"
                title={fmtMoney(openQuotesValue + ordersValue, currency)}
            >
                {fmtMoneyCompact(openQuotesValue + ordersValue, currency)}
            </p>
            <p class="eyebrow group-hover:text-white/80 transition-colors">Active Commercial Value</p>
            <p class="font-body-md text-sm text-secondary group-hover:text-white/90 mt-2 transition-colors">
                Quotes + open orders
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
                <ul class="divide-y divide-zinc-100">
                    {#each data.quotes.slice(0, 6) as q}
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
                    <h2 class="font-h3 text-h3 text-on-surface font-semibold">Open orders</h2>
                </div>
                <a href="/orders" class="btn-ghost">All orders →</a>
            </div>

            {#if data.orders.length === 0}
                <p class="text-center text-secondary py-12 font-body-md text-sm">No open orders.</p>
            {:else}
                <ul class="divide-y divide-zinc-100">
                    {#each data.orders.slice(0, 6) as o}
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

    <!-- Integration channels (full width) -->
    <section class="card p-6">
        <div class="flex items-center justify-between mb-4 pb-3 border-b border-zinc-100">
            <div>
                <p class="eyebrow mb-1">External</p>
                <h2 class="font-h3 text-h3 text-on-surface font-semibold">Integration channels</h2>
            </div>
            <a href="/settings/integrations" class="btn-ghost">Manage →</a>
        </div>

        <ul class="grid grid-cols-1 md:grid-cols-2 gap-4">
            {#each [{ name: 'Business Central', state: data.integrations?.businessCentral, kind: 'bc' }, { name: 'Salesforce', state: data.integrations?.salesforce, kind: 'sf' }] as ch}
                <li class="flex items-start justify-between gap-3 relative pl-4">
                    <span
                        class="absolute left-0 top-0 bottom-0 w-1 {ch.kind === 'bc' ? 'bg-bc/40' : 'bg-sf/40'}"
                    />
                    <div class="min-w-0">
                        <div class="font-body-md text-sm text-on-surface font-medium">{ch.name}</div>
                        <div class="font-label-sm text-xs text-secondary mt-0.5">
                            {ch.state?.configured
                                ? ch.state.lastSync
                                    ? `Last sync ${relTime(ch.state.lastSync.completedAt ?? ch.state.lastSync.startedAt)}`
                                    : 'Configured · awaiting first sync'
                                : 'Awaiting credentials'}
                        </div>
                    </div>
                    {#if ch.state?.configured && ch.state.lastSync?.status !== 'failed'}
                        {#if ch.kind === 'bc'}
                            <span class="badge-bc"><span class="dot-bc" /> Online</span>
                        {:else}
                            <span class="badge-sf"><span class="dot-sf" /> Online</span>
                        {/if}
                    {:else if ch.state?.configured}
                        <span class="badge-review">Faulted</span>
                    {:else}
                        <span class="badge-pending">Offline</span>
                    {/if}
                </li>
            {/each}
        </ul>
    </section>
</div>
