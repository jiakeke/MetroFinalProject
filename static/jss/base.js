'use strict';

async function is_authenticated() {
    const response = await fetch('/is_authenticated', {
        method: 'GET',
        }
    );
    const result = await response.json();
    if (response.status == 200) {
        document.querySelector('nav').style.display = 'block';
        document.querySelector('section').style.display = 'block';
    } else {
        document.querySelector('#login_dialog').showModal()
    }
}

function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  console.log(ca);
  for(let i = 0; i <ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
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
    header.appendChild(dialog);

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
                dialog.close();
                document.querySelector('section').style.display = 'block';
                document.querySelector('nav').style.display = 'block';
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
                dialog.close();
                document.querySelector('section').style.display = 'block';
                document.querySelector('nav').style.display = 'block';
                document.querySelector('#error_msg').innerHTML = '';
            } else {
                document.querySelector('#error_msg').innerHTML = result.msg;
            }
        }
    );

    // Authorization Dialog End

    is_authenticated();
});
