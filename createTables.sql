create user  'usuario1' identified by 'password'
grant all privileges on * . * to 'usuario1';

create database APIData;
use APIData;
create table dailyReturns(
dia date,
profit double,
amount integer,
symbol varchar(100),
idStrategy datetime,
PRIMARY KEY(dia,symbol,idStrategy)
)
