FROM --platform=$BUILDPLATFORM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /build

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Define build arguments for each platform
ARG BUILDPLATFORM
ARG SATDUMP_VERSION=1.2.2
ARG SATDUMP_RELEASE_FILE_AMD64=satdump_1.2.2_ubuntu_24.04_amd64.deb
ARG SATDUMP_RELEASE_FILE_ARM64=satdump_1.2.2_arm64.deb

# Download and install the correct .deb file based on the build platform
RUN if [ "$BUILDPLATFORM" = "linux/amd64" ]; then \
      curl -L -o satdump.deb "https://github.com/SatDump/SatDump/releases/download/${SATDUMP_VERSION}/${SATDUMP_RELEASE_FILE_AMD64}"; \
    elif [ "$BUILDPLATFORM" = "linux/arm64" ]; then \
      curl -L -o satdump.deb "https://github.com/SatDump/SatDump/releases/download/${SATDUMP_VERSION}/${SATDUMP_RELEASE_FILE_ARM64}"; \
    else \
      echo "Unsupported platform: $BUILDPLATFORM" && exit 1; \
    fi && \
    apt-get install -y --no-install-recommends ./satdump.deb && \
    rm satdump.deb

# Clean up apt cache again
RUN rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["satdump"]
CMD ["--help"]