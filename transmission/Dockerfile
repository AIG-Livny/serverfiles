FROM ubuntu:22.04

EXPOSE 5601/tcp 51413/udp
RUN apt update && apt install -yqq transmission-daemon
ENTRYPOINT [ "transmission-daemon --logfile /root/.config/transmission-daemon/transmission.log" ]