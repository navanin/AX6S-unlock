# Команда для запуска - python3 название_файла.py
# Для проверки успешности выполнения скрипта выполните команду ниже и сравните вывод:
# $ curl "http://192.168.31.1/cgi-bin/luci/;stok=${token}/api/xqnetwork/get_netmode"
# {"netmode":4,"code":0}

# Значение $token можно найти в браузере, в web-интерфейса роутера.
# Скопируйте значение парметра stok из адресной строки и вставьте его в ссылку,
# вместо ${token}.

import ssl
import socket

# This script simply replays one side of an intercepted conversation between two Xiaomi
# RB01 (International) AX3200 routers negotiating meshing.
# In effect the script poses as a mesh slave, which causes the mesh master to enable netmode4.
# Enabling netmode is needed as one step in unlocking the router and flashing OpenWrt.
# The router should already have been taken through basic set-up before running this script.
# Netmode4 can be confirmed with curl by requesting the following URL, where ${token} is the "stok"
# variable from your admin session:
# $ curl "http://192.168.31.1/cgi-bin/luci/;stok=${token}/api/xqnetwork/get_netmode"
# {"netmode":4,"code":0}

# Set the IP address and port number of the server
SERVER_IP = '192.168.31.1'
SERVER_PORT = 19553

# Create an SSL context object and configure it for the client
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Create a TCP socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Wrap the socket with SSL encryption using the context object
ssl_sock = ssl_context.wrap_socket(sock, server_hostname=SERVER_IP)

# Connect to the server
ssl_sock.connect((SERVER_IP, SERVER_PORT))

# Send a hex string to the server
hex_string = '100100a3000438633a64653a66393a62663a35643a6236000038633a64653a66393a62663a35643a6237000061646435353662636461303730380000503151527567767a6d78746b35502f70316b2b46566a724a4c716d6568494546424a6563477062516a76383d00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000033433a43443a35373a32323a31433a36310000'
byte_string = bytes.fromhex(hex_string)
ssl_sock.send(byte_string)

# Receive the response from the server
response1 = ssl_sock.recv(1024)

# Print the response
print("{}:\n{}".format('Response1',response1))

# Receive the response from the server
response2 = ssl_sock.recv(1024)

# Print the response
print("{}:\n{}".format('Response2',response2))

hex_string2 = '10010020000538633a64653a66393a62663a35643a6236000038633a64653a66393a62663a35643a623700000100000000000000000000000000000000000000000000000000000000000000'
byte_string2 = bytes.fromhex(hex_string2)
ssl_sock.send(byte_string2)

response3 = ssl_sock.recv(2048)
print("{}:\n{}".format('Response3',response3))

hex_string3 = '10010020000738633a64653a66393a62663a35643a6236000038633a64653a66393a62663a35643a62370000017265637620636f6e6669672073796e6320636f72726563746c792e0a000000'
byte_string3 = bytes.fromhex(hex_string3)
ssl_sock.send(byte_string3)

response4 = ssl_sock.recv(2048)
print("{}:\n{}".format('Response4',response4))


# Close the socket
ssl_sock.close()