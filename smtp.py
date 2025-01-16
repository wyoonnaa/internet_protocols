import os
import argparse
import socket
import ssl
import datetime
import mimetypes
import base64
from email.message import EmailMessage

ssl._create_default_https_context = ssl._create_unverified_context # отключается проверка сертификата иначе не работает 

class SMTPException(Exception):
    pass

def get_date_header(): # дата в формате, который используется в заголовках электронной почты.
    return datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')


def encode_base64(data):
    return base64.b64encode(data.encode('utf-8')).decode('utf-8')


def create_email(from_addr, to_addr, subject, attachments_directory):
    msg = EmailMessage()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject
    msg['Date'] = get_date_header()
    
    msg.set_content('С уважением, вот вам картинки)')

    for filename in os.listdir(attachments_directory):
        path = os.path.join(attachments_directory, filename)
        if os.path.isfile(path):
            ctype, encoding = mimetypes.guess_type(path) #определяет MIME-тип и кодировку файла для правильной упаковки вложения
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            # application/octet-stream -  общий MIME-тип для двоичных данных, 
            #что говорит почтовому клиенту о том, что с содержимым файла следует обращаться как с прикрепленным файлом общего типа, без специфической обработки.
            main_type, sub_type = ctype.split('/', 1)
            with open(path, 'rb') as fp:
                print(path)
                msg.add_attachment(fp.read(),
                                   maintype=main_type,
                                   subtype=sub_type,
                                   filename=filename)

    return msg


# обработка ответа сервера
def receive_response(socket):
    response = socket.recv(4096).decode('utf-8')
    print(response)
    if response.startswith('4') or response.startswith('5'): # проверяем на коды ошибок 
        raise SMTPException("Server returned error response: " + response)
    return response


# отправка письма 
def send_mail_with_ssl(server_info, from_addr, to_addr, message, verbose, use_ssl, use_auth, username, password):
    server, port = server_info.split(':')
    with socket.create_connection((server, int(port))) as sock:
        if use_ssl:
            context = ssl.create_default_context()
            client = context.wrap_socket(sock, server_hostname=server)
        else:
            client = sock

        receive_response(client)
        client.sendall(b'EHLO example.com\r\n')
        receive_response(client)

        if use_auth:
            #  аутентификация
            client.sendall(b'AUTH LOGIN\r\n')
            receive_response(client)
            client.sendall((encode_base64(username) + '\r\n').encode())
            receive_response(client)
            client.sendall((encode_base64(password) + '\r\n').encode())
            receive_response(client)

        # Отправляем данные письма
        client.sendall(f'MAIL FROM: {from_addr}\r\n'.encode())
        receive_response(client)
        client.sendall(f'RCPT TO: {to_addr}\r\n'.encode())
        receive_response(client)
        client.sendall(b'DATA\r\n')
        receive_response(client)

        client.sendall(message.as_bytes())
        client.sendall(b'\r\n.\r\n')
        receive_response(client)

        client.sendall(b'QUIT\r\n')
        response = receive_response(client)
        
        if verbose and response.startswith('221'):
            print('Email sent successfully')


def parse_args():
    parser = argparse.ArgumentParser(description='Send an email with attachments via command line')
    parser.add_argument('-s', '--server', help='SMTP server and port (example: smtp.example.com:465)', required=True)
    parser.add_argument('-f', '--from', dest='from_addr', help='FROM email address', required=True)
    parser.add_argument('-t', '--to', help='TO email address', required=True)
    parser.add_argument('--subject', help='Email subject', default='Happy Pictures')
    parser.add_argument('-d', '--directory', help='Directory of attachments', required=True)
    parser.add_argument('--ssl', help='Use SSL for connection', action='store_true')
    parser.add_argument('--auth', help='Perform authentication (username and password required)', action='store_true')
    parser.add_argument('--username', help='SMTP username')
    parser.add_argument('--password', help='SMTP password')
    parser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()

    msg = create_email(args.from_addr, args.to, args.subject, args.directory)

    send_mail_with_ssl(args.server,
                       args.from_addr,
                       args.to,
                       msg,
                       args.verbose,
                       args.ssl,
                       args.auth,
                       args.username,
                       args.password)


if __name__ == '__main__':
    main()


