import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

import ChatBot from './ChatBot/ChatBot'
import Home from './Home/Home'

const App = () => {
    return (
        <BrowserRouter>
            {/* <Home /> */}
            <Routes>
                <Route path='/' element={Home} />
                <Route path='/chatbot' element={ChatBot} />
            </Routes>
        </BrowserRouter>
    )
}

export default App