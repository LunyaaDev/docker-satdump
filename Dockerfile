FROM debian:trixie
ENV DEBIAN_FRONTEND=noninteractive

ARG SATDUMP_VERSION=master

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    cmake \
    g++ \
    pkgconf \
    libfftw3-dev \
    libpng-dev \
    libtiff-dev \
    libjemalloc-dev \
    libcurl4-openssl-dev \
    libsqlite3-dev \
    libvolk-dev \
    libnng-dev \
    libzstd-dev \
    libhdf5-dev \
    librtlsdr-dev \
    libhackrf-dev \
    libairspy-dev \
    libairspyhf-dev \
    libad9361-dev \
    libiio-dev \
    libbladerf-dev \
    libomp-dev \
    libarmadillo-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

RUN git clone --branch "${SATDUMP_VERSION}" --depth=1 https://github.com/SatDump/SatDump.git

WORKDIR /build/SatDump

RUN mkdir build

WORKDIR /build/SatDump/build

RUN cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/usr \
    -DBUILD_GUI=OFF \
    ..

# SatDump recommends -j1 on Raspberry Pi 3
RUN make -j1

RUN make install

RUN mkdir -p /data

WORKDIR /data

EXPOSE 8080/tcp
VOLUME /root/.config/satdump/

ENTRYPOINT ["satdump"]
CMD ["--help"]
