import React from "react";
import { SiteFrame } from "../../components/SiteLayout";

const About = () => (
  <SiteFrame active="/about" className="info-page about-page">
    <main className="info-main">
      <section className="info-hero">
        <div className="about-hero-copy">
          <h1>Being heard can<br /><span>change the whole day.</span></h1>
          <p>A gentle place to put your thoughts into words, at your pace.</p>
        </div>
        <svg className="about-heart" viewBox="0 0 120 120" aria-hidden="true">
          <defs>
            <linearGradient id="about-heart-face" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stopColor="#ffd5dc" />
              <stop offset="0.48" stopColor="#f18da3" />
              <stop offset="1" stopColor="#c95173" />
            </linearGradient>
            <linearGradient id="about-heart-gloss" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stopColor="#fff" stopOpacity=".8" />
              <stop offset="1" stopColor="#fff" stopOpacity="0" />
            </linearGradient>
          </defs>
          <path
            d="M60 108 15 66C-7 42 8 9 35 12c12 1 20 9 25 19 5-10 13-18 25-19 27-3 42 30 20 54Z"
            fill="#a83e62"
            transform="translate(0 7)"
          />
          <path
            d="M60 108 15 66C-7 42 8 9 35 12c12 1 20 9 25 19 5-10 13-18 25-19 27-3 42 30 20 54Z"
            fill="url(#about-heart-face)"
          />
          <path
            d="M25 58C13 42 22 23 37 24c8 1 13 5 17 12-12-5-23 2-29 22Z"
            fill="url(#about-heart-gloss)"
          />
        </svg>
        <img className="info-vector" src="/img/about/upper-divider.svg" alt="" />
      </section>
    </main>
  </SiteFrame>
);

export default About;
