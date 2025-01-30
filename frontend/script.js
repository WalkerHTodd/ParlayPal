// Function to open the chat window
function openChat() {
    let chatBox = document.getElementById("chat-box");

    if (!chatBox) {
        chatBox = document.createElement("div");
        chatBox.id = "chat-box";
        chatBox.innerHTML = `
            <div class="chat-header">
                <span>💬 Live Bet Assistant</span>
                <button onclick="closeChat()">✖</button>
            </div>
            <div class="chat-body">
                <p>Ask me for a betting suggestion!</p>
                <div id="chat-messages"></div>
                <input type="text" id="chat-input" placeholder="Type a message..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">Send</button>
            </div>
        `;
        document.body.appendChild(chatBox);
    } else {
        chatBox.style.display = "block";
    }
}

// Function to close the chat window
function closeChat() {
    document.getElementById("chat-box").style.display = "none";
}

// Function to handle sending messages
function sendMessage() {
    let inputField = document.getElementById("chat-input");
    let message = inputField.value.trim();
    if (message === "") return;

    let chatMessages = document.getElementById("chat-messages");
    let userMessage = document.createElement("p");
    userMessage.classList.add("user-message");
    userMessage.textContent = message;
    chatMessages.appendChild(userMessage);

    inputField.value = "";

    setTimeout(() => {
        let botMessage = document.createElement("p");
        botMessage.classList.add("bot-message");
        botMessage.textContent = getBettingSuggestion(message);
        chatMessages.appendChild(botMessage);
    }, 1000);
}

// Handle Enter key press
function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

// Function to generate basic betting suggestions
function getBettingSuggestion(message) {
    const suggestions = [
        "Consider taking the over on passing yards!",
        "The home team has covered the spread in 5 of their last 6 games.",
        "Player X is in great form for touchdown props!",
        "Look for strong underdog value in live bets.",
        "Defense matchups favor Player Y for rushing yards."
    ];
    return suggestions[Math.floor(Math.random() * suggestions.length)];
}
