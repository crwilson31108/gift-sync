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
        'light': {
          'surface': 'rgb(var(--v-theme-surface))',
          'background': 'rgb(var(--v-theme-background))',
          'text': 'rgb(var(--v-theme-on-surface))',
          'subtle': 'rgba(var(--v-theme-on-surface), 0.6)',
          'border': 'rgba(var(--v-theme-on-surface), 0.12)',
        },
        'dark': {
          'surface': 'rgb(var(--v-theme-surface-dark))',
          'background': 'rgb(var(--v-theme-background-dark))',
          'text': 'rgb(var(--v-theme-on-surface-dark))',
          'subtle': 'rgba(var(--v-theme-on-surface-dark), 0.6)',
          'border': 'rgba(var(--v-theme-on-surface-dark), 0.12)',
        },
        'primary': {
          DEFAULT: 'rgb(var(--v-theme-primary))',
          'dark': 'rgb(var(--v-theme-primary-dark))',
        },
        'secondary': {
          DEFAULT: 'rgb(var(--v-theme-secondary))',
          'dark': 'rgb(var(--v-theme-secondary-dark))',
        },
        'info': {
          DEFAULT: 'rgb(var(--v-theme-info))',
          'dark': 'rgb(var(--v-theme-info-dark))',
        },
        'success': {
          DEFAULT: 'rgb(var(--v-theme-success))',
          'dark': 'rgb(var(--v-theme-success-dark))',
        },
        'warning': {
          DEFAULT: 'rgb(var(--v-theme-warning))',
          'dark': 'rgb(var(--v-theme-warning-dark))',
        },
        'error': {
          DEFAULT: 'rgb(var(--v-theme-error))',
          'dark': 'rgb(var(--v-theme-error-dark))',
        }
      },
      backgroundColor: {
        'card': {
          DEFAULT: 'rgb(var(--v-theme-surface))',
          'dark': 'rgb(var(--v-theme-surface-dark))',
        }
      }
    },
  },
  plugins: [],
}