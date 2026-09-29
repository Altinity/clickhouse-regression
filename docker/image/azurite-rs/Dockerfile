FROM debian:bookworm-slim

ARG AZURITE_RS_VERSION=v0.1.0-1bc0ba9
ARG TARGETARCH

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/* \
    && arch=${TARGETARCH:-amd64} \
    && curl -fsSL "https://github.com/ClickHouse/azurite-rs/releases/download/${AZURITE_RS_VERSION}/azurite-rs-linux-${arch}.tar.gz" \
        | tar -xz -C /usr/local/bin/ \
    && mv /usr/local/bin/azurite-rs-linux-${arch} /usr/local/bin/azurite-rs \
    && chmod +x /usr/local/bin/azurite-rs

EXPOSE 10000
ENTRYPOINT ["azurite-rs"]
CMD ["--host", "0.0.0.0", "--blob-port", "10000", "--silent", "--in-memory"]
