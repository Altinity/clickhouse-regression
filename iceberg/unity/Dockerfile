# syntax=docker.io/docker/dockerfile:1.7-labs@sha256:b99fecfe00268a8b556fad7d9c37ee25d716ae08a5d7320e6d51c4dd83246894

# Unity Catalog's released images do not yet include writable Iceberg REST
# endpoints. Build a pinned post-v0.6.0 revision and keep the local S3
# compatibility patch visible and reviewable.
ARG UC_REF=e64816917eca9f3185e47a2b96351b0ad3a82f28
ARG HOME=/home/unitycatalog

FROM amazoncorretto:17-alpine3.20-jdk@sha256:c045f0537bc890f9e61924f33f35e9667f696b4f372dad4a73861a9396b5d0b5 AS build

ARG UC_REF
ARG HOME
ENV HOME=${HOME}
ENV COURSIER_CACHE=${HOME}/.cache/coursier/v1
WORKDIR ${HOME}

RUN apk add --no-cache bash git && \
    git clone --filter=blob:none https://github.com/unitycatalog/unitycatalog.git . && \
    git checkout "${UC_REF}"

COPY minio-static-credentials.patch /tmp/minio-static-credentials.patch
RUN git apply /tmp/minio-static-credentials.patch && \
    ./build/sbt -info clean package

FROM alpine:3.20@sha256:a4f4213abb84c497377b8544c81b3564f313746700372ec4fe84653e4fb03805

ARG HOME=/home/unitycatalog
ARG JAVA_HOME=/usr/lib/jvm/default-jvm
ARG USER=unitycatalog

COPY --from=build ${JAVA_HOME} ${JAVA_HOME}
ENV HOME=${HOME}
ENV JAVA_HOME=${JAVA_HOME}
ENV PATH=${JAVA_HOME}/bin:${PATH}

COPY --from=build --parents \
    ${HOME}/examples/ \
    ${HOME}/server/ \
    ${HOME}/api/ \
    ${HOME}/clients/ \
    ${HOME}/target/ \
    ${HOME}/.cache/ \
    /

RUN apk add --no-cache bash && \
    addgroup -S "${USER}" && \
    adduser -S -G "${USER}" "${USER}" && \
    chmod -R 550 "${HOME}" && \
    mkdir -p "${HOME}/etc" && \
    chmod -R 770 "${HOME}/etc" && \
    chown -R "${USER}:${USER}" "${HOME}"

COPY --from=build --chown=${USER}:${USER} ${HOME}/bin/ ${HOME}/bin/
COPY --from=build --chown=${USER}:${USER} ${HOME}/etc/ ${HOME}/etc/

USER ${USER}
WORKDIR ${HOME}
CMD ["./bin/start-uc-server"]
