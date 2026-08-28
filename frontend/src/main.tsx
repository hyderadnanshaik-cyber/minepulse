import React from "react";
import ReactDOM from "react-dom/client";
import "./i18n"; // Initialize multilingual internationalization before mounting
import App from "./App";
import "./index.css";
import { useThemeStore } from "./store/themeStore"; // Initialize in standard crisp White / Light Theme
if (typeof document !== "undefined") {
  document.documentElement.classList.remove("dark");
}
useThemeStore.getState().initTheme();
ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    {" "}
    <App />{" "}
  </React.StrictMode>,
);
