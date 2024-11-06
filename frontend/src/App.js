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

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    const userMessage = { role: 'user', content: question };
    setChatHistory((prev) => [...prev, userMessage]);
    setQuestion('');
    setLoading(true);

    try {
      const response = await axios.post('http://127.0.0.1:8000/ask', { question });
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
      <div className="chat-window">
        {chatHistory.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
          </div>
        ))}
        {loading && <p className="loading">Loading...</p>}
      </div>
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
  );
}

export default App;
