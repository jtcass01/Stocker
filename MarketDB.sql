CREATE DATABASE Stocker_Market_Data;

CREATE TABLE GE(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    cost_basis_per_share float,
    price float);

CREATE TABLE PLUG(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    cost_basis_per_share float,
    price float);

CREATE TABLE F(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    cost_basis_per_share float,
    price float);

CREATE TABLE NNDM(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    cost_basis_per_share float,
    price float);

CREATE TABLE AAPL(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    cost_basis_per_share float,
    price float);

CREATE TABLE BLNK(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    cost_basis_per_share float,
    price float);

CREATE TABLE APPH(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    cost_basis_per_share float,
    price float);

CREATE TABLE CMPS(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    cost_basis_per_share float,
    price float);

CREATE TABLE SPWR(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    cost_basis_per_share float,
    price float);

CREATE TABLE DIS(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    cost_basis_per_share float,
    price float);

CREATE TABLE CRSR(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    cost_basis_per_share float,
    price float);

CREATE TABLE NIO(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    cost_basis_per_share float,
    price float);

CREATE TABLE RUN(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    cost_basis_per_share float,
    price float);

CREATE TABLE COIN(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    cost_basis_per_share float,
    price float);

CREATE TABLE ENG(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    cost_basis_per_share float,
    price float);

CREATE TABLE ALGO(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    stake float,
    unrealized_rewards float,
    investment float,
    price float);

CREATE TABLE ADA(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    stake float,
    unrealized_rewards float,
    investment float,
    price float);

CREATE TABLE GRT(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    stake float,
    unrealized_rewards float,
    investment float,
    price float);

CREATE TABLE ETH(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    stake float,
    unrealized_rewards float,
    investment float,
    price float);

CREATE TABLE ATOM(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    stake float,
    unrealized_rewards float,
    investment float,
    price float);

CREATE TABLE DOT(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    stake float,
    unrealized_rewards float,
    investment float,
    price float);

CREATE TABLE MATIC(
    datetime DATETIME PRIMARY KEY,
    quantity float,
    stake float,
    unrealized_rewards float,
    investment float,
    price float);

