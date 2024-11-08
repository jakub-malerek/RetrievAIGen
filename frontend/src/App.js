import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './App.css';
import { FaRobot } from 'react-icons/fa';

function App() {
    const [question, setQuestion] = useState('');
    const [chatHistory, setChatHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [persona, setPersona] = useState('technical');
    const [personaLocked, setPersonaLocked] = useState(false);
    const [sessionId, setSessionId] = useState(null);
    const [sessions, setSessions] = useState([]);
    const [isSessionClosed, setIsSessionClosed] = useState(false);

    // Start a new chat session when the component mounts
    useEffect(() => {
        startNewChat();
    }, []);

    const startNewChat = async () => {
        // Save the current session if it has chat history
        if (sessionId && chatHistory.length > 0) {
            setSessions((prevSessions) => {
                // Update the current session's data
                const sessionExists = prevSessions.some((s) => s.sessionId === sessionId);
                if (sessionExists) {
                    // Update existing session
                    return prevSessions.map((s) =>
                        s.sessionId === sessionId
                            ? { sessionId, chatHistory, persona }
                            : s
                    );
                } else {
                    // Add new session
                    return [...prevSessions, { sessionId, chatHistory, persona }];
                }
            });
        }

        setChatHistory([]); // Clear the chat history for the new session
        setIsSessionClosed(false); // New sessions are open by default
        setPersonaLocked(false); // Allow persona change for new session

        try {
            const payload = {
                persona: persona,
                session_id: sessionId, // Send the current session ID to close it
            };

            // Request backend to create a new session
            const response = await axios.post('http://127.0.0.1:8000/start_session', payload);

            // Set the new session ID and reset states for the new chat session
            setSessionId(response.data.session_id);
        } catch (error) {
            console.error('Error creating new chat session:', error);
            alert('Failed to start a new chat session. Please try again.');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!question.trim()) return;

        if (!sessionId) {
            alert('Please start a new chat session before sending messages.');
            return;
        }

        if (!personaLocked) setPersonaLocked(true);

        const userMessage = { role: 'user', content: question };
        setChatHistory((prev) => [...prev, userMessage]);
        setQuestion('');
        setLoading(true);

        try {
            const response = await axios.post('http://127.0.0.1:8000/ask', {
                question,
                persona,
                session_id: sessionId,
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

    const loadSession = (session) => {
        // Save the current session if it's different from the one being loaded
        if (sessionId && sessionId !== session.sessionId && chatHistory.length > 0) {
            setSessions((prevSessions) => {
                // Update the current session's data
                const sessionExists = prevSessions.some((s) => s.sessionId === sessionId);
                if (sessionExists) {
                    return prevSessions.map((s) =>
                        s.sessionId === sessionId
                            ? { sessionId, chatHistory, persona }
                            : s
                    );
                } else {
                    return [...prevSessions, { sessionId, chatHistory, persona }];
                }
            });
        }

        // Load the selected session
        setChatHistory(session.chatHistory);
        setSessionId(session.sessionId);
        setPersona(session.persona);
        setPersonaLocked(true); // Lock persona for loaded sessions

        // Mark the session as closed to disable input (since it's an old session)
        setIsSessionClosed(true);
    };

    return (
        <div className="App">
            <nav className="navbar">
                <FaRobot className="logo" />
                <h1 className="navbar-title">TechNews Bot</h1>
            </nav>
            <div className="main-container">
                <div className="sidebar">
                    <button className="new-chat-btn" onClick={startNewChat}>
                        + New Chat
                    </button>
                    <div className="chat-sessions">
                        {sessions.map((session, index) => (
                            <div
                                key={session.sessionId}
                                className="chat-session"
                                onClick={() => loadSession(session)}
                            >
                                Chat {index + 1} -{' '}
                                {session.persona === 'technical' ? 'Tech' : 'Non-Tech'}
                            </div>
                        ))}
                    </div>
                </div>
                <div className="chat-section">
                    <div className={`persona-toggle ${personaLocked ? 'disabled' : ''}`}>
                        <span
                            className={`persona-option ${persona === 'technical' ? 'active' : ''}`}
                            onClick={() => !personaLocked && setPersona('technical')}
                        >
                            Technical
                        </span>
                        <span
                            className={`persona-option ${
                                persona === 'non-technical' ? 'active' : ''
                            }`}
                            onClick={() => !personaLocked && setPersona('non-technical')}
                        >
                            Non-Technical
                        </span>
                        <div
                            className={`slider ${persona === 'technical' ? 'left' : 'right'}`}
                        />
                    </div>

                    <div className="chat-window">
                        {chatHistory.map((msg, index) => (
                            <div key={index} className={`message ${msg.role}`}>
                                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                    {msg.content}
                                </ReactMarkdown>
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
                            disabled={isSessionClosed}
                        />
                        <button type="submit" disabled={isSessionClosed}>
                            Send
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}

export default App;
