FROM postgres
ARG MDB_HOST
ARG MREPL_USER
ARG MDB_PORT
ENV MDB_HOST ${MDB_HOST}
ENV MREPL_USER ${MREPL_USER}
ENV MDB_PORT ${MDB_PORT}
#CMD bash -c "until pg_basebackup -R --host=${DB_HOST} -U ${REPL_USER} --port=${DB_PORT}\ndo\necho 'Waiting for primary to connect...'\nsleep 1s\ndone\necho 'Backup done, starting replica...'\npostgres"
USER postgres
CMD bash -c "until pg_basebackup -R --host='${MDB_HOST}' -U ${MREPL_USER} --port=${MDB_PORT} --pgdata=/var/lib/postgresql/data -P; do echo 'Waiting for primary to connect...'; sleep 1s; done;chmod 0700 /var/lib/postgresql/data; echo 'Backup done.';postgres"
