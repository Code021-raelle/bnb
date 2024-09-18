// static/js/chat.js
$(document).ready(function() {
    var socket = io();

    // Update status indicator
    socket.on('status_update', function(data) {
        if (data.user_id == '{{ user.id }}') {
            $('#status-indicator').text(data.status);
        }
    });

    // Ping server every minute to update last seen time
    setInterval(function() {
        $.ajax({
            url: '/status',
            type: 'GET'
        });
    }, 60000);

    // Scroll to bottom of chat on page load
    $('.chat-messages').scrollTop($('.chat-messages')[0].scrollHeight);

    // Function to format timestamp
    function formatTimestamp(timestamp) {
        return moment(timestamp).format('HH:mm');
    }

    // Send message on enter press
    $('#message-input').keypress(function(e) {
        if (e.which == 13 && !e.shiftKey) {
            e.preventDefault();
            $('form.chat-input-form').submit();
        }
    });

    // Update scroll position after sending a message
    $('form.chat-input-form').submit(function() {
        setTimeout(() => {
            $('.chat-messages').scrollTop($('.chat-messages')[0].scrollHeight);
        }, 100);
    });

    function scrollToBottom() {
        const chatMessages = $('.chat-messages');
        const isAtBottom = chatMessages.scrollTop() + chatMessages.innerHeight() >= chatMessages[0].scrollHeight - 10;
        if (isAtBottom) [
            chatMessages.scrollTop(chatMessages[0].scrollHeight);
        ]
    }
});
