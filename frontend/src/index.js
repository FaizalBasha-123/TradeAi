import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";

// Enable dark mode globally
if (typeof document !== 'undefined') {
  document.documentElement.classList.add('dark');
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
