from concurrent.futures import ThreadPoolExecutor
from struct import pack
import socket
from args import Args


PACKET = b'\x13' + b'\x00' * 39 + b'\x6f\x89\xe9\x1a\xb6\xd5\x3b\xd3' #собираем пакет первый байт 13 нули и последовательность последние 8 байтов: 6f8991a653b3

# смотрим определенный сетевой протокол 
class DNS:
    @staticmethod
    def is_dns(packet: bytes) -> bool:
        transaction_id = PACKET[:2] # первые два байта переданного пакета равны первым двум байтам внутреннего пакета DNS
        return transaction_id in packet


class SNTP:
    @staticmethod
    def is_sntp(packet: bytes) -> bool: #сравнивает метку времени передачи и метку времени изначального запроса
        transmit_timestamp = PACKET[-8:]
        origin_timestamp = packet[24:32]
        is_packet_from_server = 7 & packet[0] == 4
        return len(packet) >= 48 and is_packet_from_server and origin_timestamp == transmit_timestamp  # проверяется определенный бит в первом байте пакета. Если пакет пришел от сервера, то он должен быть длиной не менее 48 байт и содержать сравнение меток времени.


class POP3:
    @staticmethod
    def is_pop3(packet: bytes) -> bool:
        return packet.startswith(b'+') 
# Проверка на начало символа '+' является распространенным способом идентификации POP3 пакетов

class HTTP:
    @staticmethod
    def is_http(packet: bytes) -> bool:
        return b'HTTP' in packet


class SMTP:
    @staticmethod
    def is_smtp(packet: bytes) -> bool:
        return packet[:3].isdigit() # начинается ли переданный пакет с трех цифр
#SMTP-серверы обычно отправляют коды ответов в виде трехзначных чисел

class Scanner: # сканирование портов и определение протоколов
    _PROTOCOL_DEFINER = {
        'SMTP': lambda packet: SMTP.is_smtp(packet),
        'DNS': lambda packet: DNS.is_dns(packet),
        'POP3': lambda packet: POP3.is_pop3(packet),
        'HTTP': lambda packet: HTTP.is_http(packet),
        'SNTP': lambda packet: SNTP.is_sntp(packet)
    }

    def __init__(self, host: str):
        self._host = host

    def tcp_port(self, port: int) -> str: # сканер tcp порта и отпрвление пакета
        socket.setdefaulttimeout(1)
        result = ''
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as scanner:
            try:
                scanner.connect((self._host, port))
                result = f'TCP {port} - Open.'
            except (socket.timeout, TimeoutError, OSError):
                pass
            try:
                scanner.send(pack('!H', len(PACKET)) + PACKET) # пакет данных на подключенный порт + добавляется длина пакета в формате big-endian unsigned short (2 байта).
                data = scanner.recv(1024)
                result += f' {self._check(data)}'
            except socket.error:
                pass
        return result

    def udp_port(self, port: int) -> str: # сканер udp порта и отпрвление пакета
        socket.setdefaulttimeout(3)
        result = ''
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as scanner:
            try:
                scanner.sendto(PACKET, (self._host, port)) 
                data, _ = scanner.recvfrom(1024)
                result = f'UDP {port} - Open. {self._check(data)}'
            except socket.error:
                pass
        return result

    def _check(self, data: bytes) -> str:
        for protocol, checker in self._PROTOCOL_DEFINER.items():
            if checker(data):
                return protocol
        return ''


def main(host: str, start: int, end: int):
    scanner = Scanner(host)
    with ThreadPoolExecutor(max_workers=300) as pool:
        for port in range(start, end + 1):
            pool.submit(execute, scanner, port)


def execute(scanner: Scanner, port: int):
    show(scanner.tcp_port(port))
    show(scanner.udp_port(port))


def show(result: str):
    if result:
        print(result)


if __name__ == "__main__":
    args = Args()
    main(args.host, args.start, args.end)

#sudo python3 scanner.py --host .com  1..1000 
# msu.ru  8.8.8.8