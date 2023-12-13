import React, { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";

import "mdb-react-ui-kit/dist/css/mdb.min.css";
import "@fortawesome/fontawesome-free/css/all.min.css";

import {
  PiPaperPlaneTiltBold,
  PiMicrophoneBold,
  PiStopCircleBold,
} from "react-icons/pi";

import "./style.css";



const ChatBot = () => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [userName, setUserName] = useState("");
  const [avatarName, setAvatarName] = useState("");
  const [avatarRelation, setAvatarRelation] = useState("");
  const [avatarAdditional, setAvatarAdditional] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [audioContext, setAudioContext] = useState(null);
  const messageContainerRef = useRef(null);
  const audioStreamRef = useRef(null);
  const mediaRecorderRef = useRef(null);


  const getStartupStuff = (e) => {
    localStorage.setItem("userName", "syedaddan")
    setUserName(localStorage.getItem("userName"))
    axios
      .get('/getUser', {
        params: {
          userName: userName
        }
      })
      .then((response) => {
        console.log(response.data);
        setAvatarName(response.data.avatarName);
        setAvatarRelation(response.data.relationship);
        setAvatarAdditional(response.data.additional);
      })
      .catch((error) => {
        console.error("Error fetching user data:", error);
      });
  }

  const initializeAudioContext = () => {
    const context = new (window.AudioContext || window.webkitAudioContext)();
    setAudioContext(context);
  };


  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  const handleSendMessage = async () => {
    if (input.trim() === "") return;
    const userMessage = { text: input, type: "user" };
    addMessage(userMessage);
    setInput("");
    await getResponse(input, avatarName, avatarRelation, avatarAdditional);
  };

  const addMessage = (message) => {
    console.log(message);
    setMessages((prevMessages) => [...prevMessages, message]);
  };

  const getResponse = async (message, avatarName, avatarRelation, avatarAdditional) => {
    await axios
      .post(`/chatbot`, { message: message, userName: userName, avatarName: avatarName, avatarRelation: avatarRelation, avatarAdditional: avatarAdditional })
      .then((response) => {
        const arrayBuffer = response.audio.arrayBuffer();
        const audioBuffer = audioContext.decodeAudioData(arrayBuffer);
        const chatbotResponse = {
          text: response.data.responseText,
          type: "bot",
        };

        const source = audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(audioContext.destination);
        source.start();

        addMessage(chatbotResponse);
      })
      .catch((error) => {
        const botResponse = {
          text: "Sorry, something went wrong.",
          type: "bot",
        };
        addMessage(botResponse);
        console.error("Error fetching chatbot response:", error);
      });
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
    // Check if the user's browser supports audio recording
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert("Audio recording is not supported in this browser.");
      return;
    }

    // Request access to the user's microphone
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then((stream) => {
        audioStreamRef.current = stream;

        // Create a MediaRecorder to record audio
        const mediaRecorder = new MediaRecorder(stream);

        // Handle audio data when available
        mediaRecorder.ondataavailable = handleAudioData;

        // Start recording
        mediaRecorder.start();

        // Store the MediaRecorder instance
        mediaRecorderRef.current = mediaRecorder;
      })
      .catch((error) => {
        console.error("Error accessing microphone:", error);
      });
  };

  const stopRecording = () => {
    // Stop recording
    mediaRecorderRef.current.stop();

    // Release the microphone
    audioStreamRef.current.getTracks().forEach((track) => {
      track.stop();
    });
  };

  const handleAudioData = (event) => {
    // Handle audio data (transcription or playback)
    const audioBlob = event.data;

    axios
      .post(
        `/stt`,
        { audio: audioBlob },
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      )
      .then((response) => {
        console.log(response.data);
        const sttText = { text: response.data.text, type: "user" };
        addMessage(sttText);
        getResponse(sttText.text, avatarName, avatarRelation, avatarAdditional);
      })
      .catch((error) => {
        console.error("Error fetching STT response:", error);
        const sttText = {
          text: "Sorry, something went wrong.",
          type: "user",
        };
        addMessage(sttText);
        const botText = {
          text: "Sorry, something went wrong.",
          type: "bot",
        };
        addMessage(botText);
      });
  };

  useEffect(() => {
    if (messageContainerRef.current) {
      messageContainerRef.current.scrollTop =
        messageContainerRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    getStartupStuff();
    initializeAudioContext();
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
        <div className="chatbot-body">
          <div className="chatbot-content">
            <div className="avatar-section">
              <img className="avatar" src="/img/Familiar-v4.png" alt="avatar" />
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
              type="text"
              placeholder="Type a message..."
              value={input}
              onChange={handleInputChange}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSendMessage();
              }}
            />
            <button className="send-button" onClick={handleSendMessage}>
              <PiPaperPlaneTiltBold />
            </button>
            <button
              className={`record-button ${isRecording ? "recording" : ""}`}
              onClick={handleToggleRecording}
            >
              {isRecording ? <PiStopCircleBold /> : <PiMicrophoneBold />}
            </button>
          </div>
        </div>
      <footer className="chatbot-footer">©️ 2023 Familiar</footer>
    </div>
  );
};

export default ChatBot;
