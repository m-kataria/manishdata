<script lang="ts">
    /** Brand-styled progress bar. Two modes:
     *  - Determinate: pass `pct` (0-100). Bar fills accordingly.
     *  - Indeterminate: omit `pct` (or pass null). Bar animates left-to-right. */
    export let label: string = 'Loading…';
    export let pct: number | null = null;
    /** Optional Tailwind padding class for the wrapper (default py-12). */
    export let padding: string = 'py-12';
</script>

<div class="text-center {padding}">
    <p class="font-body-md text-sm text-secondary mb-4">{label}</p>
    <div class="mx-auto max-w-md">
        <div class="h-2 rounded-full bg-zinc-100 overflow-hidden relative">
            {#if pct !== null}
                <div
                    class="h-full bg-gradient-to-r from-primary-container to-primary transition-all duration-500 ease-out relative"
                    style={`width: ${Math.max(0, Math.min(100, pct))}%`}
                >
                    <span class="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse"></span>
                </div>
            {:else}
                <!-- Indeterminate: 40% bar slides across -->
                <div class="h-full w-2/5 bg-gradient-to-r from-primary-container to-primary nrv-indeterminate"></div>
            {/if}
        </div>
        {#if pct !== null}
            <p class="mt-2 font-mono-data text-[0.65rem] uppercase tracking-[0.2em] text-secondary tabular-nums">
                {Math.round(pct)}%
            </p>
        {/if}
    </div>
</div>

