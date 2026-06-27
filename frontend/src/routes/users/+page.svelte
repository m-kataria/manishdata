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
                            <td class="text-secondary text-xs">
                                {u.createdAt ? new Date(u.createdAt).toLocaleDateString() : '—'}
                            </td>
                            <td class="text-right">
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
