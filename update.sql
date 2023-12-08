alter table users modify password varchar(128);

alter table airport drop primary key, add primary key (id);

/* Create table for Tasks */
create table tasks (
    id int not null auto_increment,
    user_id int not null,
    departure_id int not null,
    destination_id int not null,
    distance float default 0,
    passenger int(11) default 0,
    reward float default 0,
    is_new boolean default true,
    primary key (id),
    foreign key (user_id) references users(id),
    foreign key (departure_id) references airport(id),
    foreign key (destination_id) references airport(id)
);

update aircraft
set aircraft.image = '\/static\/imgs\/flight_1.png'
where id = 1;
update aircraft
set aircraft.image = '\/static\/imgs\/flight_2.png'
where id = 2;
update aircraft
set aircraft.image = '\/static\/imgs\/flight_3.png'
where id = 3;
update aircraft
set aircraft.image = '\/static\/imgs\/flight_4.png'
where id = 4;
update aircraft
set aircraft.image = '\/static\/imgs\/flight_5.png'
where id = 5;
update aircraft
set aircraft.image = '\/static\/imgs\/flight_6.png'
where id = 6;
update aircraft
set aircraft.image = '\/static\/imgs\/flight_7.png'
where id = 7;
update aircraft
set aircraft.image = '\/static\/imgs\/flight_8.png'
where id = 8;
update aircraft
set aircraft.image = '\/static\/imgs\/flight_9.png'
where id = 9;
alter table aircraft
modify column image varchar(128);