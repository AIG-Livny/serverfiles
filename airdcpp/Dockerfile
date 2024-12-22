FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
	LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/app/build/airdcpp-webapi:/app/build/airdcpp-core"

RUN apt update && apt install -yqq \
	libboost-regex1.74.0 \
	libboost-thread1.74.0 \
	libminiupnpc17 \
	libleveldb1d \
	libmaxminddb0

COPY [ "/src/docker-entrypoint.sh", "/" ]
ENTRYPOINT [ "/docker-entrypoint.sh" ]
