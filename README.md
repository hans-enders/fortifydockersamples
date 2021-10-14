# Fortify environment

Attempt at creating an automated way to create a typical fortify environment. (this does all the linux-based docker images; ssc-db,ssc,sast-scancentral-controller,sast-sensor,jenkins,sonatype, etc...)
```python3 fortifyEnv.py --help```:
```
Options[--debug, --check-system, --setup, --start, --stop, --build-db, --run-db, --build-ssc, --help]:

        setup                   attempts to setup your docker environment
                                (currently will create the docker network
                                and pull required images)
        check-system            checks system configuration
        start                   starts all the fortify docker containers
        stop                    stops all the fortify docker containers

        debug                   runs in debug mode
        help                    shows this help menu
        build                   **This can mess your stuff up!**will build all the images for a new version update
        release                 used in conjunction with build

-----Access-----
SSC: http://<ipaddress>:80/ssc
Scan Central Controller: http://<ipaddress>:8081/scancentral-ctrl

-----Helpful commands-----
docker exec -it ssc-web tail -f /usr/local/tomcat/fortify/ssc/logs/ssc.log
docker start|stop <containerName>
docker exec -it controller tail -f /usr/local/tomcat/logs/scancentralCtrl.log
```

***if using docker-compose to start your images, it is not recommended to use the python script to start or stop this environment***
1) copy the sample.env file to .env
2) update the paths in .env
3) ```docker-compose up -d ssc controller```   

# Building images
This is currently migrated to the fortifyEnv.py


# Blueshift updates (2-22-2019) - see README.md in fortify/centos_base for execution steps
There are scripts in centos_base to deploy to azure and blueshift environments. Use these if you want to deploy out your own environment, see how things are setup, test feature/functionality in an integrated environment. In onedrive is a 3+GB tar.gz (fortify-presales.tar.gz) of an sscdb, jenkins home, sca-jenkins-agent home along with Sonatype, SCA 18.20 and a few other scripts, that are all uploaded to blueshift via a deployToBlueshift script. I will add a README in there to describe this process further. Gist is, run a few scripts, then ```docker-compose up -d```.

*You will likely have to start the sca-jenkins-agent container after all the other services are started, havent figured out the delay start for this yet.*

# Building your own custom images
```docker-compose up <service>``` will build images that have the ```build:``` parameter if they are not downloaded. You will want to change the names (.env) for the images to not conflict and/or have accidental overwrites.
