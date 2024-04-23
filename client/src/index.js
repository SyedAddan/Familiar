import React from "react";
import ReactDOM from "react-dom/client";

// import "./index.css";

import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home/Home";
import ChatBot from "./pages/ChatBot/ChatBot";
import Contact from "./pages/Contact/Contact";
import Login from "./pages/Login/Login";
import Signup from "./pages/Signup/Signup";
import Pricing from "./pages/Pricing/Pricing";
import About from "./pages/About/About";
import NotFound from "./pages/404/404";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <BrowserRouter>
    <Routes>
      <Route path="/" exact element={<Home></Home>} />
      <Route path="/chat" exact element={<ChatBot></ChatBot>} />
      <Route path="/contact" exact element={<Contact></Contact>} />
      <Route path="/login" exact element={<Login></Login>} />
      <Route path="/signup" exact element={<Signup></Signup>} />
      <Route path="/pricing" exact element={<Pricing></Pricing>} />
      <Route path="/about" exact element={<About></About>} />
      <Route path="*" element={<NotFound></NotFound>} />
    </Routes>
  </BrowserRouter>
);
