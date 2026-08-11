/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        obsidian: {
          950: "#0B0F17", // Canvas background
          900: "#111827", // Surface base
          800: "#1F2937", // Card / surface elevated
          700: "#374151", // Border subtle
          600: "#4B5563", // Muted text
        },
        emerald: {
          500: "#10B981", // Accent primary
          600: "#059669", // Accent hover
          700: "#047857",
        },
        teal: {
          500: "#14B8A6",
          600: "#0D9488",
        },
        brand: {
          bg: "var(--color-bg)",
          surface: "var(--color-surface)",
          "surface-elevated": "var(--color-surface-elevated)",
          border: "var(--color-border)",
          text: "var(--color-text)",
          "text-muted": "var(--color-text-muted)",
          primary: "var(--color-primary)",
          "primary-hover": "var(--color-primary-hover)",
        },
      },
      fontFamily: {
        persian: ["Vazirmatn", "system-ui", "sans-serif"],
        latin: ["Inter", "system-ui", "sans-serif"],
      },
      minHeight: {
        touch: "44px",
        "touch-lg": "48px",
      },
      minWidth: {
        touch: "44px",
        "touch-lg": "48px",
      },
    },
  },
  plugins: [],
};
