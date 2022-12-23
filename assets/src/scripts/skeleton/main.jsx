// eslint-disable-next-line import/no-unresolved
import "vite/modulepreload-polyfill";
import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { PageDataProvider } from "./context/page-data-context";

// Create a root element for React to render in
const container = document.getElementById("root");
const root = createRoot(container);

// Get the choices for the dropdown from a <script> tag loaded by Django
const formData = document.getElementById(container.dataset.formData);

// Convert choices to an object from an array
const choices = JSON.parse(formData.textContent).map((choice) => ({
  value: choice.slug,
  label: choice.name,
  organisation: choice.organisation,
}));

// Get the errors for the dropdown from a <script> tag loaded by Django
const errorsEl = document.getElementById(container.dataset.errors);
// If an error is added to the script tag, parse it as JSON
const errors = errorsEl?.textContent ? JSON.parse(errorsEl.textContent) : null;

root.render(
  <React.StrictMode>
    <PageDataProvider data={choices} errors={errors}>
      <App />
    </PageDataProvider>
  </React.StrictMode>
);
