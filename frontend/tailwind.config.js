/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Outfit', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'], // Suggesting a nice mono if available, or fallback
            },
            colors: {
                // Pack Solutions Brand Colors
                'pack-blue': '#0066CC',
                'pack-blue-dark': '#004C99',
                'pack-blue-light': '#E6F2FF',
                'pack-white': '#FFFFFF',
                'pack-gray': '#6B7280',
                'pack-gray-light': '#F3F4F6',

                // Backgrounds (updated for Pack Solutions theme)
                'cosmic-void': '#0A1628',    // Deep blue-black (garder pour compatibilité)
                'cosmic-night': '#0f172a',   // Standard dark (garder pour compatibilité)
                'cosmic-dust': '#1e293b',    // Lighter panels (garder pour compatibilité)
                'pack-bg-dark': '#003366',   // Pack Blue dark variant
                'pack-bg-base': '#004C99',   // Pack Blue medium variant
                'pack-bg-light': '#0066CC',  // Pack Blue (couleur principale)

                // Accents - Pack Solutions Blue shades
                'nebula-purple': '#0066CC',  // Pack Blue as primary
                'nebula-blue': '#0099FF',    // Lighter blue accent
                'starlight': '#f8fafc',

                // Functional
                'glass-border': 'rgba(255, 255, 255, 0.08)',
                'glass-surface': 'rgba(10, 22, 40, 0.6)',
                'glass-highlight': 'rgba(255, 255, 255, 0.05)',
            },
            backgroundImage: {
                'cosmic-gradient': 'radial-gradient(circle at top center, #0A2540 0%, #0A1628 100%)', // Garder pour compatibilité
                'glass-gradient': 'linear-gradient(145deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%)',
                'active-item': 'linear-gradient(90deg, rgba(0,102,204,0.15) 0%, transparent 100%)',
                'pack-gradient': 'linear-gradient(135deg, #0066CC 0%, #0099FF 100%)',
                'pack-bg-gradient': 'radial-gradient(circle at top center, #0066CC 0%, #003366 100%)' // Nouveau gradient Pack Solutions
            },
            backdropBlur: {
                'xs': '2px',
            },
            animation: {
                'float': 'float 6s ease-in-out infinite',
                'glow': 'glow 2s ease-in-out infinite alternate',
                'slide-up': 'slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
                'fade-in': 'fadeIn 0.3s ease-out',
                'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
            keyframes: {
                float: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-10px)' },
                },
                glow: {
                    'from': { boxShadow: '0 0 10px -5px rgba(124, 58, 237, 0.3)' },
                    'to': { boxShadow: '0 0 20px 0px rgba(124, 58, 237, 0.6)' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(20px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                }
            }
        },
    },
    plugins: [],
    darkMode: 'class',
}
