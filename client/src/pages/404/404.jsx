import React from "react";
import { SiteFrame } from "../../components/SiteLayout";

const NotFound = () => (
  <SiteFrame className="info-page">
    <main className="not-found-main">
      <img src="/img/404/thinking-face.png" alt="" />
      <h1>Page not found.</h1>
    </main>
  </SiteFrame>
);

export default NotFound;
