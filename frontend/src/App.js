import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './App.css';
import { FaRobot } from 'react-icons/fa';

function App() {
    const [question, setQuestion] = useState('');
    const [chatHistory, setChatHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [persona, setPersona] = useState('technical'); // Stores chosen persona for this session
    const [personaLocked, setPersonaLocked] = useState(false); // Locks persona once chat starts

    const startNewChat = () => {
        setChatHistory([]);
        setPersonaLocked(false); // Unlock persona selection for a new chat
    };

    const handleSubmit = async (e) => {
      e.preventDefault();
      if (!question.trim()) return;
  
      if (!personaLocked) setPersonaLocked(true); // Lock persona when chat starts
  
      const userMessage = { role: 'user', content: question };
      setChatHistory((prev) => [...prev, userMessage]);
      setQuestion('');
      setLoading(true);
  
      try {
          const response = await axios.post('http://127.0.0.1:8000/ask', {
              question,
              persona,            // Send the fixed persona with each question
              new_session: !personaLocked, // Set new_session to true only if the chat is just starting
          });
          const botMessage = {
              role: 'bot',
              content: response.data?.response || 'Unexpected response from the server.',
          };
          setChatHistory((prev) => [...prev, botMessage]);
      } catch (error) {
          console.error('Error fetching answer:', error);
          const errorMessage = { role: 'bot', content: 'An error occurred. Please try again.' };
          setChatHistory((prev) => [...prev, errorMessage]);
      } finally {
          setLoading(false);
      }
  };
  

    return (
        <div className="App">
            <nav className="navbar">
                <FaRobot className="logo" />
                <h1 className="navbar-title">TechNews Bot</h1>
            </nav>
            <div className="main-container">
                <div className="sidebar">
                    <button className="new-chat-btn" onClick={startNewChat}>+ New Chat</button>
                    <div className="chat-sessions">
                        <div className="chat-session">Chat 1</div>
                        <div className="chat-session">Chat 2</div>
                    </div>
                </div>
                <div className="chat-section">
                    {/* Persona Selection as Sliding Switch (disabled if personaLocked) */}
                    <div className={`persona-toggle ${personaLocked ? 'disabled' : ''}`}>
                        <span
                            className={`persona-option ${persona === 'technical' ? 'active' : ''}`}
                            onClick={() => !personaLocked && setPersona('technical')}
                        >
                            Technical
                        </span>
                        <span
                            className={`persona-option ${persona === 'non-technical' ? 'active' : ''}`}
                            onClick={() => !personaLocked && setPersona('non-technical')}
                        >
                            Non-Technical
                        </span>
                        <div className={`slider ${persona === 'technical' ? 'left' : 'right'}`} />
                    </div>

                    {/* Chat Window */}
                    <div className="chat-window">
                        {chatHistory.map((msg, index) => (
                            <div key={index} className={`message ${msg.role}`}>
                                <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                            </div>
                        ))}
                        {loading && <p className="loading">Loading...</p>}
                    </div>

                    {/* Input Area */}
                    <form onSubmit={handleSubmit} className="input-area">
                        <input
                            type="text"
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            placeholder="Ask me anything about tech news..."
                        />
                        <button type="submit">Send</button>
                    </form>
                </div>
            </div>
        </div>
    );
}

export default App;
