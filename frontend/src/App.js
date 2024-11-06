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

  // Check if response is structured with bullet points or headings
  const hasBulletPointsOrHeadings = (text) => {
    const pattern = /(^|\n)(\d+\.\s|-|\*\s|##\s)/;
    return pattern.test(text);
  };

  // Format the response based on structure
  const formatAnswer = () => {
    if (!answer) return null;

    if (hasBulletPointsOrHeadings(answer)) {
      return <ReactMarkdown className="formatted-list">{answer}</ReactMarkdown>;
    } else {
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
