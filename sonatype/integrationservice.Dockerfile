FROM openjdk:8-jdk
LABEL maintainer="chunt" description="integration service for Sonatype to Fortify SSC"

ADD artifacts/IntegrationService/* /.work/

WORKDIR /.work/
CMD ["java", "-jar", "/.work/SonatypeFortifyIntegration-20.1.20200914.jar"]
