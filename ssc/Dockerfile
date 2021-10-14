FROM tomcat:jdk8-openjdk
LABEL maintainer="chunt" description="connects SSC to a docker mysql image*requires use of the defined configuration, or customize"

# args; expected that there be a directory named files that contains:
#	-ssc.war
#	-fortify.license
#	-Seed/Process Bundles
#	-ssc.autoconfig (optional)

# fortify ssc home dir (log/conf locations default=/root/.fortify/ssc)
# keep it with TOMCAT_HOME in its own ssc directory struture
ENV JAVA_OPTS="$JAVA_OPTS -Dfortify.home=/usr/local/tomcat/fortify"

# create temp dir for needed files
RUN mkdir /root/mytemp
COPY artifacts/* /root/mytemp/

# clear out "default" apps that tomcat includes
# put ssc war in webapps dir for deployment
# add database driver jar to tomcat lib
# (optional) add ssc.autoconfig file to ssc.home
RUN rm -rf /usr/local/tomcat/webapps/* && \
	mkdir -p /usr/local/tomcat/fortify/ssc/ssc_search_index && \
	mv /root/mytemp/ssc.war /usr/local/tomcat/webapps && \
	#mv /root/mytemp/mysql-connector-java-5.1.35.jar /usr/local/tomcat/lib && \
	mv /root/mytemp/* /usr/local/tomcat/fortify && \
	rm -rf /root/mytemp

