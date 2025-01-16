import socket
import argparse # для обработки аргументов командной строки

from timestamp import Timestamp
from sntp import SNTP


class Client:
    def __init__(self, ntp_server: str):
        self._client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP для общения с сервером
        self._ntp_server = ntp_server

    def run(self):
        data = SNTP.CLIENT_REQUEST # данные для отправки на сервер
        self._client.sendto(data.encode('utf-8'), (self._ntp_server, 123)) 
        data, address = self._client.recvfrom(1024)  #  ответ от сервера
        if data:
            print(f'Response received from: {address[0]}:{address[1]}')
        timestamp = SNTP.time_from_client_answer(data)
        time = Timestamp.normal_time(timestamp)  #  время в удобный формат
        print(f'\treceived time: {time}')


def parse_args() -> argparse.Namespace: # парсим данные из cmd
    parser = argparse.ArgumentParser(description='SNTP client')
    parser.add_argument('server', type=str, help='ntp server to request current time') # аргумент для указания сервера
    return parser.parse_args()


def start():
    args = parse_args()
    client = Client(args.server)
    client.run()


if __name__ == '__main__':
    start()

# cd /Users/mac/Desktop/python_23_24    
# sudo python3 sntp_client.py localhost  
# sudo python3 sntp_server.py -d 
# 3153600000 100 лет    -
# 315360000 10 лет      +-
# 31536000 1 год        +-
# 157680000 5-6 лет     +
# 86400 1 день          +-