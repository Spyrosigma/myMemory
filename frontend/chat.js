const chatbotContainer = document.getElementById('chatbot-container');
const chatbotMessages = document.getElementById('chatbot-messages');
const userInput = document.getElementById('user-input');
const sendMessage = document.getElementById('send-message');
const sendBtn = document.getElementById('send-btn');

const socket = io('https://mymemory-6mtb.onrender.com/', {
// const socket = io('http://localhost:5000/', {
    transports: ['websocket'],
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
    timeout: 10000
});

// gunicorn -k gevent --timeout 600 app:app -w 1
// gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 app:app --timeout 600

let userId = null;

socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('connect_error', (error) => {
    console.error('Connection error:', error);
});

socket.on('set_user_id', (data) => {
    userId = data.user_id;
    console.log('Received user ID:', userId);
    socket.emit('join', { user_id: userId });
});

socket.on('bot_response', (message) => {
    addMessage(message.data, 'bot-message');
});

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendUserMessage();
    }
});

sendBtn.addEventListener('click', sendUserMessage);

function sendUserMessage() {
    const message = userInput.value.trim();
    if (message && userId) {
        addMessage(message, 'user-message');
        userInput.value = '';
        socket.emit('user_message', { data: message, user_id: userId });
    }
}

function addMessage(message, className) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', className);
    messageElement.textContent = message;
    chatbotMessages.appendChild(messageElement);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
}

document.getElementById('memory-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const memoryText = document.getElementById('memory-text').value;

    if (memoryText.trim() !== "") {
        console.log("Memory to save:", memoryText);
        // Add memory saving function (pipeline to Pinecone, etc.)
        alert("Memory saved!");
        document.getElementById('memory-text').value = "";
    }
});
