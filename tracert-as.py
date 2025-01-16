import socket
import sys
from socket import timeout
import re

udp_port = 34434
ttl = 45
local_host = "" #адрес 

def main():
    address = sys.argv[1] #считывает название файла
    # icmp_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
    # print (address)
    traceroute(address)

def whois(address_marshrutizatora):
     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        who = socket.gethostbyname("whois.ripe.net")
        s.connect((who,43)) #обращаемся к whois
        s.sendall(b"%b\n" % address_marshrutizatora.encode("utf-8"))
        message = b""
        while True:
            stroka = s.recv(2024)
            message += stroka # считывание сообщения (по 2024 байта)
            if stroka == b"":
                break
        
        message = message.decode()
        return  (f"{whois_country(message)}\n{whois_origin(message)}'\n'{whois_netname(message)}\r\n")
     
   
     
def whois_country(message):
    country = re.findall(r"(country:\s+\w+)", message)
    if country != []:
        return country[0]
    else:
        return '' 

def whois_origin(message):
    origin = re.findall(r"origin: \s+\w+", message)
    if origin != []:
        return origin[0]
    else:
        return ''

def whois_netname(message):
    netname = re.findall(r"(netname:\s+\w+)", message)
    if netname != []:
        return netname[0]
    else:
        return ''

def traceroute(address):
    host = ''  #socket.gethostbyname(address)
    #print (host) 
    try:
        host = socket.gethostbyname(address)
    except:
        print(address," is invalid")

    TTl=1
    f=0
    address_marshrutizatora = ""
    while ((TTl<ttl) and (address_marshrutizatora!=host)):

        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # socket.AF_INET - ipV4 socket.SOCK_DGRAM - тип сокета по отправляемому сообщению (ДЕЙТАГРАММА) socket.IPPROTO_UDP - номер протокола (конст = 17)
        udp_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, TTl) #SOL_IP - настроить функции ip пакета https://stackoverflow.com/questions/72319941/what-do-socket-sol-socket-and-socket-so-reuseaddr-in-python, что настраиваем (ттл) и само значение
        udp_socket.sendto('ivanisthebest'.encode(), (host, udp_port) ) #Send data to the socket. The socket should not be connected to a remote socket, since the destination socket is specified by address. The optional flags argument has the same meaning as for recv() above. Return the number of bytes sent. (The format of address depends on the address family — see above.)   ---- (host, port) - is used for the AF_INET address family, where host is a string representing either a hostname in internet domain notation

        icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)  # class socket.socket(family=AF_INET, type=SOCK_STREAM, proto=0, fileno=None)
        icmp_socket.bind((local_host,udp_port))#один аргумент = пара (,)
        icmp_socket.settimeout(2) #от изменения значения не изменяется результат

        try:
            a = icmp_socket.recvfrom(2024)
            address_marshrutizatora = a[1][0]
            print(f"{TTl}. {address_marshrutizatora}")
            print(whois(address_marshrutizatora))

            
        except timeout:
            print(f"{TTl}. **\r\n") #мы можем ничепго не получитьь
        TTl+=1

 
if __name__ == "__main__":
    main()





#self.setsockopt(IPPROTO_UDPLITE, UDPLITE_SEND_CSCOV, length) настройки сокета
# Утилита Traceroute вместо ICMP-запроса отправляет 1 UDP-пакет на определенный порт целевого хоста и ожидает ответа о недоступности этого порта.
#  Первый пакет отправляется с TTL=1, второй с TTL=2 и так далее, пока запрос не попадет адресату. 
# Отличие от Tracert в том, как Traceroute понимает, что трассировка завершена. 
# Так как вместо ICMP-запроса он отправляет UDP-запрос, в каждом запросе есть порт отправителя (Sourсe) и порт получателя (Destination). 
# По умолчанию запрос отправляется на закрытый порт 34434.
#  Когда запрос попадёт на хост назначения, этот хост отправит ответ о недоступности порта «Destination port unreachable» (порт назначения недоступен).
# Это значит, что адресат получил запрос. Traceroute воспримет этот ответ как завершение трассировки.  