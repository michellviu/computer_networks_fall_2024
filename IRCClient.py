import socket
import ssl
import threading


class IRCClient:
    def __init__(self, host, port, nickname, use_ssl):
        self.host = host
        self.port = port
        self.nickname = nickname
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.use_ssl = use_ssl
        
        
        if self.use_ssl:
            # Crear una instancia de SSLContext para autenticación del servidor (conexión cliente)
            ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            ssl_context.check_hostname = True  # Verifica que el nombre de host en el certificado coincide con el objetivo
            ssl_context.verify_mode = ssl.CERT_REQUIRED  # Requiere un certificado válido
            # ssl_context.check_hostname = False
            # ssl_context.verify_mode = ssl.CERT_NONE  #Deshabilita la verificación del certificado
            # Envolver el socket existente en un contexto SSL
            self.socket = ssl_context.wrap_socket(self.socket, server_hostname=self.host)
            
    
    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            self.connected = True
            # Enviar comandos NICK y USER según el protocolo IRC
            self.socket.sendall(f"NICK {self.nickname}\r\n".encode())
            self.socket.sendall(f"USER {self.nickname} 0 * :Real name\r\n".encode())
        except Exception as e:
            print("Error al conectar:", e)
            self.connected = False

    def send_message(self, message):
        try:
            self.socket.sendall(f"{message}\r\n".encode())
        except Exception as e:
            print("Error al enviar mensaje:", e)