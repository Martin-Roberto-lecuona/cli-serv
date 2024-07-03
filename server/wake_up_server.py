import os
import platform
import threading


command_server = "python3 server_api.py"
command_ngrok = "ngrok http http://localhost:8000"

def manageCommand(command): 
    global command_server
    current_os = platform.system()
    if current_os == "Windows":
        command_server = "python server_api.py"
        os.system(f'start cmd /k "{command}"')
    elif current_os == "Linux":
        os.system(f'gnome-terminal -- bash -c "{command}; exec bash"')
    else :
        print(f'{current_os} is not supported')
    #exit_code = os.system(command)
    #print(f"The command '{command}' exited with code: {exit_code}")




hilo_serv = threading.Thread(target=manageCommand, args=(command_server,))
hilo_ngrok = threading.Thread(target=manageCommand, args=(command_ngrok,))


hilo_ngrok.start()
hilo_ngrok.join()


hilo_serv.start()
hilo_serv.join()
