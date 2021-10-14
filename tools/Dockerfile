from fortifydocker/fortify-ci-tools:latest

ARG clientToken

RUN mkdir -p /opt/Core/config && \
	echo "client_auth_token=$clientToken" >> /opt/Core/config/client.properties
	
WORKDIR /opt/src