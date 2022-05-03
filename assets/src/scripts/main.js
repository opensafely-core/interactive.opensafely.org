import("vite/modulepreload-polyfill");
import persist from "@alpinejs/persist";
import Alpine from "alpinejs";
import "../styles/main.css";

Alpine.plugin(persist);
window.Alpine = Alpine;

Alpine.start();

if (document.location.hostname === "interactive.opensafely.org") {
  const script = document.createElement("script");
  script.defer = true;
  script.setAttribute("data-domain", "interactive.opensafely.org");
  script.id = "plausible";
  script.src = "https://plausible.io/js/plausible.compat.js";

  document.head.appendChild(script);
}
