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
            
            
            
            
    def handle_privmsg(self, parts):
        """
        Maneja mensajes PRIVMSG.

        Args:
        parts: Lista de componentes del mensaje PRIVMSG.
        """
        # Concatena de nuevo las partes para manejar fácilmente los mensajes que contienen espacios
        full_msg = " ".join(parts)

        # Extrae el remitente del mensaje
        prefix_end = full_msg.find('!')
        sender = full_msg[1:prefix_end]

        # Extrae el texto del mensaje
        # Busca el primer carácter ':' que indica el inicio del mensaje real
        message_start = full_msg.find(':', 1)
        message = full_msg[message_start + 1:]

        # Determina si el mensaje es para un canal o es un mensaje directo
        if parts[2].startswith('#'):
            # Mensaje de canal
            print(f"Mensaje de {sender} en {parts[2]}: {message}")
        else:
            # Mensaje directo
            print(f"Mensaje directo de {sender}: {message}")

    def handle_notice(self, parts):
        full_msg = " ".join(parts)
        sender = full_msg[1:full_msg.find('!')]
        message_start = full_msg.find(':', 1)
        message = full_msg[message_start + 1:]
        print(f"Notice de {sender}: {message}")

    def handle_join(self, parts):
        user_info = parts[0][1:]
        channel = parts[2].strip() if parts[2].startswith(':') else parts[2]
        print(f"{user_info} se ha unido a {channel}")

    def handle_part(self, parts):
        user_info = parts[0][1:]
        channel = parts[2].strip() if parts[2].startswith(':') else parts[2]
        print(f"{user_info} ha dejado {channel}")

    def handle_kick(self, parts):
        channel = parts[2]
        user_kicked = parts[3]
        reason = " ".join(parts[4:]).lstrip(':')
        print(f"{user_kicked} ha sido expulsado de {channel} por la razón: {reason}")