/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // OLED-optimized palette
        'oled': {
          'black': '#000000',
          'near': '#0a0a0a',
          'panel': '#111111',
          'border': '#1a1a1a',
          'muted': '#222222',
        },
        'accent': {
          'primary': '#00ff88',    // Neon green
          'secondary': '#0088ff',  // Electric blue
          'tertiary': '#ff00ff',   // Magenta
          'warning': '#ffaa00',    // Orange
          'error': '#ff4444',      // Red
        },
        // Text colors for dark theme
        'text': {
          'primary': '#ffffff',
          'secondary': '#888888',
          'muted': '#555555',
        },
        // Achievement tiers
        'tier': {
          'bronze': '#cd7f32',
          'silver': '#c0c0c0',
          'gold': '#ffd700',
          'platinum': '#e5e4e2',
          'diamond': '#b9f2ff',
        },
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Fira Code', 'monospace'],
        'game': ['Orbitron', 'sans-serif'],
      },
      animation: {
        'glow': 'glow 2s ease-in-out infinite alternate',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 3s ease-in-out infinite',
        'achievement-pop': 'achievement-pop 0.5s ease-out forwards',
        'confetti': 'confetti 1s ease-out forwards',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px var(--tw-shadow-color), 0 0 10px var(--tw-shadow-color)' },
          '100%': { boxShadow: '0 0 10px var(--tw-shadow-color), 0 0 20px var(--tw-shadow-color), 0 0 30px var(--tw-shadow-color)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'achievement-pop': {
          '0%': { transform: 'scale(0) rotate(-10deg)', opacity: '0' },
          '50%': { transform: 'scale(1.1) rotate(5deg)' },
          '100%': { transform: 'scale(1) rotate(0)', opacity: '1' },
        },
        confetti: {
          '0%': { transform: 'translateY(0) rotate(0)', opacity: '1' },
          '100%': { transform: 'translateY(100vh) rotate(720deg)', opacity: '0' },
        },
      },
    },
  },
  plugins: [],
}
