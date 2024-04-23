/* global webkitSpeechRecognition */
import axios from "axios";
import { Link } from "react-router-dom";
import React, { useState, useRef, useEffect } from "react";

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

const ChatBot = () => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const messageContainerRef = useRef(null);
  const [video, setVideo] = useState(null);
  const [avatarImage, setAvatarImage] = useState(null);

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
      await axios
        .post(`/clearHistory`, {
          userName: "syedaddan",
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

  const getStartupStuff = async (e) => {
    const userName = sessionStorage.getItem("username");
    axios
      .post(`/getUser`, {
        userName: userName,
      })
      .then((response) => {
        if (response.data.messages.length > 0) {
          populateMessages(response.data.messages);
          setAvatarImage(`/avatars/${response.data.username}_${response.data.avatarName}_avatar.png`)
        }
      })
      .catch((error) => {
        console.error("Error fetching user data:", error);
      });
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

  const addMessage = (message) => {
    console.log(message);
    setMessages((prevMessages) => [...prevMessages, message]);
  };

  const getResponse = async (message) => {
    await axios
      .post(`/chatbot`, {
        message: message,
        userName: "syedaddan",
      })
      .then((response) => {
        const avatarResponse = response.data.reponseAvatar
        setVideo(avatarResponse)
        setAvatarImage(null)
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

  // const startRecording = () => {
  //   // Check if the user's browser supports audio recording
  //   if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
  //     alert("Audio recording is not supported in this browser.");
  //     return;
  //   }

  //   // Request access to the user's microphone
  //   navigator.mediaDevices
  //     .getUserMedia({ audio: true })
  //     .then((stream) => {
  //       audioStreamRef.current = stream;

  //       // Create a MediaRecorder to record audio
  //       const mediaRecorder = new MediaRecorder(stream);

  //       // Handle audio data when available
  //       mediaRecorder.ondataavailable = handleAudioData;

  //       // Start recording
  //       mediaRecorder.start();

  //       // Store the MediaRecorder instance
  //       mediaRecorderRef.current = mediaRecorder;
  //     })
  //     .catch((error) => {
  //       console.error("Error accessing microphone:", error);
  //     });
  // };

  // const stopRecording = () => {
  //   // Stop recording
  //   mediaRecorderRef.current.stop();

  //   // Release the microphone
  //   audioStreamRef.current.getTracks().forEach((track) => {
  //     track.stop();
  //   });
  // };

  // const handleAudioData = (event) => {
  //   // Handle audio data (transcription or playback)
  //   const audioBlob = event.data;

  //   axios
  //     .post(
  //       `/stt`,
  //       { audio: audioBlob },
  //       {
  //         headers: {
  //           "Content-Type": "multipart/form-data",
  //         },
  //       }
  //     )
  //     .then((response) => {
  //       console.log(response.data);
  //       const sttText = { text: response.data.text, type: "user" };
  //       addMessage(sttText);
  //       getResponse(sttText.text);
  //     })
  //     .catch((error) => {
  //       console.error("Error fetching STT response:", error);
  //       const sttText = {
  //         text: "Sorry, something went wrong.",
  //         type: "user",
  //       };
  //       addMessage(sttText);
  //       const botText = {
  //         text: "Seems like your message wasn't send properly. Please, try again!.",
  //         type: "bot",
  //       };
  //       addMessage(botText);
  //     });
  // };

  useEffect(() => {
    if (messageContainerRef.current) {
      messageContainerRef.current.scrollTop =
        messageContainerRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
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
              {
                video ? (
                  <video controls>
                    <source src={video} type="video/mp4" />
                  </video>
                ) : (
                  <img className="avatar" src={avatarImage} alt="avatar"/>
                )
              }
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
