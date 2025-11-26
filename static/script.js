const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

// Auto-resize textarea
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
    if (this.value === '') this.style.height = 'auto';
});

// Handle Enter key
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener('click', sendMessage);

async function sendMessage() {
    const question = userInput.value.trim();
    if (!question) return;

    // Clear input
    userInput.value = '';
    userInput.style.height = 'auto';

    // Remove welcome message if exists
    const welcome = document.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    // Add user message
    addMessage(question, 'user');

    // Add loading state
    const loadingId = addLoadingMessage();

    try {
        const response = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                top_k: 5
            })
        });

        const data = await response.json();
        
        // Remove loading message
        document.getElementById(loadingId).remove();

        if (data.detail) {
            addMessage(`Error: ${data.detail}`, 'bot');
        } else {
            addBotMessage(data);
        }

    } catch (error) {
        document.getElementById(loadingId).remove();
        addMessage(`Network Error: ${error.message}`, 'bot');
    }
}

function addMessage(text, sender) {
    const div = document.createElement('div');
    div.className = `message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = sender === 'user' ? 'U' : 'AI';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    if (sender === 'bot') {
        content.innerHTML = marked.parse(text);
    } else {
        content.textContent = text;
    }
    
    div.appendChild(avatar);
    div.appendChild(content);
    
    chatContainer.appendChild(div);
    scrollToBottom();
}

function addBotMessage(data) {
    const div = document.createElement('div');
    div.className = 'message bot';
    
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = 'AI';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    // Main Answer
    let htmlContent = marked.parse(data.answer);
    
    // Sources
    if (data.sources && data.sources.length > 0) {
        htmlContent += `
            <div class="sources-section">
                <div class="sources-title">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="8" y2="13"></line>
                        <line x1="16" y1="17" x2="8" y2="17"></line>
                        <polyline points="10 9 9 9 8 9"></polyline>
                    </svg>
                    Sources
                </div>
        `;
        
        data.sources.forEach((source, index) => {
            const fileName = source.metadata.s3_key ? source.metadata.s3_key.split('/').pop() : `Document ${index + 1}`;
            const score = (source.similarity * 100).toFixed(1);
            
            htmlContent += `
                <div class="source-item">
                    <div class="source-header">
                        <span>${fileName}</span>
                        <span class="source-score">${score}% match</span>
                    </div>
                </div>
            `;
        });
        
        htmlContent += '</div>';
    }
    
    content.innerHTML = htmlContent;
    
    div.appendChild(avatar);
    div.appendChild(content);
    
    chatContainer.appendChild(div);
    scrollToBottom();
}

function addLoadingMessage() {
    const id = 'loading-' + Date.now();
    const div = document.createElement('div');
    div.id = id;
    div.className = 'message bot';
    
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = 'AI';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.innerHTML = `
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    
    div.appendChild(avatar);
    div.appendChild(content);
    
    chatContainer.appendChild(div);
    scrollToBottom();
    return id;
}

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}
