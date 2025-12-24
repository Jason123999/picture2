import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        "brand-primary": "#6366f1",
        "brand-secondary": "#22d3ee",
      },
    },
  },
  plugins: [],
};

export default config;
