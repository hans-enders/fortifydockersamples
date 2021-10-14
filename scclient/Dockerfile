FROM openjdk:8-jdk
LABEL maintainer="chunt" description="base client" usage="requires bind mount:source code 1) source code project root (--mount type=bind,source=<fortify_sca_maven_plugin>/sca-maven/samples/EightBall,target=/project), which is also the working directory"

ARG version=Fortify_ScanCentral_Client_20.2.0_x64
ADD artifacts/${version}.zip /tmp/
ADD artifacts/client.properties /tmp/

ENV JAVA_OPTS="$JAVA_OPTS -Dfortify.home=/root/.fortify"

RUN cd /tmp/ && \
	mkdir -p /fortify /project  && \
	unzip ${version}.zip -d /fortify && \
	mv /tmp/client.properties /fortify/Core/config/ && \
	cd /fortify/bin && \
	chmod +x scancentral
#	fortifyupdate

ENV PATH="$PATH:/fortify/bin"

WORKDIR /project 

#ENTRYPOINT ["scancentral", "-url", "controller:8081/scancentral-ctrl"]
# @see scancentral user guide
# scancentral -url <controller_url> start -bt mvn -bf <custom_pom.xml> -upload -uptoken <ssc_upload_token> --application "appname" -version "1.0"
#ENTRYPOINT ["scancentral"]
# for testing 
#CMD ["/bin/bash"]
