FROM ubuntu:22.04

RUN apt update && apt install -yqq transmission-daemon
COPY [ "docker-entrypoint.sh", "/" ]
ENTRYPOINT [ "/docker-entrypoint.sh" ]