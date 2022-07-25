import legacy from "@vitejs/plugin-legacy";
import { defineConfig } from "vite";
import viteReact from "@vitejs/plugin-react";

export default defineConfig({
  base: "/static/bundle/",
  build: {
    manifest: true,
    rollupOptions: {
      input: {
        main: "assets/src/scripts/main.js",
        dropdown: "assets/src/scripts/dropdown.jsx",
      },
    },
    outDir: "assets/dist/bundle",
    emptyOutDir: true,
  },
  clearScreen: false,
  server: {
    port: 3000,
    origin: "http://localhost:3000"
  },
  plugins: [
    viteReact(),
    legacy({
      targets: ["last 2 versions, not dead, > 2%"],
    }),
  ],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./assets/src/scripts/__tests__/setup.js",
    coverage: {
      lines: 95,
      functions: 95,
      branches: 95,
      statements: 95,
    }
  },
});
