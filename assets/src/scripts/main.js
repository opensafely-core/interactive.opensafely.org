import persist from "@alpinejs/persist";
import Alpine from "alpinejs";
import "../styles/main.css";

Alpine.plugin(persist);
window.Alpine = Alpine;

Alpine.start();
