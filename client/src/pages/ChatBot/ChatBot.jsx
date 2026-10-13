import React, { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PiArrowClockwiseBold, PiMicrophoneBold, PiPaperPlaneTiltBold, PiStopBold } from "react-icons/pi";
import { TalkingHead } from "./utils/talkinghead.mjs";
import api, { apiBaseUrl, ensureCsrfToken } from "../../api";
import { SiteFrame, SiteHeader, ThemeToggle } from "../../components/SiteLayout";

const suggestions = [
  "I’ve had a lot on my mind lately",
  "Help me make sense of a tough day",
  "I just want to talk for a bit",
];

const ChatBot = () => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [profile, setProfile] = useState(null);
  const [loadingProfile, setLoadingProfile] = useState(true);
  const [sending, setSending] = useState(false);
  const [recording, setRecording] = useState(false);
  const [canRecord, setCanRecord] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [error, setError] = useState("");
  const messageContainerRef = useRef(null);
  const avatarNodeRef = useRef(null);
  const avatarRef = useRef(null);
  const recognitionRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    let mounted = true;
    const loadProfile = async () => {
      try {
        await ensureCsrfToken();
        const response = await api.get("/getUser");
        if (!mounted) return;
        setProfile(response.data);
        setVoiceEnabled(response.data.speechEnabled);
        setMessages(
          response.data.messages.map((message) => ({
            text: message.content,
            type: message.role === "assistant" ? "bot" : "user",
          }))
        );
      } catch (requestError) {
        if (requestError.response?.status === 401) {
          setProfile(null);
        } else {
          setError("We couldn’t load your conversation. Check that the Familiar server is running.");
        }
      } finally {
        if (mounted) setLoadingProfile(false);
      }
    };
    loadProfile();
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (!profile || !avatarNodeRef.current || avatarRef.current) return undefined;
    const head = new TalkingHead(avatarNodeRef.current, {
      ttsEndpoint: `${apiBaseUrl}/tts`,
      cameraView: "head",
      cameraRotateEnable: false,
    });
    avatarRef.current = head;
    let mounted = true;
    head
      .showAvatar({
        url: `${apiBaseUrl}/avatars/${encodeURIComponent(profile.username)}_${encodeURIComponent(profile.avatarName)}.glb`,
        avatarMood: "happy",
        ttsLang: "en-US",
        lipsyncLang: "en",
      })
      .then(() => {
        if (mounted) setError("");
      })
      .catch(() => {
        if (mounted) setError("Your avatar couldn’t load. You can still chat while we look into it.");
      });
    return () => {
      mounted = false;
    };
  }, [profile]);

  useEffect(() => {
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) return undefined;
    const recognition = new Recognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";
    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0].transcript)
        .join("");
      setInput(transcript);
    };
    recognition.onerror = () => {
      setRecording(false);
      setError("Microphone input stopped. You can continue by typing.");
    };
    recognition.onend = () => setRecording(false);
    recognitionRef.current = recognition;
    setCanRecord(true);
    return () => recognition.stop();
  }, []);

  useEffect(() => {
    if (messageContainerRef.current) {
      messageContainerRef.current.scrollTop = messageContainerRef.current.scrollHeight;
    }
  }, [messages, sending]);

  const sendMessage = useCallback(async (text = input) => {
    const message = text.trim();
    if (!message || sending) return;
    setError("");
    setMessages((current) => [...current, { text: message, type: "user" }]);
    setInput("");
    setSending(true);
    try {
      const response = await api.post("/chatbot", { message });
      const reply = response.data.responseText;
      setMessages((current) => [...current, { text: reply, type: "bot" }]);
      if (voiceEnabled) {
        avatarRef.current?.speakText(reply);
      }
    } catch (requestError) {
      console.error("Unable to send chat message:", requestError);
      setError(
        requestError.response?.data?.detail ||
          "That didn’t go through. Check your connection and try again."
      );
    } finally {
      setSending(false);
    }
  }, [input, sending, voiceEnabled]);

  const clearHistory = async () => {
    if (!window.confirm("Clear this conversation from your account? This cannot be undone.")) return;
    try {
      await api.post("/clearHistory");
      setMessages([]);
      setError("");
    } catch (requestError) {
      console.error("Unable to clear chat history:", requestError);
      setError("We couldn’t clear your conversation. Please try again.");
    }
  };

  const toggleRecording = () => {
    if (!recognitionRef.current) return;
    if (recording) {
      recognitionRef.current.stop();
      return;
    }
    try {
      setError("");
      recognitionRef.current.start();
      setRecording(true);
    } catch {
      setError("Microphone is already listening. Try again in a moment.");
    }
  };

  const logout = async () => {
    try {
      await api.post("/logout");
      navigate("/");
    } catch (requestError) {
      console.error("Unable to log out:", requestError);
      setError("Couldn’t log out just yet. Please try again.");
    }
  };

  if (loadingProfile) {
    return (
      <>
        <main className="chat-loading">
          <span className="loading-orb" />
          <p>Opening your space…</p>
        </main>
        <ThemeToggle />
      </>
    );
  }

  if (!profile) {
    return (
      <SiteFrame className="chat-locked-frame">
        <main className="chat-locked">
          <div className="locked-card">
            <h1>{error ? "Conversation unavailable" : "Log in to continue."}</h1>
            {error && <p role="alert">{error}</p>}
            {error && (
              <button className="text-button" onClick={() => window.location.reload()} type="button">
                Try again
              </button>
            )}
          </div>
        </main>
      </SiteFrame>
    );
  }

  return (
    <div className="conversation-app">
      <SiteHeader active="/chat" onLogout={logout} />
      <main className="conversation-layout">
        <section className="avatar-stage">
          <div className="stage-topline">
            <div>
              <h1>{profile.avatarName}</h1>
            </div>
            <span className="stage-mood"><span className="status-pulse" /> Present</span>
          </div>
          <div className="avatar-scene">
            <span className="scene-orbit scene-orbit-one" />
            <span className="scene-orbit scene-orbit-two" />
            <img className="scene-sparkle scene-sparkle-one" src="/img/home/vector.svg" alt="" />
            <img className="scene-sparkle scene-sparkle-two" src="/img/home/vector-1.svg" alt="" />
            <div className="avatar-render" id="avatar" ref={avatarNodeRef} />
          </div>
          <div className="stage-controls">
            <div className="stage-control-copy">
              <span className="control-icon">♫</span>
              <span><strong>Spoken replies</strong><small>{!profile.speechEnabled ? "Voice setup needed" : voiceEnabled ? "Voice is on" : "Voice is off"}</small></span>
            </div>
            <button
              aria-pressed={voiceEnabled}
              className={`toggle-switch ${voiceEnabled ? "toggle-on" : ""}`}
              disabled={!profile.speechEnabled}
              onClick={() => setVoiceEnabled((enabled) => !enabled)}
              title={!profile.speechEnabled ? "Configure ElevenLabs in server/.env to enable speech" : undefined}
              type="button"
            >
              <span />
              <span className="sr-only">{voiceEnabled ? "Turn voice off" : "Turn voice on"}</span>
            </button>
          </div>
        </section>

        <section className="chat-panel">
          <div className="chat-panel-heading">
            <h2>Talk it out</h2>
            <button className="icon-button" onClick={clearHistory} title="Clear conversation" aria-label="Clear conversation">
              <PiArrowClockwiseBold />
            </button>
          </div>
          <div className="conversation-messages" ref={messageContainerRef} aria-live="polite">
            {messages.length === 0 ? (
              <div className="conversation-welcome">
                <span className="welcome-flower">✿</span>
                <p>What’s on your mind?</p>
                <div className="suggestion-list">
                  {suggestions.map((suggestion) => (
                    <button key={suggestion} onClick={() => sendMessage(suggestion)} type="button">
                      {suggestion}<span aria-hidden="true">↗</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="message-list">
                {messages.map((message, index) => (
                  <article className={`chat-message ${message.type}`} key={`${index}-${message.type}`}>
                    {message.type === "bot" && <span className="message-avatar" aria-hidden="true" />}
                    <div className="message-content">
                      <span className="message-sender">{message.type === "bot" ? profile.avatarName : "You"}</span>
                      <p>{message.text}</p>
                    </div>
                  </article>
                ))}
                {sending && (
                  <div className="chat-message bot typing-message" role="status">
                    <span className="message-avatar" aria-hidden="true" />
                    <div className="typing-dots"><span /><span /><span /><span className="sr-only">Familiar is replying</span></div>
                  </div>
                )}
              </div>
            )}
          </div>
          {error && <p className="chat-error" role="alert">{error}</p>}
          <form className="message-composer" onSubmit={(event) => { event.preventDefault(); sendMessage(); }}>
            <label className="sr-only" htmlFor="chat-message">Write a message</label>
            <textarea
              id="chat-message"
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  sendMessage();
                }
              }}
              placeholder="Share what’s on your mind…"
              rows={1}
              value={input}
            />
            <div className="composer-actions">
              <div>
                {canRecord && (
                  <button
                    aria-label={recording ? "Stop voice input" : "Start voice input"}
                    aria-pressed={recording}
                    className={`icon-button mic-button ${recording ? "is-recording" : ""}`}
                    onClick={toggleRecording}
                    type="button"
                  >
                    {recording ? <PiStopBold /> : <PiMicrophoneBold />}
                  </button>
                )}
                <button className="send-message-button" disabled={!input.trim() || sending} type="submit">
                  <span>{sending ? "Sending" : "Send"}</span><PiPaperPlaneTiltBold />
                </button>
              </div>
            </div>
          </form>
          <p className="chat-disclaimer">Familiar is an AI companion, not a substitute for professional care.</p>
        </section>
      </main>
    </div>
  );
};

export default ChatBot;
