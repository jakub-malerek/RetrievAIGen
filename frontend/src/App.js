import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './App.css';
import { FaRobot } from 'react-icons/fa';
import InfoTiles from './InfoTiles';

function App() {
    const [question, setQuestion] = useState('');
    const [chatHistory, setChatHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [persona, setPersona] = useState('technical');
    const [personaLocked, setPersonaLocked] = useState(false);
    const [sessionId, setSessionId] = useState(null);
    const [sessions, setSessions] = useState([]);
    const [isSessionClosed, setIsSessionClosed] = useState(false);
    const [feedbackPromptCount, setFeedbackPromptCount] = useState(0);
    const [showFeedbackModal, setShowFeedbackModal] = useState(false);
    const [feedbackThreshold, setFeedbackThreshold] = useState(getRandomThreshold());
    const [postFeedbackMessageCount, setPostFeedbackMessageCount] = useState(0);
    const [showInfoTiles, setShowInfoTiles] = useState(true);
    const [infoTilesVisible, setInfoTilesVisible] = useState(true);

    function getRandomThreshold() {
        return Math.floor(Math.random() * 4) + 4;
    }

    useEffect(() => {
        startNewChat();
    }, []);

    useEffect(() => {
        if (!showInfoTiles) {
            const timer = setTimeout(() => setInfoTilesVisible(false), 500);
            return () => clearTimeout(timer);
        }
    }, [showInfoTiles]);

    const startNewChat = async () => {
        if (sessionId && chatHistory.length > 0) {
            saveCurrentSession();
        }

        setChatHistory([]);
        setIsSessionClosed(false);
        setPersonaLocked(false);
        setFeedbackPromptCount(0);
        setShowFeedbackModal(false);
        setFeedbackThreshold(getRandomThreshold());
        setPostFeedbackMessageCount(0);
        setShowInfoTiles(true);
        setInfoTilesVisible(true);

        try {
            const response = await axios.post('http://127.0.0.1:8000/start_session', {
                persona,
                session_id: sessionId, // Include the current sessionId
            });
            setSessionId(response.data.session_id);
        } catch (error) {
            alert('Failed to start a new chat session.');
        }
    };

    const saveCurrentSession = () => {
        setSessions((prevSessions) => {
            const sessionExists = prevSessions.some((s) => s.sessionId === sessionId);
            if (sessionExists) {
                return prevSessions;
            } else {
                return [...prevSessions, { sessionId, persona }];
            }
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!question.trim()) return;
        if (!sessionId) return alert('Please start a new chat session.');

        if (!personaLocked) setPersonaLocked(true);
        setShowInfoTiles(false);
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
            setChatHistory((prev) => [...prev, { role: 'bot', content: response.data.response }]);
            handleFeedbackPrompt();
        } catch {
            setChatHistory((prev) => [...prev, { role: 'bot', content: 'An error occurred.' }]);
        } finally {
            setLoading(false);
        }
    };

    const handleFeedbackPrompt = () => {
        setFeedbackPromptCount((count) => count + 1);
        if (feedbackPromptCount + 1 >= feedbackThreshold) {
            setShowFeedbackModal(true);
            setPostFeedbackMessageCount(0);
        } else if (showFeedbackModal) {
            setPostFeedbackMessageCount((count) => count + 1);
            if (postFeedbackMessageCount + 1 >= 2) {
                setShowFeedbackModal(false);
            }
        }
    };

    const handleFeedbackSubmit = async (rating) => {
        try {
            await axios.post('http://127.0.0.1:8000/feedback', { sessionId, rating });
            setShowFeedbackModal(false);
            setFeedbackPromptCount(0);
            setFeedbackThreshold(getRandomThreshold());
        } catch {
            alert('Failed to submit feedback.');
        }
    };

    const loadSession = async (session) => {
        if (sessionId && sessionId !== session.sessionId && chatHistory.length > 0) {
            saveCurrentSession();
        }

        try {
            const response = await axios.get(`http://127.0.0.1:8000/history/${session.sessionId}`);
            setChatHistory(response.data.map((msg) => ({ role: msg.role, content: msg.content })));
        } catch (error) {
            alert('Failed to load chat history.');
            return;
        }

        setSessionId(session.sessionId);
        setPersona(session.persona);
        setPersonaLocked(true);
        setIsSessionClosed(true);
        setShowFeedbackModal(false);

        // Hide info tiles when loading a historical chat
        setShowInfoTiles(false);
        setInfoTilesVisible(false);
    };

    return (
        <div className="App">
            <nav className="navbar">
                <FaRobot className="logo" />
                <h1 className="navbar-title">Tech Bot</h1>
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
                                Chat {index + 1} - {session.persona === 'technical' ? 'Tech' : 'Non-Tech'}
                            </div>
                        ))}
                    </div>
                </div>
                <div className="chat-section">
                    <div className="top-section-container">
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
                        {infoTilesVisible && (
                            <div className={`info-tiles ${showInfoTiles ? '' : 'slide-up'}`}>
                                <InfoTiles />
                            </div>
                        )}
                    </div>
                    <div className={`chat-window ${!infoTilesVisible ? 'no-top-padding' : ''}`}>
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
                {showFeedbackModal && (
                    <FeedbackModal
                        onSubmit={handleFeedbackSubmit}
                        closeModal={() => setShowFeedbackModal(false)}
                    />
                )}
            </div>
        </div>
    );
}

function FeedbackModal({ onSubmit, closeModal }) {
    const [selectedRating, setSelectedRating] = useState(null);

    const handleRatingSelect = (rating) => {
        setSelectedRating(rating);
        onSubmit(rating);
    };

    useEffect(() => {
        if (selectedRating !== null) {
            const timer = setTimeout(closeModal, 2000);
            return () => clearTimeout(timer);
        }
    }, [selectedRating, closeModal]);

    return (
        <div className="feedback-modal">
            <p>How do you like the conversation so far?</p>
            <div className="feedback-options">
                {[1, 2, 3, 4, 5].map((rating) => (
                    <button
                        key={rating}
                        onClick={() => handleRatingSelect(rating)}
                        className={selectedRating === rating ? 'selected' : ''}
                    >
                        {rating}
                    </button>
                ))}
            </div>
        </div>
    );
}

export default App;
