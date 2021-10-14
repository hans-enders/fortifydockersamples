#!/bin/bash

command sudo yum update -y
command sudo yum install -y yum-utils \
device-mapper-persistent-data \
lvm2 \
git

command sudo yum-config-manager \
--add-repo \
https://download.docker.com/linux/centos/docker-ce.repo

command sudo yum install -y docker-ce

command sudo systemctl start docker
command sudo systemctl enable docker.service

# requires log out/in to take effect, the remainder of the script will not reflect this change and require sudo to run docker.
# once setup is complete, run docker without sudo
command sudo usermod -aG docker chunt

#command sudo docker run --name hellworld hello-world
#command sudo docker rm hellworld
#command sudo docker rmi hello-world:latest

command sudo docker network create \
--subnet 172.18.0.0/16 \
--gateway 172.18.0.1 \
--driver bridge \
-o com.docker.network.bridge.default_bridge=false \
-o com.docker.network.bridge.enable_icc=true \
-o com.docker.network.enable_ip_masquerade=true \
-o com.docker.network.host_binding_ipv4=0.0.0.0 \
-o com.docker.network.name=docker0 \
-o com.docker.network.mtu=9001 \
fortify

#TODO verify github access

cd $HOME
command mkdir -p bin git sscdb/data
cd $HOME/git

command git clone https://github.com/therealchunt/fortify


#TODO verify docker login

#FIXME docker credential-store impl
command sudo docker login

command sudo docker pull chunt/private:ssc18.20-db
command sudo docker pull chunt/private:ssc18.21-web
command sudo docker pull chunt/private:jenkins_base
command sudo docker pull chunt/private:controller18.20
command sudo docker pull chunt/private:sca18.20-jdk-internal
command sudo docker pull chunt/private:sensor18.20
command sudo docker pull chunt/private:sca18.20-jenkins-agent
# windows os cant be used on linux yet
#command sudo docker pull vbisbest/wid

cd $HOME/fortify

command sudo curl -L "https://github.com/docker/compose/releases/download/1.23.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

command sudo chmod +x /usr/local/bin/docker-compose


echo "-------------------------"
echo "    docker setup complete"
command sudo docker --version
command sudo /usr/local/bin/docker-compose --version
echo "-------------------------"
echo "1) copy jenkins_home.tar.gz to $HOME/git/fortify/jenkins/artifacts/ and extract"
echo "2) ssc database"
echo "3) setup .env file (@see sample.env in fortify repo)"
echo "4) add artifacts to ssc/artifacts (seeds, fortify.license, ssc.autoconfig)"
echo "follow instructions from #docker channel on slack"


