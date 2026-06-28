<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    type Agent = {
        name: string;
        role: string;
        icon: string;
        accent: string;
        tasks: string[];
        savedLabel: string;
        savedValue: string;
        status: 'running' | 'idle';
    };

    const agents: Agent[] = [
        {
            name: 'Clerk',
            role: 'Clerical automation',
            icon: 'description',
            accent: '#22d3ee',
            tasks: [
                'Reconciling 47 vendor invoices against POs in QuickBooks...',
                'Importing weekly inventory variance from Excel into Business Central...',
                'Auto-categorizing 132 transactions and flagging 3 anomalies...',
                'Generating month-end close checklist for the finance team...'
            ],
            savedLabel: 'Hours saved this week',
            savedValue: '38.4 h',
            status: 'running'
        },
        {
            name: 'Nurture',
            role: 'Sales lead nurturing',
            icon: 'favorite',
            accent: '#a855f7',
            tasks: [
                'Reading CRM + email thread with Aurora Refrigeration, drafting follow-up...',
                'Scoring 14 inbound leads and routing top 3 to account owners...',
                'Generating personalized re-engagement sequence for 28 dormant leads...',
                'Summarizing last 6 touchpoints with Cascade Foods for the rep...'
            ],
            savedLabel: 'Leads nurtured this month',
            savedValue: '247',
            status: 'running'
        },
        {
            name: 'Mailwright',
            role: 'Email composition + send',
            icon: 'mail',
            accent: '#22d3ee',
            tasks: [
                'Drafting + sending 12 follow-ups from yesterday\'s discovery calls...',
                'Composing quarterly check-in email to 86 inactive accounts...',
                'Replying to inbound RFQ from Polar Systems with quote attached...',
                'Sending Monday pipeline summary to 4 account executives...'
            ],
            savedLabel: 'Emails sent this week',
            savedValue: '412',
            status: 'running'
        },
        {
            name: 'Scheduler',
            role: 'Meeting orchestration',
            icon: 'event',
            accent: '#10b981',
            tasks: [
                'Booking discovery call with Sarah Chen for Thu 2pm — calendars synced...',
                'Rescheduling 3 conflicts after the team standup moved to 9am...',
                'Sending Calendly invite + agenda to Northwind buying committee...',
                'Adding meeting prep notes from CRM into each invite description...'
            ],
            savedLabel: 'Meetings booked',
            savedValue: '38',
            status: 'running'
        },
        {
            name: 'Insight',
            role: 'Pipeline intelligence',
            icon: 'insights',
            accent: '#ec4899',
            tasks: [
                'Detected 3 deals slipping — pinged owners with last-touch summary...',
                'Forecasting Q3 close rate from 18 months of CRM activity data...',
                'Flagging Acme deal: no inbound activity in 14 days, owner notified...',
                'Identifying upsell signals across 240 customer accounts...'
            ],
            savedLabel: 'Pipeline at risk caught',
            savedValue: '$184K',
            status: 'running'
        },
        {
            name: 'Tickets',
            role: 'Support triage',
            icon: 'support_agent',
            accent: '#fbbf24',
            tasks: [
                'Triaging 14 new tickets — routing 9 to L1, escalating 2 to engineering...',
                'Drafting initial response to 6 password-reset tickets with KB links...',
                'Summarizing yesterday\'s tickets into a Slack digest for the team...',
                'Tagging recurring issue pattern detected across 7 tickets this week...'
            ],
            savedLabel: 'Avg first response',
            savedValue: '2.4 min',
            status: 'running'
        }
    ];

    let currentTask: Record<string, number> = Object.fromEntries(agents.map((a) => [a.name, 0]));
    let displayed: Record<string, string> = Object.fromEntries(agents.map((a) => [a.name, '']));
    let typing: Record<string, boolean> = Object.fromEntries(agents.map((a) => [a.name, true]));

    let intervals: ReturnType<typeof setInterval>[] = [];

    function typeOut(agent: Agent) {
        const full = agent.tasks[currentTask[agent.name]];
        let i = 0;
        typing[agent.name] = true;
        displayed[agent.name] = '';

        const id = setInterval(() => {
            if (i >= full.length) {
                clearInterval(id);
                typing[agent.name] = false;

                // Pause then advance to next task
                setTimeout(() => {
                    currentTask[agent.name] = (currentTask[agent.name] + 1) % agent.tasks.length;
                    typeOut(agent);
                }, 2800);
                return;
            }
            displayed[agent.name] = full.slice(0, i + 1);
            displayed = displayed;
            i++;
        }, 22 + Math.random() * 14);

        intervals.push(id);
    }

    onMount(() => {
        agents.forEach((a, i) => {
            setTimeout(() => typeOut(a), 200 + i * 350);
        });
    });

    onDestroy(() => {
        intervals.forEach((id) => clearInterval(id));
    });

    // Top-level stats (animated counters)
    let hoursSaved = 0;
    let tasksAutomated = 0;
    let estSavings = 0;
    onMount(() => {
        const targets = { hours: 248, tasks: 1247, savings: 34200 };
        const dur = 1600;
        const start = performance.now();

        const animate = (now: number) => {
            const t = Math.min((now - start) / dur, 1);
            const eased = 1 - Math.pow(1 - t, 3);
            hoursSaved = Math.round(targets.hours * eased);
            tasksAutomated = Math.round(targets.tasks * eased);
            estSavings = Math.round(targets.savings * eased);
            if (t < 1) requestAnimationFrame(animate);
        };
        requestAnimationFrame(animate);
    });

    const fmtMoney = (n: number) => n.toLocaleString(undefined, { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
</script>

<div class="ai-page">
    <div class="px-8 py-8 mx-auto max-w-[1480px]">
        <!-- Hero -->
        <section class="mb-10 ai-fade" style="--d:0ms">
            <div class="flex items-center gap-3 mb-2">
                <span class="ai-cube" aria-hidden="true"></span>
                <p class="ai-eyebrow">AI Workforce · 6 agents online</p>
            </div>
            <h1 class="ai-title">
                Your AI team is on the clock<span class="ai-dot">.</span>
            </h1>
            <p class="ai-sub mt-3 max-w-3xl">
                Autonomous agents handling the clerical, sales-ops, and admin work that used to
                eat your team's day. Reading CRM data, drafting emails, booking meetings,
                reconciling books — so your humans can focus on closing deals and building
                the business.
            </p>
        </section>

        <!-- Top stats -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-5 mb-10">
            {#each [
                { label: 'Hours saved this month', value: `${hoursSaved} h`, sub: 'across 6 agents' },
                { label: 'Tasks automated', value: tasksAutomated.toLocaleString(), sub: '7-day rolling' },
                { label: 'Estimated savings', value: fmtMoney(estSavings), sub: 'at $138 / hr loaded' }
            ] as stat, i}
                <div class="ai-stat ai-fade" style="--d:{120 + i * 90}ms">
                    <span class="ai-stat-glow" aria-hidden="true"></span>
                    <p class="ai-stat-value tabular-nums">{stat.value}</p>
                    <p class="ai-eyebrow ai-eyebrow-cyan mt-2">{stat.label}</p>
                    <p class="text-xs text-white/55 mt-1">{stat.sub}</p>
                </div>
            {/each}
        </div>

        <!-- Agent grid -->
        <section class="mb-8 ai-fade" style="--d:400ms">
            <div class="flex items-end justify-between mb-5">
                <div>
                    <p class="ai-eyebrow ai-eyebrow-cyan mb-1">Active agents</p>
                    <h2 class="text-xl font-semibold text-white">Watch them work, live</h2>
                </div>
                <span class="text-xs text-white/45 font-mono flex items-center gap-2">
                    <span class="ai-live-dot"></span>
                    Live · streaming
                </span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
                {#each agents as agent, i}
                    <article
                        class="ai-agent ai-fade"
                        style="--d:{480 + i * 80}ms; --accent: {agent.accent};"
                    >
                        <span class="ai-agent-glow" aria-hidden="true"></span>

                        <header class="flex items-start gap-3 mb-4">
                            <div class="ai-agent-avatar">
                                <span class="ai-agent-pulse" aria-hidden="true"></span>
                                <span class="ai-agent-pulse ai-agent-pulse-2" aria-hidden="true"></span>
                                <span class="material-symbols-outlined ai-agent-icon">{agent.icon}</span>
                            </div>
                            <div class="flex-1 min-w-0">
                                <div class="flex items-center gap-2">
                                    <h3 class="text-base font-semibold text-white leading-tight">{agent.name}</h3>
                                    <span class="ai-running">
                                        <span class="ai-running-dot"></span>
                                        <span>RUNNING</span>
                                    </span>
                                </div>
                                <p class="text-xs text-white/55 mt-0.5">{agent.role}</p>
                            </div>
                        </header>

                        <!-- Speech bubble with typewriter -->
                        <div class="ai-bubble" style="--accent: {agent.accent}">
                            <p class="ai-bubble-text">
                                {displayed[agent.name]}{#if typing[agent.name]}<span class="ai-bubble-caret"></span>{:else}<span class="ai-dots"><span></span><span></span><span></span></span>{/if}
                            </p>
                        </div>

                        <footer class="flex items-end justify-between mt-4 pt-3 border-t border-white/[0.05]">
                            <div>
                                <p class="text-[0.65rem] uppercase tracking-[0.2em] text-white/40 font-semibold">{agent.savedLabel}</p>
                                <p class="ai-saved-value tabular-nums">{agent.savedValue}</p>
                            </div>
                            <button type="button" class="ai-ghost-btn">
                                <span class="material-symbols-outlined" style="font-size: 16px">tune</span>
                                <span>Configure</span>
                            </button>
                        </footer>
                    </article>
                {/each}
            </div>
        </section>

        <!-- Bottom CTA -->
        <section class="ai-cta ai-fade" style="--d:980ms">
            <span class="ai-cta-glow ai-cta-glow-cyan" aria-hidden="true"></span>
            <span class="ai-cta-glow ai-cta-glow-violet" aria-hidden="true"></span>
            <div class="relative grid md:grid-cols-2 gap-6 items-center">
                <div>
                    <p class="ai-eyebrow ai-eyebrow-cyan mb-2">Coming soon</p>
                    <h2 class="text-2xl font-semibold text-white leading-tight">
                        Hire a custom agent for your workflow.
                    </h2>
                    <p class="text-sm text-white/65 mt-3 max-w-md">
                        Describe a recurring task — invoice reconciliation, vendor onboarding,
                        weekly board prep — and we'll spin up an agent that runs it on autopilot.
                        Your team stays in approval-loop until it's trusted to run solo.
                    </p>
                </div>
                <div class="flex md:justify-end gap-3">
                    <button type="button" class="ai-primary-btn">
                        <span class="material-symbols-outlined" style="font-size: 18px">auto_awesome</span>
                        <span>Request an agent</span>
                    </button>
                    <button type="button" class="ai-secondary-btn">
                        <span>See pricing</span>
                    </button>
                </div>
            </div>
        </section>
    </div>
</div>

<style>
    .ai-page {
        position: relative;
        min-height: calc(100vh - 56px);
        color: #ffffff;
    }

    .ai-fade {
        opacity: 0;
        transform: translateY(8px);
        animation: ai-fade-in 600ms cubic-bezier(0.22, 1, 0.36, 1) forwards;
        animation-delay: var(--d, 0ms);
    }
    @keyframes ai-fade-in {
        to { opacity: 1; transform: translateY(0); }
    }

    .ai-cube {
        display: inline-block;
        width: 14px;
        height: 14px;
        background: linear-gradient(135deg, #00d9ff 0%, #22d3ee 100%);
        transform: rotate(45deg);
        box-shadow: 0 0 12px rgba(0, 217, 255, 0.6), inset 0 0 8px rgba(255, 255, 255, 0.3);
        animation: ai-cube-pulse 2.4s ease-in-out infinite;
    }
    @keyframes ai-cube-pulse {
        0%, 100% { box-shadow: 0 0 12px rgba(0, 217, 255, 0.55); }
        50% { box-shadow: 0 0 24px rgba(0, 217, 255, 0.9); }
    }

    .ai-eyebrow {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.25em;
        color: rgba(255, 255, 255, 0.5);
        font-weight: 600;
    }
    .ai-eyebrow-cyan { color: rgba(34, 211, 238, 0.85); }

    .ai-title {
        font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
        font-size: clamp(1.75rem, 3vw, 2.75rem);
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #ffffff;
        line-height: 1.1;
    }
    .ai-dot {
        background: linear-gradient(135deg, #00d9ff, #22d3ee);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }
    .ai-sub {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.68);
        line-height: 1.6;
    }

    /* Top stats */
    .ai-stat {
        position: relative;
        overflow: hidden;
        border-radius: 14px;
        background: linear-gradient(160deg, rgba(15, 21, 48, 0.92) 0%, rgba(10, 14, 39, 0.92) 100%);
        border: 1px solid rgba(0, 217, 255, 0.18);
        padding: 1.5rem;
    }
    .ai-stat-glow {
        position: absolute;
        top: -50px;
        right: -50px;
        width: 180px;
        height: 180px;
        background: radial-gradient(circle, rgba(0, 217, 255, 0.30), transparent 70%);
        filter: blur(30px);
        pointer-events: none;
    }
    .ai-stat-value {
        font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        line-height: 1;
        background: linear-gradient(135deg, #ffffff 0%, #22d3ee 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    /* Live indicator */
    .ai-live-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 9999px;
        background: #00d9ff;
        box-shadow: 0 0 0 0 rgba(0, 217, 255, 0.6);
        animation: ai-ping 1.8s ease-out infinite;
    }
    @keyframes ai-ping {
        0% { box-shadow: 0 0 0 0 rgba(0, 217, 255, 0.6); }
        70%, 100% { box-shadow: 0 0 0 10px rgba(0, 217, 255, 0); }
    }

    /* Agent card */
    .ai-agent {
        position: relative;
        overflow: hidden;
        border-radius: 16px;
        background: linear-gradient(160deg, rgba(15, 21, 48, 0.92) 0%, rgba(10, 14, 39, 0.92) 100%);
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 1.25rem;
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    }
    .ai-agent:hover {
        transform: translateY(-2px);
        border-color: color-mix(in srgb, var(--accent) 50%, transparent);
        box-shadow: 0 0 28px color-mix(in srgb, var(--accent) 15%, transparent);
    }
    .ai-agent-glow {
        position: absolute;
        top: -40px;
        right: -40px;
        width: 140px;
        height: 140px;
        background: radial-gradient(circle, color-mix(in srgb, var(--accent) 40%, transparent), transparent 70%);
        filter: blur(20px);
        opacity: 0.55;
        pointer-events: none;
    }

    /* Agent avatar with double pulse rings */
    .ai-agent-avatar {
        position: relative;
        width: 48px;
        height: 48px;
        flex-shrink: 0;
        border-radius: 14px;
        background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 25%, transparent) 0%, transparent 100%);
        border: 1px solid color-mix(in srgb, var(--accent) 50%, transparent);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 16px color-mix(in srgb, var(--accent) 25%, transparent);
    }
    .ai-agent-icon {
        font-size: 24px !important;
        color: var(--accent);
        filter: drop-shadow(0 0 6px color-mix(in srgb, var(--accent) 60%, transparent));
    }
    .ai-agent-pulse {
        position: absolute;
        inset: -1px;
        border-radius: 14px;
        border: 1px solid var(--accent);
        opacity: 0;
        animation: ai-agent-pulse 2.4s ease-out infinite;
        pointer-events: none;
    }
    .ai-agent-pulse-2 { animation-delay: 1.2s; }
    @keyframes ai-agent-pulse {
        0% { opacity: 0.5; transform: scale(1); }
        100% { opacity: 0; transform: scale(1.45); }
    }

    .ai-running {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.1rem 0.45rem;
        font-size: 0.55rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        color: var(--accent);
        background: color-mix(in srgb, var(--accent) 12%, transparent);
        border: 1px solid color-mix(in srgb, var(--accent) 40%, transparent);
        border-radius: 9999px;
    }
    .ai-running-dot {
        width: 5px;
        height: 5px;
        border-radius: 9999px;
        background: var(--accent);
        box-shadow: 0 0 6px var(--accent);
        animation: ai-running-blink 1.4s ease-in-out infinite;
    }
    @keyframes ai-running-blink {
        50% { opacity: 0.3; }
    }

    /* Speech bubble */
    .ai-bubble {
        position: relative;
        background: rgba(5, 8, 22, 0.6);
        border: 1px solid color-mix(in srgb, var(--accent) 25%, transparent);
        border-radius: 12px;
        padding: 0.85rem 1rem;
        min-height: 72px;
    }
    .ai-bubble::before {
        content: '';
        position: absolute;
        top: -7px;
        left: 22px;
        width: 12px;
        height: 12px;
        background: rgba(5, 8, 22, 0.6);
        border-top: 1px solid color-mix(in srgb, var(--accent) 25%, transparent);
        border-left: 1px solid color-mix(in srgb, var(--accent) 25%, transparent);
        transform: rotate(45deg);
    }
    .ai-bubble-text {
        font-family: 'Inter', system-ui, sans-serif;
        font-size: 0.85rem;
        line-height: 1.55;
        color: #ffffff;
        word-break: break-word;
    }
    .ai-bubble-caret {
        display: inline-block;
        width: 7px;
        height: 14px;
        background: var(--accent);
        margin-left: 2px;
        vertical-align: -2px;
        animation: ai-blink 1.1s steps(2) infinite;
        box-shadow: 0 0 8px color-mix(in srgb, var(--accent) 60%, transparent);
    }
    @keyframes ai-blink { 50% { opacity: 0; } }

    /* Thinking dots after typing pause */
    .ai-dots {
        display: inline-flex;
        gap: 3px;
        margin-left: 6px;
        vertical-align: 1px;
    }
    .ai-dots span {
        display: inline-block;
        width: 4px;
        height: 4px;
        border-radius: 9999px;
        background: var(--accent);
        animation: ai-dots-bounce 1.2s ease-in-out infinite;
    }
    .ai-dots span:nth-child(2) { animation-delay: 0.15s; }
    .ai-dots span:nth-child(3) { animation-delay: 0.3s; }
    @keyframes ai-dots-bounce {
        0%, 100% { opacity: 0.25; transform: translateY(0); }
        50% { opacity: 1; transform: translateY(-3px); }
    }

    .ai-saved-value {
        font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
        margin-top: 0.15rem;
    }

    .ai-ghost-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.4rem 0.7rem;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: rgba(255, 255, 255, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.02);
        transition: color 0.2s ease, border-color 0.2s ease, background 0.2s ease;
    }
    .ai-ghost-btn:hover {
        color: var(--accent);
        border-color: color-mix(in srgb, var(--accent) 50%, transparent);
        background: color-mix(in srgb, var(--accent) 8%, transparent);
    }

    /* CTA */
    .ai-cta {
        position: relative;
        overflow: hidden;
        border-radius: 18px;
        background: linear-gradient(160deg, rgba(15, 21, 48, 0.92) 0%, rgba(10, 14, 39, 0.92) 100%);
        border: 1px solid rgba(0, 217, 255, 0.18);
        padding: 2rem 2rem;
    }
    .ai-cta-glow {
        position: absolute;
        border-radius: 9999px;
        filter: blur(60px);
        pointer-events: none;
    }
    .ai-cta-glow-cyan {
        top: -80px;
        left: -80px;
        width: 280px;
        height: 280px;
        background: radial-gradient(circle, rgba(0, 217, 255, 0.30), transparent 70%);
    }
    .ai-cta-glow-violet {
        bottom: -80px;
        right: -64px;
        width: 280px;
        height: 280px;
        background: radial-gradient(circle, rgba(168, 85, 247, 0.30), transparent 70%);
    }

    .ai-primary-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.7rem 1.3rem;
        font-size: 0.875rem;
        font-weight: 600;
        color: #0a0e27;
        background: linear-gradient(135deg, #00d9ff 0%, #22d3ee 100%);
        border-radius: 9999px;
        box-shadow: 0 0 24px rgba(0, 217, 255, 0.40);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .ai-primary-btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 0 32px rgba(0, 217, 255, 0.60);
    }
    .ai-secondary-btn {
        display: inline-flex;
        align-items: center;
        padding: 0.7rem 1.3rem;
        font-size: 0.875rem;
        font-weight: 600;
        color: #ffffff;
        border: 1px solid rgba(0, 217, 255, 0.40);
        border-radius: 9999px;
        background: transparent;
        transition: background 0.2s ease, border-color 0.2s ease;
    }
    .ai-secondary-btn:hover {
        background: rgba(0, 217, 255, 0.08);
        border-color: rgba(0, 217, 255, 0.70);
    }
</style>
