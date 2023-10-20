import React from "react";
import { Link } from "react-router-dom";

import "./style.css";

const Home = () => {
  return (
    <div className="home">
      <div className="div">
        <footer className="footer">
          <div className="copyright-text">© Familiar 2023</div>
          <a href="/">
            <img className="facebook-icon" alt="Facebook icon" src="/img/home/facebook-icon.png" />
          </a>
          <a href="/">
            <img className="instagram-icon" alt="Instagram icon" src="/img/home/instagram-icon.svg" />
          </a>
          <a href="/">
            <img className="twitter-icon" alt="Twitter icon" src="/img/home/twitter-icon.png" />
          </a>
        </footer>
        <div className="overlap">
          <div className="content">
            <div className="overlap-group">
              <div className="overlap-group-2">
                <img className="vector" alt="Vector" src="/img/home/vector-6.svg" />
                <img className="img" alt="Vector" src="/img/home/vector-5.svg" />
                <img className="vector-2" alt="Vector" src="/img/home/vector-2.svg" />
                <img className="vector-3" alt="Vector" src="/img/home/vector-1.svg" />
                <img className="vector-4" alt="Vector" src="/img/home/vector.svg" />
                <img className="feature-divider" alt="Feature divider" src="/img/home/upper-divider.svg" />
                <p className="body-text">A Push Towards A Much Healthier Life</p>
              </div>
              <img className="vector-5" alt="Vector" src="/img/home/vector-4.svg" />
              <img className="vector-6" alt="Vector" src="/img/home/vector-3.svg" />
            </div>
          </div>
          <div className="features">
            <div className="overlap-2">
              <img className="footer-divivder" alt="Footer divivder" src="/img/home/upper-divider.svg" />
              <div className="feature">
                <div className="overlap-group-3">
                  <img className="feature-image" alt="Feature" src="/img/home/feature-3-image.png" />
                  <p className="feature-text">
                    Ensuring the trust between the user and Familiar, the chat history is kept private. Such measures
                    are set in place to maintain transparency, trust and respect between the user and Familiar. So, you
                    can talk with Familiar to your heart's content.
                  </p>
                  <div className="feature-heading">Private</div>
                </div>
              </div>
              <div className="overlap-wrapper">
                <div className="overlap-3">
                  <img className="feature-image-2" alt="Feature" src="/img/home/feature-2-image.png" />
                  <p className="text-wrapper">
                    Using the power of the latest LLMs, Familiar provides a very soothing and calming environment.
                    Chatting with Familiar feels very natural because of the human-like responses of the underlying
                    chatbot and expressive facial features of the avatar.
                  </p>
                  <div className="feature-heading-2">Natural</div>
                </div>
              </div>
              <div className="overlap-group-wrapper">
                <div className="overlap-3">
                  <img className="feature-image-3" alt="Feature" src="/img/home/feature-1-image.png" />
                  <p className="p">
                    With AI integrated in it, Familiar is a very effective chatbot. It can effortlessly and quickly
                    determine if the person in the treatment process needs more treatment or are they well, by their
                    conversation history and their current behaviour.
                  </p>
                  <div className="feature-heading-3">Effective</div>
                </div>
              </div>
            </div>
          </div>
          <header className="header">
            <div className="overlap-4">
              <img className="upper-divider" alt="Upper divider" src="/img/home/upper-divider.svg" />
              <Link to="/">
                <div className="familiar-logo">Familiar</div>
              </Link>
              <div className="nav-buttons">
                <Link to="/login">
                  <div className="login-selection">
                    <div className="overlap-group-4">
                      <div className="login-button" />
                      <div className="text-wrapper-2">Login</div>
                    </div>
                  </div>
                </Link>
                <Link to="/pricing">
                  <div className="text-wrapper-3">Pricing</div>
                </Link>
                <Link to="/contact">
                  <div className="text-wrapper-4">Contact</div>
                </Link>
                <Link to="/about">
                  <div className="text-wrapper-5">About</div>
                </Link>
              </div>
            </div>
          </header>
        </div>
      </div>
    </div>
  );
};

export default Home;