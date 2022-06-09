import "vite/modulepreload-polyfill";
import { createRoot } from "react-dom/client";

const container = document.getElementById("react-dropdown");
const root = createRoot(container);

root.render(<p>Hello world</p>);
