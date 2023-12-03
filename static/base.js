'use strict';

const token_name = 'p_token';

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function is_logged_in(){
    const auth_token = localStorage.getItem(token_name);
    if (auth_token == null || auth_token === 'undefined') {
        return false;
    } else {
        return true;
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const header = document.querySelector('header');
    const nav = document.querySelector('nav');
    const section = document.querySelector('section');
    const footer = document.querySelector('footer');

    // Authorization Dialog Begin

    const dialog = Object.assign(
        document.createElement('dialog'),
        {
            id: 'login_dialog',
        }
    );

    const login_form = Object.assign(
        document.createElement('form'),
        {
            id: 'login_form',
            action: '',
            method: 'POST',
        }
    );

    const username = Object.assign(
        document.createElement('input'),
        {
            type: 'text',
            id: 'username',
            name: 'username',
            placeholder: 'Enter Username',
            required: true,
        }
    );

    const password = Object.assign(
        document.createElement('input'),
        {
            type: 'text',
            id: 'password',
            name: 'password',
            placeholder: 'Enter Password',
            required: true,
        }
    );

    const login = Object.assign(
        document.createElement('button'),
        {
            type: 'button',
            id: 'login',
            innerHTML: 'Login',
        }
    );

    const register = Object.assign(
        document.createElement('button'),
        {
            type: 'button',
            id: 'register',
            innerHTML: 'Register',
        }
    );

    const error_msg = Object.assign(
        document.createElement('span'),
        {
            id: 'error_msg',
        }
    );

    login_form.appendChild(username);
    login_form.appendChild(password);
    login_form.appendChild(login);
    login_form.appendChild(register);

    dialog.appendChild(login_form);
    dialog.appendChild(error_msg);
    section.appendChild(dialog);

    login.addEventListener(
        'click',
        async function() {
            const username = document.querySelector('#username').value;
            const password = document.querySelector('#password').value;
            const response = await fetch('/login', {
                method: 'POST',
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({username: username, password: password}),
                }
            );
            const result = await response.json();
            if (response.status == 200) {
                localStorage.setItem(token_name, result.access_token);
                dialog.close();
                document.querySelector('#main').style.display = 'block';
                document.querySelector('#error_msg').innerHTML = '';
            } else {
                document.querySelector('#error_msg').innerHTML = result.msg;
            }
        }
    );

    register.addEventListener(
        'click',
        async function() {
            const username = document.querySelector('#username').value;
            const password = document.querySelector('#password').value;
            const response = await fetch('/register', {
                method: 'POST',
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({username: username, password: password}),
                }
            );
            const result = await response.json();
            if (response.status == 200) {
                localStorage.setItem(token_name, result.access_token);
                dialog.close();
                document.querySelector('#main').style.display = 'block';
                document.querySelector('#error_msg').innerHTML = '';
            } else {
                document.querySelector('#error_msg').innerHTML = result.msg;
            }
        }
    );

    // Authorization Dialog End

    // Main Section Begin
    const main = Object.assign(
        document.createElement('div'),
        {
            id: 'main',
        }
    );
    main.style.display = 'none';


    const menu_game = Object.assign(
        document.createElement('button'),
        {
            id: 'game',
            type: 'button',
            innerHTML: 'Game',
        }
    );

    main.appendChild(menu_game);


    const menu_store = Object.assign(
        document.createElement('button'),
        {
            id: 'store',
            type: 'button',
            innerHTML: 'Store',
        }
    );

    main.appendChild(menu_store);

    const menu_gallery = Object.assign(
        document.createElement('button'),
        {
            id: 'gallery',
            type: 'button',
            innerHTML: 'Gallery',
        }
    );

    main.appendChild(menu_gallery);

    const menu_ranking = Object.assign(
        document.createElement('button'),
        {
            id: 'ranking',
            type: 'button',
            innerHTML: 'Ranking',
        }
    );

    main.appendChild(menu_ranking);

    const logout = Object.assign(
        document.createElement('button'),
        {
            id: 'logout',
            type: 'button',
            innerHTML: 'Logout',
        }
    );

    logout.addEventListener(
        'click',
        function(event) {
            localStorage.removeItem(token_name);
            main.style.display = 'none';
            document.querySelector('#login_dialog').showModal()
        }
    );

    main.appendChild(logout);

    section.appendChild(main);

    // Main Section End

    if (is_logged_in()) {
        document.querySelector('#main').style.display = 'block';
    } else {
        document.querySelector('#login_dialog').showModal()
    }
});
