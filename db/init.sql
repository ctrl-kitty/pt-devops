-- Создание таблицы для электронной почты
CREATE TABLE email (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE
);

-- Создание таблицы для номеров телефонов
CREATE TABLE phone (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE
);

