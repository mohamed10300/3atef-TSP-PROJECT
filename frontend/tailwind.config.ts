import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0a0a0a",
        surface: "#111111",
        "surface-2": "#1a1a1a",
        border: "#222222",
        accent: "#3b82f6",
        "accent-red": "#ef4444",
        "accent-green": "#22c55e",
        "text-primary": "#f5f5f5",
        "text-secondary": "#888888",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
