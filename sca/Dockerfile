FROM debian:stretch
LABEL maintainer="chunt" description="Fortify static code analyzer (SCA) image example"

# artifacts should contain:
# 	SCA run file for linux
#	option file for SCA (@see product documentation)
# 	fortify.license file
# 	suitable JDK
ADD artifacts/ /tmp/

# update, install java and fortify
RUN apt-get update -y -qq && \
	mkdir -p /opt/app/java && \
	# TODO: CH this needs to use the jre, not the jdk
	tar -xvf /tmp/jdk-8u161-linux-x64.tar.gz -C /opt/app/java && \
	ln -s /opt/app/java/jdk1.8.0_161/jre/bin/java /usr/bin/java && \
	mkdir -p /opt/app/fortify && \
	# TODO: CH make fortify use a custom jre and not extend debian container
	chmod +x /tmp/Fortify_SCA_and_Apps_18.10_linux_x64.run && \
	./tmp/Fortify_SCA_and_Apps_18.10_linux_x64.run --mode unattended --optionfile /tmp/sca.options
	# TODO: CH install dependencies for jenkins slave install
	#apt install -q apt-transport-https wget vim gnupg2

ENV PATH="${PATH}:/opt/app/fortify/bin"

RUN fortifyupdate && \
	sourceanalyzer --version && \
	rm -rf /tmp/*

CMD ["/bin/bash"]
