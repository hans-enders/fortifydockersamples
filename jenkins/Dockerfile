from jenkins/jenkins:lts
LABEL maintainer="chunt" description="base jenkins"

ADD artifacts/plugins.txt /usr/share/jenkins/ref/

user root

RUN apt-get update -y && \
	/usr/local/bin/install-plugins.sh < /usr/share/jenkins/ref/plugins.txt

ENV JENKINS_USER admin
ENV JENKINS_PASS admin
ENV JAVA_OPTS -Djenkins.install.runSetupWizard=false

ADD artifacts/init.groovy.d/* /usr/share/jenkins/ref/init.groovy.d/

user jenkins

EXPOSE 8080 50000 4243
