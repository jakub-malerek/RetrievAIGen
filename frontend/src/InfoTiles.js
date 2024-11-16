import React from 'react';

function InfoTiles() {
    return (
        <div className="info-tiles">
            <div className="info-tile">
                <h3>Welcome to Tech Bot</h3>
                <p>This is a specialized chatbot for technology news, programming, and related topics. Stay updated with the latest trends in tech.</p>
            </div>
            <div className="info-tile">
                <h3>Sample Prompts</h3>
                <ul>
                    <li>“Tell me the latest in AI advancements.”</li>
                    <li>“What are the trends in programming languages?”</li>
                    <li>“Explain cloud computing for a beginner.”</li>
                    <li>“How do I get started with data science?”</li>
                </ul>
            </div>
            <div className="info-tile">
                <h3>Persona Modes</h3>
                <p>Choose a persona:</p>
                <ul>
                    <li><strong>Technical:</strong> In-depth explanations and technical terms.</li>
                    <li><strong>Non-Technical:</strong> Simplified explanations for broader understanding.</li>
                </ul>
            </div>
        </div>
    );
}

export default InfoTiles;
