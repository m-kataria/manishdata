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
    const baseNav: NavItem[] = [
        { href: '/settings/integrations', label: 'Integrations' },
        { href: '/support', label: 'Contact Support' }
    ];
    $: nav = data.user?.role === 'superadmin'
        ? [{ href: '/users', label: 'Users' }, ...baseNav]
        : baseNav;

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
</style>

{#if isLogin}
    <slot />
{:else}
    <div class="min-h-screen bg-surface-container-low relative">
        <!-- Top app bar (full-width, fixed) -->
        <header class="fixed top-0 left-0 right-0 z-40 h-14 bg-white dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-700 shadow-sm flex items-center gap-3 px-4">
            <!-- Hamburger -->
            <button
                type="button"
                on:click={toggleSidebar}
                aria-label={sidebarOpen ? 'Hide menu' : 'Show menu'}
                class="inline-flex items-center justify-center h-9 w-9 rounded-full hover:bg-surface-container-high dark:hover:bg-zinc-800 text-on-surface dark:text-zinc-100 transition-colors flex-shrink-0"
            >
                <span class="material-symbols-outlined" style="font-size: 22px">
                    {sidebarOpen ? 'chevron_left' : 'menu'}
                </span>
            </button>

            <!-- ICC brand mark (no link, just identity) -->
            <span class="flex items-center gap-2 flex-shrink-0 px-1 mr-2 hidden sm:flex">
                <span class="font-h3 text-base font-semibold text-on-surface dark:text-zinc-100 leading-none">
                    ICC<span class="text-primary-container">.</span>
                </span>
            </span>

            <span class="h-6 w-px bg-zinc-200 dark:bg-zinc-700 mr-1 hidden sm:block"></span>

            <!-- Section nav (centered) -->
            <nav class="flex-1 flex items-center justify-center gap-1 overflow-x-auto no-scrollbar">
                {#each [
                    { href: '/', label: 'Home', icon: 'home', grad: 'from-zinc-700 to-zinc-900', accent: 'text-on-surface dark:text-zinc-100', exact: true },
                    { href: '/customers', label: 'Customers', icon: 'groups', grad: 'from-sky-500 to-indigo-600', accent: 'text-sky-600 dark:text-sky-400' },
                    { href: '/quotes', label: 'Quotes', icon: 'request_quote', grad: 'from-violet-500 to-fuchsia-600', accent: 'text-violet-600 dark:text-violet-400' },
                    { href: '/orders', label: 'Orders', icon: 'receipt_long', grad: 'from-emerald-500 to-teal-600', accent: 'text-emerald-600 dark:text-emerald-400' },
                    { href: '/inventory', label: 'Inventory', icon: 'inventory_2', grad: 'from-amber-500 to-orange-600', accent: 'text-amber-600 dark:text-amber-400' },
                    { href: '/pricing', label: 'Pricing', icon: 'sell', grad: 'from-cyan-500 to-blue-600', accent: 'text-cyan-600 dark:text-cyan-400' },
                    { href: '/jobs', label: 'Jobs', icon: 'engineering', grad: 'from-indigo-500 to-purple-700', accent: 'text-indigo-600 dark:text-indigo-400' },
                    { href: '/help', label: 'Help', icon: 'help', grad: 'from-rose-500 to-pink-600', accent: 'text-rose-600 dark:text-rose-400' }
                ] as item}
                    {@const isActive = item.exact ? path === item.href : path.startsWith(item.href)}
                    <a
                        href={item.href}
                        title={item.label}
                        class="group relative inline-flex items-center gap-1.5 rounded-md px-3 h-9 text-xs font-semibold uppercase tracking-wide whitespace-nowrap transition-all flex-shrink-0
                               {isActive
                                   ? `bg-gradient-to-br ${item.grad} text-white shadow-sm`
                                   : 'text-on-surface dark:text-zinc-300 hover:bg-surface-container-high dark:hover:bg-zinc-800'}"
                    >
                        <span
                            class="material-symbols-outlined {isActive ? 'text-white' : item.accent}"
                            style="font-size: 18px"
                        >{item.icon}</span>
                        <span class="hidden md:inline">{item.label}</span>
                    </a>
                {/each}
            </nav>

            <!-- User + theme toggle -->
            <div class="flex items-center gap-2 flex-shrink-0 ml-2">
                <span class="hidden md:block text-xs text-secondary dark:text-zinc-400">
                    {data.user?.displayName ?? data.user?.username ?? ''}
                </span>
                <button
                    type="button"
                    on:click={toggleTheme}
                    aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
                    title={darkMode ? 'Light mode' : 'Dark mode'}
                    class="inline-flex items-center justify-center h-9 w-9 rounded-full hover:bg-surface-container-high dark:hover:bg-zinc-800 text-on-surface dark:text-zinc-100 transition-colors"
                >
                    <span class="material-symbols-outlined" style="font-size: 22px">
                        {darkMode ? 'light_mode' : 'dark_mode'}
                    </span>
                </button>
                <form method="POST" action="/login?/logout">
                    <button
                        type="submit"
                        title="Sign out"
                        aria-label="Sign out"
                        class="inline-flex items-center gap-1.5 h-9 px-3 rounded-full hover:bg-rose-50 dark:hover:bg-rose-900/30 text-rose-600 dark:text-rose-400 transition-colors"
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
            class="fixed inset-y-0 left-0 z-40 w-52 bg-white border-r border-zinc-200 flex flex-col transform transition-transform duration-200 {sidebarOpen ? 'translate-x-0 shadow-xl' : '-translate-x-full'}"
        >
            <div class="px-5 py-6 border-b border-zinc-200 flex items-start justify-between gap-2">
                <div>
                    <div class="font-h2 text-xl font-semibold text-on-surface leading-none">
                        ICC<span class="text-primary-container">.</span>
                    </div>
                    <div class="eyebrow mt-1.5">Operations</div>
                </div>
                <button
                    type="button"
                    on:click={closeSidebar}
                    aria-label="Close menu"
                    title="Close menu"
                    class="inline-flex items-center justify-center h-9 w-9 -mr-2 rounded-full text-on-surface hover:bg-surface-container-high transition-colors flex-shrink-0"
                >
                    <span class="material-symbols-outlined" style="font-size: 22px">chevron_left</span>
                </button>
            </div>

            <form method="POST" action="/login?/logout" class="px-3 pt-3">
                <button
                    type="submit"
                    class="w-full inline-flex items-center justify-center gap-2 h-10 px-4 rounded-md bg-rose-50 hover:bg-rose-100 text-rose-700 font-semibold text-sm transition-colors border border-rose-200"
                >
                    <span class="material-symbols-outlined" style="font-size: 20px">logout</span>
                    <span>Sign out</span>
                </button>
            </form>

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
            <div class="px-5 py-4 border-t border-zinc-200">
                <div class="eyebrow mb-3">Channels</div>
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

                <div class="border-t border-zinc-200 pt-4">
                    <div class="font-body-md text-sm text-on-surface font-medium">
                        {data.user?.displayName ?? data.user?.username ?? '—'}
                    </div>
                    <div class="font-label-sm text-xs text-secondary">
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
