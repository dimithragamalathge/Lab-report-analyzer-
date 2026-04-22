/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        paper:       "#faf6ef",
        "paper-alt": "#f2ecdf",
        ink:         "#2a2420",
        "ink-sub":   "#6b6156",
        "ink-muted": "#a8a095",
        accent:      "#b85c3e",
        "accent-dark":"#8a3f26",
        "accent-light":"#f0ddd2",
        rule:        "#e3dccb",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        serif: ["Georgia", "Times New Roman", "serif"],
        mono: ["JetBrains Mono", "Menlo", "monospace"],
      },
    },
  },
  plugins: [],
}
