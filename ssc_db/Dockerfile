FROM mysql:5.7
LABEL maintainer="chunt"
LABEL description="mysql database for ssc with recommended settings"
LABEL usage="mount to an existing database"

ARG config

COPY artifacts/config-file.cnf /etc/mysql/conf.d/

EXPOSE 3306
