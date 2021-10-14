# Blueshift notes

From the Fortify Demo Image 8.0:
1. SSH (or use guacamole) as root user
2. add the /opt/software directory: ```mkdir -p /opt/software```
3. then ```deployToBlueshift.sh upload <blueshift_host> fortify-presales.tar.gz```
4. then ```cd /opt/software && chmod +x centos-blueshift-docker.sh && ./centos-blueshift-docker.sh``` and follow prompts…

This should update the base linux image with docker, docker-compose, sca 18.20, explode out the docker container data directories, and do some yum installs and updates.

For hosts file:
<blueshift_linux_ip> blueshift

Setup Fortify environment:
1. SSH (or use guacamole) as the mfadmin user
2. ```cd ~/bin```
3. ```./fortifySetup.sh setup```
4. ```cd ~/git/fortify```
5. ```cp blueshift.env .env```
6. ```docker-compose up -d```

# run fixes for Blueshift
Jenkins - permissions are jacked with using mounts vs volumes (SELinux?)
1. Use docker-compose to build jenkins container (```docker-compose up -d jenkins```)
2. ```docker exec -it -u root jenkins /bin/bash```
3. ```cd /var```
4. ```chown -R jenkins:jenkins jenkins_home```
5. exit and ```docker restart jenkins```

Controller connection to SSC
1. Log into ssc as admin
2. Go to Administration and update the controller password, save it and restart the ssc container ```docker restart ssc```

# Connections
Connection points (if aliased):
- Jenkins http://jenkins.fortify.com:8080
- SSC http://ssc.fortify.com/ssc
- Controller http://controller.fortify.com:8081\cloud-ctrl

# known issues
- cloudscan controller secret in ssc needs to be manually added (key encryption/salt issue?) and ssc restart
- jenkins home chown issue
- audit assitant auto apply doesnt work - unknown but have done plenty of troubleshooting
- im sure theres more :)
