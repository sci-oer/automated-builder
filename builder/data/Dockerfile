
ARG BASE_IMAGE=marshallasch/oo-resources:main
FROM $BASE_IMAGE

LABEL org.opencontainers.version="v1.0.0"
LABEL org.opencontainers.image.authors="Marshall Asch <masch@uoguelph.ca> (https://marshallasch.ca)"
LABEL org.opencontainers.image.url="docker.io/MarshallAsch/sample_container.git"
LABEL org.opencontainers.image.vendor="University of Guelph School of Computer Science"
LABEL org.opencontainers.image.licenses="GPL-3.0-only"
LABEL org.opencontainers.image.title="Offline Course Resouce for my example course"
LABEL org.opencontainers.image.description="A custom built version of the oo-resource image."


COPY jupyter /builtin/jupyter/
COPY lectures /opt/static/lectures/
COPY practiceProblems /builtin/practiceProblems/

ADD database.sqlite.tar /opt/wiki/
#COPY motd.txt /scripts/motd.txt

USER root
RUN chown -R ${UID}:${UID} /opt/static/lectures /opt/wiki
USER ${UNAME}


ARG BUILD_DATE
LABEL org.opencontainers.image.created="${BUILD_DATE}"
