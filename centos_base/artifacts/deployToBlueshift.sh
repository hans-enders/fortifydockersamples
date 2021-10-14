#!/bin/bash

HOST=
SOFTWARE_DIR=/opt/software
tarPkg=
function uploadArtifacts(){
	command scp fortify.sh $HOST:/etc/profile.d/
	command scp centos-blueshift-docker.sh \
		$tarPkg \
		$HOST:$SOFTWARE_DIR/
}
print_help(){
        echo -e "\nExample usage:\n\t $0 [option] <host> <fortify-presales.tar.gz>"
	echo -e "One option required $0 [upload]"
        echo -e "\tupload\t\tUpload artifacts needed for the blueshift image."
	echo -e "\ntar.gz should contain necessary files for setup"
	echo -e "\t*<host> can be defined in .ssh/config or manually entered as <user>@<ip>"
}
case $1 in
        upload) HOST=$2; tarPkg=$3;uploadArtifacts;;
        *) print_help; exit 1;;
esac
