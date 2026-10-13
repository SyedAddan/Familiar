import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { ensureCsrfToken } from "../../api";
import { SiteFrame } from "../../components/SiteLayout";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await ensureCsrfToken();
      await api.post("/loginInputs", { username, password });
      navigate("/chat");
    } catch (requestError) {
      setError(
        requestError.response?.status === 401
          ? "That username and password don’t match. Try again."
          : requestError.response?.data?.detail ||
            "We couldn’t sign you in. Check your connection and try again."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <SiteFrame active="/login" className="auth-page">
      <main className="auth-layout auth-layout-single">
        <section className="auth-card">
          <div className="auth-card-heading">
            <h1>Log in</h1>
          </div>
          <form className="auth-form" onSubmit={handleSubmit}>
            <label className="field-label" htmlFor="usernameInput">Username</label>
            <input
              autoComplete="username"
              id="usernameInput"
              onChange={(event) => setUsername(event.target.value)}
              placeholder="Your username"
              required
              value={username}
            />
            <label className="field-label" htmlFor="passwordInput">Password</label>
            <input
              autoComplete="current-password"
              id="passwordInput"
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Your password"
              required
              type="password"
              value={password}
            />
            {error && <p className="form-error" role="alert">{error}</p>}
            <button className="button button-primary auth-submit" disabled={submitting} type="submit">
              {submitting ? "Signing you in…" : "Log in"}
              <span aria-hidden="true">→</span>
            </button>
          </form>
        </section>
      </main>
    </SiteFrame>
  );
};

export default Login;
