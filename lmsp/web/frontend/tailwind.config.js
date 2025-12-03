/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      // Custom breakpoints for TV and ultrawide
      screens: {
        'xs': '480px',       // Small phones
        'sm': '640px',       // Phones landscape
        'md': '768px',       // Tablets
        'lg': '1024px',      // Small laptops
        'xl': '1280px',      // Laptops/desktops
        '2xl': '1536px',     // Large desktops
        '3xl': '1920px',     // 1080p TV/monitors
        '4k': '2560px',      // 1440p / 4K TV
        'ultrawide': '3440px', // Ultrawide monitors
      },
      colors: {
        // OLED-optimized palette
        'oled': {
          'black': '#000000',
          'near': '#0a0a0a',
          'surface': '#0d0d0d',
          'panel': '#111111',
          'border': '#1a1a1a',
          'muted': '#222222',
        },
        'accent': {
          'primary': '#00ff88',    // Neon green
          'secondary': '#0088ff',  // Electric blue
          'tertiary': '#ff00ff',   // Magenta
          'success': '#22c55e',    // Green (success)
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
      // Responsive font sizes
      fontSize: {
        // Base sizes that scale up on larger screens
        'responsive-xs': ['clamp(0.625rem, 0.5rem + 0.25vw, 0.75rem)', { lineHeight: '1.4' }],
        'responsive-sm': ['clamp(0.75rem, 0.625rem + 0.35vw, 0.875rem)', { lineHeight: '1.4' }],
        'responsive-base': ['clamp(0.875rem, 0.75rem + 0.4vw, 1.125rem)', { lineHeight: '1.5' }],
        'responsive-lg': ['clamp(1rem, 0.875rem + 0.5vw, 1.375rem)', { lineHeight: '1.5' }],
        'responsive-xl': ['clamp(1.125rem, 1rem + 0.6vw, 1.625rem)', { lineHeight: '1.4' }],
        'responsive-2xl': ['clamp(1.25rem, 1.125rem + 0.75vw, 2rem)', { lineHeight: '1.3' }],
        'responsive-3xl': ['clamp(1.5rem, 1.25rem + 1vw, 2.5rem)', { lineHeight: '1.2' }],
        'responsive-4xl': ['clamp(2rem, 1.5rem + 1.5vw, 3.5rem)', { lineHeight: '1.1' }],
      },
      // Responsive spacing
      spacing: {
        'responsive-1': 'clamp(0.25rem, 0.125rem + 0.25vw, 0.5rem)',
        'responsive-2': 'clamp(0.5rem, 0.25rem + 0.5vw, 1rem)',
        'responsive-4': 'clamp(1rem, 0.5rem + 1vw, 2rem)',
        'responsive-6': 'clamp(1.5rem, 0.75rem + 1.5vw, 3rem)',
        'responsive-8': 'clamp(2rem, 1rem + 2vw, 4rem)',
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
