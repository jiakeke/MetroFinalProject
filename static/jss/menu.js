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
        render: async function game_render() {
            const response = await fetch('/game', {
                method: 'GET',
                }
            );
            const result = await response.json();
            const map_img = new Image();
            map_img.src = result.map_info[0];
            console.log(result);
            const game_section = document.querySelector('#game_section');
            game_section.innerHTML = '';
            const fields = [
                'departure_name', 'destination_name', 'distance', 'passenger',
                'reward',
            ]

            for (let field of result.task) {

                game_section.appendChild(
                    Object.assign(
                        document.createElement('div'),
                        {
                            id: `${field[0]}`,
                            innerHTML: `${field[1]}: ${field[2]}`,
                        }
                    )
                );
            }

            game_section.appendChild(document.createElement('br'));
            game_section.appendChild(
                Object.assign(
                    document.createElement('div'),
                    {
                        id: 'tips',
                        innerHTML: 'Tips:<br>Destination weather may affect flight costs.<br> Refuel cost is 50 coins each time.',
                    }
                )
            );


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
                async function game_play(event) {
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
                                    style: `background-image: url(${result.map_info[0]})`,
                            }
                        );
                        game_section.appendChild(game_dialog);
                        game_dialog.appendChild(
                            Object.assign(
                                document.createElement('canvas'),
                                {
                                    id: 'game_playing',
                                    width: 1024,
                                    height: 768,
                                }
                            )
                        );

                        const ax = result.map_info[1][0];
                        const ay = result.map_info[1][1];
                        const bx = result.map_info[2][0];
                        const by = result.map_info[2][1];
                        /*
                        // Drawing line start
                        const canvas = document.getElementById("game_playing");
                        if(canvas.getContext){
                            var ctx = canvas.getContext("2d");
                            ctx.beginPath();
                            ctx.moveTo(ax, ay);
                            ctx.lineTo(bx, by);
                            ctx.strokeStyle = "red";
                            ctx.lineWidth = 10;
                            ctx.lineCap = 'round'; //square, round, butt
                            ctx.stroke();
                            ctx.closePath();
                        }
                        //Drawing line end
                        */
                        const plane_img = Object.assign(
                            document.createElement('img'),
                            {
                                id: 'plane_img',
                                src: '/static/imgs/plane_left.webp',
                                width: 80,
                                height: 80,
                                style: `position: absolute; left:
                                ${result.map_info[1][0]-20}px; top:
                                ${result.map_info[1][1]-20}px`,
                            }
                        );

                        game_dialog.appendChild(plane_img);

                        let img_width = plane_img.width;
                        let img_height = plane_img.height;
                        let delta_x = (bx-ax)/20;
                        let delta_y = delta_x*(by-ay)/(bx-ax);

                        if (ax > bx) {
                            plane_img.src = '/static/imgs/plane_right.webp';
                        }
                        //let current = 90;
                        //plane_img.style.transform = 'rotate('+current+'deg)';
                        
                        
                        function flying() {
                            let new_x = plane_img.offsetLeft;
                            let new_y = plane_img.offsetTop;

                            let distance_x = Math.abs(bx - new_x)
                            let distance_y = Math.abs(by - new_y)

                            if (distance_x <= Math.abs(delta_x)) {
                                plane_img.style.left = `${bx-img_width/2}px`;
                                plane_img.style.top = `${by-img_height/2}px`;
                                game_dialog.close();
                            } else {
                                plane_img.style.left = `${new_x + delta_x}px`;
                                plane_img.style.top = `${new_y + delta_y}px`;
                                setTimeout(flying, 300);
                            }

                        }
                        // Show Map Dialog
                        game_dialog.showModal();
                        flying();
                        const skip = Object.assign(
                            document.createElement('button'),
                            {
                                id: 'flying_skip',
                                type: 'button',
                                innerHTML: 'Skip',
                                style: "position: absolute; left: 900px; top: 30px;",
                            }
                        )
                        skip.addEventListener(
                            'click',
                            function(){
                                game_dialog.close()
                            }
                        );
                        game_dialog.appendChild(skip);
                        // Report start

                        let report = Object.assign(
                            document.createElement('div'),
                            {
                                id: 'game_report',
                                width: 300,
                                height: 200,
                            }
                        );
                            
                        let status = Object.assign(
                            document.createElement('h3'),
                            {
                                id: 'status',
                                innerHTML: result.report.status,
                            }
                        );
                        report.appendChild(status);

                        console.log(result.report.msgs);
                        for (let msg of result.report.msgs) {
                            let msg_p = Object.assign(
                                document.createElement('p'),
                                {
                                    id: 'message',
                                    innerHTML: msg,
                                }
                            )
                        report.appendChild(msg_p);
                        }

                        const report_confirm = Object.assign(
                            document.createElement('button'),
                            {
                                id: 'report_confirm',
                                type: 'button',
                                innerHTML: 'OK',
                            }
                        )
                        report_confirm.addEventListener(
                            'click',
                            game_render
                        );
                        report.appendChild(report_confirm);
                        game_section.appendChild(report);
                        // Report end

                    }
                }
            );

        },
    },
    {
        id: 'store',
        name: 'Store',
        method: null,
        render: async function store_render() {
            // Here is the function to render the store channelel
          const response = await fetch('/store', {
            method: 'GET',
          });
          const result = await response.json();
          const store_section = document.querySelector('#store_section');
          store_section.innerHTML = '';
          const user_info = document.createElement('p');
          user_info.setAttribute('id', 'user_info');
          user_info.innerHTML = `Current user: ${result.user.name}, balance: ${result.user.balance}`;
          store_section.appendChild(user_info);

          function updateUserBalance() {
            fetch('/store')
              .then(response => response.json())
              .then(data => {
                const user_info = document.querySelector('#user_info'); // 假设您有一个显示用户信息的元素
                user_info.innerHTML = `Current user: ${data.user.name}, balance: ${data.user.balance}`;
              });
          }

          result.planes.forEach(plane => {
            const planeDiv = document.createElement('div');
            planeDiv.className = 'plane';

            const image_container = document.createElement('dialog');
            const planeImg = document.createElement('img');
            planeImg.src = plane.img;
            planeImg.alt = plane.name;
            image_container.appendChild(planeImg);
            store_section.appendChild(image_container);

            const showImageButton = document.createElement('button');
            showImageButton.innerHTML = 'Show Plane Image';
            showImageButton.addEventListener('click', function() {
              image_container.showModal();
            })

            const buyButton = document.createElement('button');
            buyButton.innerHTML = 'Purchase';
            buyButton.addEventListener('click', async function() {
              const response = await fetch(`/store/buy/${plane.id}`, {
                method: 'POST',
              });
              const result = await response.json();
              alert(result.message);
              if (result.status === 'success') {
                updateUserBalance();
              }
            })

            planeImg.addEventListener('click', function() {
              image_container.close();
            })
            planeDiv.innerHTML = `
                <h3>${plane.name}</h3>
                <p>Range: ${plane.flight_range}, Price: ${plane.price}</p>
            `;

            planeDiv.appendChild(showImageButton);
            planeDiv.appendChild(buyButton);
            store_section.appendChild(planeDiv);
          });
        },
    },
    {
        id: 'gallery',
        name: 'Gallery',
        method: null,
        render: async function gallery_render() {
            // Here is the function to render the gallery channelel
            const response = await fetch('/gallery', {method:
            'GET'},);
            const result = await response.json()
            const gallery_section = document.querySelector('#gallery_section');
            gallery_section.innerHTML = '';
            result.planes.forEach(plane => {
                const planeDiv = document.createElement('div');
                planeDiv.className = 'plane';

                const image_container = document.createElement('dialog');
                const planeImg = document.createElement('img');
                planeImg.src = plane.img;
                planeImg.alt = plane.name;
                image_container.appendChild(planeImg);
                gallery_section.appendChild(image_container)

                const showImageButton = document.createElement('button');
                showImageButton.innerHTML = 'Show Plane Image';
                showImageButton.addEventListener('click', function (){
                    image_container.showModal();
                })

                planeImg.addEventListener('click', function () {
                    image_container.close();
                })
                planeDiv.innerHTML = `
                <h3>${plane.name}</h3>
                <p>Range: ${plane.flight_range}, Price: ${plane.price}</p>
            `;

                planeDiv.appendChild(showImageButton)
                gallery_section.appendChild(planeDiv)

            })
        },
    },
    {
        id: 'ranking',
        name: 'Ranking',
        method: null,
        render: async function ranking_render() {
            // Here is the function to render the ranking channelel
        },
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

