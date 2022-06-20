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

document.querySelectorAll("input[type='submit']").forEach((submit) => {
  const formEl = submit.parentElement.closest("form");
  let submitClick = false;

  submit.addEventListener("click", (e) => {

    // Check if required fields have been filled
    if (formEl.checkValidity()) {

      // If click has already been submitted
      // then disable the button clicks
      if (submitClick) {
        e.preventDefault();
        submit.disabled = true;
      }

      submitClick = true;
    }
  });
});
