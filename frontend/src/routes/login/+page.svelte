<script lang="ts">
    import { enhance } from '$app/forms';
    import type { ActionData } from './$types';

    export let form: ActionData;

    let submitting = false;
</script>

<div
    class="min-h-screen flex items-center justify-center p-6"
    style="background: linear-gradient(135deg, #0A2032 0%, #253443 100%);"
>
    <form
        method="POST"
        action="?/login"
        use:enhance={() => {
            submitting = true;
            return async ({ update }) => {
                await update();
                submitting = false;
            };
        }}
        class="card w-full max-w-md p-10"
    >
        <!-- Wordmark -->
        <div class="mb-8 section-heading">
            <p class="eyebrow mb-1">Nerval Corporation · est. 1985</p>
            <h1 class="font-h2 text-h2 text-on-surface font-semibold">ICC Operations.</h1>
        </div>

        <div class="flex flex-col gap-5">
            <div class="flex flex-col gap-1">
                <label for="login-username" class="field-label">User ID</label>
                <input
                    id="login-username"
                    name="username"
                    type="text"
                    autocomplete="username"
                    value={form?.username ?? ''}
                    class="field"
                    required
                />
            </div>

            <div class="flex flex-col gap-1">
                <label for="login-password" class="field-label">Passphrase</label>
                <input
                    id="login-password"
                    name="password"
                    type="password"
                    autocomplete="current-password"
                    class="field"
                    required
                />
            </div>

            {#if form?.error}
                <div
                    class="border-l-4 border-error bg-surface-container-low px-5 py-4 flex gap-3 items-start"
                >
                    <span class="material-symbols-outlined text-error">error</span>
                    <p class="font-body-md text-sm text-on-surface">{form.error}</p>
                </div>
            {/if}

            <button
                type="submit"
                disabled={submitting}
                class="signin-btn w-full mt-2 px-5 py-3 rounded-lg font-medium text-white transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
            >
                {submitting ? 'Authenticating…' : 'Sign In'}
            </button>
        </div>
    </form>
</div>

<style>
    .signin-btn {
        background-color: #4ec5c5;
    }
    .signin-btn:hover:not(:disabled) {
        background-color: #3aa8a8;
    }
</style>
