import React from "react";
import { SiteFrame } from "../../components/SiteLayout";

const Contact = () => (
  <SiteFrame active="/contact" className="info-page">
    <main className="info-main contact-main">
      <section className="contact-card">
        <h1>Say hello.</h1>
        <p>Have feedback or an idea? Familiar is still growing, and your thoughts help shape it.</p>
        <img className="contact-image" src="/img/home/upper-divider.svg" alt="" />
      </section>
    </main>
  </SiteFrame>
);

export default Contact;
