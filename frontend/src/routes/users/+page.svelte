<script lang="ts">
    import { invalidateAll } from '$app/navigation';
    import { page } from '$app/stores';
    import type { User, UserRole } from '$lib/types';
    import type { PageData } from './$types';

    export let data: PageData;

    $: me = $page.data.user as User | null;

    const accessLabels: Record<UserRole, string> = {
        superadmin: 'Superadmin',
        admin: 'Admin'
    };

    const reportsToOptions = ['Jessy', 'Manjit'];

    let busy = false;
    let formError = '';
    let newUsername = '';
    let newDisplay = '';
    let newEmail = '';
    let newPassword = '';
    let newAccess: UserRole = 'admin';
    let newJobTitle = '';
    let newReportsTo = '';
    let newMfaEnabled = false;

    // ── Password reset modal state ──────────────────────────────────────────
    // pwModalUser: the user we're resetting (null = modal closed)
    // pwInput: the password the superadmin is about to set
    // pwShow: whether to render pwInput as plain text in the input
    // pwSavedFor: once set is committed, holds the password just set — shown
    //   to the superadmin until they hit Close, then wiped. After Close the
    //   value is unrecoverable; only another reset reveals a fresh password.
    let pwModalUser: User | null = null;
    let pwInput = '';
    let pwShow = false;
    let pwSavedFor: string | null = null;
    let pwError = '';

    // Dinopass-style: {Adjective}{symbol}{Animal}{NN}, e.g. "Mild(Cheetah42".
    const PW_ADJECTIVES = [
        'Mild', 'Wild', 'Brave', 'Clever', 'Quick', 'Sneaky', 'Happy', 'Bold',
        'Fierce', 'Calm', 'Sleek', 'Jolly', 'Dusty', 'Lucky', 'Witty', 'Snappy',
        'Sunny', 'Frosty', 'Smooth', 'Spicy'
    ];
    const PW_ANIMALS = [
        'Tiger', 'Cheetah', 'Wolf', 'Bear', 'Fox', 'Lion', 'Hawk', 'Otter',
        'Lynx', 'Panda', 'Eagle', 'Falcon', 'Puma', 'Jaguar', 'Mouse', 'Shark',
        'Owl', 'Badger', 'Heron', 'Moose'
    ];
    const PW_SYMBOLS = ['!', '@', '#', '$', '%', '&', '*', '('];

    function pick<T>(arr: T[]): T {
        return arr[Math.floor(Math.random() * arr.length)];
    }

    function generatePassword(): string {
        const num = Math.floor(Math.random() * 90) + 10;
        return `${pick(PW_ADJECTIVES)}${pick(PW_SYMBOLS)}${pick(PW_ANIMALS)}${num}`;
    }

    function openPwModal(user: User) {
        pwModalUser = user;
        pwInput = generatePassword();
        pwShow = false;
        pwSavedFor = null;
        pwError = '';
    }

    function closePwModal() {
        pwModalUser = null;
        pwInput = '';
        pwShow = false;
        pwSavedFor = null;
        pwError = '';
    }

    function regenerate() {
        pwInput = generatePassword();
    }

    async function commitPasswordReset() {
        if (!pwModalUser) return;
        pwError = '';
        if (pwInput.length < 8) {
            pwError = 'Password must be at least 8 characters.';
            return;
        }
        busy = true;
        try {
            const res = await fetch(`/api/users/${pwModalUser.id}`, {
                method: 'PATCH',
                headers: { 'content-type': 'application/json' },
                body: JSON.stringify({ password: pwInput })
            });
            if (!res.ok) {
                const j = await res.json().catch(() => ({}));
                pwError = j.error ?? `Failed (${res.status})`;
                return;
            }
            pwSavedFor = pwInput;
            pwInput = '';
        } finally {
            busy = false;
        }
    }

    async function copyToClipboard(value: string) {
        try {
            await navigator.clipboard.writeText(value);
        } catch {
            /* clipboard API blocked — user can select manually */
        }
    }

    function setPwInput(e: Event) {
        pwInput = (e.currentTarget as HTMLInputElement).value;
    }

    async function createUser() {
        formError = '';
        if (!newUsername.trim() || !newPassword) {
            formError = 'Username and password are required.';
            return;
        }
        busy = true;
        try {
            const res = await fetch('/api/users', {
                method: 'POST',
                headers: { 'content-type': 'application/json' },
                body: JSON.stringify({
                    username: newUsername.trim(),
                    displayName: newDisplay.trim() || undefined,
                    email: newEmail.trim() || undefined,
                    password: newPassword,
                    role: newAccess,
                    jobTitle: newJobTitle.trim() || undefined,
                    reportsTo: newReportsTo || undefined,
                    mfaEnabled: newMfaEnabled
                })
            });
            if (!res.ok) {
                const j = await res.json().catch(() => ({}));
                formError = j.error ?? `Create failed (${res.status})`;
                return;
            }
            newUsername = '';
            newDisplay = '';
            newEmail = '';
            newPassword = '';
            newAccess = 'admin';
            newJobTitle = '';
            newReportsTo = '';
            newMfaEnabled = false;
            await invalidateAll();
        } finally {
            busy = false;
        }
    }

    async function patchUser(
        user: User,
        body: Partial<{
            role: UserRole;
            jobTitle: string;
            reportsTo: string;
            email: string;
            mfaEnabled: boolean;
        }>
    ): Promise<boolean> {
        busy = true;
        try {
            const res = await fetch(`/api/users/${user.id}`, {
                method: 'PATCH',
                headers: { 'content-type': 'application/json' },
                body: JSON.stringify(body)
            });
            if (!res.ok) {
                const j = await res.json().catch(() => ({}));
                alert(j.error ?? `Update failed (${res.status})`);
                return false;
            }
            await invalidateAll();
            return true;
        } finally {
            busy = false;
        }
    }

    async function changeAccess(user: User, role: UserRole) {
        if (role === user.role) return;
        if (!confirm(`Change ${user.username}'s access to ${accessLabels[role]}?`)) return;
        await patchUser(user, { role });
    }

    function onAccessSelect(user: User, ev: Event) {
        const target = ev.currentTarget as HTMLSelectElement;
        changeAccess(user, target.value as UserRole);
    }

    async function onJobTitleBlur(user: User, ev: Event) {
        const target = ev.currentTarget as HTMLInputElement;
        const next = target.value.trim();
        if (next === (user.jobTitle ?? '')) return;
        const ok = await patchUser(user, { jobTitle: next });
        if (!ok) target.value = user.jobTitle ?? '';
    }

    async function onReportsToChange(user: User, ev: Event) {
        const target = ev.currentTarget as HTMLSelectElement;
        const next = target.value;
        if (next === (user.reportsTo ?? '')) return;
        const ok = await patchUser(user, { reportsTo: next });
        if (!ok) target.value = user.reportsTo ?? '';
    }

    async function onEmailBlur(user: User, ev: Event) {
        const target = ev.currentTarget as HTMLInputElement;
        const next = target.value.trim();
        if (next === (user.email ?? '')) return;
        const ok = await patchUser(user, { email: next });
        if (!ok) target.value = user.email ?? '';
    }

    async function onMfaToggle(user: User, ev: Event) {
        const target = ev.currentTarget as HTMLInputElement;
        const next = target.checked;
        if (next === user.mfaEnabled) return;
        const ok = await patchUser(user, { mfaEnabled: next });
        if (!ok) target.checked = user.mfaEnabled;
    }

    async function deleteUser(user: User) {
        const msg =
            `Remove ${user.username}? This blocks their access immediately.\n` +
            `Their audit trail (e.g. quote ownership) stays intact.`;
        if (!confirm(msg)) return;
        busy = true;
        try {
            const res = await fetch(`/api/users/${user.id}`, { method: 'DELETE' });
            if (!res.ok && res.status !== 204) {
                const j = await res.json().catch(() => ({}));
                alert(j.error ?? `Delete failed (${res.status})`);
                return;
            }
            await invalidateAll();
        } finally {
            busy = false;
        }
    }
</script>

<div class="px-8 py-8 mx-auto max-w-[1580px]">
    <div class="mb-8">
        <p class="eyebrow mb-1">Settings</p>
        <h1 class="font-h2 text-h2 text-on-surface font-semibold">Users.</h1>
        <p class="font-body-md text-sm text-secondary mt-2 max-w-2xl">
            Manage portal access. <strong>Access</strong> controls permissions
            (Superadmin can delete; Admin cannot). <strong>Role</strong> is a free-text
            job title. <strong>Reports&nbsp;to</strong> records the manager.
            <strong>Email</strong> is used for password reset and the 2FA email-code
            challenge (when 2FA is on for that user).
        </p>
    </div>

    {#if data.error}
        <div class="border-l-4 border-error bg-surface-container-low px-5 py-4 mb-6 flex gap-3 items-start">
            <span class="material-symbols-outlined text-error">error</span>
            <p class="font-body-md text-sm text-on-surface">{data.error}</p>
        </div>
    {/if}

    <!-- New user form -->
    <section class="card mb-8">
        <div class="px-6 py-4 border-b border-zinc-100">
            <p class="eyebrow">New user</p>
        </div>
        <form
            on:submit|preventDefault={createUser}
            class="px-6 py-5 grid grid-cols-1 md:grid-cols-4 gap-4 items-end"
        >
            <div class="flex flex-col gap-1">
                <label for="nu-username" class="field-label">Username</label>
                <input
                    id="nu-username"
                    bind:value={newUsername}
                    placeholder="email or short handle"
                    class="field"
                    autocomplete="off"
                    required
                />
            </div>
            <div class="flex flex-col gap-1">
                <label for="nu-display" class="field-label">Display name</label>
                <input
                    id="nu-display"
                    bind:value={newDisplay}
                    placeholder="Shown in UI (optional)"
                    class="field"
                    autocomplete="off"
                />
            </div>
            <div class="flex flex-col gap-1">
                <label for="nu-email" class="field-label">Email</label>
                <input
                    id="nu-email"
                    type="email"
                    bind:value={newEmail}
                    placeholder="for password reset + MFA"
                    class="field"
                    autocomplete="off"
                />
            </div>
            <div class="flex flex-col gap-1">
                <label for="nu-password" class="field-label">Password</label>
                <input
                    id="nu-password"
                    type="password"
                    bind:value={newPassword}
                    class="field"
                    autocomplete="new-password"
                    required
                />
            </div>

            <div class="flex flex-col gap-1">
                <label for="nu-access" class="field-label">Access</label>
                <select id="nu-access" bind:value={newAccess} class="field">
                    <option value="admin">Admin</option>
                    <option value="superadmin">Superadmin</option>
                </select>
            </div>
            <div class="flex flex-col gap-1">
                <label for="nu-jobtitle" class="field-label">Role</label>
                <input
                    id="nu-jobtitle"
                    bind:value={newJobTitle}
                    placeholder="e.g. Director of Sales"
                    class="field"
                    autocomplete="off"
                />
            </div>
            <div class="flex flex-col gap-1">
                <label for="nu-reports" class="field-label">Reports to</label>
                <select id="nu-reports" bind:value={newReportsTo} class="field">
                    <option value="">—</option>
                    {#each reportsToOptions as opt}
                        <option value={opt}>{opt}</option>
                    {/each}
                </select>
            </div>
            <div class="flex flex-col gap-1">
                <span class="field-label">2FA</span>
                <label class="inline-flex items-center gap-2 h-[42px] px-3 border border-zinc-300 rounded-md cursor-pointer">
                    <input
                        type="checkbox"
                        bind:checked={newMfaEnabled}
                        class="h-4 w-4"
                        disabled={!newEmail.trim()}
                    />
                    <span class="font-body-md text-sm text-on-surface">
                        Email code on login
                    </span>
                </label>
            </div>

            <div class="md:col-span-4 flex justify-end">
                <button type="submit" class="btn-primary px-8" disabled={busy}>
                    {busy ? 'Working…' : '+ Add user'}
                </button>
            </div>

            {#if formError}
                <div class="md:col-span-4 -mt-2">
                    <p class="font-body-md text-sm text-error">{formError}</p>
                </div>
            {/if}
        </form>
    </section>

    <!-- Users table -->
    <section class="card overflow-hidden">
        <div class="flex items-center justify-between px-6 py-4 border-b border-zinc-100">
            <p class="eyebrow">{data.users.length} active user{data.users.length === 1 ? '' : 's'}</p>
        </div>
        <div class="overflow-x-auto">
            <table class="nrv-table">
                <thead>
                    <tr>
                        <th class="w-12">ID</th>
                        <th>Username</th>
                        <th>Display name</th>
                        <th>Email</th>
                        <th>Access</th>
                        <th>Role</th>
                        <th>Reports to</th>
                        <th class="text-center">2FA</th>
                        <th>Password</th>
                        <th>Created</th>
                        <th class="text-right">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {#each data.users as u (u.id)}
                        {@const isSelf = me?.id === u.id}
                        <tr>
                            <td class="tabular-nums text-secondary">{u.id}</td>
                            <td class="font-medium">
                                {u.username}
                                {#if isSelf}
                                    <span class="ml-2 text-xs text-secondary">(you)</span>
                                {/if}
                            </td>
                            <td>{u.displayName ?? '—'}</td>
                            <td>
                                <input
                                    type="email"
                                    class="field !py-1 !text-xs w-full min-w-[200px]"
                                    value={u.email ?? ''}
                                    placeholder="—"
                                    on:blur={(e) => onEmailBlur(u, e)}
                                    disabled={busy}
                                />
                            </td>
                            <td>
                                <select
                                    class="field !py-1 !text-xs"
                                    value={u.role}
                                    on:change={(e) => onAccessSelect(u, e)}
                                    disabled={busy || isSelf}
                                    title={isSelf ? "You can't change your own access" : ''}
                                >
                                    <option value="admin">Admin</option>
                                    <option value="superadmin">Superadmin</option>
                                </select>
                            </td>
                            <td>
                                <input
                                    class="field !py-1 !text-xs w-full min-w-[140px]"
                                    type="text"
                                    value={u.jobTitle ?? ''}
                                    placeholder="—"
                                    on:blur={(e) => onJobTitleBlur(u, e)}
                                    disabled={busy}
                                />
                            </td>
                            <td>
                                <select
                                    class="field !py-1 !text-xs"
                                    value={u.reportsTo ?? ''}
                                    on:change={(e) => onReportsToChange(u, e)}
                                    disabled={busy}
                                >
                                    <option value="">—</option>
                                    {#each reportsToOptions as opt}
                                        <option value={opt}>{opt}</option>
                                    {/each}
                                </select>
                            </td>
                            <td class="text-center">
                                <input
                                    type="checkbox"
                                    class="h-4 w-4"
                                    checked={u.mfaEnabled}
                                    on:change={(e) => onMfaToggle(u, e)}
                                    disabled={busy || !u.email}
                                    title={!u.email ? 'Set an email first' : 'Email code on login'}
                                />
                            </td>
                            <td>
                                <span
                                    class="font-mono text-secondary tracking-widest select-none"
                                    title="Passwords are hashed and cannot be revealed. Use Change password to set a new one."
                                >
                                    ••••••••
                                </span>
                            </td>
                            <td class="text-secondary text-xs">
                                {u.createdAt ? new Date(u.createdAt).toLocaleDateString() : '—'}
                            </td>
                            <td class="text-right whitespace-nowrap">
                                <button
                                    on:click={() => openPwModal(u)}
                                    class="btn-outline !py-1 !px-3 !text-xs mr-1"
                                    disabled={busy}
                                    title="Reset this user's password"
                                >
                                    Change password
                                </button>
                                <button
                                    on:click={() => deleteUser(u)}
                                    class="btn-danger !py-1 !px-3 !text-xs"
                                    disabled={busy || isSelf}
                                    title={isSelf ? "You can't remove your own account" : ''}
                                >
                                    Remove
                                </button>
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>
    </section>
</div>

<!-- ── Change-password modal ───────────────────────────────────────────── -->
{#if pwModalUser}
    <div class="fixed inset-0 z-50 bg-zinc-900/40 flex items-center justify-center p-4">
        <div class="bg-white rounded-card shadow-2xl max-w-md w-full">
            <div class="px-6 py-4 border-b border-zinc-200 flex items-center justify-between">
                <div>
                    <p class="eyebrow">{pwSavedFor ? 'Done' : 'Reset password'}</p>
                    <p class="font-h3 text-base text-on-surface font-semibold mt-0.5">
                        {pwModalUser.username}
                    </p>
                </div>
                <button
                    type="button"
                    on:click={closePwModal}
                    aria-label="Close"
                    class="inline-flex items-center justify-center h-9 w-9 rounded-full text-on-surface hover:bg-surface-container-high"
                >
                    <span class="material-symbols-outlined" style="font-size: 22px">close</span>
                </button>
            </div>

            {#if pwSavedFor}
                <!-- ── Success state: show password once, then it's gone ─── -->
                <div class="px-6 py-5">
                    <p class="font-body-md text-sm text-on-surface mb-3">
                        Password set. Copy it now and share it with the user via a
                        secure channel — once you close this window, it can't be
                        revealed again.
                    </p>
                    <div class="flex gap-2 items-stretch">
                        <code
                            class="flex-1 font-mono text-base bg-surface-container-low border border-zinc-300 rounded-md px-3 py-2 text-on-surface select-all break-all"
                        >
                            {pwSavedFor}
                        </code>
                        <button
                            type="button"
                            on:click={() => copyToClipboard(pwSavedFor ?? '')}
                            class="btn-primary px-4 text-sm"
                            title="Copy to clipboard"
                        >
                            Copy
                        </button>
                    </div>
                </div>
                <div class="px-6 py-4 border-t border-zinc-100 flex justify-end gap-3">
                    <button type="button" on:click={closePwModal} class="btn-primary px-6">
                        Close
                    </button>
                </div>
            {:else}
                <!-- ── Edit state: generate or override, then Reset ─────── -->
                <div class="px-6 py-5">
                    <p class="font-body-md text-sm text-secondary mb-4">
                        Generate a memorable animal-style password, or type your own
                        override. The user can change it later from their account
                        page.
                    </p>

                    <label class="field-label" for="pw-input">New password</label>
                    <div class="relative mt-1">
                        <input
                            id="pw-input"
                            type={pwShow ? 'text' : 'password'}
                            value={pwInput}
                            on:input={setPwInput}
                            class="field !pr-20 w-full font-mono"
                            autocomplete="new-password"
                            spellcheck="false"
                        />
                        <div class="absolute inset-y-0 right-0 flex items-center">
                            <button
                                type="button"
                                on:click={() => (pwShow = !pwShow)}
                                aria-label={pwShow ? 'Hide password' : 'Show password'}
                                title={pwShow ? 'Hide password' : 'Show password'}
                                class="px-2 flex items-center text-secondary hover:text-on-surface"
                            >
                                <span class="material-symbols-outlined" style="font-size: 20px">
                                    {pwShow ? 'visibility_off' : 'visibility'}
                                </span>
                            </button>
                            <button
                                type="button"
                                on:click={regenerate}
                                aria-label="Regenerate"
                                title="Generate a new password"
                                class="px-2 flex items-center text-secondary hover:text-on-surface"
                            >
                                <span class="material-symbols-outlined" style="font-size: 20px">
                                    refresh
                                </span>
                            </button>
                        </div>
                    </div>
                    <p class="font-label-sm text-xs text-secondary mt-1">
                        At least 8 characters.
                    </p>

                    {#if pwError}
                        <div class="mt-3 border-l-4 border-error bg-rose-50 px-3 py-2 flex items-start gap-2">
                            <span class="material-symbols-outlined text-error" style="font-size: 18px">
                                error
                            </span>
                            <p class="font-body-md text-sm text-on-surface">{pwError}</p>
                        </div>
                    {/if}
                </div>
                <div class="px-6 py-4 border-t border-zinc-100 flex justify-end gap-3">
                    <button type="button" on:click={closePwModal} class="btn-outline px-5">
                        Cancel
                    </button>
                    <button
                        type="button"
                        on:click={commitPasswordReset}
                        class="btn-primary px-6"
                        disabled={busy || pwInput.length < 8}
                    >
                        {busy ? 'Working…' : 'Reset'}
                    </button>
                </div>
            {/if}
        </div>
    </div>
{/if}
