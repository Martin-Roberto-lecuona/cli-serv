import socket
import threading
from pyngrok import ngrok
from cryptography.fernet import Fernet

import requests
base_url = "https://5879-190-192-155-209.ngrok-free.app"

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
    response_api = add_text_api(url_cifrada)
    print(f"Partida creada. codigo de sala: {response_api}")
    print(f"Esperando conexión en el puerto: {puerto}")

    conn, addr = server_socket.accept()
    print(f"Conectado con {addr}")

    mi_turno = True
    hilo = threading.Thread(target=manejar_conexion, args=(conn,))
    hilo.start()
    hilo.join()

def unirse_partida(code):
    global mi_turno
    # Obtiene la IP y el puerto del URL de ngrok
    
    url_ngrok = get_text_api(code)
    url_ngrok = url_ngrok["text"]
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

def add_text_api(puerto_encriptado):
    url = f"{base_url}/add/"
    payload = {
        "text": puerto_encriptado
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error al agregar el texto:", response.status_code, response.json())
        exit(-1)

# Ejemplo de cómo obtener un texto (GET)
def get_text_api(codigo_sala):
    url = f"{base_url}/get/{codigo_sala}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error al obtener el texto:", response.status_code, response.json())
        exit(-1)

# Ejemplo de cómo eliminar un texto (DELETE)
def delete_text_api(item_id):
    url = f"{base_url}/delete/{item_id}"
    response = requests.delete(url)
    if response.status_code == 200:
        print("Texto eliminado:", response.json())
    else:
        print("Error al eliminar el texto:", response.status_code, response.json())
        exit(-1)

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

