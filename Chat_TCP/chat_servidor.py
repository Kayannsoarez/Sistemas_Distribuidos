import socket
import threading

host = socket.gethostbyname(socket.gethostname())
port = 1819
address = (host, port)
char_format = 'utf-8'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(address)
server.listen()

print("Servidor Online!")
print("IP Servidor:", address)

clients = []
nicknames = []
lock = threading.Lock()


# Envia uma mensagem para todos os clientes conectados
def broadcast(mensagem):
    with lock:
        targets = list(clients)
    for client in targets:
        try:
            client.send(mensagem)
        except:
            pass


# Envia ao cliente a lista de usuários atualmente conectados
def usuarios(client):
    with lock:
        lista = ', '.join(nicknames) if nicknames else 'nenhum'
    client.send('Usuários conectados: {}'.format(lista).encode(char_format))


# Troca o apelido de um cliente, verificando se o novo já está em uso
def novo_nick(client, nickname, novonick):
    with lock:
        if novonick in nicknames:
            client.send('ERRO: Apelido "{}" já está em uso.'.format(novonick).encode(char_format))
            return nickname
        for i in range(len(nicknames)):
            if nicknames[i] == nickname:
                nicknames[i] = novonick
                break

    broadcast('{} mudou o apelido para {}'.format(nickname, novonick).encode(char_format))
    return novonick


# Remove o cliente das listas, fecha a conexão e avisa os demais
def desconectar(client, nickname):
    with lock:
        if client in clients:
            clients.remove(client)
        if nickname in nicknames:
            nicknames.remove(nickname)
    try:
        client.send('Você saiu do chat.'.encode(char_format))
        client.close()
    except:
        pass
    broadcast('{} saiu do chat.'.format(nickname).encode(char_format))
    print('{} saiu.'.format(nickname))


# Processa as mensagens recebidas de um cliente já conectado (roda em thread por cliente)
def handle(client, nickname):
    while True:
        try:
            mensagem = client.recv(1024)
            texto = mensagem.decode(char_format)

            if texto.startswith('/'):
                if texto == '/SAIR':
                    desconectar(client, nickname)
                    break
                elif texto == '/USUARIOS':
                    usuarios(client)
                elif texto.startswith('/NICK '):
                    novonick = texto[6:].strip()
                    if novonick:
                        nickname = novo_nick(client, nickname, novonick)
                    else:
                        client.send('ERRO: Informe o novo apelido. Uso: /NICK <apelido>'.encode(char_format))
                else:
                    client.send('Comando inválido. Comandos: /USUARIOS /NICK <apelido> /SAIR'.encode(char_format))
            else:
                broadcast(mensagem)

        except:
            desconectar(client, nickname)
            break


# Aguarda novas conexões, faz o handshake de apelido e cria uma thread por cliente
def receber():
    while True:
        # Sempre aceita a conexão primeiro para poder responder ao cliente
        client, addr = server.accept()
        print("Tentativa de conexão de {}".format(addr))

        with lock:
            lotado = len(clients) >= 4

        if lotado:
            client.send('LOTADO: Servidor cheio (máx. 4 clientes).'.encode(char_format))
            client.close()
            print("Conexão recusada: servidor lotado.")
            continue

        # Solicita o apelido, aceitando novas tentativas se duplicado
        try:
            client.send('NICK'.encode(char_format))
            while True:
                nickname = client.recv(1024).decode(char_format).strip()
                with lock:
                    duplicado = nickname in nicknames
                if not duplicado:
                    break
                client.send('NICK_DUPLICADO: Apelido "{}" já está em uso.'.format(nickname).encode(char_format))
                print("Apelido '{}' duplicado, aguardando nova tentativa.".format(nickname))
        except:
            client.close()
            continue

        with lock:
            clients.append(client)
            nicknames.append(nickname)

        client.send('CONECTADO'.encode(char_format))
        broadcast('{} entrou no chat!'.format(nickname).encode(char_format))
        print("Conectado: {} ({})".format(nickname, addr))

        thread = threading.Thread(target=handle, args=(client, nickname))
        thread.daemon = True
        thread.start()

receber()
