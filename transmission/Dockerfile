FROM ubuntu:22.04

RUN apt update && apt install -yqq transmission-daemon
RUN echo 'transmission-daemon -f' >> /docker-entrypoint.sh
ENTRYPOINT [ "/docker-entrypoint.sh" ]