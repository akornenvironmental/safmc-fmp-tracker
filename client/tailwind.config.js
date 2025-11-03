/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class', // Enable class-based dark mode
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Josefin Sans"', 'sans-serif'], // Body font
        heading: ['"Josefin Sans"', 'sans-serif'], // Heading font (matching FMP theme)
      },
      colors: {
        brand: {
          blue: '#08306b',      // Primary blue
          green: '#209d5c',     // Primary green
          'blue-light': '#2171b5',
          'blue-dark': '#081d42',
          'green-light': '#41b883',
          'green-dark': '#1a7d47',
        },
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
};
