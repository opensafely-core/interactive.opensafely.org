import "vite/modulepreload-polyfill";
import { createRoot } from "react-dom/client";
import App from "./App";

// Create a root element for React to render in
const container = document.getElementById("react-dropdown");
const root = createRoot(container);

// Get the choices for the dropdown from a <script> tag loaded by Django
const choicesEl = document.getElementById(container.dataset.choices);

// Convert choices to an object from an array
const choices = JSON.parse(choicesEl.textContent).map((choice, i) => {
  return {
    value: choice.slug,
    label: choice.name,
    organisation: choice.organisation,
  };
});

// Get the errors for the dropdown from a <script> tag loaded by Django
const errorsEl = document.getElementById(container.dataset.errors);
// If an error is added to the script tag, parse it as JSON
const errors = errorsEl?.textContent ? JSON.parse(errorsEl.textContent) : null;

// Render the React component
root.render(
  <App choices={choices} data={container.dataset} errors={errors} />
);
