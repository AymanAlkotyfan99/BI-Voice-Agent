/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#1C5083",   // اللون الأساسي لمشروع BI Voice Agent
        accent: "#fc9922",    // اللون البرتقالي الثانوي
      },
    },
  },
  plugins: [],
}
