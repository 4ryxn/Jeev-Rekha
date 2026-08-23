import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0D1B1E",
        paper: "#F7F6F1",
        teal: "#0F766E",
        lime: "#C9F542",
        line: "#D8DDD5",
        risk: { green: "#198754", amber: "#B45309", red: "#B42318", grey: "#475569" },
      },
      fontFamily: {
        display: ["ui-rounded", "Avenir Next", "Inter", "sans-serif"],
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: { float: "0 16px 40px rgba(13, 27, 30, 0.08)" },
    },
  },
  plugins: [],
};

export default config;
