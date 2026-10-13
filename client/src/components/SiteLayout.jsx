import React, { useEffect, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import {
  FaBookOpen,
  FaCompass,
  FaDiscord,
  FaGithub,
  FaInstagram,
  FaMoon,
  FaSignOutAlt,
  FaSignInAlt,
  FaSun,
  FaUserPlus,
} from "react-icons/fa";

const randomBetween = (min, max) => min + Math.random() * (max - min);

function AmbientBlobs() {
  const [blobs] = useState(() => {
    const count = Math.floor(randomBetween(10, 15));
    const scale = Math.min(1, Math.max(0.38, window.innerWidth / 1200));
    const slots = Array.from({ length: 16 }, (_, index) => index);
    for (let index = slots.length - 1; index > 0; index -= 1) {
      const swapIndex = Math.floor(Math.random() * (index + 1));
      [slots[index], slots[swapIndex]] = [slots[swapIndex], slots[index]];
    }

    return slots.slice(0, count).map((slot, index) => ({
      id: slot,
      left: `${((slot % 4) + randomBetween(0.25, 0.75)) * 25}%`,
      top: `${(Math.floor(slot / 4) + randomBetween(0.25, 0.75)) * 25}%`,
      width: `${Math.round(randomBetween(170, 330) * scale)}px`,
      height: `${Math.round(randomBetween(140, 290) * scale)}px`,
      opacity: randomBetween(0.28, 0.48),
      rotation: `${Math.round(randomBetween(-35, 35))}deg`,
      color: index % 3,
    }));
  });

  return (
    <div aria-hidden="true" className="ambient-blobs">
      {blobs.map((blob) => (
        <span
          className={`ambient-blob ambient-blob-${blob.color}`}
          key={blob.id}
          style={{
            left: blob.left,
            top: blob.top,
            width: blob.width,
            height: blob.height,
            opacity: blob.opacity,
            transform: `translate(-50%, -50%) rotate(${blob.rotation})`,
          }}
        />
      ))}
    </div>
  );
}

const navigation = [
  { to: "/pricing", label: "Explore", Icon: FaCompass },
  { to: "/about", label: "Story", Icon: FaBookOpen },
];

export function ThemeToggle() {
  const [darkMode, setDarkMode] = useState(() => {
    const savedTheme = window.localStorage.getItem("familiar-theme");
    return savedTheme ? savedTheme === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  useEffect(() => {
    document.documentElement.dataset.theme = darkMode ? "dark" : "light";
  }, [darkMode]);

  const toggleTheme = () => {
    setDarkMode((current) => {
      const nextTheme = current ? "light" : "dark";
      window.localStorage.setItem("familiar-theme", nextTheme);
      return !current;
    });
  };

  return (
    <button
      aria-label={darkMode ? "Switch to light mode" : "Switch to dark mode"}
      className="theme-toggle"
      onClick={toggleTheme}
      title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
      type="button"
    >
      {darkMode ? <FaSun aria-hidden="true" /> : <FaMoon aria-hidden="true" />}
      <span className="sr-only">{darkMode ? "Switch to light mode" : "Switch to dark mode"}</span>
    </button>
  );
}

export function SiteHeader({ active, onLogout }) {
  return (
    <>
      <header className="site-header">
        <div className="site-header-inner">
          <Link aria-label="Familiar home" className="brand" to="/">
            <span>Familiar</span>
          </Link>
          <nav aria-label="Main navigation" className="site-nav">
            {navigation.map((item) => (
              <NavLink
                aria-label={item.label}
                key={item.to}
                className={active === item.to ? "site-nav-link is-active" : "site-nav-link"}
                to={item.to}
              >
                <item.Icon aria-hidden="true" className="nav-icon" />
                <span className="nav-label">{item.label}</span>
              </NavLink>
            ))}
          </nav>
          <div className="site-header-actions">
                {onLogout ? (
              <button aria-label="Log out" className="header-action" onClick={onLogout} type="button">
                <FaSignOutAlt aria-hidden="true" className="nav-icon" />
                <span className="nav-label">Log out</span>
              </button>
            ) : (
              <>
                {active !== "/login" && (
                  <Link aria-label="Log in" className="header-action" to="/login">
                    <FaSignInAlt aria-hidden="true" className="nav-icon" />
                    <span className="nav-label">Log in</span>
                  </Link>
                )}
                {active !== "/signup" && (
                  <Link aria-label="Get started" className="header-action header-action-primary" to="/signup">
                    <FaUserPlus aria-hidden="true" className="nav-icon" />
                    <span className="nav-label">Sign up</span>
                  </Link>
                )}
              </>
            )}
          </div>
        </div>
      </header>
      <ThemeToggle />
    </>
  );
}

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <Link aria-label="Familiar home" className="brand" to="/">
        <span>Familiar</span>
      </Link>
      <div className="footer-socials" aria-label="Social accounts">
        <span aria-label="Instagram — link coming soon" role="img" title="Instagram">
          <FaInstagram aria-hidden="true" />
        </span>
        <span aria-label="GitHub — link coming soon" role="img" title="GitHub">
          <FaGithub aria-hidden="true" />
        </span>
        <span aria-label="Discord — link coming soon" role="img" title="Discord">
          <FaDiscord aria-hidden="true" />
        </span>
      </div>
      <small>© Familiar 2026</small>
    </footer>
  );
}

export function SiteFrame({ active, children, className = "" }) {
  return (
    <div className={`site-frame ${className}`}>
      <SiteHeader active={active} />
      <AmbientBlobs />
      {children}
      <SiteFooter />
    </div>
  );
}
