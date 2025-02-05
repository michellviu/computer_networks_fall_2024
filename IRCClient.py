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
            
    
    def send_pong(self, data):
        self.socket.sendall(f"PONG {data}\r\n".encode())
            
            
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
        
    
    def handle_mode(self, parts):
        source = parts[0][1:]
        channel_or_user = parts[2]
        mode_changes = parts[3:]

        # Imprime o procesa el cambio de modo
        print(f"{source} cambió el modo de {channel_or_user} a {' '.join(mode_changes)}")


    def handle_nick_change(self, parts):
        old_nick = parts[0][1:].split('!')[0]
        new_nick = parts[2].lstrip(':')
        if old_nick == self.nickname:
            self.nickname = new_nick  # Actualiza el nickname almacenado
            print(f"Tu nickname ha sido cambiado a {new_nick}.")
        else:
            print(f"{old_nick} ahora es conocido como {new_nick}.")
            
            
    def handle_whois_response(self, parts):
        code = parts[1]
        if code == "311":  # Respuesta WHOIS con información del usuario
            nickname = parts[3]
            username = parts[4]
            hostname = parts[5]
            realname = ' '.join(parts[7:])[1:]
            print(f"Usuario {nickname} ({realname}) está en {hostname}")
        elif code == "319":  # Canales en los que el usuario está
            nickname = parts[3]
            channels = ' '.join(parts[4:])[1:]
            print(f"{nickname} está en los canales {channels}")
    
    
    def handle_numeric_response(self, parts):
        code = parts[1]
        if code == "322":  # Respuesta a LIST
            channel = parts[3]
            user_count = parts[4]
            topic = ' '.join(parts[5:])[1:]
            print(f"Canal: {channel} ({user_count} usuarios) - Tema: {topic}")
        elif code == "323":  # Fin de la lista LIST
            print("Fin de la lista de canales.")
        elif code == "353":  # Respuesta a NAMES
            channel = parts[4]
            names = ' '.join(parts[5:])[1:]
            print(f"Usuarios en {channel}: {names}")
        elif code == "366":  # Fin de la lista NAMES
            channel = parts[3]
            print(f"Fin de la lista de usuarios en {channel}.")
        elif code == "433":
            print("El nickname deseado está en uso o es inválido.")
        elif code == "431":  # Sin nickname dado
            print("No se ha proporcionado un nickname.")
        elif code == "432":  # Erroneous Nickname
            print("El nickname es inválido.")
        elif code == "324":  # Respuesta de modo de canal
            channel = parts[3]
            modes = ' '.join(parts[4:])
            print(f"Modos actuales para {channel}: {modes}")
        elif code == "311":  # Respuesta WHOIS con información del usuario
            nickname = parts[3]
            username = parts[4]
            hostname = parts[5]
            realname = ' '.join(parts[7:])[1:]
            print(f"Usuario {nickname} ({realname}) está en {hostname}")
        elif code == "319":  # Canales en los que el usuario está
            nickname = parts[3]
            channels = ' '.join(parts[4:])[1:]
            print(f"{nickname} está en los canales {channels}")