import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FaCommentDots, FaEnvelope } from "react-icons/fa";
import api from "../../api";
import { SiteFrame } from "../../components/SiteLayout";

const Home = () => {
  const [signedIn, setSignedIn] = useState(false);
  useEffect(() => {
    let mounted = true;
    api.get("/getUser")
      .then(() => {
        if (mounted) setSignedIn(true);
      })
      .catch((error) => {
        if (error.response?.status !== 401) {
          console.error("Unable to check Familiar sign-in status.", error);
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <SiteFrame className="home-page">
      <main>
        <section className="hero-section">
          <div className="hero-copy">
            <h1>
              A familiar face.
              <span> A little more understood.</span>
            </h1>
            <div className="hero-actions">
              <Link className="button button-quiet" to="/contact">
                <FaEnvelope aria-hidden="true" />
                Reach out
              </Link>
              <Link className="button button-primary" to={signedIn ? "/chat" : "/login"}>
                <FaCommentDots aria-hidden="true" />
                Chat
              </Link>
            </div>
          </div>
          <div className="hero-art" aria-label="A welcoming illustrated space">
            <div className="hero-art-glow" />
            <div className="hero-portrait-card">
              <div className="portrait-image-wrap">
                <img src="/img/home/feature-2-image.png" alt="Familiar's friendly avatar" />
              </div>
            </div>
          </div>
        </section>
      </main>
    </SiteFrame>
  );
};

export default Home;
