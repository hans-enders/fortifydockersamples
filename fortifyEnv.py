#!/usr/local/bin/python3

import sys
import os
import subprocess
import getopt
import pathlib
import ntpath
import time
from configparser import ConfigParser, ExtendedInterpolation

config = ConfigParser(interpolation=ExtendedInterpolation())
config.read('env.config')

errorMessages = []
def printError(string, printMe=True):
	message = '[ERROR] ' + str(string)
	errorMessages.append(message)
	if printMe:
		print(message)
	
def printInfo(string):
	print('[INFO] '+str(string))

isSetup = False
isDebug = False
def printDebug(string):
	if isDebug:
		print('[DEBUG] '+str(string))

print('current dir: ', pathlib.Path(__file__).parent.absolute())

# next version
version = '20.2.0'
	
sscdbImage = config.get('sscdb', 'image')
dbEnvs = '--env MYSQL_DATABASE=' + config.get('sscdb', 'dbName') + ' --env MYSQL_USER=' + config.get('sscdb', 'dbUser') + ' --env MYSQL_PASSWORD=' + config.get('sscdb', 'dbUserPw') + ' --env MYSQL_ROOT_PASSWORD=' + config.get('sscdb', 'dbRootPw')
def __build_ssc_db(with_tests=True):
	'''We need to initialize the mysql database with our (recommended) conf. Then seed a temporary
	database in order to fully initialize the mysql container. We then commit the completely initialized 
	mysql image that can mount to any existing data (i.e. docker volume or bind mount to /var/lib/mysql)'''
	# update first-run-Dockerfile to from new _base image
	os.system('docker build -t ' + sscdbImage + '_base --no-cache -f ssc_db/Dockerfile ssc_db/')
	
	tmpDb = 'tmp-sscdb'
	tmpName = 'ssc-db-init'
	os.system('docker volume create ' + tmpDb)
	os.system('docker run --name ' + tmpName + ' --mount type=volume,src=' + tmpDb + ',dst=/var/lib/mysql ' + dbEnvs + ' -d ' + sscdbImage + '_base')	
	
	time.sleep(10)
	
	os.system('docker stop ' + tmpName)
	os.system('docker commit ' + tmpName + ' ' + sscdbImage + '_base')
	#os.system('docker push chunt/ssc-db:' + version + '_base')
	
	os.system('docker build -t ' + sscdbImage + ' --no-cache -f ssc_db/first-run-Dockerfile ssc_db/')
	
	# run ssc-db
	
	os.system('docker run --name ssc-db --mount type=volume,src=ssc-db,dst=/var/lib/mysql ' + dbEnvs  + ' -d ' + sscdbImage)
	time.sleep(45)
	os.system('docker stop ssc-db')
	os.system('docker commit ssc-db ' + sscdbImage)
	#os.system('docker push ' + sscdbImage)
	
	os.system('docker rm ssc-db')
	os.system('docker rm ssc-db-init')
	os.system('docker volume rm tmp-sscdb')
	#os.system('docker rmi ' + sscdbImage + '_base')
	if with_tests:
		pass
		#__runTests()

# Properties
# running on a local network (fortify @see blueshift related scripts for 'docker network create fortify' params
network = '--network=' + config.get('network', 'name')
# IP's for fortify docker network-based local deployment
sscdbIP=config.get('sscdb', 'ipAddr')
sscIP=config.get('ssc', 'ipAddr')
controllerIP=config.get('scancentral-controller', 'ipAddr')

# hosts
sscdbHost=config.get('sscdb', 'hostname') + ':' + sscdbIP
controllerHost=config.get('scancentral-controller', 'hostname') + ':'  + controllerIP
sscHost=config.get('ssc', 'hostname') + ':' + sscIP
sscdbName = 'ssc-db'
def __run_ssc_db():
	# run ssc-db
	os.system('docker run --name ' + sscdbName  + ' -p 3306:3306 ' + 
		network + 
		' --ip ' + sscdbIP + 
		' --mount type=volume,src='+ config.get('sscdb', 'volumeName') +',dst=' + config.get('sscdb', 'mountPath')  + ' ' + 
		dbEnvs + 
		' -d ' + sscdbImage)
	time.sleep(20)

sscImage = config.get('ssc', 'image')
def __build_ssc(with_tests=True):
	os.system('docker build -t ' + sscImage + ' --no-cache -f ssc/Dockerfile ssc/')

edastHost='edast:'+config.get('scancentral-dast', 'ipAddr')
sscHosts = '--add-host ' + sscdbHost + ' --add-host ' + controllerHost + ' --add-host ' + edastHost
sensor2IP='172.18.0.8'
sscName = 'ssc-web'
def __run_ssc():
	os.system('docker run --name ' + sscName  + ' -p 80:8080 --ip ' +
		sscIP + ' ' +
		sscHosts + ' ' + 
		network + 
		' -d ' + sscImage)
	time.sleep(30)

controllerHosts = '--add-host ' + sscHost
controllerImage = config.get('scancentral-controller', 'image')
controllerName = 'controller'
sensor1Name = 'sensor1'
sensor2Name = 'sensor2'
def __build_controller():
	os.system('docker build -t ' + controllerImage + ' --no-cache sccontroller/')
	time.sleep(10)

scaImage = config.get('sca', 'image')
sensorImage = config.get('scancentral-sast-sensor', 'image')
def __build_sca():
	os.system('docker build --tag ' + scaImage + ' --no-cache --build-arg scaRun='+ config.get('sca', 'runFile') + ' -f sca/sca-jdk-internal sca/')
	os.system('docker build --tag ' + sensorImage + ' --no-cache scsensor/')

scClientImage=config.get('scancentral-client', 'image')
def __buildScanCentralClient():
	os.system('docker build --tag ' + scClientImage + ' --no-cache -f scclient/Dockerfile scclient/')
	#os.system('docker run --rm --name test-scclient -it ' + scClientImage + ' ls -al /fortify/Core/config')
	os.system('docker build --tag ' + scClientImage + '_mvn --no-cache -f scclient/maven-Dockerfile scclient/')

def __run_controller():
    os.system('docker run --name ' + controllerName + ' -p 8081:8080 --ip ' +
        controllerIP + ' ' +
        controllerHosts + ' ' + 
        network + 
        ' -d ' + controllerImage)
    time.sleep(30)
    os.system('docker run -it --name ' + sensor1Name + 
        ' --hostname sca1 ' + network +
	' --add-host ' + controllerHost +
        ' -d ' + sensorImage + 
        ' --url ' + config.get('scancentral-sast-sensor', 'url') + ' worker')
    os.system('docker run --name ' + sensor2Name + 
        ' --hostname sca2 ' + network +
	' --add-host ' + controllerHost +
        ' --memory=6g' +
        ' -d ' + sensorImage + 
        ' --url ' + config.get('scancentral-sast-sensor', 'url') + ' worker')

jenkinsImage=config.get('jenkins', 'image')
jenkinsName='jenkins'
def __buildJenkins():
	os.system('docker build --tag chunt/private:jenkins-dind -f jenkins/jenkins-dind --no-cache jenkins')

jenkinsIP=config.get('jenkins', 'ipAddr')
jenkinsHosts='--add-host ' + sscHost + ' --add-host ' + edastHost
jenkinsPorts=config.get('jenkins', 'ports')
def __runJenkins():
	#run jenkins
	os.system('docker run --name ' + jenkinsName + 
	' --hostname ' + jenkinsName + ' ' + network +
	' --ip ' + jenkinsIP +
	' -v ' + config.get('jenkins', 'volumeName') + ':' + config.get('jenkins', 'mountPath') +
	' -v /var/run/docker.sock:/var/run/docker.sock' +
	' -p ' + jenkinsPorts + ':8080 -p 5000:5000 -p 4243:4243 ' +
	jenkinsHosts +
	' -d ' + jenkinsImage)

def __backupJenkins():
	pass
	# backup
	# start jenkins, dont create if not found
	# __startContainer(jenkinsName, createIfNotFound=False)
	#os.system('docker run --rm --volumes-from ' + jenkinsName + ' -v presales-distro/jenkins/backup:/backup ubuntu tar cvfz /backup/jenkins-docker.tar.gz /var/jenkins_home')
	

def __restoreJenkins():
	# restore from backup
	newVolNome = 'jenkins-bkp'
	os.system('docker run --rm -it -v '+config.get('jenkins', 'volumeName')+':/var/jenkins_home --name ubuntu -d ubuntu /bin/bash')
	time.sleep(5)
	os.system('docker run --rm --volumes-from ubuntu -v /home/chunt/git/fortify/presales-distro/jenkins:/restore -d ubuntu bash -c "cd /var && tar xvfz /restore/jenkins-docker.tar.gz --strip 1"')
	#os.system('docker rm jenkins-restore')

richesName='riches'
def __runRiches():
	os.system('docker run --name '+ richesName + ' ' + network +' --hostname riches' +
			' -p 81:8080 --memory=4g' +
			' -v riches:/usr/local/tomcat/WI_Agent/log' +
			' -d chunt/private:riches-wia18.20')

def __printImages(images):
	printInfo('----Fortify and chunt docker repo related images (filtered)----')
	for i in images:
		# only print specific ones
		if 'fortify' in i or 'chunt' in i:
			printInfo('\t\t'+i)

f3containers = [sscdbName, sscName, controllerName, sensor1Name, sensor2Name, jenkinsName, richesName]
def __getAllContainers():
	dpsA = subprocess.check_output(['docker', 'ps', '--format', '{{.Names}}', '-a'])
	return dpsA.decode('UTF-8').split('\n')
	
def __getExitedContainers():
	dpsE = subprocess.check_output(['docker', 'ps', '--filter', 'status=exited', '--format', '{{.Names}}'])
	return dpsE.decode('UTF-8').split('\n')

def __getRunningContainers():
	dps = subprocess.check_output(['docker', 'ps', '--format', '{{.Names}}'])
	return dps.decode('UTF-8').split('\n')

volumeList = ['ssc-db','jenkins']
def __checkVolumes():
	dvls = subprocess.check_output(['docker', 'volume', 'ls', '-q'])
	volumes = dvls.decode('UTF-8').split('\n')
	_compare(volumeList, volumes, 'volume')
	if 'ssc-db' not in volumes:
		printError('ssc-db volume not found. you need to create the ssc-db docker volume and populate it')
		sys.exit(2)
	printDebug('required volume(s) check complete')
	return True
    
# Linux
toolsImage = 'fortifydocker/fortify-ci-tools:latest'
dtrackImage = 'owasp/dependency-track:latest'
sonatypeImage = 'sonatype/nexus-iq-server:latest'
sscwebImage = 'fortifydocker/ssc-webapp:20.2.0.0149'
richesImage = 'fortifydocker/riches:latest'
aaWebImage = 'fortifydocker/audit-assistant-webapp:19.2.1.0023'
aaDaemonImage = 'fortifydocker/audit-assistant-daemon:19.2.1.0023'
aaInstallImage = 'fortifydocker/audit-assistant-install:19.2.1.0023'
aaDataImage = 'fortifydocker/audit-assistant-data:2019.12.0002'
scaImage = 'chunt/sca:20.2.0-internal'
# Windows
dastControllerImage = 'fortifydocker/scancentral-dast-globalservice:latest'
dastApiImage = 'fortifydocker/scancentral-dast-api:latest'
limImage = 'fortifydocker/lim:latest'
webinspectImage = 'fortifydocker/webinspect:latest'
winImageList = [dastControllerImage,dastApiImage,limImage,webinspectImage]
imageList = [sscdbImage,sscImage,controllerImage,sensorImage,toolsImage,jenkinsImage,
    dtrackImage,sonatypeImage,richesImage,scaImage]
def __checkImages():
	di = subprocess.check_output(['docker', 'images', '--format', '{{.Repository}}:{{.Tag}}'])
	images = di.decode('UTF-8').split('\n')
	_compare(imageList, images, 'image')
	printDebug('required image(s) check complete')
	return True
	
def _compare(required, test, comparator):
	for i in required:
		if i in test:
			printDebug(i + ' ' + comparator + ' found')
		else:
			m = i + ' ' + comparator + ' is missing...'
			if 'image' == comparator:
				if isSetup:
					printInfo(i + ' image was not found, pulling...')
					os.system('docker pull ' + i)
				else:
					m+= '\n\trun "docker pull ' + i + '"'
					printError(m, printMe=False)
			elif 'volume' == comparator:
				m+= '\n\trun "docker volume create ' + i + '"'
				printError(m, printMe=False)

fortifyNetwork = ('docker network create ' +
	'--subnet 172.18.0.0/16 ' + 
	'--gateway 172.18.0.1 ' +
     '--driver bridge ' +
     '-o com.docker.network.bridge.default_bridge=false ' +
     '-o com.docker.network.bridge.enable_icc=true ' +
     '-o com.docker.network.enable_ip_masquerade=true ' +
     '-o com.docker.network.host_binding_ipv4=0.0.0.0 ' +
     '-o com.docker.network.name=docker0 ' +
     '-o com.docker.network.mtu=9001 ' +
     'fortify')
def __checkNetwork():
	dn = subprocess.check_output(['docker', 'network', 'ls', '--format', '{{.Name}}'])
	networks = dn.decode('UTF-8').split('\n')
	if 'fortify' not in networks:
		if isSetup:
			os.system(fortifyNetwork)
			printError('fortify network not found, an attempt was made to create it\n\tif not successful, manually run "'+ fortifyNetwork +'"', printMe=False)
		else:
			printError('fortify network not setup.\n\trun "'+ fortifyNetwork +'"', printMe=False)
	else:
		printDebug('required network(s) found')

def __check_system():
    printInfo('Checking system configuration....')
    dVersion = subprocess.check_output(['docker', '--version'])
    dv = dVersion.decode('UTF-8').split('\n')[0]
    if 'Docker version' not in dv:
        printError('docker is not installed')
        sys.exit(2)

    printDebug(dv)
    #printInfo('Docker network(s)...')
    printInfo('Looking for required docker network...')
    __checkNetwork()
    
    #printInfo('Docker volumes(s)...')
    printInfo('Looking for required docker volumes...')
    __checkVolumes()
	
    #printInfo('Docker images(s)...')
    printInfo('Looking for required docker images...')
    __checkImages()
	
    printDebug('windows images: ' + str(winImageList))
    
	#__k8PrintInfo()
	
    if len(errorMessages) > 0:
        print('\n\nSystem checks failed. Correct these issues:')
        __printErrorMessages()
        sys.exit(2)
	
    if isSetup:
        printInfo('setup complete.')
    else:
        printInfo('system checks good')

def _handleRun(removeContainers=False, withInfo=False):
	if withInfo:
		__printImages()
	__check_system()
	sscDbStarted = False
	sscStarted = False
	controllerStarted = False
	sensor1Started = False
	sensor2Started = False
	richesStarted = False
	jenkinsStarted = False
	
	printDebug('Check running containers....')
	rcs = __getRunningContainers()
	
	if sscdbName in rcs:
		printInfo(sscdbName + ' is running')
		sscDbStarted = True
	else:
		printInfo(sscdbName + ' not running, attempting to start...')
		__startContainer(sscdbName)
	
	if sscName in rcs:
		printInfo(sscName + ' running')
		sscStarted = True
	else:
		printInfo(sscName + ' not running...')
		__startContainer(sscName)
	
	if controllerName in rcs:
		printInfo('scan central controller running')
		controllerStarted = True
	else:
		printInfo(controllerName + ' not running...')
		__startContainer(controllerName)
		time.sleep(10)
	
	# chunt - the controller needs to be fully started prior to
	# starting the sensors
	# TODO check that the controller is operational before attempting to start sensors
	if 'sensor1' in rcs:
		printInfo('scan central sensor1 running')
		sensor1Started = True
	else:
		printInfo('scan central sensor1 not running...')
		__startContainer('sensor1')
	
	if 'sensor2' in rcs:
		printInfo('scan central sensor2 running')
		sensor2Started = True
	else:
		printInfo('scan central sensor2 not running...')
		__startContainer('sensor2')
	
	if jenkinsName in rcs:
		printInfo(jenkinsName + ' running')
		jenkinsStarted = True
	else:
		printInfo(jenkinsName + ' not running...')
		__startContainer(jenkinsName)
	
	if richesName in rcs:
		printInfo(richesName + ' running')
		richesStarted = True
	else:
		printInfo(richesName + ' not running... use --run-riches option to start')
		#__startContainer(richesName)
	__printHelpInfo()
	
# stop ssc-db
retries = 0
retryLimit = 5
def __handleStopSscDb():
	global retries
	printInfo('handling stopping ssc-db')
	if retries >= retryLimit:
		printError('Retry limit of shutting down ' + sscdbName + ' reached. You may need to manually stop the ssc container.')
		sys.exit(2)
	
	if sscName not in __getAllContainers():
		os.system('docker stop ' + sscdbName)
		return

	if sscName not in __getExitedContainers():
		printInfo('Stopping ' + sscdbName + ' however ssc is still running. Sleeping...')
		time.sleep(5)
		retries += 1
		__handleStopSscDb()
	
	os.system('docker stop ' + sscdbName)

def __stopContainer(name):
	printInfo('stopping ' + name)
	if sscdbName == name:
		__handleStopSscDb()
	os.system('docker stop ' + name)
	
def _handleStop():
    printInfo('Stopping related containers...')
    for c in reversed(f3containers):
        if sscdbName == c:
            __handleStopSscDb()
        else:
            __stopContainer(c)
			
def __startContainer(name, createIfNotFound=True):
	printInfo('attempting to start ' + name + ' container...')
	
	if name in __getExitedContainers():
		printInfo(name + ' container found. starting...')
		os.system('docker start ' + name)
		if sscName == name:
			time.sleep(25)
		elif controllerName == name:
			time.sleep(15)
	elif createIfNotFound:
		printDebug(name + ' container was not found, creating...')
		if sscName == name:
			__run_ssc()
		elif sscdbName == name:
			__run_ssc_db()
		elif controllerName == name:
			__run_controller()
		elif 'sensor1' == name or 'sensor2' == name:
			
			printInfo('docker run needed for: ' + name)
		elif jenkinsName == name:
			__runJenkins()
		elif richesName == name:
			__runRiches()
	else:
		printError(name + ' container was not found and it was not set to be automatically created')
		sys.exit(2)

def __printErrorMessages():
	if len(errorMessages) > 0:
		for m in errorMessages:
			print(m)

def __printHelpInfo():
	print('\n-----Access-----\nSSC: http://<ipaddress>:80/ssc\nScan Central Controller: http://<ipaddress>:8081/scancentral-ctrl')
	print('\n-----Helpful commands-----\ndocker exec -it ssc-web tail -f /usr/local/tomcat/fortify/ssc/logs/ssc.log\ndocker start|stop <containerName>\ndocker exec -it controller tail -f /usr/local/tomcat/logs/scancentralCtrl.log')

setupMessage = '\n\tsetup\t\t\tattempts to setup your docker environment\n\t\t\t\t(currently will create the docker network\n\t\t\t\tand pull required images)'
debugMessage = '\n\tdebug\t\t\truns in debug mode'
checkSysMessage = '\tcheck-system\t\tchecks system configuration'
startMessage = '\tstart\t\t\tstarts all the fortify docker containers'
stopMessage = '\tstop\t\t\tstops all the fortify docker containers'
helpMessage = '\thelp\t\t\tshows this help menu'
buildMessage = '\tbuild\t\t\t**This can mess your stuff up!**will build all the images for a new version update'
releaseMessage = '\trelease\t\t\tused in conjunction with build'
messages = [setupMessage, checkSysMessage, startMessage, stopMessage, debugMessage, helpMessage, buildMessage, releaseMessage]
def _printHelp():
    print('\nOptions[--debug, --check-system, --setup, --start, --stop, --build-db, --run-db, --build-ssc, --help]:')
    for m in messages:
        print(m)
    __printHelpInfo()
    print('\n***if using docker-compose to start your images, it is not recommended to use this script to start or stop your docker environment***\n\t1) copy the sample.env file to .env\n\t2) update the paths in .env\n\t3) run "docker-compose up -d ssc controller"')

# 'k8-start', 'k8-stop', 'k8-info'
aOpts = ['setup', 'debug', 'start', 'stop', 'check-system', 'build', 'release', 'build-db', 'build-ssc', 'build-controller', 'build-scclient', 'build-sca', 'run-scclient', 'run-jenkins', 'restore-jenkins', 'build-jenkins', 'run-riches', 'help']
opts, args = getopt.getopt(sys.argv[1:],'', aOpts)
printDebug('opts: ' + str(opts))
# set debug if it is in the options
for opt in opts:
	if '--debug' in opt:
		isDebug = True
		printDebug('setting debug to true and removing opt')
		opts.remove(opt)

l = [i for i, v in enumerate(opts) if v[0] == '--setup']
if len(l) > 0:
    printInfo('Setting up fortify docker environment...')
    isSetup = True
    __check_system()
    
    isSetup = False
    __check_system()
    
    printInfo('***if using docker-compose to start your images, it is not recommended to use this script to start/stop your environment***\n\t1) copy the sample.env file to .env\n\t2) update the paths\n\t3) run "docker-compose up -d ssc controller"')
    sys.exit(0)

for opt, arg in opts:
	if opt == '--check-system':
		__check_system()
		sys.exit(0)
	if opt == '--start':
		_handleRun()
		__printErrorMessages()
		sys.exit(0)
	if opt == '--stop':
		_handleStop()
		__printErrorMessages()
		printInfo('shutdown complete')
		sys.exit(0)
	if opt == '--release':
		os.system('docker push ' + sscdbImage + '_base')
		os.system('docker push ' + sscdbImage)
		os.system('docker push ' + sscImage)
		os.system('docker push ' + controllerImage)
		os.system('docker push ' + scaImage)
		os.system('docker push ' + sensorImage)
	if opt == '--build':
		printInfo('removing containers and images in order to rebuild')
		_handleStop()
		for c in f3containers:
			os.system('docker rm ' + c)
		os.system('docker rmi ' + sscdbImage)
		os.system('docker rmi ' + sscImage)
		os.system('docker rmi ' + controllerImage)
		os.system('docker rmi ' + scaImage)
		os.system('docker rmi ' + sensorImage)
		
		os.system('docker volume rm ' + sscdbName)
		os.system('docker volume create ' + sscdbName)
		
		__build_ssc_db(with_tests=True)
		__build_ssc()
		__build_controller()
		__build_sca()
		printInfo('Hopefully everything went well. later... :) ... (: ...')
		sys.exit(0)
	if opt == '--run-riches':
		__runRiches()
		sys.exit(0)
	if opt == '--run-jenkins':
		__runJenkins()
		sys.exit(0)
	if opt == '--restore-jenkins':
		__restoreJenkins()
		sys.exit(0)
	if opt == '--build-jenkins':
		__buildJenkins()
		sys.exit(0)
	if opt == '--build-controller':
		__build_controller()
		sys.exit(0)
	if opt == '--build-scclient':
		os.system('docker rmi ' + scClientImage)
		os.system('docker rmi ' + scClientImage+'_mvn')
		__buildScanCentralClient()
		sys.exit(0)
	if opt == '--run-scclient':
		#printInfo('docker run ' + network + ' --add-host ' + controllerHost + ' -v <src>:/project -d ' + scClientImage + ' -url http://' + controllerName + ':' + config.get('scancentral-controller', 'internalPorts') +'/scancentral-ctrl <options>')
		
# riches source scan
	#	os.system('docker run --rm ' + network + ' --add-host ' + controllerHost + ' -v client-logs:/root/.fortify/scancentral/log -v /home/chunt/git/fortify/riches/riches-src:/project -it ' + scClientImage + ' scancentral -url http://' + controllerName + ':' + config.get('scancentral-controller', 'internalPorts') +'/scancentral-ctrl start -bt none -upload -uptoken 1bcdf321-c9f7-4abd-9103-627c187b06c6 --application-version-id 2')
# eightball source scan
	#	os.system('docker run --rm ' + network + ' --add-host ' + controllerHost + ' -v client-logs-mvn:/root/.fortify/scancentral/log -v /home/chunt/git/Eightball:/project -it ' + scClientImage + '_mvn scancentral -url http://' + controllerName + ':' + config.get('scancentral-controller', 'internalPorts') +'/scancentral-ctrl start -bt mvn -upload -uptoken 1bcdf321-c9f7-4abd-9103-627c187b06c6 --application-version-id 3')
#--application \'riches\' --application-version \'1.0\'')
		sys.exit(0)
	if opt == '--build-db':
		__build_ssc_db(with_tests=True)
		sys.exit(0)
	if opt == '--build-ssc':
		__build_ssc()
		sys.exit(0)
	if opt == '--build-sca':
		__build_sca()
		sys.exit(0)
	if opt in ('--help','-h'):
		_printHelp()
