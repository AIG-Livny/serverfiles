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

def install_ftp(user:str,password:str):
    sh('systemctl stop aig_ftp.service')
    sh('docker build -t ftp ./ftp')
    exec = [
        'docker',
        'run',
        '--rm',
        '-i',
        f'-e FTP_PASS={password}',
        f'-e FTP_USER={user}',
        '--name ftp',
        '--publish 20-21:20-21/tcp',
        '-p 40000-40009:40000-40009/tcp',
        '-v /home/ivan:/home/ivan',
        'ftp'
    ]

    exec = ' '.join(exec)
    with open('/etc/systemd/system/aig_ftp.service','w+') as f:
        f.write(get_docker_service_text('FTP server',exec))
    sh('systemctl daemon-reload')
    sh('systemctl enable aig_ftp.service')
    sh('systemctl start aig_ftp.service')

def install_postgres(user:str,password:str):
    sh('systemctl stop postgres.service')
    os.makedirs('/home/ivan/postgres-base',exist_ok=True)
    exec = [
        'docker',
        'run',
        '--rm',
        '-i',
        '-p 5432:5432',
        '--name pg',
        f'-e POSTGRES_USER={user}',
        f'-e POSTGRES_PASSWORD={password}',
        '-v /home/ivan/postgres-base:/var/lib/postgresql/data',
        'postgres',
    ]
    exec = ' '.join(exec)
    with open('/etc/systemd/system/postgres.service','w+') as f:
        f.write(get_docker_service_text('PostgreSQL server',exec))
    sh('systemctl daemon-reload')
    sh('systemctl enable postgres.service')
    sh('systemctl start postgres.service')

def install_nginx():
    sh('systemctl stop nginx.service')
    os.makedirs('/home/ivan/nginx_content',exist_ok=True)
    exec = [
        'docker',
        'run',
        '--rm',
        '-i',
        '-p 80:80',
        '--name nginx',
        '-v /home/ivan/nginx_content:/usr/share/nginx/html',
        'nginx',
    ]
    exec = ' '.join(exec)
    with open('/etc/systemd/system/nginx.service','w+') as f:
        f.write(get_docker_service_text('Nginx',exec))
    sh('systemctl daemon-reload')
    sh('systemctl enable nginx.service')
    sh('systemctl start nginx.service')

def install_transmission():
    sh('docker build -t transmission ./transmission')
    sh('systemctl stop transmission.service')
    os.makedirs('/home/ivan/dcshare/Downloads',exist_ok=True)
    exec = [
        'docker',
        'run',
        '--rm',
        '-i',
        '-p 5601:5601/tcp',
        '-p 51413:51413/udp',
        '--name transmission',
        '-v /home/ivan/transmission:/root/.config/transmission-daemon',
        '-v /home/ivan/dcshare/Downloads:/Downloads',
        'transmission',
    ]
    exec = ' '.join(exec)
    with open('/etc/systemd/system/transmission.service','w+') as f:
        f.write(get_docker_service_text('Transmission',exec))
    sh('systemctl daemon-reload')
    sh('systemctl enable transmission.service')
    sh('systemctl start transmission.service')

def install_airdcpp():
    sh('docker build -t airdcpp ./airdcpp')
    sh('systemctl stop airdcpp.service')
    os.makedirs('/home/ivan/dcshare/Downloads',exist_ok=True)
    exec = [
        'docker',
        'run',
        '--rm',
        '-i',
        '--name airdcpp',
        '-p 21248:21248/tcp',
        '-p 21248:21248/udp',
        '-p 21249:21249/tcp',
        '-p 5600:5600/tcp',
        '-p 4430:5601/tcp',
        '-v /home/ivan/Downloads:/Downloads',
        '-v /home/ivan/dcshare:/Share',
        '-v /home/ivan/airdcpp-webclient:/app',
        '-v /home/ivan/.airdc++:/root/.airdc++',
        'airdcpp'
    ]
    exec = ' '.join(exec)
    with open('/etc/systemd/system/airdcpp.service','w+') as f:
        f.write(get_docker_service_text('AirDC++ dchub client',exec))
    sh('systemctl daemon-reload')
    sh('systemctl enable airdcpp.service')
    sh('systemctl start airdcpp.service')

def install_telegram_api(api_id:str, api_hash:str):
    sh('systemctl stop telegram-bot-api.service')
    service_text = f'''
[Unit]
Description=Telegram bot API
After=network.target

[Service]
User=ivan
ExecStart=/home/ivan/tg_bots/telegram-bot-api --api-id={api_id} --api-hash={api_hash} --local --dir /home/ivan/tg_bots

[Install]
WantedBy=multi-user.target
'''
    with open('/etc/systemd/system/telegram-bot-api.service','w+') as f:
        f.write(service_text)
    sh('systemctl daemon-reload')
    sh('systemctl enable telegram-bot-api.service')
    sh('systemctl start telegram-bot-api.service')

def install_telegram_recog_bot(token):
    sh('systemctl stop telegram-recog-bot.service')
    service_text = f'''
[Unit]
Description=Telegram Speech Recognition bot
After=telegram-bot-api.service

[Service]
User=ivan
ExecStart=python3 /home/ivan/tg_bots/speech_recog_bot.py {token}

[Install]
WantedBy=multi-user.target
'''
    with open('/etc/systemd/system/telegram-recog-bot.service','w+') as f:
        f.write(service_text)
    sh('systemctl daemon-reload')
    sh('systemctl enable telegram-recog-bot.service')
    sh('systemctl start telegram-recog-bot.service')

def install_telegram_currency_bot(token):
    sh('systemctl stop telegram-currency-bot.service')
    service_text = f'''
[Unit]
Description=Telegram Currency Converter bot
After=telegram-bot-api.service

[Service]
User=ivan
ExecStart=python3 /home/ivan/tg_bots/tgCurrencyConverter_bot.py {token}

[Install]
WantedBy=multi-user.target
'''
    with open('/etc/systemd/system/telegram-currency-bot.service','w+') as f:
        f.write(service_text)
    sh('systemctl daemon-reload')
    sh('systemctl enable telegram-currency-bot.service')
    sh('systemctl start telegram-currency-bot.service')

def install_lenta_set(pg_connect_string):
    sh('systemctl stop mitmproxy.service')
    service_text = f'''
[Unit]
Description=MITM Proxy
After=network.target

[Service]
User=ivan
Environment="PG_CONNECT_STRING={pg_connect_string}"
ExecStart=mitmdump -s /home/ivan/mitm/proxy_script.py

[Install]
WantedBy=multi-user.target
'''
    with open('/etc/systemd/system/mitmproxy.service','w+') as f:
        f.write(service_text)
    sh('systemctl daemon-reload')
    sh('systemctl enable mitmproxy.service')
    sh('systemctl start mitmproxy.service')
    sh('systemctl stop mitmproxy.service')

    sh('systemctl stop lentawalker.service')
    service_text = f'''
[Unit]
Description=Bot Lenta Walker
After=mitmproxy.service

[Service]
User=ivan
Environment="PG_CONNECT_STRING={pg_connect_string}"
ExecStart=python3 /home/ivan/mitm/bot_loader.py

[Install]
WantedBy=multi-user.target
'''
    with open('/etc/systemd/system/lentawalker.service','w+') as f:
        f.write(service_text)
    sh('systemctl daemon-reload')
    sh('systemctl enable lentawalker.service')
    sh('systemctl start lentawalker.service')