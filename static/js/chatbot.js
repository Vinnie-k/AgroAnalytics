/**
 * Kenya-Agor AI Chatbot JavaScript
 * Handles chatbot interactions and UI management
 */

class KenyaAgorChatbot {
    constructor() {
        this.isOpen = false;
        this.isTyping = false;
        this.messageHistory = [];
        this.maxMessages = 50;
        this.init();
    }

    init() {
        console.log('Initializing Kenya-Agor AI Chatbot...');
        this.bindEvents();
        this.loadChatHistory();
        this.addWelcomeMessage();
    }

    bindEvents() {
        // Chat toggle button
        const toggleBtn = document.getElementById('chat-toggle');
        const closeBtn = document.getElementById('close-chat');
        const chatWidget = document.getElementById('chatbot-widget');
        
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggleChat());
        }
        
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeChat());
        }

        // Send message events
        const sendBtn = document.getElementById('send-message');
        const chatInput = document.getElementById('chat-input');
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }
        
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            chatInput.addEventListener('input', () => {
                this.adjustInputHeight();
            });
        }

        // Quick reply buttons (if any are added dynamically)
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('quick-reply-btn')) {
                const message = e.target.textContent;
                this.sendQuickReply(message);
            }
        });

        // Close chat when clicking outside
        document.addEventListener('click', (e) => {
            if (this.isOpen && 
                !e.target.closest('#chatbot-container') && 
                !e.target.closest('#chat-toggle')) {
                // Don't close immediately, give user a chance
                setTimeout(() => {
                    if (!document.querySelector('#chatbot-container:hover')) {
                        // this.closeChat();
                    }
                }, 100);
            }
        });
    }

    toggleChat() {
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }

    openChat() {
        const chatWidget = document.getElementById('chatbot-widget');
        const toggleBtn = document.getElementById('chat-toggle');
        
        if (chatWidget && toggleBtn) {
            chatWidget.style.display = 'block';
            toggleBtn.style.display = 'none';
            this.isOpen = true;
            
            // Focus on input
            setTimeout(() => {
                const input = document.getElementById('chat-input');
                if (input) input.focus();
            }, 300);
            
            // Scroll to bottom
            this.scrollToBottom();
            
            console.log('Chatbot opened');
        }
    }

    closeChat() {
        const chatWidget = document.getElementById('chatbot-widget');
        const toggleBtn = document.getElementById('chat-toggle');
        
        if (chatWidget && toggleBtn) {
            chatWidget.style.display = 'none';
            toggleBtn.style.display = 'flex';
            this.isOpen = false;
            
            console.log('Chatbot closed');
        }
    }

    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input?.value?.trim();
        
        if (!message || this.isTyping) {
            return;
        }
        
        // Clear input
        input.value = '';
        this.adjustInputHeight();
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send message to backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            if (response.ok && data.response) {
                // Add bot response
                this.addMessage(data.response, 'bot');
                
                // Add quick replies if relevant
                this.addQuickReplies(message);
            } else {
                // Error handling
                this.addMessage(
                    "I'm sorry, I'm having trouble responding right now. Please try again later.", 
                    'bot', 
                    'error'
                );
            }
            
        } catch (error) {
            console.error('Chat API error:', error);
            this.hideTypingIndicator();
            
            this.addMessage(
                "I'm experiencing connection issues. Please check your internet connection and try again.", 
                'bot', 
                'error'
            );
        }
        
        // Save to history
        this.saveToHistory(message, 'user');
    }

    sendQuickReply(message) {
        const input = document.getElementById('chat-input');
        if (input) {
            input.value = message;
            this.sendMessage();
        }
    }

    addMessage(message, sender, type = 'normal') {
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `mb-3`;
        
        const timestamp = new Date().toLocaleTimeString('en-KE', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        if (sender === 'user') {
            messageDiv.innerHTML = `
                <div class="d-flex justify-content-end">
                    <div class="bg-agricultural-green text-white rounded-3 p-3 max-width-80">
                        <p class="mb-0">${this.escapeHtml(message)}</p>
                        <small class="opacity-75">${timestamp}</small>
                    </div>
                </div>
            `;
        } else {
            const iconClass = type === 'error' ? 'fas fa-exclamation-circle text-danger' : 'fas fa-robot text-agricultural-green';
            const bgClass = type === 'error' ? 'bg-danger-subtle' : 'bg-light';
            
            messageDiv.innerHTML = `
                <div class="d-flex align-items-start">
                    <div class="flex-shrink-0 me-2">
                        <i class="${iconClass}"></i>
                    </div>
                    <div class="${bgClass} rounded-3 p-3 max-width-80">
                        <p class="mb-0">${this.formatBotMessage(message)}</p>
                        <small class="text-muted">${timestamp}</small>
                    </div>
                </div>
            `;
        }
        
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Limit message history
        this.cleanupMessages();
    }

    addWelcomeMessage() {
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer || messagesContainer.children.length > 1) return;
        
        const welcomeMessage = `
            Hello! I'm your agricultural assistant for Kenya. I can help you with:
            
            🌱 Crop recommendations for your area
            💰 Market price information  
            🌧️ Weather and farming advice
            📊 Understanding your agricultural data
            
            What would you like to know about farming?
        `;
        
        setTimeout(() => {
            this.addMessage(welcomeMessage, 'bot');
            this.addQuickReplies('welcome');
        }, 1000);
    }

    addQuickReplies(context) {
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return;
        
        let replies = [];
        
        if (context === 'welcome' || context.toLowerCase().includes('help')) {
            replies = [
                "What crops should I plant?",
                "Current maize prices",
                "Weather advice",
                "Soil management tips"
            ];
        } else if (context.toLowerCase().includes('price') || context.toLowerCase().includes('market')) {
            replies = [
                "Tea prices",
                "Coffee prices", 
                "Bean prices",
                "Market trends"
            ];
        } else if (context.toLowerCase().includes('weather') || context.toLowerCase().includes('rain')) {
            replies = [
                "Planting calendar",
                "Drought preparedness",
                "Irrigation advice"
            ];
        } else if (context.toLowerCase().includes('crop') || context.toLowerCase().includes('plant')) {
            replies = [
                "Maize farming",
                "Tea cultivation",
                "Vegetable growing",
                "Organic farming"
            ];
        }
        
        if (replies.length > 0) {
            const quickRepliesDiv = document.createElement('div');
            quickRepliesDiv.className = 'mb-3';
            quickRepliesDiv.innerHTML = `
                <div class="d-flex align-items-start">
                    <div class="flex-shrink-0 me-2">
                        <i class="fas fa-robot text-agricultural-green"></i>
                    </div>
                    <div class="bg-light rounded-3 p-2">
                        <small class="text-muted d-block mb-2">Quick replies:</small>
                        <div class="d-flex flex-wrap gap-1">
                            ${replies.map(reply => 
                                `<button class="btn btn-sm btn-outline-agricultural-green quick-reply-btn">${reply}</button>`
                            ).join('')}
                        </div>
                    </div>
                </div>
            `;
            
            messagesContainer.appendChild(quickRepliesDiv);
            this.scrollToBottom();
        }
    }

    showTypingIndicator() {
        if (this.isTyping) return;
        
        this.isTyping = true;
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return;
        
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'mb-3';
        typingDiv.innerHTML = `
            <div class="d-flex align-items-start">
                <div class="flex-shrink-0 me-2">
                    <i class="fas fa-robot text-agricultural-green"></i>
                </div>
                <div class="bg-light rounded-3 p-3">
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
        
        // Add typing animation CSS if not already present
        if (!document.getElementById('typing-animation-styles')) {
            const styles = document.createElement('style');
            styles.id = 'typing-animation-styles';
            styles.textContent = `
                .typing-dots {
                    display: flex;
                    gap: 3px;
                    align-items: center;
                }
                .typing-dots span {
                    height: 6px;
                    width: 6px;
                    background-color: #6c757d;
                    border-radius: 50%;
                    animation: typing 1.4s infinite ease-in-out;
                }
                .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
                .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
                .typing-dots span:nth-child(3) { animation-delay: 0s; }
                @keyframes typing {
                    0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
                    40% { transform: scale(1); opacity: 1; }
                }
                .max-width-80 { max-width: 80%; }
            `;
            document.head.appendChild(styles);
        }
    }

    hideTypingIndicator() {
        this.isTyping = false;
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    formatBotMessage(message) {
        // Convert line breaks to HTML
        let formatted = this.escapeHtml(message);
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Convert bullet points
        formatted = formatted.replace(/[•🌱💰🌧️📊]/g, '<br>$&');
        
        // Make important terms bold
        const importantTerms = [
            'maize', 'beans', 'tea', 'coffee', 'wheat', 'rice',
            'planting', 'harvest', 'fertilizer', 'irrigation',
            'KES', 'price', 'market', 'weather', 'rainfall'
        ];
        
        importantTerms.forEach(term => {
            const regex = new RegExp(`\\b${term}\\b`, 'gi');
            formatted = formatted.replace(regex, `<strong>$&</strong>`);
        });
        
        return formatted;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chat-messages');
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    adjustInputHeight() {
        const input = document.getElementById('chat-input');
        if (input) {
            input.style.height = 'auto';
            input.style.height = Math.min(input.scrollHeight, 100) + 'px';
        }
    }

    cleanupMessages() {
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return;
        
        const messages = messagesContainer.children;
        if (messages.length > this.maxMessages) {
            // Remove oldest messages, keeping welcome message
            for (let i = 1; i < messages.length - this.maxMessages; i++) {
                messages[i].remove();
            }
        }
    }

    loadChatHistory() {
        // Load recent chat history from localStorage if needed
        const saved = localStorage.getItem('kenya_agor_chat_history');
        if (saved) {
            try {
                this.messageHistory = JSON.parse(saved).slice(-20); // Keep last 20
            } catch (e) {
                console.warn('Failed to load chat history:', e);
                this.messageHistory = [];
            }
        }
    }

    saveToHistory(message, sender) {
        this.messageHistory.push({
            message,
            sender,
            timestamp: new Date().toISOString()
        });
        
        // Keep only recent messages
        if (this.messageHistory.length > 50) {
            this.messageHistory = this.messageHistory.slice(-50);
        }
        
        // Save to localStorage
        try {
            localStorage.setItem('kenya_agor_chat_history', JSON.stringify(this.messageHistory));
        } catch (e) {
            console.warn('Failed to save chat history:', e);
        }
    }

    // Clear chat history
    clearHistory() {
        const messagesContainer = document.getElementById('chat-messages');
        if (messagesContainer) {
            // Keep only the first message (info message)
            const children = Array.from(messagesContainer.children);
            children.forEach((child, index) => {
                if (index > 0) {
                    child.remove();
                }
            });
        }
        
        this.messageHistory = [];
        localStorage.removeItem('kenya_agor_chat_history');
        
        // Add welcome message again
        setTimeout(() => this.addWelcomeMessage(), 500);
    }

    // Export chat history
    exportHistory() {
        const data = {
            timestamp: new Date().toISOString(),
            farmer: window.currentUser?.full_name || 'Unknown',
            messages: this.messageHistory
        };
        
        const dataStr = JSON.stringify(data, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `kenya-agor-chat-history-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        URL.revokeObjectURL(url);
    }

    // Get farming tips based on context
    getFarmingTip() {
        const tips = [
            "💡 Tip: Plant maize during the long rains (March-May) for better yields.",
            "🌱 Remember: Rotate your crops to maintain soil fertility.",
            "💰 Market tip: Check prices at multiple markets before selling.",
            "🌧️ Weather: Monitor rainfall patterns for optimal planting times.",
            "📊 Data: Track your farm expenses and income for better planning."
        ];
        
        const randomTip = tips[Math.floor(Math.random() * tips.length)];
        this.addMessage(randomTip, 'bot');
    }
}

// Initialize chatbot when page loads
let chatbot;
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if chatbot elements exist (user is authenticated)
    if (document.getElementById('chatbot-container')) {
        chatbot = new KenyaAgorChatbot();
        
        // Make chatbot available globally
        window.chatbot = chatbot;
        
        console.log('Kenya-Agor AI Chatbot initialized successfully');
    }
});

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KenyaAgorChatbot;
}
