/**
 * Tailwind v3 port of Nerval's brand tokens (which target Tailwind v4 @theme syntax).
 * Class names match the brand guide exactly: bg-primary-container, text-on-surface, etc.
 */

/** @type {import('tailwindcss').Config} */
export default {
    content: ['./src/**/*.{html,js,svelte,ts}'],
    theme: {
        // Override radius globally — sharp corners are the rule.
        // Only `rounded-card` (8px) and `rounded-full` allowed.
        borderRadius: {
            none: '0',
            DEFAULT: '0',
            sm: '0',
            md: '0',
            lg: '0',
            xl: '0',
            '2xl': '0',
            '3xl': '0',
            full: '9999px',
            card: '8px'
        },
        extend: {
            colors: {
                // ── Primary (Nerval red) ────────────────────────────────────
                primary: {
                    DEFAULT: '#a82628',
                    container: '#d23235',
                    fixed: '#ffdad8',
                    'fixed-dim': '#ffb3b1'
                },
                'on-primary': '#ffffff',
                'on-primary-container': '#ffdad8',
                'on-primary-fixed': '#410007',
                'on-primary-fixed-variant': '#92001c',
                'inverse-primary': '#ffb3b1',

                // ── Secondary (warm grays) ─────────────────────────────────
                secondary: {
                    DEFAULT: '#5f5e5e',
                    container: '#e2dfde',
                    fixed: '#e5e2e1',
                    'fixed-dim': '#c8c6c5'
                },
                'on-secondary': '#ffffff',
                'on-secondary-container': '#636262',

                // ── Tertiary (deep teal) ───────────────────────────────────
                tertiary: {
                    DEFAULT: '#005468',
                    container: '#006e87'
                },
                'on-tertiary': '#ffffff',
                'on-tertiary-container': '#b6ebff',

                // ── Error ──────────────────────────────────────────────────
                error: {
                    DEFAULT: '#ba1a1a',
                    container: '#ffdad6'
                },
                'on-error': '#ffffff',
                'on-error-container': '#93000a',

                // ── Surfaces ───────────────────────────────────────────────
                background: '#fbf9f8',
                surface: {
                    DEFAULT: '#fbf9f8',
                    bright: '#fbf9f8',
                    dim: '#dbdad9',
                    'container-lowest': '#ffffff',
                    'container-low': '#f5f3f3',
                    container: '#efeded',
                    'container-high': '#eae8e7',
                    'container-highest': '#e4e2e2',
                    variant: '#e4e2e2'
                },
                'on-background': '#1b1c1c',
                'on-surface': '#1b1c1c',
                'on-surface-variant': '#5c403f',
                'inverse-surface': '#303030',
                'inverse-on-surface': '#f2f0f0',

                // ── Outlines ───────────────────────────────────────────────
                outline: {
                    DEFAULT: '#906f6e',
                    variant: '#e5bdbb'
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
                sans: ['Roboto', 'sans-serif'],
                h1: ['manifold-cf', 'sans-serif'],
                h2: ['manifold-cf', 'sans-serif'],
                h3: ['manifold-cf', 'sans-serif'],
                'body-lg': ['Roboto', 'sans-serif'],
                'body-md': ['Roboto', 'sans-serif'],
                'label-sm': ['Roboto', 'sans-serif'],
                cta: ['Arimo', 'sans-serif'],
                'mono-data': ['ui-monospace', 'monospace']
            },
            fontSize: {
                h1: ['52px', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
                h2: ['32px', { lineHeight: '1.2', letterSpacing: '-0.01em' }],
                h3: ['24px', { lineHeight: '1.3' }],
                'body-lg': ['18px', { lineHeight: '1.6' }],
                'body-md': ['16px', { lineHeight: '1.6' }],
                'label-sm': ['14px', { lineHeight: '1.2', letterSpacing: '0.02em' }]
            }
        }
    },
    plugins: []
};
