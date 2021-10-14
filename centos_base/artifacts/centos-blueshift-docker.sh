#!/bin/bash

BLUESHIFT_YUM_PROXY="http://131.124.54.210:8088\nproxy=http://proxy.mfdemoportal.com:8088"
SOFTWARE_DIR="/opt/software"
tarPkg="fortify-presales.tar.gz"
groupname="fortify"
username="fortify"
JENKINS_TAR="jenkins_volume.tar.gz"
SCA_JENKINS_TAR="sca-jenkins-agent_volume.tar.gz"
SSCDB_TAR="ssc_db.tar.gz"
SCA_RUN_VERSION="Fortify_SCA_and_Apps_18.20_linux_x64.run"
SCA_LICENSE="fortify.license"
SCA_OPTIONS="sca.options"
GIT_URL="https://github.com/therealchunt/fortify"

function pause(){
	read -p "$*"
}

echo "-------------------------------------"
echo "        Fortify Centos Setup         "
echo "-------------------------------------"

echo -e "\nYou will need to enter some values\nduring this script. Some\nare re-printed to the console for validation.\nThere is also some general hand-holding\nrequired, but it should be quick!\nLet's time it...\n"

# update yum conf to add proxy settings - can only test this in blueshift environment
function addYumConfigProxy(){
	echo -e "adding the blueshift proxy info ($BLUESHIFT_YUM_PROXY) to the yum config"
	command echo -e "\n# blueshift proxy configuration\nproxy=$BLUESHIFT_YUM_PROXY" >> /etc/yum.conf
	pause "---sanity check---should see the proxy the last few lines...continue?"
	command cat /etc/yum.conf | grep "proxy"
	pause "---sanity check---if good [Enter] to continue, [ctrl+c] to quit..."
}
function isBlueshift(){
	pause "---sanity check---should see the proxy the last few lines...continue?"
        command cat /etc/yum.conf | grep "proxy"
        echo "Is the proxy configuration already there?"
	select yorn in "Yes" "No"; do
		case $yorn in
			Yes) break;;
			No) addYumConfigProxy;break;;
		esac
	done
}
function envCheck(){
	echo -e "Which environment is this script executed on?\n(Not a trick answer below...)"
	select yOrN in "Blueshift" "Other"; do
		case $yOrN in 
			Blueshift) isBlueshift; break;;
			Other) break;;
		esac
	done
}
# comment out to disable environment checking
envCheck

# BEGIN script functions
options=(
	"yum update and install required libraries"
	"create user and home directories, setup"
	"selinux fix"
	"vnc"
	"install docker"
	"install sca"
	"install docker-compose"
	"create docker network"
	"setup user"
)
function printSelection(){
	# TODO use list or array
	actionA="initial setup"
	actionB="print system config"
	#echo -e "\n---------------------------------------------------"
	#echo -e "***Only use these if setup was interupted or failed"
	#n=1
	#for option in "${options[@]}"; do
        #        echo -e "$n) $option"
	#	n=$[$n + 1]
        #done
	#echo -e "***Only use these if setup was interupted or failed"
	#echo -e "---------------------------------------------------\n"
	echo -e "-----------------------------------------"
	echo -e "a) $actionA"
	echo -e "b) $actionB"
	echo -e "------------------------------------------"
	echo -e "Type 'exit' to quit"
	echo "What would you like to do, a|b or individual options?"
}
function yumupdate(){
	#pause "Press [Enter] to update and install required libraries..."
	command yum update -y
	command yum install -y yum-utils \
		device-mapper-persistent-data \
		lvm2 \
		git \
		vim \
		java-1.8.0-openjdk-devel
		# chunt - i am commenting this out because of RPMDB alteration warnings. i added this because of warnings thrown during docker installation to see if it would address it. there dont seem to be any side effects of the docker warnings as docker runs fine.
		#rpm-build 
	echo -e "\nUpdate and install of required libraries complete."
	#pause "Continue..."
}
function createGroup(){
	echo -e "Creating a new group."
	read -p "Enter new group name: " group
	#echo -e "\nIs this correct? [$group]"
	#pause "Press [Enter] if yes...ctrl+c to cancel"
	command groupadd $group
	command groups
}
function updatePassword(){
	command passwd $1
}
function createUser(){
	echo "Creating a new user"
	read -p "Enter the new user's name(case sensitive): " username
	#echo -e "\nIs this correct? [$username]"
	#pause "Press [Enter] to continue...ctrl+c to cancel"

	# FIXME this sux and needs to be broken out better
	#createGroup
	#read -p "Enter the group for the user." group
	#echo -e "\nIs this correct? [$group]"
	#pause "Press [Enter] if yes...ctrl+c to cancel"
	#echo "Is this group created?"
	#select yorn in "Yes" "No"; do
	#	case $yorn in
	#		Yes) break;;
/	#		No) createGroup;break;;
	#	esac
	#done
	
	command useradd -m $username -g $group
	echo "Would you like to set the password for $username?"
	select yOrN in "Yes" "No"; do
		case $yOrN in
			Yes) updatePassword $username;break;;
			No) break;;
		esac
	done
	echo "creating user bin directory and adding to $username's path"
	command mkdir -p /home/$username/bin
	command chown $username:$group /home/$username/bin
	command usermod -aG wheel $username
	#pause "Press any key to continue..."
}
function printConfig(){
	echo -e "------------------------------------------"
	echo -e "\n---------------------"
	echo "os-release:"
	command cat /etc/os-release
	echo -e "---------------------"
	echo -e "\n---------------------"
	echo "proc/version:"
	command cat /proc/version
	echo -e "---------------------"
	echo -e "\n---------------------"
	echo "uname -a:"
	command uname -a
	echo -e "---------------------"
	echo -e "\n---------------------"
	echo "hostnamectl:"
	command hostnamectl
	echo -e "---------------------"
	echo -e "\n---------------------"
        echo "yum config: blueshift proxy - if set will print"
        command cat /etc/yum.conf | grep "proxy"
        echo -e "---------------------"
	echo -e "\n---------------------"
	echo "sca and java version:"
	command sourceanalyzer -version
	echo -e ""
	command java -version
	echo -e "---------------------"
	echo -e "\n---------------------"
	echo "docker info:"
	command docker --version
	echo -e ""
	command docker-compose --version
	echo -e ""
	command docker images
	echo -e ""
	command docker network ls
	echo -e ""
	command docker volume ls
	echo -e "---------------------"
	echo -e "\n---------------------"
	echo "df -h:"
	command df -h
	echo -e "---------------------"
	echo -e "\n---------------------"
	echo "various directory permissions and contents:"
	command ls -l /opt/data/*
	command ls -l /opt/software/*
	command ls -l /home/mfadmin/*
	echo -e "---------------------"
	echo -e "\n------------------------------------------"
	pause "press any key to continue..."
}
function installSca(){
	echo -e "Installing sca: $SCA_RUN_VERSION"
	command chmod +x $SOFTWARE_DIR/sca/$SCA_RUN_VERSION
	command $SOFTWARE_DIR/sca/$SCA_RUN_VERSION --mode unattended --optionfile $SOFTWARE_DIR/sca/$SCA_OPTIONS	
	echo -e "SCA installed..."
}
function installDocker(){
	echo -e "Installing docker"
	command mkdir -p /opt/app/docker
	command ln -s /opt/app/docker /var/lib/docker
	command yum-config-manager \
	--add-repo \
	https://download.docker.com/linux/centos/docker-ce.repo
	command yum install -y containerd.io docker-ce docker-ce-cli
	command systemctl start docker
	command systemctl enable docker.service
	command sudo usermod -aG docker mfadmin
	echo -e "Docker installed..."
}
function installDockerCompose(){
	echo -e "Installing docker-compose"
	command curl -L "https://github.com/docker/compose/releases/download/1.23.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
	command chmod +x /usr/local/bin/docker-compose
	echo -e "docker-compose installed..."
}
function createFortifyDockerNetwork(){
	echo -e "Creating fortify network in docker"
	command docker network create \
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
	echo -e "Fortify docker network created..."
}
function setupUserHome(){
	echo "Starting user home setup"
	read -p "Please select username: " username
	userHome="/home/$username"
	# this is done in the user setup script @see fortifySetup.sh
	#command cd $userHome
	#command mkdir -p bin git fortify 
	#command cd git
	#command git clone $GIT_URL
	command cd /home/
	command mkdir -p $userHome/bin
	command mv $SOFTWARE_DIR/fortifySetup.sh $userHome/bin/
	command chown -R $username:$username $userHome
	echo "User setup complete."
}
function bye(){
	echo -e "\nMay the schwartz be with you...."
}
function checkFilesPresent(){
	echo "Checking for required files..."
	if [ ! -f "$SOFTWARE_DIR/$tarPkg" ]; then
		echo "$tarPkg not found."
		echo -e "Upload the necessary files and run this script again if needed."
		exit
	fi
	echo "Here we go..."
	echo "Unzipping software package..."
	command cd $SOFTWARE_DIR
	command tar -zxvf $tarPkg
	echo "done..."
	command ls -l $SOFTWARE_DIR/*
	
	#pause "Everything look good?"
}
function createPaths(){
	echo -e "Creating paths and unzipping data into directories."
	command mkdir -p /opt/data/sscdb /opt/data/jenkins /opt/data/sonatype
	
	# change to leverage mounts
	#command cd /opt/data/jenkins
	#command tar -zxvf $SOFTWARE_DIR/jenkins/$JENKINS_TAR
	#command tar -zxvf $SOFTWARE_DIR/jenkins/$SCA_JENKINS_TAR
	command mv $SOFTWARE_DIR/jenkins/*.tar.gz /opt/data/jenkins/
#	command rm -rf $SOFTWARE_DIR/jenkins
	
	command mv $SOFTWARE_DIR/sonatype/*.tar.gz /opt/data/sonatype/
#	command rm -rf $SOFTWARE_DIR/sonatype
	
	command cd $SOFTWARE_DIR/sscdb
	command tar -zxvf $SSCDB_TAR -C /opt/data/sscdb
#	command rm -rf $SOFTWARE_DIR/sscdb
#	command chown -R mfadmin:mfadmin /opt/data
	echo -e "Done creating paths and unzipping data..."
}
function auto(){
	echo -e "--------------------------------------------"
	echo -e "Starting setup of box"
	checkFilesPresent
	createPaths
	yumupdate
	#createUser
	installSca
	installDocker
	installDockerCompose
	createFortifyDockerNetwork
	command docker volume create jenkins
	command docker volume create sca-jenkins-agent
	command docker volume create sonatype-work
	setupUserHome
	# TODO chunt- clean up left over files in software_dir
	echo -e "--------------------------------------------"
	echo -e "Setup complete."
}
# TODO set hostname
# TODO remove selinux
while true; do
	printSelection
	read -p "" action
	#echo "[DEBUG] action: $action"
	case $action in
		1) yumupdate;;
		2) createUser;;
		3) pause "should be se linux fix";;
		4) pause "should be vnc";;
		5) installDocker;;
		6) installSca;;
		7) installDockerCompose;;
		8) createFortifyDockerNetwork;;
		9) setupUserHome;;
		10) pause "should create a group";;
		a) auto;;
		b) printConfig;;
		exit) bye;break;;
		*) echo "Please pick a valid selection";;
	esac
done

#echo "1) setup .env file (@see sample.env in fortify repo)"
#echo "2) add artifacts to ssc/artifacts (seeds, fortify.license, ssc.autoconfig), and other locations"
#echo "follow instructions from #docker channel on slack"
