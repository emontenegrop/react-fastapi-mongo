// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}", // Esto es importante: escaneará todos los archivos JS, TS, JSX, TSX en la carpeta src
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
