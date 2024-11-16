import React from 'react';

function InfoTiles() {
    return (
        <div className="info-tiles">
            <div className="info-tile">
                <h3>Welcome to Tech Bot</h3>
                <p>Tech Bot is your go-to assistant for the latest technology news, programming insights, and more. Whether you're a seasoned developer or just starting out, Tech Bot helps you stay informed and improve your skills with up-to-date information and easy-to-understand explanations.</p>
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
                <p>Choose a persona that best fits your needs:</p>
                <ul>
                    <li><strong>Technical:</strong> Provides in-depth explanations with technical terms. Ideal for users with a background in technology and programming.</li>
                    <li><strong>Non-Technical:</strong> Offers simplified explanations for a broader audience. Perfect for those new to technology or looking for easy-to-understand information.</li>
                </ul>
            </div>
        </div>
    );
}

export default InfoTiles;
