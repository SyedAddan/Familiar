import React from "react";
import { Link } from "react-router-dom";

import Layout from '../../components/layout/layout'

const Home = () => {
  return (
    <Layout>
      <div className="main-box">
        <img className="line" alt="Line" src="/img/line-4.svg" />
        <img className="img" alt="Line" src="/img/line-5.svg" />
      </div>
      <p className="a-push-towards-a">
        A PUSH TOWARDS A MUCH HEALTHIER LIFE FROM SOMEONE FAMILIAR
      </p>
      <div className="CTA">
        <div className="contact-button">
          <Link to="/contact">
            <div className="overlap-group">
              <div className="contact">CONTACT</div>
            </div>
          </Link>
        </div>
        <div className="chat-button">
          <Link to="/chatbot">
            <div className="chat-wrapper">
              <div className="chat">CHAT</div>
            </div>
          </Link>
        </div>
      </div>
      <img className="familiar" alt="Familiar" src="/img/familiar.png" />
      <div className="feature">
        <div className="overlap-group-2">
          <div className="feature-BG" />
          <img
            className="feature-diagram"
            alt="Feature diagram"
            src="/img/feature-3-diagram.png"
          />
        </div>
        <img
          className="feature-UR-stuff"
          alt="Feature UR stuff"
          src="/img/feature-3-ur-stuff.png"
        />
        <div className="feature-text">Natural</div>
      </div>
      <div className="feature-2">
        <div className="overlap-2">
          <div className="feature-BG" />
          <img
            className="feature-diagram-2"
            alt="Feature diagram"
            src="/img/feature-2-diagram.png"
          />
        </div>
        <img
          className="feature-UR-stuff"
          alt="Feature UR stuff"
          src="/img/feature-2-ur-stuff.png"
        />
        <div className="feature-text-2">Private</div>
      </div>
      <div className="feature-3">
        <div className="overlap-3">
          <div className="feature-BG" />
          <img
            className="feature-diagram-3"
            alt="Feature diagram"
            src="/img/feature-1-diagram.png"
          />
        </div>
        <img
          className="feature-UR-stuff"
          alt="Feature UR stuff"
          src="/img/feature-1-ur-stuff.png"
        />
        <div className="feature-text-2">Effective</div>
      </div>
    </Layout>
  );
};

export default Home;
