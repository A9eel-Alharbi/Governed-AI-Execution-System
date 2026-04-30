import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0f1d26",
        slate: "#213543",
        mist: "#d7e2e8",
        cloud: "#eef3f1",
        parchment: "#f6f1e8",
        moss: "#2f5d50",
        sage: "#84a89a",
        amber: "#d6a45d",
        ember: "#bb6946",
        blush: "#f0dfd5",
      },
      fontFamily: {
        display: ["Georgia", "serif"],
        body: ["Segoe UI", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
