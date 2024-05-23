import os
import platform
import threading

def manageCommand(command): 
    current_os = platform.system()
    if current_os == "Windows":
        os.system(f'start cmd /k "{command}"')
    elif current_os == "Linux":
        os.system(f'gnome-terminal -- bash -c "{command}; exec bash"')
    else :
        print(f'{current_os} is not supported')
    #exit_code = os.system(command)
    #print(f"The command '{command}' exited with code: {exit_code}")


command_server = "python3 server_api.py"
command_ngrok = "ngrok http http://localhost:8000"


hilo_serv = threading.Thread(target=manageCommand, args=(command_server,))
hilo_ngrok = threading.Thread(target=manageCommand, args=(command_ngrok,))


hilo_ngrok.start()
hilo_ngrok.join()


hilo_serv.start()
hilo_serv.join()
