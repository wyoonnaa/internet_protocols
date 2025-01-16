tracert-as [10]
Формулировка
Написать скрипт, который выводит маршрут (traceroute) и номера автономных систем промежуточных узлов, используя ответы службы whois региональных регистраторов.
Вход: IP-адрес (или DNS-имя) передается в качестве аргумента командной строки
Выход:
[1-3 балла] вывести результат трассировки (в пределах разумного TTL), для "белых" IP-адресов из него указать номер автономной системы и название сети,
[4-6 балла] то же, плюс обращение к правильному whois-серверу и определение страны промежуточного IP,
[7-10 баллов] то же, плюс самостоятельная реализация traceroute (сборка пакета с нужным TTL и разбор ICMP)
Формат вывода
Формат вывода для каждого адреса из трассировки:
N. IP\r\n
NETNAME, AS, COUNTRY\r\n
\r\n

где N -- номер хоста в трассировке (начинается с 1), IP - ipv4-адрес хоста; NETNAME, AS, COUNTRY - имя сети, номер автономной системы (^\d+$) и страна соответственно. Вся информация должна быть получена из ответа/ответов whois-сервера. После вывода информации о хосте пустая строка (\r\n). 

Если какая-либо информация отсутствует, то не включаем ее в вывод. Например, если нашли в ответе от whois-сервера только имя сети и страну, то во второй строке пишем:
NETNAME, COUNTRY

Если ip-адрес в трассировке является локальным, пишем в строке с информацией слово local

Обращаем внимание, что EU - это не страна.

Если узел в трассировке не отвечает, то вместо IP пишем *, строка с информацией пропадает, пустая строка остается.

Если указан некорректный адрес, то вместо трассировки пишем 
ADDRESS is invalid, где ADDRESS - некорректный параметр

Если не хватает прав, то нужно вежливо об этом сказать, а не падать, выдавая весь стектрейс.

Пример вывода:
192.168.1.1
local

2. *

3. 92.242.29.74
miralogic-net-200, 12668, RU

4. 212.193.163.6
imgu-net, 60600, RU


sntp [7]
Формулировка
Написать "обманывающий" сервер времени
Вход: передается количество секунд (+ или -) смещения относительно точного времени
Выход:
[1-4 балла] ответить на корректные запросы по протоколу SNTP корректными ответами (поля: LI, VN, Mode, Stratum и время должны быть заполнены осмысленным образом)
[5-7 баллов] то же, плюс многопоточность (thread pool)
Формат ввода-вывода
Параметры:
-d - delay, может быть как положительным, так и отрицательным целым числом, означающим число секунд, на которое должны обманывать клиентов, по умолчанию 0
--port, -p - порт, который слушаем, по умолчанию 123

./sntp.py -d 5
сервер в ответе добавляет 5 секунд к текущему времени
Сервер сообщает на stdout о начале работы, а при подключении очередного клиента выводит его ip-адрес 

Не забываем проверять работоспособность со стандартными утилитами:
ntpdate -d -q localhost
rdate -u -n -v -p localhost

При реализации многопоточности обращаем внимание, что время на запуск нового треда будет сравнимо со временем на формирование ответного пакета



portscan [15]
Формулировка
Написать сканер TCP- и UDP-портов удалённого компьютера.
Вход: адрес хоста и диапазон портов
Выход: итоговая оценка складывается как сумма:
[1-2 балла] список открытых TCP-портов,
[1-4 балла] список открытых UDP-портов,
[1-3 балла] многопоточность,
[1-6 балла] распознать прикладной протокол по сигнатуре (NTP/DNS/SMTP/POP3/IMAP/HTTP).

Формат ввода-вывода
Параметры:
-t - сканировать tcp
-u - сканировать udp
-p N1 N2, --ports N1 N2 - диапазон портов

Вывод:
В одной строке информация об одном открытом порте (через пробел):
TCP 80 HTTP
UDP 128
UDP 123 SNTP

Если протокол не распознали, то пишем только TCP/UDP и номер порта.
Если нужно больше прав при запуске, то стоит вежливо об этом сказать, а не громко падать.


dns-cache [20]
Формулировка
Написать кеширующий DNS-сервер, отвечающий на корректные запросы по протоколу DNS (RFC 1035) корректными ответами, данные сервер должен брать из своего кэша или (в случае устаревания или отсутствия данных в кэше) переспрашивать у указанного сервера (см. BIND forwarders).

[1-7] реализация кэша на основе query records в качестве ключа.
[8-15] парсинг пакета для помещения в кэш записей из секций AN, NS, AR (в серии запросов dig mail.ru mx; dig mxs.mail.ru второй ответ - из кеша). Самостоятельная сборка пакета с ответом.
[16-20] обработка зацикливания (корректное поведение сервера в случае, если в качестве «старшего сервера» указан он же сам, или экземпляр его, запущенный на другой машине)

Обязательно должно быть реализовано
* устаревание данных в кэше (обработка TTL), при этом клиентам должны отдавать актуальное значение ttl, то есть если 10 секунд назад от форвардера получили ответ, что данные устареют через 700 секунд, то клиенту говорим, что ttl для имеющейся у нас в кэше записи равен 690
* временный отказ вышестоящего сервера (сервер не должен терять работоспособность (уходить в бесконечное ожидание, падать с ошибкой и т.д.), если старший сервер почему-то не ответил на запрос к нему)

Формат ввода-вывода
Параметры:
-p, --port - слушаемый порт udp (по умолчанию 53)
-f --forwarder - ip-адрес или символьное имя форвардера, с возможным указанием порта, например, 8.8.8.8 или 8.8.8.8:53 (порт по умолчанию 53)
-h, --help - вывод справки

При запуске сервера выводим на stdout информацию об успехе запуска сервера.
Для каждого запроса от клиентов выводим на stdout информацию в следующем формате:
IP, TYPE, QUESTION, SOURCE,
где IP - адрес клиента, TYPE - тип DNS-запроса (латиницей, заглавными буквами), QUESTION - информацию о чем запрашивают, SOURCE - источник, откуда взяли ответ (cache или forwarder). Пример вывода:
10.11.12.13, A, urfu.ru, forwarder
4.8.15.16, A, urfu.ru, cache
smtp-mime [10]
Формулировка
Написать скрипт, который отправляет получателю все картинки из указанного (или рабочего) каталога в качестве вложения.

Параметры:
-h/--help - справка
--ssl - разрешить использование ssl, если сервер поддерживает (по умолчанию не использовать)
-s/--server - адрес (или доменное имя) SMTP-сервера в формате адрес[:порт] (порт по умолчанию 25)
-t/--to - почтовый адрес получателя письма 
-f/--from - почтовый адрес отправителя (по умолчанию <>)
--subject - необязательный параметр, задающий тему письма, по умолчанию тема “Happy Pictures”
--auth - запрашивать ли авторизацию (по умолчанию нет), если запрашивать, то сделать это после запуска, без отображения пароля
-v/--verbose - отображение протокола работы (команды и ответы на них), за исключением текста письма
-d/--directory - каталог с изображениями (по умолчанию $pwd)

Итоговая оценка складывается как сумма
[1-3 балла] формирование письма в соответствии с MIME,
[1-3 балла] работа с SMTP-сервером с авторизацией и без,
[1-2 балла] работа по защищенному соединению (+starttls),
[1-2 балла] использование ESMTP (напр., pipelining, size).
Обязательна обработка ответов сервера, в том числе многострочных.


imap [10]
Формулировка
Написать скрипт, выводящий информацию о письмах в почтовом ящике

Параметры:
-h/--help - справка
--ssl - разрешить использование ssl, если сервер поддерживает (по умолчанию не использовать).
-s/--server - адрес (или доменное имя) IMAP-сервера в формате адрес[:порт] (порт по умолчанию 143).
-n N1 [N2] - диапазон писем, по умолчанию все.
-u/--user - имя пользователя, пароль спросить после запуска и не отображать на экране.

Итоговая оценка складывается как сумма
[1-3 балла] вывод заголовков писем как списка или таблицы с полями "кому, от кого, тема, дата, размер письма",
[1-3 балла] декодирование заголовков From/Subject,
[1-2 балла] работа по защищенному соединению,
[1-2 балла] вывод количества аттачей, имен файлов и размеров.
Обязательна обработка ответов сервера, в том числе многострочных.



http-api [10]
Формулировка
Майнинг данных через HTTP

﻿1) [VK] скачать фотографии в максимальном разрешении из выбранного альбома
2) [VK | Facebook | Instagram] Отобразить новости за указанный промежуток времени, упорядоченные по убыванию лайков
3) [VK | Facebook] Вывести список друзей по уменьшению популярности. Популярность = функция (количество друзей, количество лайков к фотографиям профиля)
4) [VK+LastFM] Вывести статистику по жанрам прослушиваемой музыки
5) [VK | Facebook | Twitter] Вывести список недрузей, упорядоченных по уменьшению числа общих друзей
6) [VK] Загрузка всех фото из указанной папки в указанный альбом
7) [VK | Facebook | Instagram ] Список друзей, упорядоченных по уменьшению числа оставленных лайков и комментариев для записей текущего пользователя
8) [ANY] вывести прогноз погоды для заданного города на заданный промежуток времени
9) [VK + сервис, склоняющий русские слова (по желанию) ] Вывести наиболее часто используемые при переписке слова (только исходящие сообщения)
10) [VK | Facebook ] топ друзей, упорядоченный по общему числу подписок
11) [VK | OK] Определить победителей конкурса, проводимого одновременно в нескольких соцсетях (требование подписки на группы и репоста в вк, класса на одноклассниках)
12) [VK | OK] Скачать все фото, прикрепленные к указанной публикации

Если обработка данных занимает “много” времени, то отображаем прогресс-бар.

Для авторизации используем OAuth, НЕ запрашиваем у пользователя логин/пароль. 






oidc-server [7]
Формулировка
Написать скрипт, работающий как сервер авторизации по протоколу OpenId Connect


