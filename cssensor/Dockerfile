FROM chunt/sca:20.1.2-internal
LABEL maintainer="chunt" description="testing as a sensor for scancentral"

ADD artifacts/worker.properties /opt/app/fortify/Core/config/

#ENTRYPOINT scancentral -url http://controller:8080/cloud-ctrl worker
ENTRYPOINT ["scancentral"]
