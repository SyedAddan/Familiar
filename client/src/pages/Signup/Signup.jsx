import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { ensureCsrfToken } from "../../api";
import { SiteFrame } from "../../components/SiteLayout";

const initialProfile = {
  avatarName: "",
  relationship: "",
  gender: "neutral",
  additional: "",
};

const Signup = () => {
  const [step, setStep] = useState(1);
  const [profile, setProfile] = useState(initialProfile);
  const [account, setAccount] = useState({
    email: "",
    username: "",
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const updateProfile = (event) => {
    setProfile((current) => ({ ...current, [event.target.name]: event.target.value }));
  };
  const updateAccount = (event) => {
    setAccount((current) => ({ ...current, [event.target.name]: event.target.value }));
  };

  const submitSignup = async (event) => {
    event.preventDefault();
    if (step === 1) {
      setError("");
      setStep(2);
      return;
    }
    if (account.password !== account.confirmPassword) {
      setError("Those passwords don’t match yet.");
      return;
    }

    setSubmitting(true);
    setError("");
    try {
      await ensureCsrfToken();
      await api.post("/signupInputs", {
        ...profile,
        ...account,
      });
      navigate("/chat");
    } catch (requestError) {
      setError(
        requestError.response?.status === 409
          ? "That email or username is already in use. Try signing in instead."
          : requestError.response?.data?.detail ||
            "We couldn’t create your space. Check your connection and try again."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <SiteFrame active="/signup" className="auth-page signup-page">
      <main className="auth-layout auth-layout-single">
        <section className="auth-card signup-card">
          <div className="signup-progress">
            <div><span className={step === 1 ? "progress-number active" : "progress-number complete"}>{step > 1 ? "✓" : "01"}</span><span>Companion</span></div>
            <span className="progress-line"><i className={step === 2 ? "filled" : ""} /></span>
            <div><span className={`progress-number ${step === 2 ? "active" : ""}`}>02</span><span>Your account</span></div>
          </div>
          <div className="auth-card-heading">
            <h1>{step === 1 ? "Your companion" : "Your account"}</h1>
          </div>
          <form className="auth-form" onSubmit={submitSignup}>
            {step === 1 ? (
              <>
                <label className="field-label" htmlFor="avatarNameInput">What should we call them?</label>
                <input
                  autoFocus
                  id="avatarNameInput"
                  maxLength={80}
                  name="avatarName"
                  onChange={updateProfile}
                  placeholder="A name that feels familiar"
                  required
                  value={profile.avatarName}
                />
                <label className="field-label" htmlFor="relationshipInput">How would you like them to show up?</label>
                <input
                  id="relationshipInput"
                  maxLength={1024}
                  name="relationship"
                  onChange={updateProfile}
                  placeholder="A supportive friend, a thoughtful listener…"
                  required
                  value={profile.relationship}
                />
                <label className="field-label" htmlFor="genderInput">Avatar voice style</label>
                <select id="genderInput" name="gender" onChange={updateProfile} value={profile.gender}>
                  <option value="neutral">Neutral</option>
                  <option value="F">Feminine</option>
                  <option value="M">Masculine</option>
                </select>
                <label className="field-label" htmlFor="additionalInput">Anything else they should know? <span>Optional</span></label>
                <textarea
                  id="additionalInput"
                  maxLength={1024}
                  name="additional"
                  onChange={updateProfile}
                  placeholder="A little context, your interests, or what matters to you"
                  rows={3}
                  value={profile.additional}
                />
              </>
            ) : (
              <>
                <label className="field-label" htmlFor="emailInput">Email</label>
                <input
                  autoComplete="email"
                  autoFocus
                  id="emailInput"
                  name="email"
                  onChange={updateAccount}
                  placeholder="you@example.com"
                  required
                  type="email"
                  value={account.email}
                />
                <label className="field-label" htmlFor="usernameInput">Choose a username</label>
                <input
                  autoComplete="username"
                  id="usernameInput"
                  maxLength={80}
                  name="username"
                  onChange={updateAccount}
                  placeholder="How you’ll sign in"
                  required
                  value={account.username}
                />
                <div className="field-row">
                  <div>
                    <label className="field-label" htmlFor="passwordInput">Password</label>
                    <input
                      autoComplete="new-password"
                      id="passwordInput"
                      minLength={8}
                      name="password"
                      onChange={updateAccount}
                      placeholder="At least 8 characters"
                      required
                      type="password"
                      value={account.password}
                    />
                  </div>
                  <div>
                    <label className="field-label" htmlFor="confirmPasswordInput">Confirm</label>
                    <input
                      autoComplete="new-password"
                      id="confirmPasswordInput"
                      minLength={8}
                      name="confirmPassword"
                      onChange={updateAccount}
                      placeholder="Type it again"
                      required
                      type="password"
                      value={account.confirmPassword}
                    />
                  </div>
                </div>
              </>
            )}
            {error && <p className="form-error" role="alert">{error}</p>}
            <div className="signup-actions">
              {step === 2 && (
                <button className="button button-quiet" onClick={() => { setError(""); setStep(1); }} type="button">
                  <span aria-hidden="true">←</span> Back
                </button>
              )}
              <button className="button button-primary auth-submit" disabled={submitting} type="submit">
                {submitting ? "Making your space…" : step === 1 ? "Continue" : "Create your space"}
                <span aria-hidden="true">→</span>
              </button>
            </div>
          </form>
        </section>
      </main>
    </SiteFrame>
  );
};

export default Signup;
