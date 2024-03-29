import React from "react";
import { Link } from "react-router-dom";

import "./style.css";

// const handleInputs = async () => {
//   const username = document.getElementById("usernameInput").value;
//   const password = document.getElementById("passwordInput").value;

//   await axios
//     .post(
//       "/loginInputs",
//       {
//         username: username,
//         password: password,
//       },
//       {
//         headers: {
//           "Content-Type": "application/json",
//         },
//       }
//     )
//     .then((response) => {
//       console.log("Server response:", response);
//       window.location.href = "/chat";
//     }).catch((error) => {
//       console.log("Error:", error);
//     });
// };


const Login = () => {
  return (
    <div className="login">
      <div className="div">
        <footer className="footer">
          <div className="copyright-text">© Familiar 2023</div>
          <a href="/login">
            <img
              className="facebook-icon"
              alt="Facebook icon"
              src="/img/login/facebook-icon.png"
            />
          </a>
          <a href="/login">
            <img
              className="instagram-icon"
              alt="Instagram icon"
              src="/img/login/instagram-icon.svg"
            />
          </a>
          <a href="/login">
            <img
              className="twitter-icon"
              alt="Twitter icon"
              src="/img/login/twitter-icon.png"
            />
          </a>
          <img
            className="footer-divivder"
            alt="Footer divivder"
            src="/img/login/upper-divider.svg"
          />
        </footer>
        <div className="content">
          <Link to="/signup">
            <div className="text-wrapper">New here? Sign Up</div>
          </Link>
          <Link to="/404">
            <div className="text-wrapper-2">Forgot Password?</div>
          </Link>
          <div className="sign-in">
            <div className="overlap-group">
              <div className="sign-in-text">Sign In</div>
            </div>
          </div>
          <div className="password">
            <div className="overlap">
              <div className="text-wrapper-3">Password</div>
            </div>
          </div>
          <div className="email">
            <div className="overlap">
              <div className="text-wrapper-4">Email</div>
            </div>
          </div>
          <div className="text-wrapper-5">Sign In</div>
        </div>
        <header className="header">
          <div className="overlap-2">
            <img
              className="upper-divider"
              alt="Upper divider"
              src="/img/login/upper-divider.svg"
            />
            <Link to="/">
              <div className="familiar-logo">Familiar</div>
            </Link>
            <div className="nav-buttons">
              <Link to="/login">
                <div className="login-selection">
                  <div className="overlap-group-2">
                    <div className="login-button" />
                    <div className="text-wrapper-6">Login</div>
                  </div>
                </div>
              </Link>
              <Link to="/pricing">
                <div className="text-wrapper-7">Pricing</div>
              </Link>
              <Link to="/contact">
                <div className="text-wrapper-8">Contact</div>
              </Link>
              <Link to="/about">
                <div className="text-wrapper-9">About</div>
              </Link>
            </div>
          </div>
        </header>
      </div>
    </div>
  );
};

export default Login;
