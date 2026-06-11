<script lang="ts">
    import { enhance } from '$app/forms';
    import type { ActionData, PageData } from './$types';

    export let data: PageData;
    export let form: ActionData;

    let submitting = false;
    let q = '';
    $: filtered = q
        ? data.customers.filter(
              (c) =>
                  c.number.toLowerCase().includes(q.toLowerCase()) ||
                  (c.displayName || '').toLowerCase().includes(q.toLowerCase())
          )
        : data.customers.slice(0, 50);
</script>

<div class="px-8 py-8 max-w-[760px]">
    <div class="mb-8 flex items-end justify-between gap-6 flex-wrap">
        <div>
            <p class="eyebrow mb-1"><a href="/quotes" class="hover:text-primary-container">Quotes</a> · New</p>
            <h1 class="font-h2 text-h2 text-on-surface font-semibold">New Quote.</h1>
            <p class="font-body-md text-sm text-secondary mt-2">
                Pick a customer and an optional document date. BC assigns the quote number; you'll
                add lines on the next screen.
            </p>
        </div>
        <a href="/quotes" class="btn-outline">← Cancel</a>
    </div>

    {#if form?.error}
        <div class="border-l-4 border-error bg-surface-container-low px-5 py-4 mb-6 flex gap-3 items-start">
            <span class="material-symbols-outlined text-error">error</span>
            <p class="font-body-md text-sm text-on-surface">{form.error}</p>
        </div>
    {/if}

    <form
        method="POST"
        action="?/create"
        use:enhance={() => {
            submitting = true;
            return async ({ update }) => {
                await update();
                submitting = false;
            };
        }}
        class="card p-6 space-y-5"
    >
        <div class="flex flex-col gap-1">
            <label for="cust-search" class="field-label">Customer search</label>
            <input
                id="cust-search"
                type="text"
                bind:value={q}
                placeholder="Customer #, name…"
                class="field"
            />
        </div>

        <div class="flex flex-col gap-1">
            <label for="customerId" class="field-label">Customer <span class="text-primary-container">*</span></label>
            <select id="customerId" name="customerId" class="field" required size={Math.min(10, Math.max(5, filtered.length))}>
                {#each filtered as c}
                    <option value={c.id}>#{c.number} — {c.displayName}{#if c.city} · {c.city}{/if}</option>
                {/each}
            </select>
        </div>

        <div class="flex flex-col gap-1">
            <label for="documentDate" class="field-label">Document date</label>
            <input id="documentDate" name="documentDate" type="date" class="field" />
        </div>

        <div class="flex items-center justify-end gap-3 pt-2">
            <a href="/quotes" class="btn-outline">Cancel</a>
            <button type="submit" class="btn-primary" disabled={submitting}>
                {submitting ? 'Creating in BC…' : 'Create Draft & Add Lines →'}
            </button>
        </div>
    </form>
</div>
