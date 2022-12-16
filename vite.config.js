import legacy from "@vitejs/plugin-legacy";
import { defineConfig } from "vite";
import { viteStaticCopy } from "vite-plugin-static-copy";
import viteReact from "@vitejs/plugin-react";

export default defineConfig({
  base: "/static/bundle/",
  build: {
    manifest: true,
    rollupOptions: {
      input: {
        main: "assets/src/scripts/main.js",
        bootstrap: "assets/src/scripts/bootstrap.js",
        form: "assets/src/scripts/form/index.jsx",
      },
    },
    outDir: "assets/dist/bundle",
    emptyOutDir: true,
  },
  clearScreen: false,
  server: {
    port: 5173,
    origin: "http://localhost:5173"
  },
  plugins: [
    viteReact(),
    legacy({
      targets: ["last 2 versions, not dead, > 2%"],
    }),
    viteStaticCopy({
      targets: [
        {
          src: "./node_modules/jquery/dist/jquery.slim.min.*",
          dest: "vendor",
        },
        {
          src: "./node_modules/select2/dist/css/select2.min.css",
          dest: "vendor",
        },
        {
          src: "./node_modules/select2/dist/js/select2.min.js",
          dest: "vendor",
        },
        {
          src: "./node_modules/@ttskch/select2-bootstrap4-theme/dist/select2-bootstrap4.min.css",
          dest: "vendor",
        },
      ]
    })
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
    }
  },
});
