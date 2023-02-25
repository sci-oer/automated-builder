

ARG BASE_IMAGE=scioer/java-resource:latest
FROM $BASE_IMAGE

LABEL org.opencontainers.version="v1.0.0"
LABEL org.opencontainers.image.authors="Marshall Asch <masch@uoguelph.ca> (https://marshallasch.ca)"
LABEL org.opencontainers.image.url="https://github.com/sci-oer/automated-builder.git"
LABEL org.opencontainers.image.vendor="sci-oer"
LABEL org.opencontainers.image.licenses="GPL-3.0-only"
LABEL org.opencontainers.image.title="Offline Course Resouce"
LABEL org.opencontainers.image.description="A custom build course resource"
LABEL org.opencontainers.image.base.name="registry-1.docker.io/$BASE_IMAGE"

COPY --chown=${UID}:${UID} jupyter /builtin/jupyter/
COPY --chown=${UID}:${UID} practiceProblems /builtin/practiceProblems/
ADD --chown=${UID}:${UID} database.sqlite.tar /opt/wiki/
COPY --chown=${UID}:${UID} lectures /opt/static/lectures/
COPY --chown=${UID}:${UID} motd.txt /scripts/motd.txt

ARG REMOTE_STATIC_SERVER_URL=""
ENV REMOTE_STATIC_SERVER_URL=$REMOTE_STATIC_SERVER_URL

ARG BUILD_DATE
LABEL org.opencontainers.image.created="${BUILD_DATE}"
