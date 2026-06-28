<script lang="ts">
    type Lead = {
        name: string;
        company: string;
        email: string;
        source: string;
        score: number;
        status: 'New' | 'Working' | 'Nurturing' | 'Qualified' | 'Unqualified';
        owner: string;
    };

    type Opp = {
        name: string;
        amount: number;
        stage: string;
        probability: number;
        closeDate: string;
        owner: string;
    };

    const leads: Lead[] = [
        { name: 'Sarah Chen', company: 'Northwind Logistics', email: 's.chen@northwind.io', source: 'Web', score: 92, status: 'Qualified', owner: 'M. Patel' },
        { name: 'Diego Romero', company: 'Aurora Refrigeration', email: 'diego@aurora-co.com', source: 'Referral', score: 88, status: 'Working', owner: 'A. Kim' },
        { name: 'Priya Anand', company: 'Cascade Foods', email: 'p.anand@cascadefoods.com', source: 'Webinar', score: 81, status: 'Nurturing', owner: 'M. Patel' },
        { name: 'Liam O\'Connor', company: 'Glacier Cold Storage', email: 'liam.o@glaciercold.ca', source: 'LinkedIn', score: 76, status: 'Working', owner: 'J. Tran' },
        { name: 'Mei Tanaka', company: 'Sakura Distribution', email: 'mei@sakura-dist.jp', source: 'Trade show', score: 71, status: 'Qualified', owner: 'A. Kim' },
        { name: 'Marcus Webb', company: 'Iron Peak HVAC', email: 'mwebb@ironpeak.com', source: 'Web', score: 64, status: 'New', owner: 'Unassigned' },
        { name: 'Hannah Müller', company: 'Polar Systems GmbH', email: 'h.mueller@polar-sys.de', source: 'Email', score: 58, status: 'Nurturing', owner: 'J. Tran' },
        { name: 'Tomás Vega', company: 'Andina Logística', email: 't.vega@andina.cl', source: 'Web', score: 42, status: 'Unqualified', owner: 'M. Patel' }
    ];

    const stages = [
        { key: 'Discovery', color: '#22d3ee' },
        { key: 'Qualification', color: '#06b6d4' },
        { key: 'Proposal', color: '#a855f7' },
        { key: 'Negotiation', color: '#ec4899' },
        { key: 'Closed Won', color: '#10b981' }
    ];

    const opps: Opp[] = [
        { name: 'Northwind — Walk-in cooler retrofit', amount: 187000, stage: 'Discovery', probability: 25, closeDate: '2026-08-12', owner: 'M. Patel' },
        { name: 'Aurora — 3-store refrigeration', amount: 412000, stage: 'Qualification', probability: 45, closeDate: '2026-07-30', owner: 'A. Kim' },
        { name: 'Cascade — Blast freezer upgrade', amount: 96500, stage: 'Discovery', probability: 20, closeDate: '2026-09-04', owner: 'M. Patel' },
        { name: 'Glacier — Annual service contract', amount: 64000, stage: 'Proposal', probability: 70, closeDate: '2026-07-18', owner: 'J. Tran' },
        { name: 'Sakura — Asia distribution pilot', amount: 285000, stage: 'Qualification', probability: 40, closeDate: '2026-08-22', owner: 'A. Kim' },
        { name: 'Iron Peak — HVAC controls', amount: 52000, stage: 'Proposal', probability: 65, closeDate: '2026-07-25', owner: 'J. Tran' },
        { name: 'Polar — Compressor replacement', amount: 38000, stage: 'Negotiation', probability: 85, closeDate: '2026-07-10', owner: 'M. Patel' },
        { name: 'Andina — Combo cold room', amount: 124000, stage: 'Closed Won', probability: 100, closeDate: '2026-06-22', owner: 'A. Kim' }
    ];

    const fmtMoney = (n: number) => n.toLocaleString(undefined, { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
    const fmtCompact = (n: number) => n.toLocaleString(undefined, { style: 'currency', currency: 'USD', notation: 'compact', maximumFractionDigits: 1 });
    const fmtDate = (s: string) => new Date(s).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });

    const totalPipeline = opps.reduce((s, o) => s + o.amount, 0);
    const weightedPipeline = opps.reduce((s, o) => s + o.amount * (o.probability / 100), 0);
    const closedWon = opps.filter((o) => o.stage === 'Closed Won').reduce((s, o) => s + o.amount, 0);
    const avgLeadScore = Math.round(leads.reduce((s, l) => s + l.score, 0) / leads.length);

    function statusClass(s: string) {
        if (s === 'Qualified') return 'crm-pill crm-pill-cyan';
        if (s === 'Working') return 'crm-pill crm-pill-amber';
        if (s === 'Nurturing') return 'crm-pill crm-pill-violet';
        if (s === 'New') return 'crm-pill crm-pill-white';
        return 'crm-pill crm-pill-muted';
    }

    function scoreColor(score: number) {
        if (score >= 80) return '#22d3ee';
        if (score >= 60) return '#a855f7';
        if (score >= 40) return '#fbbf24';
        return 'rgba(255, 255, 255, 0.35)';
    }
</script>

<div class="crm-page">
    <div class="px-8 py-8 mx-auto max-w-[1480px]">
        <!-- Hero -->
        <section class="mb-8 crm-fade" style="--d:0ms">
            <div class="flex items-center gap-3 mb-2">
                <span class="crm-cube" aria-hidden="true"></span>
                <p class="crm-eyebrow">CRM · Live pipeline</p>
            </div>
            <h1 class="crm-title">Customer Relationships<span class="crm-dot">.</span></h1>
            <p class="crm-sub mt-3">
                <span class="crm-prompt">$</span> tis crm — {leads.length} leads tracked,
                {opps.length} opportunities, {fmtCompact(weightedPipeline)} weighted pipeline
                <span class="crm-caret"></span>
            </p>
        </section>

        <!-- KPI row -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
            {#each [
                { label: 'Total Pipeline', value: fmtCompact(totalPipeline), sub: `${opps.length} open deals` },
                { label: 'Weighted Pipeline', value: fmtCompact(weightedPipeline), sub: 'Probability-weighted' },
                { label: 'Closed Won (Q2)', value: fmtCompact(closedWon), sub: '+18% vs Q1' },
                { label: 'Avg Lead Score', value: `${avgLeadScore}`, sub: 'AI-scored' }
            ] as kpi, i}
                <div class="crm-kpi crm-fade" style="--d:{80 + i * 60}ms">
                    <span class="crm-kpi-accent" aria-hidden="true"></span>
                    <p class="crm-kpi-value tabular-nums">{kpi.value}</p>
                    <p class="crm-eyebrow crm-eyebrow-cyan mt-1">{kpi.label}</p>
                    <p class="text-xs text-white/55 mt-2">{kpi.sub}</p>
                </div>
            {/each}
        </div>

        <!-- Opportunity pipeline (Kanban-style) -->
        <section class="crm-panel crm-fade mb-8" style="--d:340ms">
            <div class="flex items-end justify-between mb-5">
                <div>
                    <p class="crm-eyebrow crm-eyebrow-cyan mb-1">Pipeline</p>
                    <h2 class="text-xl font-semibold text-white">Opportunities by stage</h2>
                </div>
                <span class="text-xs text-white/45 font-mono">Updated {fmtDate(new Date().toISOString())} · auto-synced</span>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-3">
                {#each stages as stage, si}
                    {@const stageOpps = opps.filter((o) => o.stage === stage.key)}
                    {@const stageValue = stageOpps.reduce((s, o) => s + o.amount, 0)}
                    <div class="crm-stage crm-fade" style="--d:{420 + si * 70}ms; --stage-color: {stage.color}">
                        <div class="crm-stage-header">
                            <span class="crm-stage-dot" style="background: {stage.color}; box-shadow: 0 0 10px {stage.color}80;"></span>
                            <span class="text-xs uppercase tracking-wider font-semibold text-white/85">{stage.key}</span>
                            <span class="ml-auto text-xs text-white/45 tabular-nums">{stageOpps.length}</span>
                        </div>
                        <p class="text-sm font-semibold text-white tabular-nums mt-1 mb-3">{fmtCompact(stageValue)}</p>

                        <div class="space-y-2">
                            {#each stageOpps as o}
                                <div class="crm-deal">
                                    <p class="text-xs text-white font-medium truncate">{o.name}</p>
                                    <div class="flex items-center justify-between mt-1.5">
                                        <span class="text-xs text-white/55 font-mono">{fmtDate(o.closeDate)}</span>
                                        <span class="text-xs font-semibold tabular-nums" style="color: {stage.color}">
                                            {fmtCompact(o.amount)}
                                        </span>
                                    </div>
                                    <div class="crm-deal-bar mt-2">
                                        <div class="crm-deal-bar-fill" style="width: {o.probability}%; background: {stage.color};"></div>
                                    </div>
                                </div>
                            {/each}
                            {#if stageOpps.length === 0}
                                <div class="text-xs text-white/30 italic py-3">No deals</div>
                            {/if}
                        </div>
                    </div>
                {/each}
            </div>
        </section>

        <!-- Leads table -->
        <section class="crm-panel crm-fade" style="--d:760ms">
            <div class="flex items-end justify-between mb-5">
                <div>
                    <p class="crm-eyebrow crm-eyebrow-cyan mb-1">Inbound</p>
                    <h2 class="text-xl font-semibold text-white">Leads</h2>
                </div>
                <span class="text-xs text-white/45 font-mono">AI-scored · refreshed 4m ago</span>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead>
                        <tr class="border-b border-white/[0.08]">
                            <th class="crm-th">Name</th>
                            <th class="crm-th">Company</th>
                            <th class="crm-th">Source</th>
                            <th class="crm-th">Score</th>
                            <th class="crm-th">Status</th>
                            <th class="crm-th">Owner</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each leads as l, i}
                            <tr class="crm-row crm-fade" style="--d:{820 + i * 40}ms">
                                <td class="crm-td">
                                    <div class="font-medium text-white">{l.name}</div>
                                    <div class="text-xs text-white/45 font-mono">{l.email}</div>
                                </td>
                                <td class="crm-td text-white/85">{l.company}</td>
                                <td class="crm-td text-white/65 text-xs uppercase tracking-wider">{l.source}</td>
                                <td class="crm-td">
                                    <div class="flex items-center gap-2">
                                        <span class="tabular-nums font-semibold text-white w-8">{l.score}</span>
                                        <div class="crm-score-bar">
                                            <div class="crm-score-bar-fill" style="width: {l.score}%; background: {scoreColor(l.score)}; box-shadow: 0 0 8px {scoreColor(l.score)}66;"></div>
                                        </div>
                                    </div>
                                </td>
                                <td class="crm-td"><span class={statusClass(l.status)}>{l.status}</span></td>
                                <td class="crm-td text-white/65 text-sm">{l.owner}</td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        </section>
    </div>
</div>

<style>
    .crm-page {
        position: relative;
        min-height: calc(100vh - 56px);
        color: #ffffff;
    }

    .crm-fade {
        opacity: 0;
        transform: translateY(8px);
        animation: crm-fade-in 600ms cubic-bezier(0.22, 1, 0.36, 1) forwards;
        animation-delay: var(--d, 0ms);
    }
    @keyframes crm-fade-in {
        to { opacity: 1; transform: translateY(0); }
    }

    .crm-cube {
        display: inline-block;
        width: 14px;
        height: 14px;
        background: linear-gradient(135deg, #00d9ff 0%, #22d3ee 100%);
        transform: rotate(45deg);
        box-shadow: 0 0 12px rgba(0, 217, 255, 0.6), inset 0 0 8px rgba(255, 255, 255, 0.3);
        animation: crm-cube-pulse 2.4s ease-in-out infinite;
    }
    @keyframes crm-cube-pulse {
        0%, 100% { box-shadow: 0 0 12px rgba(0, 217, 255, 0.55); }
        50% { box-shadow: 0 0 24px rgba(0, 217, 255, 0.9); }
    }

    .crm-eyebrow {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.25em;
        color: rgba(255, 255, 255, 0.5);
        font-weight: 600;
    }
    .crm-eyebrow-cyan { color: rgba(34, 211, 238, 0.85); }

    .crm-title {
        font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
        font-size: clamp(1.75rem, 3vw, 2.5rem);
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #ffffff;
        line-height: 1.1;
    }
    .crm-dot {
        background: linear-gradient(135deg, #00d9ff, #22d3ee);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }
    .crm-sub {
        font-size: 0.875rem;
        color: rgba(255, 255, 255, 0.6);
        font-family: 'JetBrains Mono', 'Courier New', monospace;
    }
    .crm-prompt { color: #00d9ff; }
    .crm-caret {
        display: inline-block;
        width: 8px;
        height: 14px;
        background: #00d9ff;
        margin-left: 4px;
        vertical-align: -2px;
        animation: crm-blink 1.1s steps(2) infinite;
    }
    @keyframes crm-blink { 50% { opacity: 0; } }

    .crm-kpi {
        position: relative;
        overflow: hidden;
        border-radius: 14px;
        background: linear-gradient(160deg, rgba(15, 21, 48, 0.92) 0%, rgba(10, 14, 39, 0.92) 100%);
        border: 1px solid rgba(0, 217, 255, 0.15);
        padding: 1.5rem;
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    }
    .crm-kpi:hover {
        transform: translateY(-2px);
        border-color: rgba(0, 217, 255, 0.45);
        box-shadow: 0 0 24px rgba(0, 217, 255, 0.18);
    }
    .crm-kpi-accent {
        position: absolute;
        top: 0;
        left: 0;
        width: 3px;
        height: 100%;
        background: linear-gradient(180deg, #00d9ff, #a855f7);
        box-shadow: 0 0 12px rgba(0, 217, 255, 0.6);
    }
    .crm-kpi-value {
        font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
        font-size: 2rem;
        font-weight: 700;
        line-height: 1;
        background: linear-gradient(135deg, #ffffff 0%, #22d3ee 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    .crm-panel {
        position: relative;
        overflow: hidden;
        border-radius: 16px;
        background: linear-gradient(160deg, rgba(15, 21, 48, 0.85) 0%, rgba(10, 14, 39, 0.85) 100%);
        border: 1px solid rgba(0, 217, 255, 0.12);
        padding: 1.5rem;
    }

    .crm-stage {
        border-radius: 12px;
        background: rgba(5, 8, 22, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 1rem;
        border-top: 2px solid var(--stage-color);
    }
    .crm-stage-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .crm-stage-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 9999px;
    }

    .crm-deal {
        background: rgba(15, 21, 48, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 0.625rem 0.75rem;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    .crm-deal:hover {
        border-color: rgba(0, 217, 255, 0.35);
        transform: translateX(2px);
    }
    .crm-deal-bar {
        height: 3px;
        border-radius: 2px;
        background: rgba(255, 255, 255, 0.06);
        overflow: hidden;
    }
    .crm-deal-bar-fill {
        height: 100%;
        border-radius: 2px;
        transition: width 0.3s ease;
    }

    /* Table */
    .crm-th {
        text-align: left;
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        color: rgba(34, 211, 238, 0.75);
        font-weight: 600;
        padding: 0.75rem 1rem;
    }
    .crm-row {
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        transition: background 0.2s ease;
    }
    .crm-row:hover { background: rgba(0, 217, 255, 0.04); }
    .crm-td {
        padding: 0.85rem 1rem;
        font-size: 0.875rem;
        vertical-align: middle;
    }

    .crm-score-bar {
        flex: 1;
        height: 4px;
        background: rgba(255, 255, 255, 0.06);
        border-radius: 2px;
        overflow: hidden;
        max-width: 100px;
    }
    .crm-score-bar-fill {
        height: 100%;
        border-radius: 2px;
    }

    /* Pills */
    .crm-pill {
        display: inline-flex;
        align-items: center;
        padding: 0.18rem 0.6rem;
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        border-radius: 9999px;
        border: 1px solid;
    }
    .crm-pill-cyan {
        color: #22d3ee;
        background: rgba(0, 217, 255, 0.10);
        border-color: rgba(0, 217, 255, 0.40);
    }
    .crm-pill-amber {
        color: #fbbf24;
        background: rgba(251, 191, 36, 0.10);
        border-color: rgba(251, 191, 36, 0.35);
    }
    .crm-pill-violet {
        color: #c084fc;
        background: rgba(168, 85, 247, 0.10);
        border-color: rgba(168, 85, 247, 0.40);
    }
    .crm-pill-white {
        color: rgba(255, 255, 255, 0.85);
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 255, 255, 0.20);
    }
    .crm-pill-muted {
        color: rgba(255, 255, 255, 0.45);
        background: rgba(255, 255, 255, 0.04);
        border-color: rgba(255, 255, 255, 0.10);
    }
</style>
