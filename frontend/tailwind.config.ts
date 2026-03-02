import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        gridBg: "#070b1a",
        panel: "#0f1730",
        panelSoft: "#121d3f",
        line: "#2ae9ff",
        lineSoft: "#177992",
        textMain: "#e8f7ff",
        textMuted: "#9ab6c7",
        alert: "#ff6f61",
        good: "#1bf8b6",
      },
      boxShadow: {
        neon: "0 0 0 1px rgba(42,233,255,0.6), 0 0 24px rgba(42,233,255,0.18)",
      },
      fontFamily: {
        tron: ["Orbitron", "sans-serif"],
        body: ["Rajdhani", "sans-serif"],
      },
      backgroundImage: {
        "grid-pattern":
          "linear-gradient(rgba(42,233,255,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(42,233,255,0.08) 1px, transparent 1px)",
      },
      backgroundSize: {
        grid: "40px 40px",
      },
    },
  },
  plugins: [],
};

export default config;
