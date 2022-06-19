create database python_final;
use python_final;

create table accounts(
idaccounts int primary key auto_increment,
login varchar(30) not null,
password varchar(30) not null
);

create table account_info(
account int,
total_solved int not null,
spend_points int not null,
primary key(account),
foreign key (account) references accounts(idaccounts)
);