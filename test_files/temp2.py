import socket, ssl

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.verify_mode = ssl.CERT_REQUIRED
context.keylog_filename = 'keylog.txt'
context.check_hostname = True
context.load_default_certs()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssl_sock = context.wrap_socket(s, server_hostname='parser-dev.up.railway.app')
ssl_sock.connect(('parser-dev.up.railway.app', 443))
ssl_sock.sendall(b'GET / HTTP/1.1\r\nHost: parser-dev.up.railway.app\r\n\r\n')
data = ssl_sock.recv(1024)
print(data)
ssl_sock.close()