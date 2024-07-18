// Javascript to auto-hide flash messages after 5 seconds
window.addEventListener('DOMContentLoaded', (event) => {
    setTimeout(() => {
        const alerts = document.querySelectorAll('#flash-messages .alert');
        alerts.forEach(alert => {
            // Bootstrap method to close alert
            $(alert).alert('close');
        });
    }, 5000); // 5000 milliseconds = 5 seconds
});


document.addEventListener('DOMContentLoaded', function () {
    // Initialize WebSocket connection
    const ws = new WebSocket('ws://localhost:5000/ws');  // Replaced with my WebSocket server URL

    // Handle incoming messages from WebSocket server
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.type === 'message') {
            // Update chat UI with the new message
            const message = data.message;
            const chatMessages = document.querySelector('.chat-messages');
            const newMessageElement = document.createElement('div');
            newMessageElement.className = `chat-message ${message.sender === current_user ? 'sent' : 'received'}`;
            newMessageElement.innerHTML = `
                <div class="chat-message-content">
                    <img src="{{ url_for('static', filename='images/profile_placeholder.png') }}" alt="profile picture" class="chat-message-avatar">
                    <div class="chat-message-bubble">
                        <p>${message.body}</p>
                        <span class="chat-message-timestamp">${message.timestamp}</span>
                    </div>
                </div>
            `;
            chatMessages.appendChild(newMessageElement);
        }
    };

    // Handle form submission
    const messageForm = document.getElementById('messageForm');
    messageForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(messageForm);
        const message = formData.get('message');
        const recipient = formData.get('recipient');
        
        // Send message via WebSocket
        ws.send(JSON.stringify({
            type: 'message',
            sender: '{{ current_user.username }}',  // Replace with actual username
            recipient: recipient,
            body: message,
            timestamp: new Date().toISOString()
        }));

        // Clear input field after sending message
        messageForm.reset();
    });

    // Handle reply modal display
    const replyButtons = document.querySelectorAll('.reply-btn');
    replyButtons.forEach(button => {
        button.addEventListener('click', function () {
            const sender = this.getAttribute('data-sender');
            document.getElementById('replyTo').innerText = sender;
            document.getElementById('modal-recipient').value = sender;
            $('#replyModal').modal('show');
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const replyButtons = document.querySelectorAll('.reply-btn');
    replyButtons.forEach(button => {
        button.addEventListener('click', function () {
            const sender = this.getAttribute('data-sender');
            document.getElementById('replyTo').innerText = sender;
            document.getElementById('modal-recipient').value = sender;
            $('#replyModal').modal('show');
        });
    });

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;

            fetch('{{ url_for('save_location') }}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token() }}'
                },
                body: JSON.stringify({latitude: lat, longitude: lon})
            });
        });
    } else {
        console.log("Geolocation is not supported by this browser.");
    }
});