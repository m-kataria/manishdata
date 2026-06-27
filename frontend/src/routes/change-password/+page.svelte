<script lang="ts">
    import { page } from '$app/stores';

    let current = '';
    let next = '';
    let confirm = '';
    let showCurrent = false;
    let showNext = false;
    let showConfirm = false;
    let busy = false;
    let error = '';
    let toast = '';

    $: me = $page.data.user;
    $: nextLen = next.length;
    $: meetsLength = nextLen >= 8;
    $: barPct = Math.min(100, (nextLen / 8) * 100);
    $: barColor = nextLen === 0
        ? 'bg-zinc-200'
        : meetsLength
            ? 'bg-emerald-500'
            : 'bg-amber-400';

    function showToast(msg: string) {
        toast = msg;
        setTimeout(() => {
            toast = '';
        }, 2500);
    }

    // Svelte disallows dynamic `type` together with `bind:value`. Use one-way value
    // bindings + explicit input handlers so the eye toggle can switch text/password.
    function setCurrent(e: Event) {
        current = (e.currentTarget as HTMLInputElement).value;
    }
    function setNext(e: Event) {
        next = (e.currentTarget as HTMLInputElement).value;
    }
    function setConfirm(e: Event) {
        confirm = (e.currentTarget as HTMLInputElement).value;
    }

    async function submit() {
        error = '';
        if (!current || !next || !confirm) {
            error = 'All fields are required.';
            return;
        }
        if (next.length < 8) {
            error = 'New password must be at least 8 characters.';
            return;
        }
        if (next !== confirm) {
            error = "New password and confirmation don't match.";
            return;
        }
        if (next === current) {
            error = 'New password must be different from the current one.';
            return;
        }
        busy = true;
        try {
            const res = await fetch('/api/auth/change-password', {
                method: 'POST',
                headers: { 'content-type': 'application/json' },
                body: JSON.stringify({ currentPassword: current, newPassword: next })
            });
            if (!res.ok) {
                const j = await res.json().catch(() => ({}));
                error = j.error ?? `Failed (${res.status})`;
                return;
            }
            current = '';
            next = '';
            confirm = '';
            showToast('Password changed successfully.');
        } finally {
            busy = false;
        }
    }
</script>

<!-- Toast (fixed, top-right, auto-dismisses) -->
{#if toast}
    <div
        class="fixed top-20 right-6 z-50 bg-emerald-50 border-2 border-emerald-500 text-emerald-800 rounded-card px-5 py-3 shadow-lg flex items-center gap-3 nrv-toast-in"
        role="status"
    >
        <span class="material-symbols-outlined text-emerald-600" style="font-size: 22px">
            check_circle
        </span>
        <span class="font-body-md text-sm font-medium">{toast}</span>
    </div>
{/if}

<div class="px-8 py-8 mx-auto max-w-[560px]">
    <div class="mb-8">
        <p class="eyebrow mb-1">Account</p>
        <h1 class="font-h2 text-h2 text-on-surface font-semibold">Change password.</h1>
        <p class="font-body-md text-sm text-secondary mt-2">
            Signed in as <span class="font-medium text-on-surface">{me?.displayName ?? me?.username}</span>.
        </p>
    </div>

    <section class="card">
        <form on:submit|preventDefault={submit} class="px-6 py-6 flex flex-col gap-5">
            <!-- Current password -->
            <div class="flex flex-col gap-1">
                <label for="cp-current" class="field-label">Current password</label>
                <div class="relative">
                    <input
                        id="cp-current"
                        type={showCurrent ? 'text' : 'password'}
                        value={current}
                        on:input={setCurrent}
                        class="field !pr-11 w-full"
                        autocomplete="current-password"
                        required
                    />
                    <button
                        type="button"
                        on:click={() => (showCurrent = !showCurrent)}
                        aria-label={showCurrent ? 'Hide password' : 'Show password'}
                        title={showCurrent ? 'Hide password' : 'Show password'}
                        class="absolute inset-y-0 right-0 px-3 flex items-center text-secondary hover:text-on-surface"
                    >
                        <span class="material-symbols-outlined" style="font-size: 20px">
                            {showCurrent ? 'visibility_off' : 'visibility'}
                        </span>
                    </button>
                </div>
            </div>

            <!-- New password -->
            <div class="flex flex-col gap-1">
                <label for="cp-new" class="field-label">New password</label>
                <div class="relative">
                    <input
                        id="cp-new"
                        type={showNext ? 'text' : 'password'}
                        value={next}
                        on:input={setNext}
                        class="field !pr-11 w-full"
                        autocomplete="new-password"
                        required
                    />
                    <button
                        type="button"
                        on:click={() => (showNext = !showNext)}
                        aria-label={showNext ? 'Hide password' : 'Show password'}
                        title={showNext ? 'Hide password' : 'Show password'}
                        class="absolute inset-y-0 right-0 px-3 flex items-center text-secondary hover:text-on-surface"
                    >
                        <span class="material-symbols-outlined" style="font-size: 20px">
                            {showNext ? 'visibility_off' : 'visibility'}
                        </span>
                    </button>
                </div>

                <!-- Strength / length bar -->
                <div class="h-1.5 mt-2 rounded-full bg-zinc-100 overflow-hidden">
                    <div
                        class="h-full {barColor} transition-all duration-200"
                        style="width: {barPct}%"
                    ></div>
                </div>
                <p
                    class="font-label-sm text-xs mt-1 {meetsLength
                        ? 'text-emerald-600'
                        : 'text-secondary'}"
                >
                    {#if nextLen === 0}
                        At least 8 characters.
                    {:else if meetsLength}
                        Length OK ({nextLen} characters).
                    {:else}
                        {nextLen} of 8 characters.
                    {/if}
                </p>
            </div>

            <!-- Confirm new password -->
            <div class="flex flex-col gap-1">
                <label for="cp-confirm" class="field-label">Confirm new password</label>
                <div class="relative">
                    <input
                        id="cp-confirm"
                        type={showConfirm ? 'text' : 'password'}
                        value={confirm}
                        on:input={setConfirm}
                        class="field !pr-11 w-full"
                        autocomplete="new-password"
                        required
                    />
                    <button
                        type="button"
                        on:click={() => (showConfirm = !showConfirm)}
                        aria-label={showConfirm ? 'Hide password' : 'Show password'}
                        title={showConfirm ? 'Hide password' : 'Show password'}
                        class="absolute inset-y-0 right-0 px-3 flex items-center text-secondary hover:text-on-surface"
                    >
                        <span class="material-symbols-outlined" style="font-size: 20px">
                            {showConfirm ? 'visibility_off' : 'visibility'}
                        </span>
                    </button>
                </div>
                {#if confirm && next && confirm !== next}
                    <p class="font-label-sm text-xs text-error mt-1">
                        Doesn't match the new password yet.
                    </p>
                {/if}
            </div>

            {#if error}
                <div class="border-l-4 border-error bg-rose-50 px-4 py-3 flex items-start gap-3">
                    <span class="material-symbols-outlined text-error" style="font-size: 20px">
                        error
                    </span>
                    <p class="font-body-md text-sm text-on-surface">{error}</p>
                </div>
            {/if}

            <div class="flex justify-end gap-3 pt-2">
                <a href="/" class="btn-outline px-6">Cancel</a>
                <button type="submit" class="btn-primary px-8" disabled={busy}>
                    {busy ? 'Updating…' : 'Update password'}
                </button>
            </div>
        </form>
    </section>
</div>

<style>
    @keyframes toast-in {
        0% {
            opacity: 0;
            transform: translateY(-8px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }
    :global(.nrv-toast-in) {
        animation: toast-in 180ms ease-out;
    }
</style>
