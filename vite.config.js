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
  plugins: [
    viteReact(),
    legacy({
      targets: ["last 2 versions, not dead, > 2%"],
    }),
  ],
});
