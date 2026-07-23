document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('logout-form');
    var navRight = document.querySelector('#jazzy-navbar .navbar-nav.ms-auto');
    if (!form || !navRight) return;

    var li = document.createElement('li');
    li.className = 'nav-item d-flex align-items-center';

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'btn btn-sm btn-outline-danger ms-2';
    btn.innerHTML = '<i class="fas fa-sign-out-alt me-1"></i> Logout';
    btn.addEventListener('click', function () {
        form.submit();
    });

    li.appendChild(btn);
    navRight.insertBefore(li, navRight.firstChild);
});
