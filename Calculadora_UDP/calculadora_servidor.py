import socket
import json

HOST = ''
PORT = 6789

def main():
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    skt.bind((HOST, PORT))
    print('--- Calculadora UDP (Servidor) ---')

    i = 0
    try:
        while True:
            i += 1
            print(f'Esperando operação {i}')

            data, address = skt.recvfrom(1024)
            host_client, port = address

            try:
                data_json = json.loads(data)
                n1 = float(data_json['n1'])
                n2 = float(data_json['n2'])
                op = data_json['op']

                print(f'| Cliente: {host_client} - Porta: {port}')
                print(f'| Operação: {data_json["n1"]}{op}{data_json["n2"]}')

                if op == '+':
                    result = n1 + n2
                elif op == '-':
                    result = n1 - n2
                elif op == '*':
                    result = n1 * n2
                elif op == '/':
                    result = n1 / n2
                else:
                    result = 'Erro: operador inválido'

            except KeyError:
                result = 'Erro: campos ausentes na requisição'
            except ValueError:
                result = 'Erro: entrada inválida de números'
            except ZeroDivisionError:
                result = 'Erro: divisão por zero'

            skt.sendto(str(result).encode('utf-8'), address)

    except KeyboardInterrupt:
        print('\nServidor encerrado.')
    finally:
        skt.close()

if __name__ == '__main__':
    main()
