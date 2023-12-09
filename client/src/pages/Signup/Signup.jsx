import React from "react";
import { Link } from "react-router-dom";

import "./style.css";

const Signup = () => {
  return (
    <div className="sign-up">
      <div className="div">
        <header className="header">
          <div className="overlap-2">
            <img
              className="upper-divider"
              alt="Upper divider"
              src="/img/signup/upper-divider.svg"
            />
            <Link to="/">
              <div className="familiar-logo">Familiar</div>
            </Link>
            <div className="nav-buttons">
              <Link to="/login">
                <div className="login-selection">
                  <div className="overlap-group-2">
                    <div className="login-button" />
                    <div className="text-wrapper-4">Login</div>
                  </div>
                </div>
              </Link>
              <Link to="/pricing">
                <div className="text-wrapper-5">Pricing</div>
              </Link>
              <Link to="/contact">
                <div className="text-wrapper-6">Contact</div>
              </Link>
              <Link to="about">
                <div className="text-wrapper-7">About</div>
              </Link>
            </div>
          </div>
        </header>
        <div className="content">
          <div className="text-wrapper-3">Sign Up</div>
          <form>
            <div className="email">
              <inputs
                className="text-field-wrapper"
                placeholder="Email*"
                type="email"
                required
              />
            </div>
            <div className="username">
              <input
                className="text-field-wrapper"
                placeholder="Username*"
                type="text"
                required
              />
            </div>
            <div className="avatar-name">
              <input
                className="text-field-wrapper"
                placeholder="Avatar Name*"
                type="text"
                required
              />
            </div>
            <div className="relationship">
              <textarea
                className="text-field-wrapper"
                placeholder="Relationship*"
                rows={3}
                style={{ resize: "none" }}
                required
              />
            </div>
            <div className="additional">
              <textarea
                className="text-field-wrapper"
                placeholder="Any additional details"
                rows={3}
                style={{ resize: "none" }}
              />
            </div>
            <div className="password">
              <input />
              <div className="overlap">
                <div className="text-wrapper-2">Password*</div>
              </div>
            </div>
            <div className="confirm-password">
              <div className="overlap">
                <div className="confirm-password-2">Confirm Password*</div>
              </div>
            </div>
            <div className="voice">
              <div className="overlap">
                <img
                  className="upload"
                  alt="Upload"
                  src="/img/signup/upload.png"
                />
                <img
                  className="microphone"
                  alt="Microphone"
                  src="/img/signup/microphone.png"
                />
                <p className="p">Upload/Record Voice of the Avatar*</p>
              </div>
            </div>
            <div className="image">
              <div className="overlap">
                <img
                  className="upload"
                  alt="Upload"
                  src="/img/signup/upload-1.png"
                />
                <p className="p">Upload Image of the Avatar*</p>
              </div>
            </div>
            <div className="overlap-group-wrapper">
              <div className="overlap-group">
                <div className="sign-up-text">Sign Up</div>
              </div>
            </div>
            <Link to="/login">
              <p className="text-wrapper">Already have an account? Sign In</p>
            </Link>
          </form>
        </div>
        <footer className="footer">
          <div className="copyright-text">© Familiar 2023</div>
          <a href="/signup">
            <img
              className="facebook-icon"
              alt="Facebook icon"
              src="/img/signup/facebook-icon.png"
            />
          </a>
          <a href="/signup">
            <img
              className="instagram-icon"
              alt="Instagram icon"
              src="/img/signup/instagram-icon.svg"
            />
          </a>
          <a href="/signup">
            <img
              className="twitter-icon"
              alt="Twitter icon"
              src="/img/signup/twitter-icon.png"
            />
          </a>
          <img
            className="footer-divivder"
            alt="Footer divivder"
            src="/img/signup/upper-divider.svg"
          />
        </footer>
      </div>
    </div>
  );
};

export default Signup;
