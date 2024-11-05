import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import './App.css';

function App() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) {
      setAnswer('Please enter a question.');
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post('http://127.0.0.1:8000/ask', { question });
      if (response.data && response.data.response) {
        setAnswer(response.data.response);
      } else {
        setAnswer('Unexpected response from the server.');
      }
    } catch (error) {
      console.error('Error fetching answer:', error);
      setAnswer('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Function to determine if the response is likely a bullet-point list
  const isBulletPointResponse = (text) => {
    // Check for common bullet point patterns (e.g., "1. ", "2. ", "- ", "* ")
    const bulletPointPattern = /(^|\n)(\d+\.\s|-|\*\s)/;
    return bulletPointPattern.test(text);
  };

  // Function to format the answer using react-markdown
  const formatAnswer = () => {
    if (!answer) return null;

    // Check dynamically if the answer contains bullet points
    if (isBulletPointResponse(answer)) {
      // Split by newlines before bullet points
      const items = answer
        .split(/\n(?=\d+\.\s|-|\*\s)/) // Adjust the regex to capture more bullet patterns
        .filter(item => item.trim() !== ""); // Remove empty items

      return (
        <ul className="formatted-list">
          {items.map((item, index) => (
            <li key={index}>
              <ReactMarkdown>{item.trim()}</ReactMarkdown>
            </li>
          ))}
        </ul>
      );
    } else {
      // Fallback to rendering as plain text
      return <ReactMarkdown className="formatted-text">{answer}</ReactMarkdown>;
    }
  };

  return (
    <div className="App">
      <h1>Chat with AI</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask me anything..."
        />
        <button type="submit">Send</button>
      </form>
      {loading ? <p>Loading...</p> : formatAnswer()}
    </div>
  );
}

export default App;
