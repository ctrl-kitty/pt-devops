# Используем официальный образ PostgreSQL
FROM postgres:latest

# Копирование файла инициализации базы данных
COPY init.sql /docker-entrypoint-initdb.d/

#RUN echo "ALTER USER ${DB_USER} PASSWORD '${DB_PASSWORD}';" > /docker-entrypoint-initdb.d/update_password.sql
