document.querySelector('.user-form').addEventListener('submit', function (event) {
    const login = document.getElementById('login').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;

    if (login.length < 4) {
        showAlert('Логин должен содержать не менее 4 символов.');
        event.preventDefault();
        return;
    }

    const hasLetter = /[a-zA-Zа-яА-Я]/.test(password);
    const hasNumber = /\d/.test(password);
    if (password.length < 6 || !hasLetter || !hasNumber) {
        showAlert('Пароль должен быть не менее 6 символов и содержать буквы и цифры.');
        event.preventDefault();
        return;
    }
});

function showAlert(message) {
    document.getElementById('alert-message').textContent = message;
    document.getElementById('custom-alert').classList.remove('hidden');
}

function closeAlert() {
    document.getElementById('custom-alert').classList.add('hidden');
}