document.getElementById('togglePassword').addEventListener('click', function (e) {
    const passwordInput = document.getElementById('{{ form.password.id }}');
    const icon = e.target;
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);
    icon.classList.toggle('fa-eye');
    icon.classList.toggle('fa-eye-slash');
});
