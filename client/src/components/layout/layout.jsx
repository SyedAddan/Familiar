import React from "react";
import { Link } from "react-router-dom";

import './layout.css'

const Layout = ({ children }) => {
  return (
    <div className="home">
      <div className="div">
        <div className="overlap">
          <div className="page-layout">
            <div className="page">
              <div className="familiar-logo">Familiar</div>
              <div className="nav-buttons">
                <div className="text-wrapper">
                  <Link to="/login">Login</Link>
                </div>
                <div className="text-wrapper-2">
                  <Link to="/pricing">Pricing</Link>
                </div>
                <div className="text-wrapper-3">
                  <Link to="/contact">Contact</Link>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div>{ children }</div>
      </div>
    </div>
  );
};

export default Layout;
