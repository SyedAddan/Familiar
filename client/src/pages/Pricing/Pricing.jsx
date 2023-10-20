import React from "react";
import { Link } from "react-router-dom";

import "./style.css";

const Pricing = () => {
  return (
    <div className="about">
      <div className="div">
        <footer className="footer">
          <div className="copyright-text">© Familiar 2023</div>
          <a href="/pricing">
            <img
              className="facebook-icon"
              alt="Facebook icon"
              src="/img/about/facebook-icon.png"
            />
          </a>
          <a href="/pricing">
            <img
              className="instagram-icon"
              alt="Instagram icon"
              src="/img/about/instagram-icon.svg"
            />
          </a>
          <a href="/pricing">
            <img
              className="twitter-icon"
              alt="Twitter icon"
              src="/img/about/twitter-icon.png"
            />
          </a>
          <a href="/pricing">
            <img
              className="footer-divivder"
              alt="Footer divivder"
              src="/img/about/upper-divider.svg"
            />
          </a>
        </footer>
        <div className="content">
          <div className="title">Still Building This Page!!!</div>
          <img
            className="dizzy-face"
            alt="Dizzy face"
            src="/img/about/dizzy-face.png"
          />
        </div>
        <header className="header">
          <div className="overlap">
            <img
              className="upper-divider"
              alt="Upper divider"
              src="/img/about/upper-divider.svg"
            />
            <Link to="/">
              <div className="familiar-logo">Familiar</div>
            </Link>
            <div className="nav-buttons">
              <Link to="/login">
                <div className="login-selection">
                  <div className="overlap-group">
                    <div className="login-button" />
                    <div className="text-wrapper">Login</div>
                  </div>
                </div>
              </Link>
              <Link to="/pricing">
                <div className="text-wrapper-2">Pricing</div>
              </Link>
              <Link to="/contact">
                <div className="text-wrapper-3">Contact</div>
              </Link>
              <Link to="/about">
                <div className="text-wrapper-4">About</div>
              </Link>
            </div>
          </div>
        </header>
      </div>
    </div>
  );
};

export default Pricing;
