import React from "react";
import { Link } from "react-router-dom";
import axios from "axios";

import "./style.css";

const handleInputs = () => {
  const audioInput = document.getElementById("voiceInput");
  const audioFile = audioInput.files[0];

  if (audioFile) {
    convertToAudioBlob(audioFile)
      .then((audioBlob) => {
        const formData = new FormData();
        formData.append("email", document.getElementById("emailInput").value);
        formData.append("username", document.getElementById("usernameInput").value);
        formData.append("avatarName", document.getElementById("avatarNameInput").value);
        formData.append("relationship", document.getElementById("relationshipInput").value);
        formData.append("additional", document.getElementById("additionalInput").value);
        formData.append("password", document.getElementById("passwordInput").value);
        formData.append("confirmPassword", document.getElementById("confirmPasswordInput").value);
        formData.append("voice", audioBlob, "voice.wav");
        sendToServer(formData);
      })
      .catch((err) => {
        console.error("Error converting to AudioBlob:", err);
      });
  }
};

function convertToAudioBlob(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = function () {
      const audioContext = new (window.AudioContext ||
        window.webkitAudioContext)();
      audioContext.decodeAudioData(reader.result, function (buffer) {
        const source = audioContext.createBufferSource();
        source.buffer = buffer;

        const scriptNode = audioContext.createScriptProcessor(4096, 1, 1);
        scriptNode.onaudioprocess = function (event) {
          const audioData = event.inputBuffer.getChannelData(0);
          const audioBlob = new Blob([audioData], { type: "audio/wav" });
          resolve(audioBlob);
        };

        source.connect(scriptNode);
        scriptNode.connect(audioContext.destination);
        source.start();
      });
    };

    reader.readAsArrayBuffer(file);
  });
}

const sendToServer = (formData) => {
  const config = {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  };
  axios
    .post("/signupInputs", formData, config)
    .then((response) => {
      console.log("Server response:", response.data);
      window.location.href = "/chat";
    })
    .catch((error) => {
      console.error("Error sending to server:", error);
    });
};

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
          <form
            id="sign-up-form"
            className="form"
            name="sign-up-form"
            method="post"
            onSubmit={(e) => {
              e.preventDefault();
              handleInputs();
            }}
          >
            <div className="email">
              <input
                id="emailInput"
                className="text-field-wrapper"
                placeholder="Email*"
                type="email"
                required
              />
            </div>
            <div className="username">
              <input
                id="usernameInput"
                className="text-field-wrapper"
                placeholder="Username*"
                type="text"
                required
              />
            </div>
            <div className="avatar-name">
              <input
                id="avatarNameInput"
                className="text-field-wrapper"
                placeholder="Avatar Name*"
                type="text"
                required
              />
            </div>
            <div className="relationship">
              <textarea
                id="relationshipInput"
                className="text-field-wrapper"
                placeholder="Relationship*"
                rows={3}
                style={{ resize: "none" }}
                required
              />
            </div>
            <div className="additional">
              <textarea
                id="additionalInput"
                className="text-field-wrapper"
                placeholder="Any additional details"
                rows={3}
                style={{ resize: "none" }}
              />
            </div>
            <div className="password">
              <input
                id="passwordInput"
                className="text-field-wrapper"
                placeholder="Password*"
                type="password"
                required
              />
            </div>
            <div className="confirm-password">
              <input
                id="confirmPasswordInput"
                className="text-field-wrapper"
                placeholder="Confirm Password*"
                type="password"
                required
              />
            </div>
            <div className="voice">
              <div className="overlap">
                <input
                  id="voiceInput"
                  className="text-field-wrapper"
                  placeholder="Voice of the Avatar*"
                  type="file"
                  accept="audio/*"
                  required
                />
              </div>
            </div>
            {/* <div className="image">
              <div className="overlap">
                <input
                  className="text-field-wrapper"
                  placeholder="Image of the Avatar*"
                  type="file"
                  required
                />
              </div>
            </div> */}
            <div className="overlap-group-wrapper">
              <button
                className="overlap-group"
                onClick={(e) => {
                  e.preventDefault();
                  handleInputs();
                }}
              >
                <div className="sign-up-text">Sign Up</div>
              </button>
            </div>
          </form>
          <Link to="/login">
            <p className="text-wrapper">Already have an account? Sign In</p>
          </Link>
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
