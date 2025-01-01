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
        // Primary Colors
        primary: '#D32F2F',    // Modern Christmas red
        secondary: '#388E3C',  // Rich evergreen
        accent: '#FFD700',     // Celebratory gold

        // Light Mode
        light: {
          bg: '#FFFFFF',      // Light background
          surface: '#F8F9FA',  // Surface/card background
          text: '#212121',    // Primary text
          subtle: '#757575',  // Secondary/subtle text
        },

        // Dark Mode
        dark: {
          bg: '#121212',      // Dark background
          surface: '#1E1E1E', // Surface/card background
          text: '#FFFFFF',    // Primary text
          subtle: '#BDBDBD',  // Secondary/subtle text
        }
      }
    },
  },
  plugins: [],
  // Important to prevent conflicts with Vuetify
  important: true,
}