<script lang="ts">
    import { enhance } from '$app/forms';
    import type { ActionData, PageData } from './$types';

    export let data: PageData;
    export let form: ActionData;

    let saving = false;
    $: c = data.customer;
    $: systemId = c?.systemId || c?.id || '';
</script>

<div class="px-8 py-8 mx-auto max-w-[920px]">
    <div class="mb-8 flex items-end justify-between gap-6 flex-wrap">
        <div>
            <p class="eyebrow mb-1">
                <a href="/customers" class="hover:text-primary-container">Customers</a> · Edit
            </p>
            <h1 class="font-h2 text-h2 text-on-surface font-semibold">
                {data.number}.
            </h1>
            {#if c}
                <p class="font-body-md text-sm text-secondary mt-2">
                    {c.displayName} ·
                    {#if c.customerPriceGroup}
                        <span class="badge-pending">{c.customerPriceGroup}</span>
                    {/if}
                    {#if c.currencyCode}
                        <span class="ml-2 muted">{c.currencyCode}</span>
                    {/if}
                </p>
            {/if}
        </div>
        <a href="/customers" class="btn-outline">← Cancel</a>
    </div>

    {#if data.error}
        <div class="border-l-4 border-error bg-surface-container-low px-5 py-4 mb-6 flex gap-3 items-start">
            <span class="material-symbols-outlined text-error">error</span>
            <p class="font-body-md text-sm text-on-surface">{data.error}</p>
        </div>
    {/if}

    {#if form?.error}
        <div class="border-l-4 border-error bg-surface-container-low px-5 py-4 mb-6 flex gap-3 items-start">
            <span class="material-symbols-outlined text-error">error</span>
            <p class="font-body-md text-sm text-on-surface">{form.error}</p>
        </div>
    {/if}

    {#if form?.success}
        <div class="border-l-4 border-emerald-500 bg-surface-container-low px-5 py-4 mb-6 flex gap-3 items-start">
            <span class="material-symbols-outlined text-emerald-600">check_circle</span>
            <p class="font-body-md text-sm text-on-surface">Saved to Business Central.</p>
        </div>
    {/if}

    {#if !c}
        <div class="card p-12 text-center text-secondary font-body-md text-sm">
            Customer not found.
        </div>
    {:else}
        <form
            method="POST"
            action="?/save"
            use:enhance={() => {
                saving = true;
                return async ({ update }) => {
                    await update();
                    saving = false;
                };
            }}
            class="space-y-6"
        >
            <input type="hidden" name="systemId" value={systemId} />

            <!-- Identity -->
            <section class="card p-6">
                <div class="section-heading mb-5">
                    <p class="font-h3 text-base font-semibold text-on-surface">1 · Identity</p>
                    <p class="font-body-md text-secondary text-sm">Customer-facing name and primary contact.</p>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="flex flex-col gap-1 md:col-span-2">
                        <label for="displayName" class="field-label">Name <span class="text-primary-container">*</span></label>
                        <input
                            id="displayName"
                            name="displayName"
                            type="text"
                            required
                            value={c.displayName ?? ''}
                            class="field"
                        />
                    </div>
                    <div class="flex flex-col gap-1">
                        <label for="contactName" class="field-label">Contact name</label>
                        <input id="contactName" name="contactName" type="text" value={c.contactName ?? ''} class="field" />
                    </div>
                    <div class="flex flex-col gap-1">
                        <label for="phoneNumber" class="field-label">Phone</label>
                        <input id="phoneNumber" name="phoneNumber" type="tel" value={c.phoneNumber ?? ''} class="field" />
                    </div>
                    <div class="flex flex-col gap-1 md:col-span-2">
                        <label for="email" class="field-label">Email</label>
                        <input id="email" name="email" type="email" value={c.email ?? ''} class="field" />
                    </div>
                </div>
            </section>

            <!-- Address -->
            <section class="card p-6">
                <div class="section-heading mb-5">
                    <p class="font-h3 text-base font-semibold text-on-surface">2 · Address</p>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="flex flex-col gap-1 md:col-span-2">
                        <label for="addressLine1" class="field-label">Address line 1</label>
                        <input id="addressLine1" name="addressLine1" type="text" value={c.addressLine1 ?? ''} class="field" />
                    </div>
                    <div class="flex flex-col gap-1 md:col-span-2">
                        <label for="addressLine2" class="field-label">Address line 2</label>
                        <input id="addressLine2" name="addressLine2" type="text" value={c.addressLine2 ?? ''} class="field" />
                    </div>
                    <div class="flex flex-col gap-1">
                        <label for="city" class="field-label">City</label>
                        <input id="city" name="city" type="text" value={c.city ?? ''} class="field" />
                    </div>
                    <div class="flex flex-col gap-1">
                        <label for="state" class="field-label">Province / State</label>
                        <input id="state" name="state" type="text" value={c.state ?? ''} class="field" />
                    </div>
                    <div class="flex flex-col gap-1">
                        <label for="postalCode" class="field-label">Postal code</label>
                        <input id="postalCode" name="postalCode" type="text" value={c.postalCode ?? ''} class="field" />
                    </div>
                    <div class="flex flex-col gap-1">
                        <label for="countryRegionCode" class="field-label">Country code</label>
                        <input
                            id="countryRegionCode"
                            name="countryRegionCode"
                            type="text"
                            placeholder="CA"
                            maxlength="10"
                            value={c.countryRegionCode ?? ''}
                            class="field"
                        />
                    </div>
                </div>
            </section>

            <!-- Dimensions -->
            <section class="card p-6">
                <div class="section-heading mb-5">
                    <p class="font-h3 text-base font-semibold text-on-surface">3 · Dimensions</p>
                    <p class="font-body-md text-secondary text-sm">
                        Cust Category (Global Dim 1) and Business Type (Global Dim 2).
                    </p>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="flex flex-col gap-1">
                        <label for="custCategory" class="field-label">Cust Category</label>
                        <select id="custCategory" name="custCategory" class="field" value={c.custCategory ?? ''}>
                            <option value="">— Not assigned —</option>
                            {#each data.custCategoryValues as v}
                                <option value={v.code}>{v.code}{#if v.name && v.name !== v.code} — {v.name}{/if}</option>
                            {/each}
                        </select>
                    </div>
                    <div class="flex flex-col gap-1">
                        <label for="businessType" class="field-label">Business Type</label>
                        <select id="businessType" name="businessType" class="field" value={c.businessType ?? ''}>
                            <option value="">— Not assigned —</option>
                            {#each data.businessTypeValues as v}
                                <option value={v.code}>{v.code}{#if v.name && v.name !== v.code} — {v.name}{/if}</option>
                            {/each}
                        </select>
                    </div>
                </div>
            </section>

            <div class="flex items-center justify-end gap-3">
                <a href="/customers" class="btn-outline">Cancel</a>
                <button type="submit" class="btn-primary" disabled={saving || !systemId}>
                    {saving ? 'Saving…' : 'Save changes'}
                </button>
            </div>
        </form>
    {/if}
</div>
