import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          50: '#e6eef7',
          100: '#ccddef',
          200: '#99bbdf',
          300: '#6699cf',
          400: '#3377bf',
          500: '#001f3f', // Azul marino principal
          600: '#001933',
          700: '#001327',
          800: '#000d1a',
          900: '#00060d',
        },
        pastel: {
          50: '#fffef5',
          100: '#fffceb',
          200: '#fff9d6',
          300: '#fff5c2',
          400: '#fff2ad',
          500: '#ffeb99', // Amarillo pastel principal
          600: '#ffe680',
          700: '#ffe066',
          800: '#ffdb4d',
          900: '#ffd633',
        },
        romantic: {
          50: '#fef2f3',
          100: '#fde6e7',
          200: '#fbd0d5',
          300: '#f7aab2',
          400: '#f27a8a',
          500: '#e63946',
          600: '#d62839',
          700: '#b01e2c',
          800: '#931b29',
          900: '#7c1a26',
        },
      },
      backgroundImage: {
        'gradient-romantic': 'linear-gradient(135deg, #001f3f 0%, #000000 100%)',
        'gradient-love': 'linear-gradient(135deg, #001f3f 0%, #003366 100%)',
        'gradient-accent': 'linear-gradient(135deg, #ffeb99 0%, #ffd633 100%)',
      },
    },
  },
  plugins: [],
};
export default config;
