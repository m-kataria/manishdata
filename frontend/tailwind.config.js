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
                // ── Primary = TotalITsuite electric cyan ─────────
                primary: {
                    DEFAULT: '#22d3ee',
                    container: '#00d9ff',
                    fixed: '#0a323a',
                    'fixed-dim': '#155060'
                },
                'on-primary': '#0a0e27',
                'on-primary-container': '#0a0e27',
                'on-primary-fixed': '#cdf8ff',
                'on-primary-fixed-variant': '#22d3ee',
                'inverse-primary': '#00d9ff',

                // ── Secondary = muted gray for dark surfaces ────────
                secondary: {
                    DEFAULT: '#9aa5b8',
                    container: '#1a1f3a',
                    fixed: '#1a1f3a',
                    'fixed-dim': '#252b4a'
                },
                'on-secondary': '#0a0e27',
                'on-secondary-container': '#ffffff',

                // ── Tertiary = white text / cyan highlight ───────────────────
                tertiary: {
                    DEFAULT: '#ffffff',
                    container: '#22d3ee'
                },
                'on-tertiary': '#0a0e27',
                'on-tertiary-container': '#0a0e27',

                // ── Error ──────────────────────────────────────────────────
                error: {
                    DEFAULT: '#ef4444',
                    container: '#3f1212'
                },
                'on-error': '#ffffff',
                'on-error-container': '#fecaca',

                // ── Surfaces (TotalITsuite dark navy) ────────
                background: '#0a0e27',
                surface: {
                    DEFAULT: '#0a0e27',
                    bright: '#15193a',
                    dim: '#050816',
                    'container-lowest': '#050816',
                    'container-low': '#0a0e27',
                    container: '#0f1530',
                    'container-high': '#15193a',
                    'container-highest': '#1a1f3a',
                    variant: '#15193a'
                },
                'on-background': '#ffffff',
                'on-surface': '#ffffff',
                'on-surface-variant': '#9aa5b8',
                'inverse-surface': '#ffffff',
                'inverse-on-surface': '#0a0e27',

                // ── Outlines ───────────────────────────────────────────────
                outline: {
                    DEFAULT: '#1f2a4a',
                    variant: '#15193a'
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
