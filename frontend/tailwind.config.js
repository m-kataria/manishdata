/**
 * Tailwind v3 brand tokens for the ICC App (Nerval Ops) — see
 * C:\Users\manish\Downloads\ICC theme\icc-style-guide.md.
 * Navy is the primary brand color (used for text + dark accents); teal is the
 * accent color (CTAs, links, badges). Backgrounds are off-white.
 * Class names like `bg-primary-container` / `text-on-surface` stay the same —
 * only the values behind them changed.
 */

/** @type {import('tailwindcss').Config} */
export default {
    darkMode: 'class',
    content: ['./src/**/*.{html,js,svelte,ts}'],
    theme: {
        // ICC: default 4px radius everywhere; buttons stay pill (full).
        borderRadius: {
            none: '0',
            DEFAULT: '4px',
            sm: '4px',
            md: '4px',
            lg: '4px',
            xl: '4px',
            '2xl': '8px',
            '3xl': '12px',
            full: '9999px',
            card: '4px'
        },
        extend: {
            colors: {
                // ── Primary = ICC Teal (accent / CTAs / highlights) ─────────
                // Kept as `primary*` so existing utility classes
                // (bg-primary-container, text-on-primary-container, etc.) re-skin.
                primary: {
                    DEFAULT: '#3ba5a5', // teal-dark — hover state
                    container: '#4ec5c5', // teal — accents, primary actions
                    fixed: '#cdeeee',
                    'fixed-dim': '#9bdcdc'
                },
                'on-primary': '#0d2942', // navy text on teal
                'on-primary-container': '#0d2942',
                'on-primary-fixed': '#0d2942',
                'on-primary-fixed-variant': '#15405f',
                'inverse-primary': '#4ec5c5',

                // ── Secondary = muted slate (captions / helper text) ────────
                secondary: {
                    DEFAULT: '#6b7785',
                    container: '#e5e7eb',
                    fixed: '#e5e7eb',
                    'fixed-dim': '#cbd1d8'
                },
                'on-secondary': '#ffffff',
                'on-secondary-container': '#0d2942',

                // ── Tertiary = Navy (deep brand) ───────────────────────────
                tertiary: {
                    DEFAULT: '#0d2942',
                    container: '#15405f'
                },
                'on-tertiary': '#ffffff',
                'on-tertiary-container': '#cdeeee',

                // ── Error ──────────────────────────────────────────────────
                error: {
                    DEFAULT: '#b91c1c',
                    container: '#fee2e2'
                },
                'on-error': '#ffffff',
                'on-error-container': '#7f1d1d',

                // ── Surfaces (ICC off-white background, white cards) ────────
                background: '#f7f9fa',
                surface: {
                    DEFAULT: '#f7f9fa',
                    bright: '#ffffff',
                    dim: '#e5e7eb',
                    'container-lowest': '#ffffff',
                    'container-low': '#f7f9fa',
                    container: '#f1f4f6',
                    'container-high': '#e9eef1',
                    'container-highest': '#dde3e8',
                    variant: '#e5e7eb'
                },
                'on-background': '#0d2942',
                'on-surface': '#0d2942',
                'on-surface-variant': '#6b7785',
                'inverse-surface': '#0d2942',
                'inverse-on-surface': '#f7f9fa',

                // ── Outlines ───────────────────────────────────────────────
                outline: {
                    DEFAULT: '#d1d5db',
                    variant: '#e5e7eb'
                },

                // ── Explicit ICC brand aliases ─────────────────────────────
                // For pages that want to hit the colors by name.
                icc: {
                    navy: '#0d2942',
                    'navy-soft': '#15405f',
                    teal: '#4ec5c5',
                    'teal-dark': '#3ba5a5',
                    bg: '#f7f9fa',
                    border: '#d1d5db',
                    muted: '#6b7785'
                },

                // ── Integration-channel colors (BC / SF identification) ────
                // Tuned for readability on light surfaces. Used to identify
                // external systems, not as Nerval brand colors.
                bc: {
                    DEFAULT: '#0d6cf3',
                    soft: '#3a8eff'
                },
                sf: {
                    DEFAULT: '#0094d4',
                    soft: '#22b5e8'
                }
            },
            fontFamily: {
                // ICC fonts: Plus Jakarta Sans (headings), Inter (body), Arimo (CTAs/labels).
                sans: ['Inter', 'system-ui', 'sans-serif'],
                h1: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
                h2: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
                h3: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
                'body-lg': ['Inter', 'system-ui', 'sans-serif'],
                'body-md': ['Inter', 'system-ui', 'sans-serif'],
                'label-sm': ['Arimo', 'system-ui', 'sans-serif'],
                cta: ['Arimo', 'system-ui', 'sans-serif'],
                'mono-data': ['ui-monospace', 'monospace']
            },
            fontSize: {
                // ICC type scale.
                h1: ['48px', { lineHeight: '1.05', letterSpacing: '-0.01em' }],
                h2: ['38px', { lineHeight: '1.10', letterSpacing: '-0.01em' }],
                h3: ['22px', { lineHeight: '1.30' }],
                'body-lg': ['18px', { lineHeight: '1.65' }],
                'body-md': ['16px', { lineHeight: '1.65' }],
                'label-sm': ['12px', { lineHeight: '1.40', letterSpacing: '0.12em' }]
            }
        }
    },
    plugins: []
};
