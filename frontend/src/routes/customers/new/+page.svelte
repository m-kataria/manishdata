<script lang="ts">
    import { enhance } from '$app/forms';
    import type { ActionData, PageData } from './$types';

    export let data: PageData;
    export let form: ActionData;

    let submitting = false;
    let selectedTemplateId = '';

    $: selectedTemplate = data.templates.find((t) => t.systemId === selectedTemplateId);
</script>

<div class="px-8 py-8 mx-auto max-w-[920px]">
    <div class="mb-8 flex items-end justify-between gap-6 flex-wrap">
        <div>
            <p class="eyebrow mb-1">
                <a href="/customers" class="hover:text-primary-container">Customers</a> · New
            </p>
            <h1 class="font-h2 text-h2 text-on-surface font-semibold">Create Customer.</h1>
            <p class="font-body-md text-sm text-secondary mt-2 max-w-xl">
                Pick a BC template — posting groups, payment terms, customer price group, and
                currency auto-fill. You only need to enter name, address, and contact info.
            </p>
        </div>
        <a href="/customers" class="btn-outline">← Cancel</a>
    </div>

    {#if data.templatesError}
        <div class="border-l-4 border-error bg-surface-container-low px-5 py-4 mb-6 flex gap-3 items-start">
            <span class="material-symbols-outlined text-error">error</span>
            <p class="font-body-md text-sm text-on-surface">
                Couldn't load templates: {data.templatesError}
            </p>
        </div>
    {/if}

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
        class="space-y-6"
    >
        <!-- Template -->
        <section class="card p-6">
            <div class="section-heading mb-5">
                <p class="font-h3 text-base font-semibold text-on-surface">1 · Template</p>
                <p class="font-body-md text-secondary text-sm">Choose the customer type — BC fills the back-office fields.</p>
            </div>

            <div class="flex flex-col gap-1">
                <label for="templateSystemId" class="field-label">Customer Template</label>
                <select
                    id="templateSystemId"
                    name="templateSystemId"
                    class="field"
                    bind:value={selectedTemplateId}
                    required
                >
                    <option value="">— Pick a template —</option>
                    {#each data.templates as t}
                        <option value={t.systemId}>{t.code} · {t.description}</option>
                    {/each}
                </select>
            </div>

            {#if selectedTemplate}
                <dl class="grid grid-cols-2 md:grid-cols-3 gap-3 mt-5 font-mono-data text-xs">
                    {#if selectedTemplate.customerPriceGroup}
                        <div class="bg-surface-container-low p-3">
                            <dt class="text-secondary uppercase tracking-[0.15em] text-[0.65rem]">Price Group</dt>
                            <dd class="text-on-surface mt-1">{selectedTemplate.customerPriceGroup}</dd>
                        </div>
                    {/if}
                    {#if selectedTemplate.customerPostingGroup}
                        <div class="bg-surface-container-low p-3">
                            <dt class="text-secondary uppercase tracking-[0.15em] text-[0.65rem]">Posting Group</dt>
                            <dd class="text-on-surface mt-1">{selectedTemplate.customerPostingGroup}</dd>
                        </div>
                    {/if}
                    {#if selectedTemplate.genBusPostingGroup}
                        <div class="bg-surface-container-low p-3">
                            <dt class="text-secondary uppercase tracking-[0.15em] text-[0.65rem]">Gen Bus Group</dt>
                            <dd class="text-on-surface mt-1">{selectedTemplate.genBusPostingGroup}</dd>
                        </div>
                    {/if}
                    {#if selectedTemplate.paymentTermsCode}
                        <div class="bg-surface-container-low p-3">
                            <dt class="text-secondary uppercase tracking-[0.15em] text-[0.65rem]">Payment Terms</dt>
                            <dd class="text-on-surface mt-1">{selectedTemplate.paymentTermsCode}</dd>
                        </div>
                    {/if}
                    {#if selectedTemplate.currencyCode}
                        <div class="bg-surface-container-low p-3">
                            <dt class="text-secondary uppercase tracking-[0.15em] text-[0.65rem]">Currency</dt>
                            <dd class="text-on-surface mt-1">{selectedTemplate.currencyCode}</dd>
                        </div>
                    {/if}
                    {#if selectedTemplate.salespersonCode}
                        <div class="bg-surface-container-low p-3">
                            <dt class="text-secondary uppercase tracking-[0.15em] text-[0.65rem]">Salesperson</dt>
                            <dd class="text-on-surface mt-1">{selectedTemplate.salespersonCode}</dd>
                        </div>
                    {/if}
                </dl>
            {/if}
        </section>

        <!-- Customer info -->
        <section class="card p-6">
            <div class="section-heading mb-5">
                <p class="font-h3 text-base font-semibold text-on-surface">2 · Customer info</p>
                <p class="font-body-md text-secondary text-sm">Only Name is required.</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="flex flex-col gap-1 md:col-span-2">
                    <label for="name" class="field-label">Name <span class="text-primary-container">*</span></label>
                    <input id="name" name="name" type="text" required value={form?.form?.name ?? ''} class="field" />
                </div>
                <div class="flex flex-col gap-1">
                    <label for="contactName" class="field-label">Contact name</label>
                    <input id="contactName" name="contactName" type="text" value={form?.form?.contactName ?? ''} class="field" />
                </div>
                <div class="flex flex-col gap-1">
                    <label for="phoneNo" class="field-label">Phone</label>
                    <input id="phoneNo" name="phoneNo" type="tel" value={form?.form?.phoneNo ?? ''} class="field" />
                </div>
                <div class="flex flex-col gap-1 md:col-span-2">
                    <label for="email" class="field-label">Email</label>
                    <input id="email" name="email" type="email" value={form?.form?.email ?? ''} class="field" />
                </div>
                <div class="flex flex-col gap-1 md:col-span-2">
                    <label for="addressLine1" class="field-label">Address line 1</label>
                    <input id="addressLine1" name="addressLine1" type="text" value={form?.form?.addressLine1 ?? ''} class="field" />
                </div>
                <div class="flex flex-col gap-1 md:col-span-2">
                    <label for="addressLine2" class="field-label">Address line 2</label>
                    <input id="addressLine2" name="addressLine2" type="text" value={form?.form?.addressLine2 ?? ''} class="field" />
                </div>
                <div class="flex flex-col gap-1">
                    <label for="city" class="field-label">City</label>
                    <input id="city" name="city" type="text" value={form?.form?.city ?? ''} class="field" />
                </div>
                <div class="flex flex-col gap-1">
                    <label for="county" class="field-label">Province / State</label>
                    <input id="county" name="county" type="text" value={form?.form?.county ?? ''} class="field" />
                </div>
                <div class="flex flex-col gap-1">
                    <label for="postCode" class="field-label">Postal code</label>
                    <input id="postCode" name="postCode" type="text" value={form?.form?.postCode ?? ''} class="field" />
                </div>
                <div class="flex flex-col gap-1">
                    <label for="countryRegionCode" class="field-label">Country code</label>
                    <input id="countryRegionCode" name="countryRegionCode" type="text" placeholder="CA" maxlength="10" value={form?.form?.countryRegionCode ?? ''} class="field" />
                </div>
                <div class="flex flex-col gap-1">
                    <label for="taxAreaCode" class="field-label">Tax Area Code</label>
                    <input id="taxAreaCode" name="taxAreaCode" type="text" placeholder="AB" maxlength="20" value={form?.form?.taxAreaCode ?? ''} class="field" />
                </div>
                <div class="flex flex-col gap-1">
                    <label for="paymentTermsCode" class="field-label">Payment Terms</label>
                    <select id="paymentTermsCode" name="paymentTermsCode" class="field" value={form?.form?.paymentTermsCode ?? ''}>
                        <option value="">— Keep template default —</option>
                        {#each data.paymentTerms as p}
                            <option value={p.code}>{p.code}{#if p.displayName && p.displayName !== p.code} — {p.displayName}{/if}</option>
                        {/each}
                    </select>
                </div>
                <div class="flex flex-col gap-1">
                    <label for="locationCode" class="field-label">Location</label>
                    <select id="locationCode" name="locationCode" class="field" value={form?.form?.locationCode ?? ''}>
                        <option value="">— Keep template default —</option>
                        {#each data.locations as l}
                            <option value={l.code}>{l.code}{#if l.displayName && l.displayName !== l.code} — {l.displayName}{/if}</option>
                        {/each}
                    </select>
                </div>
                <div class="flex items-center gap-2 md:col-span-2 pt-2">
                    <input id="taxLiable" name="taxLiable" type="checkbox" class="h-4 w-4" checked={form?.form?.taxLiable ?? true} />
                    <label for="taxLiable" class="field-label !mb-0">Tax Liable</label>
                </div>
            </div>
        </section>

        <!-- Dimensions -->
        <section class="card p-6">
            <div class="section-heading mb-5">
                <p class="font-h3 text-base font-semibold text-on-surface">3 · Dimensions</p>
                <p class="font-body-md text-secondary text-sm">
                    Tag the customer for reporting — Global Dim 1 (Cust Category) and Global Dim 2 (Business Type) in BC.
                </p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="flex flex-col gap-1">
                    <label for="custCategory" class="field-label">Cust Category</label>
                    <select
                        id="custCategory"
                        name="custCategory"
                        class="field"
                        value={form?.form?.custCategory ?? ''}
                    >
                        <option value="">— Not assigned —</option>
                        {#each data.custCategoryValues as v}
                            <option value={v.code}
                                >{v.code}{#if v.name && v.name !== v.code} — {v.name}{/if}</option
                            >
                        {/each}
                    </select>
                </div>
                <div class="flex flex-col gap-1">
                    <label for="businessType" class="field-label">Business Type</label>
                    <select
                        id="businessType"
                        name="businessType"
                        class="field"
                        value={form?.form?.businessType ?? ''}
                    >
                        <option value="">— Not assigned —</option>
                        {#each data.businessTypeValues as v}
                            <option value={v.code}
                                >{v.code}{#if v.name && v.name !== v.code} — {v.name}{/if}</option
                            >
                        {/each}
                    </select>
                </div>
            </div>
        </section>

        <div class="flex items-center justify-end gap-3">
            <a href="/customers" class="btn-outline">Cancel</a>
            <button type="submit" class="btn-primary" disabled={submitting}>
                {submitting ? 'Creating in BC…' : 'Create Customer'}
            </button>
        </div>
    </form>
</div>
