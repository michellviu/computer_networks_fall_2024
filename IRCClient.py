import socket
import ssl
import threading
import sys
import getopt


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
            
    

    def send_privmsg(self, target, message):
        self.socket.sendall(f"PRIVMSG {target} :{message}\r\n".encode())
    def join_channel(self, channel):
        self.socket.sendall(f"JOIN {channel}\r\n".encode())
    def leave_channel(self, channel):
        self.socket.sendall(f"PART {channel}\r\n".encode())
    def set_channel_mode(self, channel, mode):
        self.socket.sendall(f"MODE {channel} {mode}\r\n".encode())
    def send_notice(self, target, message):
        self.socket.sendall(f"NOTICE {target} :{message}\r\n".encode())
    def list_channels(self):
        self.socket.sendall("LIST\r\n".encode())
    def list_users_in_channel(self, channel=""):
        if channel:
            self.socket.sendall(f"NAMES {channel}\r\n".encode())
        else:
            self.socket.sendall("NAMES\r\n".encode())
    def change_nickname(self, new_nickname):
        self.socket.sendall(f"NICK {new_nickname}\r\n".encode())

    def change_user_mode(self, nickname, mode):
        self.socket.sendall(f"MODE {nickname} {mode}\r\n".encode())
    def whois_query(self, nickname):
        self.socket.sendall(f"WHOIS {nickname}\r\n".encode())
        
    
    
    def process_command(self, command):
        parts = command.split(' ', 1)
        cmd = parts[0].lower()

        if cmd == "/join" and len(parts) > 1:
            self.join_channel(parts[1])
        elif cmd == "/part" and len(parts) > 1:
            self.leave_channel(parts[1])
        elif cmd == "/msg" and len(parts) > 1:
            target_message = parts[1].split(' ', 1)
            if len(target_message) > 1:
                self.send_privmsg(target_message[0], target_message[1])
        elif cmd == "/notice" and len(parts) > 1:
            target_message = parts[1].split(' ', 1)
            if len(target_message) > 1:
                self.send_notice(target_message[0], target_message[1])
        elif cmd == "/mode" and len(parts) > 1:
            mode_args = parts[1].split(' ', 1)
            if len(mode_args) > 1:
                self.set_channel_mode(mode_args[0], mode_args[1])
        elif cmd == "/list":
            self.list_channels()
        elif cmd == "/names":
            if len(parts) > 1:
                self.list_users_in_channel(parts[1])
            else:
                self.list_users_in_channel()
        elif cmd == "/nick" and len(parts) > 1:
            new_nickname = parts[1]
            self.change_nickname(new_nickname)
        elif cmd == "/whois" and len(parts) > 1:
            nickname = parts[1]
            self.whois_query(nickname)
        else:
            print("Comando desconocido o faltan argumentos.")



    def receive_messages(self):
        buffer = ""  # Búfer para acumular datos recibidos
        while self.connected:
            try:
                data = self.socket.recv(4096)  # Recibe bytes del socket
                if not data:
                    continue  # Si no hay datos, continúa el bucle

                # Decodifica y añade al búfer, manejando errores de decodificación
                buffer += data.decode('utf-8', errors='replace')

                # Procesa todos los mensajes completos que hay en el búfer
                while "\r\n" in buffer:
                    message, buffer = buffer.split("\r\n", 1)  # Separa el primer mensaje completo del buffer
                    parts = message.split(" ")

                    # Lógica para manejar diferentes tipos de mensajes basada en 'parts'
                    if parts[0] == "PING":
                        self.send_pong(parts[1])
                    elif parts[1] in ["322", "323", "353", "366", "433", "431", "432", "311", "319", "324"]:
                        self.handle_numeric_response(parts)
                    elif parts[0].startswith(":") and parts[1] == "NICK":
                        self.handle_nick_change(parts)
                    elif parts[1] == "PRIVMSG":
                        self.handle_privmsg(parts)
                    elif parts[1] == "NOTICE":
                        self.handle_notice(parts)
                    elif parts[1] == "JOIN":
                        self.handle_join(parts)
                    elif parts[1] == "PART":
                        self.handle_part(parts)
                    elif parts[1] == "KICK":
                        self.handle_kick(parts)
                    elif parts[1] == "MODE":
                        self.handle_mode(parts)


                    print(message)  # Imprime todos los mensajes para depuración.

            except UnicodeDecodeError as e:
                print(f"Error de decodificación en la recepción de mensajes: {e}.")
            except Exception as e:
                print(f"Error al recibir mensaje: {e}.")
                self.connected = False
                break
    
    
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "H:p:n:c:a:", ["port=", "host=", "nick=", "command=", "argument="])
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)

    server_ip = None
    port = None
    nickname = None
    command = None
    argument = None
    use_ssl = False

    for opt, arg in opts:
        if opt in ("-p", "--port"):
            port = int(arg)
        elif opt in ("-H", "--host"):
            server_ip = arg
        elif opt in ("-n", "--nick"):
            nickname = arg
        elif opt in ("-c", "--command"):
            command = arg
        elif opt in ("-a", "--argument"):
            argument = arg

    if not server_ip or not port or not nickname:
        print("Uso: IRCClient.py -H <host> -p <port> -n <nick> [-c <command>] [-a <argument>]")
        sys.exit(2)

    # tmp = True
    # while tmp:
    #     if usarssl == '1':
    #         use_ssl = True
    #         tmp = False
    #     elif usarssl == '2':
    #         use_ssl = False
    #         tmp = False
    #     else:
    #         usarssl = input ("Ingrese 1 para usar conexión segura. Ingrese 2 para el caso contrario ")





    irc_client = IRCClient(server_ip, port, nickname, use_ssl)
    irc_client.connect()

    if irc_client.connected:
        print(f"Bienvenido, {nickname}!\n")
        threading.Thread(target=irc_client.receive_messages, daemon=True).start()

        # while True:
        #     # user_input = input()
        user_input = f"{command} {argument}"
            
        if user_input.startswith('/'):
                irc_client.process_command(user_input)
        else:
                irc_client.send_message(user_input)

    else:
        print("No se pudo conectar al servidor. Por favor, vuelva a intentarlo más tarde.")

if __name__ == "__main__":
    main()