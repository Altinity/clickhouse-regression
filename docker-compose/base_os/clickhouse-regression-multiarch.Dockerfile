ARG BASE_OS=altinityinfra/clickhouse-regression-multiarch:3.0
FROM $BASE_OS

# Whenever possible, install dependencies in the base image instead of in this one.
# See `docker/image/clickhouse-regression-multiarch/Dockerfile`

RUN ln -s /usr/bin/clickhouse /usr/bin/clickhouse-keeper

RUN export LLVM_VERSION=$(llvm-symbolizer --version | grep -oP '(?<=version )\d+') && \
    echo "Detected LLVM version: ${LLVM_VERSION}" && \
    ln -sf /usr/bin/llvm-symbolizer-${LLVM_VERSION} /usr/bin/llvm-symbolizer && \
    ls -l /usr/bin/llvm-symbolizer

# Fix for 22.x keeper
RUN mkdir -p /var/lib/clickhouse/coordination

ARG CLICKHOUSE_PACKAGE
COPY $CLICKHOUSE_PACKAGE /tmp/

RUN case "$CLICKHOUSE_PACKAGE" in \
  *.deb) \
    apt-get install -y /tmp/*.deb ;; \
  *.tgz) \
    tar xvzf /tmp/*.tgz --strip-components=1 -C / && \
    rm -v /install -r ;; \
  *) \
    cp /tmp/* /usr/bin/ && \
    chmod +x /usr/bin/clickhouse ;; \
  esac && \
  rm -v /tmp/*