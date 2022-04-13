import legacy from "@vitejs/plugin-legacy";
import { defineConfig } from "vite";

export default defineConfig({
  base: "/static/bundle/",
  build: {
    manifest: true,
    rollupOptions: {
      input: {
        main: "assets/src/scripts/main.js",
      },
    },
    outDir: "assets/dist/bundle",
    emptyOutDir: true,
  },
  clearScreen: false,
  plugins: [
    legacy({
      targets: ["last 2 versions, not dead, > 2%"],
    }),
  ],
});
