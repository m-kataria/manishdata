<script lang="ts">
    import { invalidateAll } from '$app/navigation';
    import { page } from '$app/stores';
    import type { User, UserRole } from '$lib/types';
    import type { PageData } from './$types';

    export let data: PageData;

    $: me = $page.data.user as User | null;

    const roleLabels: Record<UserRole, string> = {
        superadmin: 'Superadmin',
        admin: 'Admin'
    };

    let busy = false;
    let formError = '';
    let newUsername = '';
    let newDisplay = '';
    let newPassword = '';
    let newRole: UserRole = 'admin';

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
                    password: newPassword,
                    role: newRole
                })
            });
            if (!res.ok) {
                const j = await res.json().catch(() => ({}));
                formError = j.error ?? `Create failed (${res.status})`;
                return;
            }
            newUsername = '';
            newDisplay = '';
            newPassword = '';
            newRole = 'admin';
            await invalidateAll();
        } finally {
            busy = false;
        }
    }

    async function patchUser(user: User, body: Partial<{ role: UserRole; isActive: boolean }>) {
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
                return;
            }
            await invalidateAll();
        } finally {
            busy = false;
        }
    }

    async function changeRole(user: User, role: UserRole) {
        if (role === user.role) return;
        if (!confirm(`Change ${user.username}'s role to ${roleLabels[role]}?`)) return;
        await patchUser(user, { role });
    }

    function onRoleSelect(user: User, ev: Event) {
        const target = ev.currentTarget as HTMLSelectElement;
        changeRole(user, target.value as UserRole);
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

<div class="px-8 py-8 mx-auto max-w-[1180px]">
    <div class="mb-8">
        <p class="eyebrow mb-1">Settings</p>
        <h1 class="font-h2 text-h2 text-on-surface font-semibold">Users.</h1>
        <p class="font-body-md text-sm text-secondary mt-2 max-w-2xl">
            Manage portal access. Superadmins can do everything including delete records.
            Admins can do everything except delete.
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
        <form on:submit|preventDefault={createUser} class="px-6 py-5 grid grid-cols-1 md:grid-cols-5 gap-4 items-end">
            <div class="flex flex-col gap-1 md:col-span-1">
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
            <div class="flex flex-col gap-1 md:col-span-1">
                <label for="nu-display" class="field-label">Display name</label>
                <input
                    id="nu-display"
                    bind:value={newDisplay}
                    placeholder="Shown in UI (optional)"
                    class="field"
                    autocomplete="off"
                />
            </div>
            <div class="flex flex-col gap-1 md:col-span-1">
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
            <div class="flex flex-col gap-1 md:col-span-1">
                <label for="nu-role" class="field-label">Role</label>
                <select id="nu-role" bind:value={newRole} class="field">
                    <option value="admin">Admin</option>
                    <option value="superadmin">Superadmin</option>
                </select>
            </div>
            <div class="md:col-span-1 flex">
                <button type="submit" class="btn-primary w-full" disabled={busy}>
                    {busy ? 'Working…' : '+ Add user'}
                </button>
            </div>
            {#if formError}
                <div class="md:col-span-5 -mt-2">
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
                        <th>Role</th>
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
                                <select
                                    class="field !py-1 !text-xs"
                                    value={u.role}
                                    on:change={(e) => onRoleSelect(u, e)}
                                    disabled={busy || isSelf}
                                    title={isSelf ? "You can't change your own role" : ''}
                                >
                                    <option value="admin">Admin</option>
                                    <option value="superadmin">Superadmin</option>
                                </select>
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
