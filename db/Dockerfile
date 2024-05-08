FROM postgres

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
RUN useradd -m ${RM_USER}
RUN echo "${RM_USER}:${RM_PASSWORD}" | chpasswd
#RUN echo -e ${RM_PASSWORD} | passwd ${RM_USER}
RUN usermod -aG postgres ${RM_USER}
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN mkdir -p /oracle/pg_data/archive/
RUN chown ${DB_USER}:postgres /oracle/pg_data/archive
RUN chmod ug+rw /oracle/pg_data/archive
RUN mkdir -p /var/log/postgres
RUN chown ${RM_USER} /var/log/postgres
RUN chmod -R a+wr /var/log/postgres
RUN echo "host replication all 0.0.0.0/0 md5" >> /usr/share/postgresql/16/pg_hba.conf.sample
EXPOSE ${RM_PORT}
CMD sh -c "/usr/sbin/sshd;docker-entrypoint.sh -c max_replication_slots=10 -c max_wal_senders=10 -c wal_level=replica -c archive_command='cp %p /oracle/pg_data/archive/%f' -c log_replication_commands='on' -c log_file_mode=0640 -c log_filename=postgres.log -c wal_log_hints=on -c logging_collector=on -c log_directory=/var/log/postgres/ -c archive_mode=on"
#CMD ["sh", "-c", "/usr/sbin/sshd;sed -i '/flags\+=(\$@)/a flags+=(\"-c\" \"cp %p /oracle/pg_data/archive/%f\")\n' /opt/bitnami/scripts/run.sh; /opt/bitnami/scripts/postgresql/run.sh"]
#CMD ["sh", "-c", "/usr/sbin/sshd;sed -i '/flags\+=(\$@)/a flags+=(\"-c\" \"cp %p /oracle/pg_data/archive/%f\")\n' /opt/bitnami/scripts/run.sh; /opt/bitnami/scripts/postgresql/run.sh"]
#CMD [ "/opt/bitnami/scripts/postgresql/run.sh" ]
