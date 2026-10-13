import React from "react";
import { SiteFrame } from "../../components/SiteLayout";

const Pricing = () => (
  <SiteFrame active="/pricing" className="info-page pricing-page">
    <main className="info-main">
      <section className="info-hero explore-hero">
        <h1>Simple to start.<br /><span>Free in early access.</span></h1>
        <img className="info-hero-art" src="/img/home/feature-1-image.png" alt="" />
        <img className="info-vector" src="/img/home/vector-6.svg" alt="" />
      </section>
      <section className="early-access-wrap pricing-content">
        <article className="early-access-card">
          <h2>What’s included</h2>
          <div className="access-price">Free<span>provider usage limits may apply</span></div>
          <ul>
            <li><span>✓</span> A companion shaped around you</li>
            <li><span>✓</span> Your conversation saved to your account</li>
            <li><span>✓</span> A lifelike avatar and optional spoken replies</li>
          </ul>
        </article>
      </section>
    </main>
  </SiteFrame>
);

export default Pricing;
