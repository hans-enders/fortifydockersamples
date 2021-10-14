FROM tomcat:9.0.1
LABEL maintainer "chunt"

#args used during building of this image
ARG MY_FILES_DIR=files
ARG TMP_DIR=/root/mytemp
ARG WI_AGENT="Fortify_WebInspect_Runtime_Agent_Java_18.4"
ARG WI_AGENT_TAR="$WI_AGENT.tar.gz"
ARG TOMCAT_DIR=/usr/local/tomcat
ARG WI_AGENT_DIR=/usr/local/tomcat/WI_Agent

#create temp dir for needed files
RUN mkdir $TMP_DIR/
COPY $MY_FILES_DIR/* $TMP_DIR/

#clear out "default" apps that tomcat includes
#put riches war in webapps dir
#setup for webinspect agent
RUN rm -rf $TOMCAT_DIR/webapps/* && \
	mv $TMP_DIR/riches.war $TOMCAT_DIR/webapps && \
#	tar -xvf $TMP_DIR/$WI_AGENT_TAR -C $TOMCAT_DIR/ && \
#	mv $WI_AGENT/ WI_Agent && \
#	mkdir $TOMCAT_DIR/WI_Agent/log && \
#	sed -i '264i\ #WI Agent installation for Riches demo' $TOMCAT_DIR/bin/catalina.sh && \
#	sed -i '265i \CATALINA_OPTS=" -javaagent:$CATALINA_HOME/WI_Agent/lib/FortifyAgent.jar $CATALINA_OPTS"' $TOMCAT_DIR/bin/catalina.sh && \
	rm -rf $TMP_DIR
