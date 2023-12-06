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
