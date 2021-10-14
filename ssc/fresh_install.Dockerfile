FROM tomcat:9.0.1
LABEL maintainer="chunt" description="connects SSC to a docker mysql image*requires use of the defined configuration, or customize"

# args; expected that there be a directory named files that contains:
# 	-jdbc jar
#	-ssc.war
#	-fortify.license
#	-ssc.autoconfig (optional)
ARG TMP_DIR=/root/mytemp
ARG TOMCAT_DIR=/usr/local/tomcat
ARG MYSQL_JAR=mysql-connector-java-5.1.35.jar
ARG FORTIFY_HOME=$TOMCAT_DIR/fortify
# fortify ssc home dir (log/conf locations default=/root/.fortify/ssc)
# since TOMCAT_HOME is /usr/local/tomcat, keep it there in its own
# ssc directory struture (including the search_index)
ENV JAVA_OPTS="$JAVA_OPTS -Dfortify.home=$FORTIFY_HOME"

# create temp dir for needed files
RUN mkdir $TMP_DIR/
ADD artifacts/* $TMP_DIR/

# clear out "default" apps that tomcat includes
# put ssc war in webapps dir for deployment
# add database driver jar to tomcat lib
RUN rm -rf $TOMCAT_DIR/webapps/* && \
	mkdir -p $FORTIFY_HOME/ssc/ssc_search_index && \
	mv $TMP_DIR/ssc.war $TOMCAT_DIR/webapps && \
	mv $TMP_DIR/$MYSQL_JAR $TOMCAT_DIR/lib

# cleanup temp dir
RUN rm -rf $TMP_DIR

# still have to use the -p flag on run
EXPOSE 80
