FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -yqq \
	libboost-regex1.74.0 \
	libboost-thread1.74.0 \
	libminiupnpc17 \
	libleveldb1d \
	libmaxminddb0

COPY [ "docker-entrypoint.sh", "/" ]
ENTRYPOINT [ "/docker-entrypoint.sh" ]
