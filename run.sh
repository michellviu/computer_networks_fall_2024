#!/bin/bash

# Replace the next shell command with the entrypoint of your solution

host="127.0.0.1"
port="8080"
nick="TestUser1"
command="/nick"
argument="NewNick"

# Ejecutar el script IRCClient.py con los parámetros proporcionados
python3 IRCClient.py -H "$host" -p "$port" -n "$nick" -c "$command" -a "$argument"