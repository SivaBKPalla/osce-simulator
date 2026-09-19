import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#102033",
          muted: "#4a5a6a",
        },
        paper: {
          DEFAULT: "#f4efe6",
          card: "#fffdf8",
        },
        clinic: {
          DEFAULT: "#1b6b5c",
          dark: "#12493f",
          soft: "#d7efe8",
        },
        rust: "#9a4a1c",
      },
      fontFamily: {
        serif: ["var(--font-serif)", "Georgia", "serif"],
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        station: "0 18px 40px -24px rgba(16, 32, 51, 0.35)",
      },
    },
  },
  plugins: [],
};

export default config;
