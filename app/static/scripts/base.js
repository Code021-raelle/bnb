// Javascript to auto-hide flash messages after 5 seconds
window.addEventListener('DOMContentLoaded', (event) => {
    setTimeout(() => {
        const alerts = document.querySelectorAll('#flash-messages .alert');
        alerts.forEach(alert => {
            // Bootstrap method to close alert
            $(alert).alert('close');
        });
    }, 3000); // 3000 milliseconds = 3 seconds
});

document.addEventListener('DOMContentLoaded', function () {
    // Initialize WebSocket connection
    const ws = new WebSocket(`ws://localhost:5000/ws`);  // Replace with your WebSocket server URL

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
                    <img src="${window.location.origin}/static/images/profile_placeholder.png" alt="profile picture" class="chat-message-avatar">
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
    if (messageForm) {
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
    }

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

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;

            fetch('{{ url_for(`save_location`) }}', {
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

    // Sliding up of words in the homepage
    var slideElements = document.querySelectorAll('.slide-up');

    function checkSlide() {
        slideElements.forEach(function(el) {
            var slideInAt = (window.scrollY + window.innerHeight) - el.clientHeight / 2;
            var isHalfShown = slideInAt > el.offsetTop;
            var isNotScrolledPast = window.scrollY < el.offsetTop + el.clientHeight;

            if (isHalfShown && isNotScrolledPast) {
                el.classList.add('visible');
            } else {
                el.classList.remove('visible');
            }
        });
    }

    window.addEventListener('scroll', checkSlide);
    checkSlide(); // Run on load in case elements are already in view
});

document.addEventListener('DOMContentLoaded', function() {
    // Simulate loading completion (e.g., after AJAX call or page content fully loaded)
    setTimeout(function() {
        document.getElementById('loading-screen').style.display = 'none';
        document.getElementById('main-content').classList.remove('hidden');
    }, 500); // Replace 3000 with the actual loading time if necessary
});

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Flatpickr on inputs with specific classes or IDs
    flatpickr("input[placeholder='Check-in']", {
        dateFormat: "Y-m-d",
    });
    flatpickr("input[placeholder='Check-out']", {
        dateFormat: "Y-m-d",
    });

    // Your existing code for slide-up elements
    var slideElements = document.querySelectorAll('.slide-up');

    function checkSlide() {
        slideElements.forEach(function(el) {
            var slideInAt = (window.scrollY + window.innerHeight) - el.clientHeight / 2;
            var isHalfShown = slideInAt > el.offsetTop;
            var isNotScrolledPast = window.scrollY < el.offsetTop + el.clientHeight;

            if (isHalfShown && isNotScrolledPast) {
                el.classList.add('visible');
            } else {
                el.classList.remove('visible');
            }
        });
    }

    window.addEventListener('scroll', checkSlide);
});

// Initialize HERE platform with your API key
const platform = new H.service.Platform({
    apikey: 'CWa4Zb9yiDDfEW1j1RAThuf3YUDEvRJOM1Qfy_McO9M'
});

const service = platform.getSearchService();

// Get the input element
const locationInput = document.getElementById('location-input');

// Function to fetch location suggestions based on user input
function fetchLocationSuggestions(query) {
    service.autosuggest({
        q: query,
        at: '52.5200,13.4050' // Default location, can be user location
    }, (result) => {
        // Handle the suggestions here
        console.log(result);
        // You can display suggestions in a dropdown or list format below the input
    }, (error) => {
        console.error(error);
    });
}

// Event listener for input changes
locationInput.addEventListener('input', (event) => {
    const query = event.target.value;
    if (query.length > 2) {
        fetchLocationSuggestions(query);
    }
});
