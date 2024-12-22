#!/usr/bin/python3

import logging
import sys
import os
import subprocess

# Logging

app_logger : logging.Logger = None

def color_text(color, text):
    return f"\033[{color}m{text}\033[0m"

class ConsoleFormatter(logging.Formatter):
    def __init__(self):
        super().__init__('[%(levelname)s]: %(message)s')

    def format(self, record: logging.LogRecord) -> str:
        if record.levelno >= logging.ERROR:
            record.msg = color_text(91,record.message)
        if record.levelno == logging.WARNING:
            record.msg = color_text(31,record.message)
        return super().format(record)


file_formatter = logging.Formatter('%(asctime)-15s|PID:%(process)-11s|%(levelname)-8s|%(filename)s:%(lineno)s| %(message)s')

file_path = f"{os.path.dirname(os.path.realpath(__file__))}/debug.log"
file_handler = logging.FileHandler(file_path,'w',encoding='utf8')
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(ConsoleFormatter())

rootlog = logging.getLogger()
rootlog.addHandler(file_handler)

app_logger = logging.getLogger('main')
app_logger.propagate = False
app_logger.setLevel(logging.DEBUG)
app_logger.addHandler(file_handler)
app_logger.addHandler(console_handler)

# END Logging

# Utils

def sh(cmd:list[str] | str) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8',
                                shell=False if type(cmd) is list else True)
    app_logger.debug(f'{result}')
    return result

# END Utils

def get_docker_service_text(description,exec):
    return f'''
[Unit]
Description={description}
After=docker.service
After=network.target

[Service]
User=ivan
ExecStart={exec}

[Install]
WantedBy=multi-user.target
'''

def install_ftp(user:str,password:str,local_path:str):
    sh('docker build -t ftp ./ftp')
    exec = f'docker run --rm -i -e FTP_PASS={password} -e FTP_USER={user} --name ftp --publish 20-21:20-21/tcp -p 40000-40009:40000-40009/tcp -v {local_path}:/home/ivan ftp'
    with open('/etc/systemd/system/aig_ftp.service','w+') as f:
        f.write(get_docker_service_text('FTP server',exec))
    sh('systemctl daemon-reload')
    sh('systemctl enable aig_ftp.service')
    sh('systemctl start aig_ftp.service')