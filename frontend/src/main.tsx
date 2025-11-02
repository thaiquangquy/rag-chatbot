import React from "react";
import ReactDOM from "react-dom/client";

import { IndexPage } from "./pages/index";

const container = document.getElementById("root");

if (!container) {
  throw new Error("Root container element not found");
}

const root = ReactDOM.createRoot(container);
root.render(
  <React.StrictMode>
    <IndexPage />
  </React.StrictMode>
);
