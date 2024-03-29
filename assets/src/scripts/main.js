import "vite/modulepreload-polyfill";
import "@alpinejs/persist/dist/cdn";
import Alpine from "alpinejs/packages/csp/dist/module.esm";
import "@alpinejs/persist";
import "../styles/main.css";

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

Alpine.data("account-menu", () => ({
  isAccountMenuOpen: false,

  accountMenuToggle() {
    this.isAccountMenuOpen = !this.isAccountMenuOpen;
  },
  accountMenuHide() {
    this.isAccountMenuOpen = false;
  },
}));

Alpine.data("beta-banner", function () {
  return {
    isBetaBannerVisible: this.$persist(true),

    hideBetaBanner() {
      this.isBetaBannerVisible = false;
    },
  };
});

Alpine.data("notify-banner", function () {
  return {
    isNotifyBannerVisible: this.$persist(true),

    hideNotifyBanner() {
      this.isNotifyBannerVisible = false;
    },
  };
});

Alpine.data("toast", () => ({
  isToastVisible: true,

  init() {
    setTimeout(() => (this.isToastVisible = false), 5000);
  },

  hideToast() {
    this.isToastVisible = false;
  },
}));

window.Alpine = Alpine;
window.Alpine.start();
