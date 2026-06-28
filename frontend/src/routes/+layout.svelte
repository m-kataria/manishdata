<script lang="ts">
    import '../app.css';
    import { onMount } from 'svelte';
    import { page, navigating } from '$app/stores';
    import type { LayoutData } from './$types';

    export let data: LayoutData;

    $: path = $page.url.pathname;
    $: isLogin = path === '/login';

    let sidebarOpen = false;
    let darkMode = false;
    onMount(() => {
        const saved = localStorage.getItem('nrv.sidebarOpen');
        if (saved === '1') sidebarOpen = true;
        const theme = localStorage.getItem('nrv.theme');
        darkMode = theme === 'dark';
        applyTheme();
    });
    function toggleSidebar() {
        sidebarOpen = !sidebarOpen;
        try { localStorage.setItem('nrv.sidebarOpen', sidebarOpen ? '1' : '0'); } catch {}
    }
    function closeSidebar() {
        if (sidebarOpen) {
            sidebarOpen = false;
            try { localStorage.setItem('nrv.sidebarOpen', '0'); } catch {}
        }
    }
    function applyTheme() {
        if (typeof document === 'undefined') return;
        document.documentElement.classList.toggle('dark', darkMode);
    }
    function toggleTheme() {
        darkMode = !darkMode;
        try { localStorage.setItem('nrv.theme', darkMode ? 'dark' : 'light'); } catch {}
        applyTheme();
    }

    type NavItem = { href: string; label: string };
    // The top app bar already covers Home / Customers / Quotes / Orders / Inventory /
    // Pricing / Jobs / Help — the sidebar is reserved for settings + utility links.
    // Users + Integrations are superadmin-only; everyone sees Contact Support.
    $: nav = (data.user?.role === 'superadmin'
        ? [
              { href: '/users', label: 'Users' },
              { href: '/support', label: 'Contact Support' },
              { href: '/settings/integrations', label: 'Integrations' }
          ]
        : [{ href: '/support', label: 'Contact Support' }]) satisfies NavItem[];

    $: bcOnline =
        !!data.integrations?.businessCentral.configured &&
        data.integrations.businessCentral.lastSync?.status !== 'failed';
    $: sfOnline =
        !!data.integrations?.salesforce.configured &&
        data.integrations.salesforce.lastSync?.status !== 'failed';
</script>

{#if $navigating}
    <!-- Top progress bar (matches LoadingBar brand styling) -->
    <div class="fixed top-0 left-0 right-0 z-50 h-1 bg-zinc-100 overflow-hidden">
        <div class="h-full w-2/5 bg-gradient-to-r from-primary-container to-primary nrv-indeterminate"></div>
    </div>
    <!-- Floating LOADING pill -->
    <div
        class="fixed top-4 right-6 z-40 bg-white border-2 border-primary-container rounded-card px-4 py-2 flex items-center gap-2.5 pointer-events-none"
    >
        <span class="relative flex h-2.5 w-2.5">
            <span
                class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-container opacity-75"
            ></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-primary-container"></span>
        </span>
        <span
            class="font-label-sm text-xs uppercase tracking-[0.2em] text-primary-container font-semibold"
        >
            Loading
            {#if $navigating?.to?.url.pathname}
                <span class="text-on-surface opacity-60">·</span>
                <span class="text-on-surface">{$navigating.to.url.pathname}</span>
            {/if}
        </span>
    </div>
{/if}

<style>
    @keyframes indeterminate {
        0% {
            width: 0;
            margin-left: 0;
        }
        50% {
            width: 50%;
            margin-left: 25%;
        }
        100% {
            width: 0;
            margin-left: 100%;
        }
    }

    /* ── TotalITsuite app shell (dark cyan AI theme) ──────────────────── */
    :global(.tis-app-shell) {
        background:
            radial-gradient(1100px 600px at 15% 0%, rgba(0, 217, 255, 0.08), transparent 60%),
            radial-gradient(900px 500px at 95% 10%, rgba(168, 85, 247, 0.06), transparent 60%),
            linear-gradient(180deg, #050816 0%, #0a0e27 50%, #050816 100%);
        color: #ffffff;
        overflow-x: hidden;
    }

    :global(.tis-app-grid) {
        position: fixed;
        inset: 0;
        background-image:
            linear-gradient(rgba(0, 217, 255, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 217, 255, 0.04) 1px, transparent 1px);
        background-size: 64px 64px;
        mask-image: radial-gradient(ellipse at center, black 0%, transparent 75%);
        animation: tis-grid-drift 40s linear infinite;
        pointer-events: none;
        z-index: 0;
    }
    @keyframes tis-grid-drift {
        from { background-position: 0 0, 0 0; }
        to { background-position: 64px 64px, 64px 64px; }
    }

    :global(.tis-app-scan) {
        position: fixed;
        left: 0;
        right: 0;
        top: 0;
        height: 220px;
        background: linear-gradient(180deg, transparent 0%, rgba(0, 217, 255, 0.05) 50%, transparent 100%);
        animation: tis-scan-move 12s linear infinite;
        pointer-events: none;
        mix-blend-mode: screen;
        z-index: 0;
    }
    @keyframes tis-scan-move {
        0% { transform: translateY(-220px); opacity: 0; }
        15% { opacity: 1; }
        85% { opacity: 1; }
        100% { transform: translateY(100vh); opacity: 0; }
    }

    /* Topbar */
    :global(.tis-topbar) {
        background: linear-gradient(180deg, rgba(10, 14, 39, 0.92) 0%, rgba(15, 21, 48, 0.82) 100%);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border-bottom: 1px solid rgba(0, 217, 255, 0.12);
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
        color: #ffffff;
    }

    /* Icon-only button (hamburger, close, etc.) */
    :global(.tis-iconbtn) {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        border-radius: 9999px;
        color: rgba(255, 255, 255, 0.85);
        transition: background 0.2s ease, color 0.2s ease;
    }
    :global(.tis-iconbtn:hover) {
        background: rgba(0, 217, 255, 0.10);
        color: #00d9ff;
    }

    /* Wordmark cube (small, for top bar / sidebar) */
    :global(.tis-cube-sm) {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: linear-gradient(135deg, #00d9ff 0%, #22d3ee 100%);
        transform: rotate(45deg);
        box-shadow:
            0 0 10px rgba(0, 217, 255, 0.6),
            inset 0 0 6px rgba(255, 255, 255, 0.3);
        animation: tis-cube-pulse 2.4s ease-in-out infinite;
    }
    @keyframes tis-cube-pulse {
        0%, 100% { box-shadow: 0 0 10px rgba(0, 217, 255, 0.55), inset 0 0 6px rgba(255, 255, 255, 0.3); }
        50% { box-shadow: 0 0 20px rgba(0, 217, 255, 0.9), inset 0 0 6px rgba(255, 255, 255, 0.5); }
    }
    :global(.tis-dot-cyan) {
        background: linear-gradient(135deg, #00d9ff, #22d3ee);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    /* Nav items */
    :global(.tis-navitem) {
        position: relative;
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0 0.75rem;
        height: 36px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        white-space: nowrap;
        color: rgba(255, 255, 255, 0.75);
        transition: background 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
        flex-shrink: 0;
    }
    :global(.tis-navitem:hover) {
        background: rgba(0, 217, 255, 0.08);
        color: #ffffff;
    }
    :global(.tis-navitem-active) {
        background: linear-gradient(135deg, #00d9ff 0%, #22d3ee 100%);
        color: #0a0e27;
        box-shadow: 0 0 18px rgba(0, 217, 255, 0.35), inset 0 0 12px rgba(255, 255, 255, 0.15);
    }
    :global(.tis-navitem-active:hover) {
        color: #0a0e27;
        background: linear-gradient(135deg, #00d9ff 0%, #22d3ee 100%);
    }
    :global(.tis-navitem .material-symbols-outlined) {
        color: inherit;
    }

    /* Sign out (top bar) */
    :global(.tis-signout) {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        height: 36px;
        padding: 0 0.75rem;
        border-radius: 9999px;
        color: #fb7185;
        transition: background 0.2s ease, color 0.2s ease;
    }
    :global(.tis-signout:hover) {
        background: rgba(244, 63, 94, 0.12);
        color: #fda4af;
    }

    /* Sidebar */
    :global(.tis-sidebar) {
        background: linear-gradient(180deg, rgba(5, 8, 22, 0.96) 0%, rgba(10, 14, 39, 0.96) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-right: 1px solid rgba(0, 217, 255, 0.12);
        color: #ffffff;
    }

    /* Sidebar action buttons */
    :global(.tis-signout-block) {
        background: rgba(244, 63, 94, 0.10);
        color: #fb7185;
        border: 1px solid rgba(244, 63, 94, 0.30);
        font-weight: 600;
        font-size: 0.875rem;
        transition: background 0.2s ease, border-color 0.2s ease;
    }
    :global(.tis-signout-block:hover) {
        background: rgba(244, 63, 94, 0.18);
        border-color: rgba(244, 63, 94, 0.50);
    }
    :global(.tis-secondary-btn) {
        background: rgba(0, 217, 255, 0.06);
        color: #ffffff;
        border: 1px solid rgba(0, 217, 255, 0.20);
        font-weight: 600;
        font-size: 0.875rem;
        transition: background 0.2s ease, border-color 0.2s ease;
    }
    :global(.tis-secondary-btn:hover) {
        background: rgba(0, 217, 255, 0.12);
        border-color: rgba(0, 217, 255, 0.40);
    }

    /* Push <main> above the ambient backdrop */
    :global(.tis-app-shell > main) {
        position: relative;
        z-index: 1;
    }
</style>

{#if isLogin}
    <slot />
{:else}
    <div class="min-h-screen relative tis-app-shell">
        <!-- Global AI ambient backdrop -->
        <div class="tis-app-grid" aria-hidden="true"></div>
        <div class="tis-app-scan" aria-hidden="true"></div>

        <!-- Top app bar (full-width, fixed) -->
        <header class="fixed top-0 left-0 right-0 z-40 h-14 tis-topbar flex items-center gap-3 px-4">
            <!-- Hamburger -->
            <button
                type="button"
                on:click={toggleSidebar}
                aria-label={sidebarOpen ? 'Hide menu' : 'Show menu'}
                class="tis-iconbtn flex-shrink-0"
            >
                <span class="material-symbols-outlined" style="font-size: 22px">
                    {sidebarOpen ? 'chevron_left' : 'menu'}
                </span>
            </button>

            <!-- Brand mark with cube glyph -->
            <span class="flex items-center gap-2 flex-shrink-0 px-1 mr-2 hidden sm:flex">
                <span class="tis-cube-sm" aria-hidden="true"></span>
                <span class="font-h3 text-base font-semibold text-white leading-none">
                    TIS<span class="tis-dot-cyan">.</span>
                </span>
            </span>

            <span class="h-6 w-px bg-white/[0.08] mr-1 hidden sm:block"></span>

            <!-- Section nav (centered) -->
            <nav class="flex-1 flex items-center justify-center gap-1 overflow-x-auto no-scrollbar">
                {#each [
                    { href: '/', label: 'Home', icon: 'home', exact: true },
                    { href: '/customers', label: 'Customers', icon: 'groups' },
                    { href: '/quotes', label: 'Quotes', icon: 'request_quote' },
                    { href: '/orders', label: 'Orders', icon: 'receipt_long' },
                    { href: '/inventory', label: 'Inventory', icon: 'inventory_2' },
                    { href: '/pricing', label: 'Pricing', icon: 'sell' },
                    { href: '/jobs', label: 'Jobs', icon: 'engineering' },
                    { href: '/help', label: 'Help', icon: 'help' }
                ] as item}
                    {@const isActive = item.exact ? path === item.href : path.startsWith(item.href)}
                    <a
                        href={item.href}
                        title={item.label}
                        class="tis-navitem {isActive ? 'tis-navitem-active' : ''}"
                    >
                        <span class="material-symbols-outlined" style="font-size: 18px">{item.icon}</span>
                        <span class="hidden md:inline">{item.label}</span>
                    </a>
                {/each}
            </nav>

            <!-- User -->
            <div class="flex items-center gap-2 flex-shrink-0 ml-2">
                <span class="hidden md:block text-xs text-white/60">
                    {data.user?.displayName ?? data.user?.username ?? ''}
                </span>
                <form method="POST" action="/login?/logout">
                    <button
                        type="submit"
                        title="Sign out"
                        aria-label="Sign out"
                        class="tis-signout"
                    >
                        <span class="material-symbols-outlined" style="font-size: 20px">logout</span>
                        <span class="hidden md:inline text-xs font-semibold uppercase tracking-wide">Sign out</span>
                    </button>
                </form>
            </div>
        </header>

        <!-- Backdrop when sidebar is open -->
        {#if sidebarOpen}
            <button
                type="button"
                aria-label="Close menu"
                on:click={closeSidebar}
                class="fixed inset-0 z-30 bg-zinc-900/30 lg:bg-transparent"
            ></button>
        {/if}

        <!-- Sidebar (drawer, hidden by default) -->
        <aside
            class="fixed inset-y-0 left-0 z-40 w-52 tis-sidebar flex flex-col transform transition-transform duration-200 {sidebarOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full'}"
        >
            <div class="px-5 py-6 border-b border-white/[0.06] flex items-start justify-between gap-2">
                <div>
                    <div class="flex items-center gap-2">
                        <span class="tis-cube-sm" aria-hidden="true"></span>
                        <div class="font-h2 text-xl font-semibold text-white leading-none">
                            TIS<span class="tis-dot-cyan">.</span>
                        </div>
                    </div>
                    <div class="eyebrow mt-2 text-[#22d3ee]/80">Client Portal</div>
                </div>
                <button
                    type="button"
                    on:click={closeSidebar}
                    aria-label="Close menu"
                    title="Close menu"
                    class="tis-iconbtn flex-shrink-0 -mr-2"
                >
                    <span class="material-symbols-outlined" style="font-size: 22px">chevron_left</span>
                </button>
            </div>

            <div class="px-3 pt-3 flex flex-col gap-2">
                <form method="POST" action="/login?/logout">
                    <button
                        type="submit"
                        class="w-full inline-flex items-center justify-center gap-2 h-10 px-4 rounded-md tis-signout-block"
                    >
                        <span class="material-symbols-outlined" style="font-size: 20px">logout</span>
                        <span>Sign out</span>
                    </button>
                </form>
                <a
                    href="/change-password"
                    class="w-full inline-flex items-center justify-center gap-2 h-10 px-4 rounded-md tis-secondary-btn"
                >
                    <span class="material-symbols-outlined" style="font-size: 20px">key</span>
                    <span>Change password</span>
                </a>
            </div>

            <nav class="flex-1 px-3 py-5 flex flex-col gap-1">
                {#each nav as item (item.href)}
                    {@const active = item.href === '/' ? path === '/' : path.startsWith(item.href)}
                    {@const navTarget = $navigating?.to?.url.pathname ?? ''}
                    {@const loading =
                        !!navTarget &&
                        !active &&
                        (item.href === '/' ? navTarget === '/' : navTarget.startsWith(item.href))}
                    <a
                        href={item.href}
                        class="{active ? 'nav-item-active' : 'nav-item'} justify-between"
                        data-sveltekit-preload-data="tap"
                    >
                        <span>{item.label}</span>
                        {#if loading}
                            <span class="inline-flex items-center gap-1">
                                <span class="w-1 h-1 rounded-full bg-current animate-pulse"></span>
                                <span
                                    class="w-1 h-1 rounded-full bg-current animate-pulse"
                                    style="animation-delay: 0.2s"
                                ></span>
                                <span
                                    class="w-1 h-1 rounded-full bg-current animate-pulse"
                                    style="animation-delay: 0.4s"
                                ></span>
                            </span>
                        {/if}
                    </a>
                {/each}
            </nav>

            <!-- Channel status mini-panel -->
            <div class="px-5 py-4 border-t border-white/[0.06]">
                <div class="eyebrow mb-3 text-[#22d3ee]/80">Channels</div>
                <ul class="space-y-2 mb-5">
                    <li class="flex items-center justify-between">
                        <span class="flex items-center gap-2">
                            <span class={bcOnline ? 'dot-bc' : 'dot-off'} />
                            <span class="font-body-md text-sm text-on-surface">BC</span>
                        </span>
                        <span class="font-label-sm text-xs text-secondary">
                            {bcOnline ? 'Online' : 'Offline'}
                        </span>
                    </li>
                    <li class="flex items-center justify-between">
                        <span class="flex items-center gap-2">
                            <span class={sfOnline ? 'dot-sf' : 'dot-off'} />
                            <span class="font-body-md text-sm text-on-surface">SF</span>
                        </span>
                        <span class="font-label-sm text-xs text-secondary">
                            {sfOnline ? 'Online' : 'Offline'}
                        </span>
                    </li>
                </ul>

                <div class="border-t border-white/[0.06] pt-4">
                    <div class="font-body-md text-sm text-white font-medium">
                        {data.user?.displayName ?? data.user?.username ?? '—'}
                    </div>
                    <div class="font-label-sm text-xs text-white/55">
                        {data.user?.role === 'superadmin' ? 'Superadmin' : 'Administrator'}
                    </div>
                </div>
            </div>
        </aside>

        <main class="w-full overflow-x-hidden pt-16">
            <slot />
        </main>
    </div>
{/if}
