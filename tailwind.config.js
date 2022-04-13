const defaultTheme = require("tailwindcss/defaultTheme");

module.exports = {
  content: ["./interactive/templates/**/*.html"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Public Sans", ...defaultTheme.fontFamily.sans],
      },
      colors: {
        oxford: {
          DEFAULT: "#002147",
          50: "#f1f7ff",
          100: "#cfe5ff",
          200: "#9ccaff",
          300: "#69afff",
          400: "#3693ff",
          500: "#0378ff",
          600: "#0058be",
          700: "#00397a",
          800: "#002147",
          900: "#001936",
        },
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
