import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const backendUrl = env.BACKEND_URL || "http://localhost:8000";
  const previewPort = Number(env.PORT) || 4173;

  const apiProxy = {
    target: backendUrl,
    changeOrigin: true,
    secure: true,
  };

  return {
    plugins: [react()],
    server: {
      port: 3000,
      proxy: {
        "/api": apiProxy,
        "/docs": apiProxy,
        "/health": apiProxy,
      },
    },
    preview: {
      host: "0.0.0.0",
      port: previewPort,
      strictPort: true,
      proxy: {
        "/api": apiProxy,
        "/docs": apiProxy,
        "/health": apiProxy,
      },
    },
    build: {
      outDir: "dist",
      sourcemap: true,
    },
  };
});
