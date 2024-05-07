FROM bitnami/postgresql

ARG RM_USER
ARG RM_PASSWORD
ARG RM_PORT
ARG DB_USER
# Копирование файла инициализации базы данных
COPY init.sql /docker-entrypoint-initdb.d/
#RUN echo "ALTER USER ${DB_USER} PASSWORD '${DB_PASSWORD}';" > /docker-entrypoint-initdb.d/update_password.sq
#RUN echo "CREATE ROLE \"$DB_REPL_USER\" REPLICATION LOGIN ENCRYPTED PASSWORD '$DB_REPL_PASSWORD';" > /docker-entrypoint-initdb.d/init.sql

USER root
RUN apt-get update && apt-get install -y openssh-server
RUN mkdir /var/run/sshd
RUN groupadd postgres
RUN id -u ${RM_USER} &>/dev/null || useradd -m ${RM_USER}
RUN echo "${RM_USER}:${RM_PASSWORD}" | chpasswd
RUN usermod -aG postgres ${RM_USER}
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN mkdir -p /oracle/pg_data/archive/
RUN chown ${DB_USER} /oracle/pg_data/archive
RUN chmod u+rw /oracle/pg_data/archive
RUN mkdir -p /var/log/postgres
RUN chown ${RM_USER} /var/log/postgres
RUN chmod -R a+wr /var/log/postgres
EXPOSE ${RM_PORT}
CMD sh -c "/usr/sbin/sshd;/opt/bitnami/scripts/postgresql/run.sh && psql -U postgres -c \"alter system set archive_command='cp %p /oracle/pg_data/archive/%f';select pg_reload_conf();select pg_switch_wal();\""
#CMD ["sh", "-c", "/usr/sbin/sshd;sed -i '/flags\+=(\$@)/a flags+=(\"-c\" \"cp %p /oracle/pg_data/archive/%f\")\n' /opt/bitnami/scripts/run.sh; /opt/bitnami/scripts/postgresql/run.sh"]
#CMD ["sh", "-c", "/usr/sbin/sshd;sed -i '/flags\+=(\$@)/a flags+=(\"-c\" \"cp %p /oracle/pg_data/archive/%f\")\n' /opt/bitnami/scripts/run.sh; /opt/bitnami/scripts/postgresql/run.sh"]
#CMD [ "/opt/bitnami/scripts/postgresql/run.sh" ]
