/* eslint-disable import/no-extraneous-dependencies */
import legacy from "@vitejs/plugin-legacy";
import react from "@vitejs/plugin-react-swc";
import { defineConfig } from "vite";

export default defineConfig({
  base: "/static/bundle/",
  build: {
    manifest: true,
    rollupOptions: {
      input: {
        bootstrap: "assets/src/scripts/bootstrap.js",
        main: "assets/src/scripts/main.js",
        skeleton: "assets/src/scripts/skeleton/main.jsx",
      },
    },
    outDir: "assets/dist/bundle",
    emptyOutDir: true,
  },
  clearScreen: false,
  server: {
    port: 5173,
    origin: "http://localhost:5173",
  },
  plugins: [
    react(),
    legacy({
      targets: ["last 2 versions, not dead, > 2%"],
    }),
  ],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./assets/src/scripts/form/__tests__/setup.js",
    coverage: {
      lines: 95,
      functions: 95,
      branches: 95,
      statements: 95,
    },
  },
});
