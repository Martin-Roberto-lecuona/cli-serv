import socket
import threading
from pyngrok import ngrok
from cryptography.fernet import Fernet

import requests
api_key = 'lWT_LSQw0JnLxSqJdv3GhWMZ5tfIxVV-'

# Para usar una clave guardada
with open("clave.key", "rb") as key_file:
    clave = key_file.read()

# Crear un objeto Fernet con la clave
cipher_suite = Fernet(clave)

mi_turno = None

def cifrar_datos(datos):
    datos_bytes = datos.encode('utf-8') 
    return cipher_suite.encrypt(datos_bytes).decode()

def descifrar_datos(datos):
    datos_bytes = cipher_suite.decrypt(datos.encode())  
    return datos_bytes.decode('utf-8')      

def manejar_conexion(conn):
    global mi_turno
    while True:
        if mi_turno:
            mensaje = input("Tu turno: ")
            conn.sendall(mensaje.encode())
            mi_turno = False
        else:
            datos = conn.recv(1024)
            if not datos:
                break
            print(f"Turno del oponente: {datos.decode()}")
            mi_turno = True


def crear_partida():
    global mi_turno
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 0))  # Bind a cualquier puerto disponible
    server_socket.listen(1)
    puerto = server_socket.getsockname()[1]

    # Inicia un túnel ngrok para el puerto del servidor
    url_tunel = ngrok.connect(puerto, "tcp")
    url_cifrada = cifrar_datos(url_tunel.public_url)
    response_api = post_api(url_cifrada)
    print(f"Partida creada. URL de ngrok: {response_api}")
    print(f"Esperando conexión en el puerto: {puerto}")

    conn, addr = server_socket.accept()
    print(f"Conectado con {addr}")

    mi_turno = True
    hilo = threading.Thread(target=manejar_conexion, args=(conn,))
    hilo.start()
    hilo.join()

def post_api(url_cifrada):
    data_api = {
    'api_dev_key': api_key,
    'api_option': 'paste',
    'api_paste_code': url_cifrada,
    'api_paste_name': 'Codigo Juego',
    }
    response_api = requests.post('https://pastebin.com/api/api_post.php', data=data_api)
    if response_api.status_code == 200:
        return response_api.text.split('/')[-1]
    print(f'Error al obtener el paste: {response_api.status_code}')
    exit(-1)

def unirse_partida(code):
    global mi_turno
    # Obtiene la IP y el puerto del URL de ngrok
    
    url_ngrok = get_api(code)
    
    url_ngrok = descifrar_datos(url_ngrok)
    _, direccion = url_ngrok.split("//")
    ip_remota, puerto_codificado = direccion.split(":")
    puerto = int(puerto_codificado)
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip_remota, puerto))
    print(f"Conectado al servidor en IP: {ip_remota}, Puerto: {puerto}")

    mi_turno = False
    hilo = threading.Thread(target=manejar_conexion, args=(client_socket,))
    hilo.start()
    hilo.join()

def get_api(code):
    url = f'https://pastebin.com/raw/{code}'
    response = requests.get(url)
    return response.text

def main():
    while True:
        comando = input("Escribe 'crear' para crear una partida o 'unir' para unirte a una partida: ").strip().lower()
        if comando == 'crear':
            crear_partida()
            break
        elif comando == 'unir':
            url_ngrok = input("Introduce la URL de ngrok de la partida a la que deseas unirte: ").strip()
            unirse_partida(url_ngrok)
            break
        else:
            print("Comando no reconocido. Por favor, escribe 'crear' o 'unir'.")

if __name__ == "__main__":
    main()

