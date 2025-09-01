# Stage 1: grab bash + the exact libs it needs
FROM debian:stable-slim AS src
RUN apt-get update && apt-get install -y --no-install-recommends bash && rm -rf /var/lib/apt/lists/*
RUN set -e; mkdir -p /rootfs/bin; cp /bin/bash /rootfs/bin/; \
    ldd /bin/bash | awk '{print $3}' | grep -E '^/' \
      | xargs -I{} sh -c 'mkdir -p /rootfs$(dirname {}) && cp {} /rootfs$(dirname {})/'; \
    ldso="$(ldd /bin/bash | awk "/ld-linux/ {print \$1}")"; \
    mkdir -p "/rootfs$(dirname "$ldso")" && cp "$ldso" "/rootfs$ldso"

# Stage 2: final image with a working /bin/bash
FROM altinity/ice:debug-0.6.0
COPY --from=src /rootfs/ /
