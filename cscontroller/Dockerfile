FROM tomcat:jdk8-openjdk
LABEL maintainer "chunt" description="cloudscan controller v20.1.0"

# files necessary to build
# - scan central controller software package
# - config.properties (if customized and merged with latest)
# - pwtool-keys (if used)

ARG SC_VERSION=20.1.0
ARG SC_NAME=Fortify_ScanCentral_Controller_${SC_VERSION}_x64
# artifacts directory contains the above files
ADD artifacts/ /tmp/

RUN rm -rf /usr/local/tomcat/webapps/* && \
	mkdir /usr/local/tomcat/jobFiles /usr/local/tomcat/opensource /usr/local/tomcat/client && \
	mv /tmp/${SC_NAME}/tomcat/opensource/* /usr/local/tomcat/opensource/ && \
	mv /tmp/${SC_NAME}/tomcat/client/* /usr/local/tomcat/client && \
#	mv /tmp/pwtool-keys /usr/local/tomcat/ && \
	cp -R /tmp/${SC_NAME}/tomcat/webapps/scancentral-ctrl /usr/local/tomcat/webapps/ && \
	mv /tmp/config.properties /usr/local/tomcat/webapps/scancentral-ctrl/WEB-INF/classes/config.properties && \
	mkdir /fortify && \
	mv /tmp/${SC_NAME}/tomcat/client /fortify && \
	ls -al /usr/local/tomcat/* && \
	ls -al /fortify/* && \
	rm -rf /tmp/*

