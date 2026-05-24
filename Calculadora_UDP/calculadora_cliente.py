import socket
import json

HOST = '127.0.0.1'
PORT = 6789

def main():
    print('--- Calculadora UDP (Cliente) ---')

    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    skt.settimeout(1)

    try:
        while True:
            number1 = input('Digite o número 1: ')
            operacao = input('Digite a operação: ')
            number2 = input('Digite o número 2: ')

            request = {'n1': number1, 'n2': number2, 'op': operacao}
            request_json = json.dumps(request)

            try:
                skt.sendto(request_json.encode('utf-8'), (HOST, PORT))
                response, address = skt.recvfrom(1024)
                server, port = address
                print(f'Resultado: {response.decode("utf-8")}')
                print(f'| Servidor: {server} - Porta: {port}')
            except socket.timeout:
                print('Tempo excedido — servidor não respondeu')

            continuar = input('Deseja realizar outra operação? (s/n): ').strip()
            if continuar not in ('s', 'S'):
                print('Encerrando cliente.')
                break
    finally:
        skt.close()

if __name__ == '__main__':
    main()
