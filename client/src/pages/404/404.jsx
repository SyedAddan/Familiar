import React from "react";
import { Link } from "react-router-dom";

import "./style.css";

const NotFound = () => {
  return (
    <div className="element-page">
      <div className="div">
        <footer className="footer">
          <div className="copyright-text">© Familiar 2023</div>
          <a href="/404">
            <img
              className="facebook-icon"
              alt="Facebook icon"
              src="/img/404/facebook-icon.png"
            />
          </a>
          <a href="/404">
            <img
              className="instagram-icon"
              alt="Instagram icon"
              src="/img/404/instagram-icon.svg"
            />
          </a>
          <a href="/404">
            <img
              className="twitter-icon"
              alt="Twitter icon"
              src="/img/404/twitter-icon.png"
            />
          </a>
          <a href="/404">
            <img
              className="footer-divivder"
              alt="Footer divivder"
              src="/img/404/upper-divider.svg"
            />
          </a>
        </footer>
        <div className="content">
          <img
            className="thinking-face"
            alt="Thinking face"
            src="/img/404/thinking-face.png"
          />
          <p className="title">Please check the path again!</p>
        </div>
        <header className="header">
          <div className="overlap">
            <img
              className="upper-divider"
              alt="Upper divider"
              src="/img/404/upper-divider.svg"
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

export default NotFound;
