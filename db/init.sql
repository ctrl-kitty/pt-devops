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
ALTER SYSTEM SET log_replication_commands = 'on';
ALTER SYSTEM SET archive_command = 'cp %p /oracle/pg_data/archive/%f';
select pg_reload_conf();
select pg_switch_wal();
CREATE ROLE $DB_REPL_USER WITH REPLICATION LOGIN PASSWORD '$DB_REPL_PASSWORD';
SELECT pg_create_physical_replication_slot('replication_slot');
