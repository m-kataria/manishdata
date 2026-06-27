<script lang="ts">
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';

    let current = '';
    let next = '';
    let confirm = '';
    let busy = false;
    let error = '';
    let success = false;

    $: me = $page.data.user;

    async function submit() {
        error = '';
        success = false;
        if (!current || !next || !confirm) {
            error = 'All fields are required.';
            return;
        }
        if (next.length < 8) {
            error = 'New password must be at least 8 characters.';
            return;
        }
        if (next !== confirm) {
            error = "New passwords don't match.";
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
            success = true;
            current = '';
            next = '';
            confirm = '';
            setTimeout(() => goto('/'), 1500);
        } finally {
            busy = false;
        }
    }
</script>

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
            <div class="flex flex-col gap-1">
                <label for="cp-current" class="field-label">Current password</label>
                <input
                    id="cp-current"
                    type="password"
                    bind:value={current}
                    class="field"
                    autocomplete="current-password"
                    required
                />
            </div>

            <div class="flex flex-col gap-1">
                <label for="cp-new" class="field-label">New password</label>
                <input
                    id="cp-new"
                    type="password"
                    bind:value={next}
                    class="field"
                    autocomplete="new-password"
                    required
                    minlength="8"
                />
                <p class="font-label-sm text-xs text-secondary mt-1">
                    At least 8 characters.
                </p>
            </div>

            <div class="flex flex-col gap-1">
                <label for="cp-confirm" class="field-label">Confirm new password</label>
                <input
                    id="cp-confirm"
                    type="password"
                    bind:value={confirm}
                    class="field"
                    autocomplete="new-password"
                    required
                />
            </div>

            {#if error}
                <p class="font-body-md text-sm text-error">{error}</p>
            {/if}
            {#if success}
                <p class="font-body-md text-sm text-emerald-600">
                    Password updated. Redirecting…
                </p>
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
