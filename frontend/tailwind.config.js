/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#8B5CF6',
          dark: '#7C3AED',
        },
        secondary: {
          DEFAULT: '#3B82F6',
          dark: '#2563EB',
        },
        background: {
          DEFAULT: '#1F2937',
          light: '#374151',
        },
      },
      animation: {
        'glow': 'glow 2s infinite',
      },
      keyframes: {
        glow: {
          '0%, 100%': { boxShadow: '0 0 5px rgba(139, 92, 246, 0.5)' },
          '50%': { boxShadow: '0 0 20px rgba(139, 92, 246, 0.8)' },
        },
      },
    },
  },
  plugins: [],
} 