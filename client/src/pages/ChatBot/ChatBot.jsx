import React, { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  MDBInput,
  MDBRow,
  MDBBtn,
} from "mdb-react-ui-kit";
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
  const [avatarName, setAvatarName] = useState("");
  const [avatarContext, setAvatarContext] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const messageContainerRef = useRef(null);
  const audioStreamRef = useRef(null);
  const mediaRecorderRef = useRef(null);


  const handleAvatarSubmissions = async (e) => {
    e.preventDefault();
    if (document.getElementById("avatarName").value === "") {
      return;
    }
    if (document.getElementById("avatarContext").value === "") {
      return;
    }
    console.log("Yo my dude")
    setAvatarName(document.getElementById("avatarName").value);
    setAvatarContext(document.getElementById("avatarContext").value);
    await axios.post(
      `/avatarInputs`, { avatarName: document.getElementById("avatarName").value, avatarContext: document.getElementById("avatarContext").value}
    ).then((response) => {
      console.log(response.data);
    }).catch((error) => {
      console.error("Error fetching avatar inputs:", error);
    });
  }


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

  const addMessage = (message) => {
    console.log(message);
    setMessages((prevMessages) => [...prevMessages, message]);
  };

  const getResponse = async (message) => {
    await axios
      .post(`/chatbot`, { message: message })
      .then((response) => {
        console.log(response.data);
        const chatbotResponse = {
          text: response.data.responseText,
          type: "bot",
        };
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
        getResponse(sttText.text);
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
      {avatarName === "" || avatarContext === "" ? (
        <div className="avatar-inputs">
          <form>
            <MDBRow>
              <MDBInput
                wrapperClass="mb-4"
                id="avatarName"
                label="Avatar Name"
                onSubmit={(e) => e.preventDefault()}
                onKeyDown={(e) => {if (e.key === "Enter") handleAvatarSubmissions(e)}}
              />
              <MDBInput wrapperClass="mb-4" id="avatarContext" textarea rows={4} label="Your Relationship with the Avatar..." onSubmit={(e) => e.preventDefault()} onKeyDown={(e) => {if (e.key === "Enter") handleAvatarSubmissions(e)}}
              />
              <MDBBtn
                type="submit"
                block
                onClick={(e) => handleAvatarSubmissions(e)}
                onSubmit={(e) => handleAvatarSubmissions(e)}
              >
                Chat
              </MDBBtn>
            </MDBRow>
          </form>
        </div>
      ) : (
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
      )}
      <footer className="chatbot-footer">©️ 2023 Familiar</footer>
    </div>
  );
};

export default ChatBot;
