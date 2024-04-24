/* global webkitSpeechRecognition */
import axios from "axios";
import { Link } from "react-router-dom";
import React, { useState, useRef, useEffect } from "react";
import { TalkingHead } from "./utils/talkinghead.mjs";

import "mdb-react-ui-kit/dist/css/mdb.min.css";
import "@fortawesome/fontawesome-free/css/all.min.css";

import {
  PiPaperPlaneTiltBold,
  PiMicrophoneBold,
  PiStopCircleBold,
  PiXCircleBold,
  PiXFill,
} from "react-icons/pi";

import "./style.css";

let avatar;

const ChatBot = () => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const messageContainerRef = useRef(null);

  let loggedIn = sessionStorage.getItem("loggedIn");
  let recognition = new webkitSpeechRecognition();

  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = "en-US";

  const clearMessages = () => {
    if (
      window.confirm(
        "Are you sure you want to clear all messages? (This will not clear chat history)"
      )
    ) {
      setMessages([]);
    }
  };

  const clearHistory = async () => {
    if (
      window.confirm(
        "Are you sure you want to clear all chat history? (This will clear the database of all messages of current user)"
      )
    ) {
      setMessages([]);
      const userName = sessionStorage.getItem("username");
      await axios
        .post(`/clearHistory`, {
          userName: userName,
        })
        .then((response) => {
          console.log(response);
        })
        .catch((error) => {
          console.error("Error clearing chat history:", error);
        });
    }
  };

  const populateMessages = (dbMessages) => {
    const newMessages = dbMessages.map((message) => {
      return {
        text: message.content,
        type: message.role,
      };
    });
    setMessages(newMessages);
  };

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  const handleSendMessage = async () => {
    if (input.trim() === "") return;
    const userMessage = { text: input, type: "user" };
    addMessage(userMessage);
    setInput("");
    await getResponse(input);
  };

  const getResponse = async (message) => {
    const userName = sessionStorage.getItem("username");
    await axios
      .post(`/chatbot`, {
        message: message,
        userName: userName,
      })
      .then((response) => {
        const chatbotResponse = {
          text: response.data.responseText,
          type: "bot",
        };
        addMessage(chatbotResponse);
        avatar.speakText(response.data.responseText);
      })
      .catch((error) => {
        const botResponse = {
          text: "Sorry, something went wrong.",
          type: "bot",
        };
        addMessage(botResponse);
        console.error("Error fetching chatbot response:", error);
        avatar.speakText(
          "Hmmmmm... It seems like the language model powering me is having problems. I'm sorry about that."
        );
      });
  };

  const addMessage = (message) => {
    setMessages((prevMessages) => [...prevMessages, message]);
  };

  const handleToggleRecording = () => {
    if (!isRecording) {
      startRecording();
    } else {
      stopRecording();
    }
    setIsRecording(!isRecording);
  };

  const startRecording = () => {
    // Check if the user's browser supports SpeechRecognition
    if (!window.webkitSpeechRecognition) {
      alert("Speech recognition is not supported in this browser.");
      return;
    }

    recognition.start();

    recognition.onresult = handleSpeechResult;

    recognition.onerror = handleSpeechError;

    recognition.onspeechend = handleSpeechEnd;
  };

  const stopRecording = () => {
    if (recognition) {
      recognition.stop();
    }
  };

  const handleSpeechResult = (event) => {
    const transcript = Array.from(event.results)
      .map((result) => result[0].transcript)
      .join("");

    setInput(transcript);
  };

  const handleSpeechError = (event) => {
    console.error("Speech recognition error:", event.error);
    alert("Speech recognition error occurred. Please try again: ", event.error);
  };

  const handleSpeechEnd = (event) => {
    console.log(event);
    setIsRecording(false);
    stopRecording();
  };

  useEffect(() => {
    if (messageContainerRef.current) {
      messageContainerRef.current.scrollTop =
        messageContainerRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    const getAvatar = async () => {
      if (avatar) {
        return
      }

      // Instantiate the class
      const nodeAvatar = document.getElementById("avatar");
      avatar = new TalkingHead(nodeAvatar, {
        ttsEndpoint:
          "https://texttospeech.googleapis.com/v1beta1/text:synthesize",
        ttsApikey: process.env.REACT_APP_GOOGLE_API_KEY,
        cameraView: "head",
      });

      // Load and show the avatar
      const userName = sessionStorage.getItem("username");
      try {
        await avatar.showAvatar({
          url: `/avatars/${userName}_Ryan_avatar.glb`,
          avatarMood: "neutral",
          ttsLang: "en-US",
          ttsVoice: "en-US-Casual-K",
          lipsyncLang: "en",
        });
        console.log("Avatar fully loaded!");
      } catch (error) {
        console.log(error);
      }
    };
    getAvatar();
  }, []);

  useEffect(() => {
    const getStartupStuff = async (e) => {
      const userName = sessionStorage.getItem("username");
      axios
        .post(`/getUser`, {
          userName: userName,
        })
        .then((response) => {
          if (response.data.messages.length > 0) {
            sessionStorage.setItem("avatarID", response.data.avatarID);
            sessionStorage.setItem("avatarGender", response.data.avatarGender);
            populateMessages(response.data.messages);
          }
        })
        .catch((error) => {
          console.error("Error fetching user data:", error);
        });
    };
    getStartupStuff();
  }, []);

  return (
    <div className="chatbot">
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
            {loggedIn ? (
              <Link to="/login">
                <div className="login-selection">
                  <div className="overlap-group">
                    <div className="login-button" />
                    <div className="text-wrapper">Logout</div>
                  </div>
                </div>
              </Link>
            ) : (
              <div className="login-selection">
                <div className="overlap-group">
                  <div className="login-button" />
                  <div className="text-wrapper">Login</div>
                </div>
              </div>
            )}
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
      {loggedIn ? (
        <div className="chatbot-body">
          <div className="chatbot-content">
            <div className="avatar-section">
              <div id="avatar" />
            </div>
            <div className="transcript-section" ref={messageContainerRef}>
              {messages.map((message, index) => (
                <div key={index} className={`message ${message.type}`}>
                  {message.text}
                </div>
              ))}
            </div>
          </div>
          <div className="chatbot-input">
            <input
              id="chatbot-input"
              type="text"
              placeholder="Type a message..."
              value={input}
              onChange={handleInputChange}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSendMessage();
              }}
            />
            <button className="clear-history-button" onClick={clearHistory}>
              <PiXFill />
            </button>
            <button className="clear-messages-button" onClick={clearMessages}>
              <PiXCircleBold />
            </button>
            <button
              className={`record-button ${isRecording ? "recording" : ""}`}
              onClick={handleToggleRecording}
            >
              {isRecording ? <PiStopCircleBold /> : <PiMicrophoneBold />}
            </button>
            <button className="send-button" onClick={handleSendMessage}>
              <PiPaperPlaneTiltBold />
            </button>
          </div>
        </div>
      ) : (
        <div className="content">
          <div className="text-wrapper-3">
            Please <Link to={"/login"}>Log In!</Link>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatBot;
