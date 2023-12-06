'use strict';

// Main Menu Section Begin
const nav = document.querySelector('nav');
nav.style.display = 'none';

const section = document.querySelector('section');

const menu_items = [
    {
        id: 'game',
        name: 'Game',
        method: null,
        render: async function() {
            const response = await fetch('/game', {
                method: 'GET',
                }
            );
            const result = await response.json();
            console.log(result);
            const game_section = document.querySelector('#game_section');
            game_section.innerHTML = '';
            const fields = [
                'departure_name', 'destination_name', 'distance', 'passenger',
                'reward',
            ]

            for (let field of fields) {

                game_section.appendChild(
                    Object.assign(
                        document.createElement('div'),
                        {
                            id: `${field}`,
                            innerHTML: `${field}: ${result.task[field]}`,
                        }
                    )
                );
            }

            game_section.appendChild(document.createElement('br'));
            game_section.appendChild(
                Object.assign(
                    document.createElement('div'),
                    {
                        id: 'planes',
                    }
                )
            );

            const flight_form = Object.assign(
                document.createElement('form'),
                {
                    id: 'flight_form',
                    action: '',
                    method: 'POST',
                }
            )
            document.querySelector('#planes').appendChild(flight_form);

            const planes = result.planes;
            for (let i=0; i< planes.length; i++) {
                let plane_div = Object.assign(
                    document.createElement('div'),
                    {
                        className: 'plane',
                    }
                )
                flight_form.appendChild(plane_div);

                plane_div.appendChild(
                    Object.assign(
                        document.createElement('input'),
                        {
                            id: `plane_${i}`,
                            type: 'radio',
                            name: 'plane',
                            required: true,
                            value: planes[i].id,
                        }
                    )
                );

                plane_div.appendChild(
                    Object.assign(
                        document.createElement('span'),
                        {
                            innerHTML: 
                                `${planes[i].name} - 
                                Range: ${planes[i].flight_range} - 
                                Capacity: ${planes[i].passenger}`
                        }
                    )
                );

            }
            const launch = Object.assign(
                document.createElement('button'),
                {
                    id: 'launch',
                    type: 'button',
                    innerHTML: 'Launch',
                }
            )
            flight_form.appendChild(launch);
            launch.addEventListener(
                'click',
                async function(event) {
                    const plane = document.querySelector('input[name="plane"]:checked').value;
                    const response = await fetch('/game/play', {
                        method: 'POST',
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({plane: plane}),
                        }
                    );
                    const result = await response.json();
                    if (response.status == 200) {
                        console.log(result);
                        const game_dialog = Object.assign(
                            document.createElement('dialog'),
                            {
                                id: 'game_dialog',
                            }
                        );
                        game_section.appendChild(game_dialog);
                        game_dialog.appendChild(
                            Object.assign(
                                document.createElement('img'),
                                {
                                    id: 'game_map',
                                    src: result.map_url,
                                    width: 1000,
                                    height: 800,
                                }
                            )
                        )
                        game_dialog.showModal();
                    }
                }
            );

        },
    },
    {
        id: 'store',
        name: 'Store',
        method: null,
    },
    {
        id: 'gallery',
        name: 'Gallery',
        method: null,
    },
    {
        id: 'ranking',
        name: 'Ranking',
        method: null,
    },
    {
        id: 'logout',
        name: 'Logout',
        method: async function(event) {

            const response = await fetch('/logout', {
                method: 'POST',
                }
            );
            const result = await response.json();
            nav.style.display = 'none';
            section.style.display = 'none';
            document.querySelector('#login_dialog').showModal()
        },
    },
]

for (let item of menu_items){
    const menu_item = Object.assign(
        document.createElement('button'),
        {
            id: item.id,
            type: 'button',
            innerHTML: item.name,
        }
    );

    nav.appendChild(menu_item);

    const item_section = Object.assign(
        document.createElement('div'),
        {
            id: `${item.id}_section`,
            style: 'display: none;',
            className: 'channel',
            innerHTML: `<h1>${item.name}</h1>`,
        }
    );
    section.appendChild(item_section);


    if (item.method) {
        menu_item.addEventListener(
            'click',
            item.method,
        );
    } else {
        menu_item.addEventListener(
            'click',
            function(event) {

                for (let item_b of menu_items){
                    if (item_b.id == item.id) {
                        document.querySelector(`#${item_b.id}_section`).style.display = 'block';
                        document.querySelector(`#${item.id}`).setAttribute('class', 'selected');
                    } else {
                        document.querySelector(`#${item_b.id}_section`).style.display = 'none';
                        document.querySelector(`#${item_b.id}`).setAttribute('class', 'unselected');
                    }
                };
                item.render();
            },
        );
    }

}

// Main Menu Section End

