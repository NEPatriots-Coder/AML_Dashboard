import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".", "");
  const backendTarget = env.VITE_BACKEND_PROXY_TARGET || "http://127.0.0.1:8000";

  return {
    plugins: [react()],
    server: {
      port: 5180,
      proxy: {
        "/api": {
          target: backendTarget,
          changeOrigin: true,
        },
      },
    },
  };
});
