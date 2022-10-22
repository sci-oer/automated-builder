FROM python:3

LABEL org.opencontainers.version="v1.0.0"

LABEL org.opencontainers.image.authors="Marshall Asch <masch@uoguelph.ca> (https://marshallasch.ca)"
LABEL org.opencontainers.image.url="https://github.com/sci-oer/automated-builder.git"
LABEL org.opencontainers.image.source="https://github.com/sci-oer/automated-builder.git"
LABEL org.opencontainers.image.vendor="University of Guelph School of Computer Science"
LABEL org.opencontainers.image.licenses="GPL-3.0-only"
LABEL org.opencontainers.image.title="Offline Course Resouce"
LABEL org.opencontainers.image.description="This image is can be used to build customized oo-resources image. This will generate a customized image with pre seeded data."

ARG VERSION=v0.1.2
LABEL org.opencontainers.image.version="$VERSION"

WORKDIR /app

VOLUME [ "/output" ]

COPY . .

ARG SETUPTOOLS_SCM_PRETEND_VERSION=$VERSION
RUN pip install . && rm -rf builder

ENTRYPOINT [ "./entrypoint.sh" ]

# these two labels will change every time the container is built
# put them at the end because of layer caching
ARG VCS_REF
LABEL org.opencontainers.image.revision="${VCS_REF}"

ARG BUILD_DATE
LABEL org.opencontainers.image.created="${BUILD_DATE}"