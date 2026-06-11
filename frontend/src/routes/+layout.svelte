<script lang="ts">
    import '../app.css';
    import { page, navigating } from '$app/stores';
    import type { LayoutData } from './$types';

    export let data: LayoutData;

    $: path = $page.url.pathname;
    $: isLogin = path === '/login';

    const nav = [
        { href: '/', label: 'Overview' },
        { href: '/customers', label: 'Customers' },
        { href: '/jobs', label: 'Jobs' },
        { href: '/quotes', label: 'Quotes' },
        { href: '/orders', label: 'Orders' },
        { href: '/inventory', label: 'Inventory' },
        { href: '/pricing', label: 'Pricing' },
        { href: '/settings/integrations', label: 'Integrations' }
    ];

    $: bcOnline =
        !!data.integrations?.businessCentral.configured &&
        data.integrations.businessCentral.lastSync?.status !== 'failed';
    $: sfOnline =
        !!data.integrations?.salesforce.configured &&
        data.integrations.salesforce.lastSync?.status !== 'failed';
</script>

{#if $navigating}
    <!-- Top progress bar -->
    <div class="fixed top-0 left-0 right-0 z-50 h-[3px] bg-primary-container/20 overflow-hidden">
        <div class="h-full bg-primary-container animate-[indeterminate_1.2s_ease-in-out_infinite]" />
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
    <div class="min-h-screen bg-surface-container-low flex">
        <!-- Sidebar -->
        <aside class="w-64 bg-white border-r border-zinc-200 flex flex-col">
            <div class="px-5 py-6 border-b border-zinc-200">
                <div class="font-h2 text-xl font-semibold text-on-surface leading-none">
                    ICC<span class="text-primary-container">.</span>
                </div>
                <div class="eyebrow mt-1.5">Operations</div>
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
                        {data.user?.isAdmin ? 'Administrator' : 'Operator'}
                    </div>
                    <form method="POST" action="/login?/logout" class="mt-2">
                        <button class="btn-ghost">Sign out</button>
                    </form>
                </div>
            </div>
        </aside>

        <main class="flex-1 overflow-x-hidden">
            <slot />
        </main>
    </div>
{/if}
