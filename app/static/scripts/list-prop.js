document.addEventListener('DOMContentLoaded', function() {
    // Simulate loading completion (e.g., after AJAX call or page content fully loaded)
    setTimeout(function() {
        document.getElementById('loading-screen').style.display = 'none';
        document.getElementById('main-content').classList.remove('hidden');
    }, 500); // Replace 3000 with the actual loading time if necessary
});
