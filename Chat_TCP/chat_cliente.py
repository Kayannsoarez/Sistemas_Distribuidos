import socket
import threading

char_format = 'utf-8'
nick_lock = threading.Lock()


# Recebe mensagens do servidor e exibe no terminal (roda em thread separada)
def receber(client_socket, nickname_ref):
    while True:
        try:
            msn = client_socket.recv(1024).decode(char_format)
            print(msn)
        except:
            print('Conexão encerrada.')
            break


# Lê o que o usuário digita e envia ao servidor (roda em thread separada)
def escrever(client_socket, nickname_ref):
    while True:
        try:
            text = input('').strip()
            if not text:
                continue

            if text.startswith('/'):
                if text == '/NICK':
                    # Pede novo apelido localmente antes de enviar o comando
                    novonick = input('Novo apelido: ').strip()
                    if novonick:
                        client_socket.send('/NICK {}'.format(novonick).encode(char_format))
                        with nick_lock:
                            nickname_ref[0] = novonick
                    else:
                        print('Apelido inválido.')
                elif text == '/SAIR':
                    client_socket.send('/SAIR'.encode(char_format))
                    client_socket.close()
                    break
                else:
                    client_socket.send(text.encode(char_format))
            else:
                with nick_lock:
                    nick = nickname_ref[0]
                client_socket.send('{}: {}'.format(nick, text).encode(char_format))

        except:
            break


# Ponto de entrada: solicita comando inicial ao usuário
print('Bem Vindo - uCHAT\nDigite /ENTRAR para iniciar')
cmd = input('').strip()

if cmd == '/ENTRAR':
    print("Login no uCHAT: informe IP do servidor, porta e apelido.")
    server_ip = input("IP_Servidor: ").strip()
    port     = input("Porta: ").strip()
    nickname = input("Apelido: ").strip()

    address = (server_ip, int(port))

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(address)

        # Handshake: negociação de apelido no thread principal, antes de iniciar as threads
        msg = client_socket.recv(1024).decode(char_format)

        if msg.startswith('LOTADO:'):
            print(msg)
            client_socket.close()
        else:
            # Servidor enviou 'NICK': envia apelido e aguarda confirmação ou erro
            nickname_ref = [nickname]
            client_socket.send(nickname_ref[0].encode(char_format))

            msg = client_socket.recv(1024).decode(char_format)
            while msg.startswith('NICK_DUPLICADO:'):
                print(msg)
                novonick = input('Digite outro apelido: ').strip()
                if novonick:
                    nickname_ref[0] = novonick
                client_socket.send(nickname_ref[0].encode(char_format))
                msg = client_socket.recv(1024).decode(char_format)

            if msg == 'CONECTADO':
                print('Conectado ao chat! Digite /USUARIOS, /NICK <apelido> ou /SAIR.')

                rcve_thread = threading.Thread(target=receber, args=(client_socket, nickname_ref))
                rcve_thread.daemon = True
                rcve_thread.start()

                wrte_thread = threading.Thread(target=escrever, args=(client_socket, nickname_ref))
                wrte_thread.start()
            else:
                print('Resposta inesperada do servidor:', msg)
                client_socket.close()

    except Exception as e:
        print('Erro ao conectar:', e)
else:
    print('Comando não reconhecido. Use /ENTRAR para conectar.')
