import tkinter as tk
from tkinter import scrolledtext
import threading
from IRCClient import *  # Assuming IRCClient is defined in a file named IRCClient.py
  # Assuming IRCClient is defined in a file named IRCClient.py
import sys

class IRCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IRC Client")

        self.server_ip_label = tk.Label(root, text="Server IP:")
        self.server_ip_label.grid(row=0, column=0, sticky="w")
        self.server_ip_entry = tk.Entry(root)
        self.server_ip_entry.grid(row=0, column=1, sticky="ew")

        self.port_label = tk.Label(root, text="Port:")
        self.port_label.grid(row=1, column=0, sticky="w")
        self.port_entry = tk.Entry(root)
        self.port_entry.grid(row=1, column=1, sticky="ew")

        self.nickname_label = tk.Label(root, text="Nickname:")
        self.nickname_label.grid(row=2, column=0, sticky="w")
        self.nickname_entry = tk.Entry(root)
        self.nickname_entry.grid(row=2, column=1, sticky="ew")

        self.ssl_var = tk.IntVar()
        self.ssl_checkbox = tk.Checkbutton(root, text="Use SSL", variable=self.ssl_var)
        self.ssl_checkbox.grid(row=3, column=1, sticky="w")

        self.connect_button = tk.Button(root, text="Connect", command=self.connect)
        self.connect_button.grid(row=4, column=0, columnspan=2, sticky="ew")

        self.message_label = tk.Label(root, text="Message:")
        self.message_label.grid(row=5, column=0, sticky="w")
        self.message_entry = tk.Entry(root)
        self.message_entry.grid(row=5, column=1, sticky="ew")
        self.message_entry.bind("<Return>", self.send_message)

        self.chat_output = scrolledtext.ScrolledText(root, width=40, height=10)
        self.chat_output.grid(row=6, column=0, columnspan=2, sticky="nsew")

        # Redirect stdout and stderr to the GUI
        sys.stdout = self
        sys.stderr = self

        self.irc_client = None
        
     # Make the grid cells expand with the window
        for i in range(7):
            root.grid_rowconfigure(i, weight=1)
        root.grid_columnconfigure(1, weight=1)

    def write(self, text):
        self.chat_output.insert(tk.END, text)
        self.chat_output.see(tk.END)  # Auto-scroll to the end

    def flush(self):
        pass

    def connect(self):
        server_ip = self.server_ip_entry.get()
        port = int(self.port_entry.get())
        nickname = self.nickname_entry.get()
        use_ssl = bool(self.ssl_var.get())

        self.irc_client = IRCClient(server_ip, port, nickname, use_ssl)
        self.irc_client.connect()

        if self.irc_client.connected:
            self.chat_output.insert(tk.END, f"Connected to {server_ip}:{port} as {nickname}\n")
            threading.Thread(target=self.receive_messages, daemon=True).start()
        else:
            self.chat_output.insert(tk.END, "Failed to connect to the server\n")

    def receive_messages(self):
         while self.irc_client.connected:
            message = self.irc_client.receive_messages()
            if message:
                self.chat_output.insert(tk.END, message + "\n")
                self.chat_output.see(tk.END)  # Auto-scroll to the end

    def send_message(self, event):
        message = self.message_entry.get()
        
        if self.irc_client:
            if message.startswith('/'):
                self.irc_client.process_command(message)
            else:
                self.irc_client.send_message(message)
            self.message_entry.delete(0, tk.END)

def main():
    root = tk.Tk()
    app = IRCApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
