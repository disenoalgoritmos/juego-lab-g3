import socket
import json

def __init__(self):
    self.user=""
    self.password=""
    self.new_password=""

def menu():
    opcion = input("Seleccione una opción: ")
    print("1. Iniciar sesión")
    print("2. Registrarme como nuevo usuario")
    print("3. Salir")

    if opcion.isdigit():
        opcion = int(opcion)
        if opcion == 1:
            login()
        elif opcion == 2:
            register()
        elif opcion == 3:
            exit()
        else:
            print("Opción inválida, opción no disponible")
            menu()
    else:
        print("Opción inválida, introduzca un número")
        menu()

def login():
    username = input("Ingrese su nombre de usuario: ")
    password = input("Ingrese su contraseña: ")
    return {"Type": "LOG_IN", "user": username , "pass" : password}

def register():
    username = input("Ingrese su nombre de usuario: ")
    password = input("Ingrese su contraseña: ")
    return {"Type" : "ADD_USER", "user" : username,"pass" : password}

def comprobeResponse(self, message):
    response = client_socket.recv(1024).decode()
    if message['Type']== "ADD_USER" and response == "OK":
        print("Usuario registrado correctamente. Puede iniciar sesión")
        message=login()
        client_socket.send(json.dumps(message).encode())
        comprobeResponse(message)
    elif message['Type']== "ADD_USER" and response == "ERROR":
        print("El usuario ya existe. Intente con otro nombre de usuario")
        message = menu()
        client_socket.send(json.dumps(message).encode())
        comprobeResponse(message)
    elif message['Type']== "LOG_IN" and response == "OK":
        print("Bienvenido")
        self.user=message['user']
        self.password=message['pass']
        message = menu2()
        client_socket.send(json.dumps(message).encode())
        comprobeResponse2(message)
    elif message['Type']== "LOG_IN" and response == "ERROR":
        print("Usuario o contraseña incorrectos. Intente de nuevo")
        message = menu()
        client_socket.send(json.dumps(message).encode())
        comprobeResponse(message)

def menu2():
    opcion = input("Seleccione una opción: ")
    print("1. Modificar mi usuario")
    print("2. Eliminar mi usuario")
    print("3. Crear una partida")
    print("4. Buscar una partida")
    print("5. Cerrar sesión")

    if opcion.isdigit():
        opcion = int(opcion)
        if opcion == 1:
            modifyUser()
        elif opcion == 2:
            return {"Type" : "DELETE_USER", "user" : self.user, "pass" : self.password}
        elif opcion == 3:
            return {"Type" : "NEW_GAME"}
        elif opcion == 4:
            return {"Type" : "SEARCH_GAME"}
        elif opcion == 5:
            return {"Type" : "LOG_OUT"}
            message = menu()
            client_socket.send(json.dumps(message).encode())

            comprobeResponse(message)
        else:
            print("Opción inválida, opción no disponible")
            menu2()
    else:
        print("Opción inválida, introduzca un número")
        menu2()

def modifyUser(self):
    new_password = input("Ingrese su nueva contraseña: ")
    return {"Type" : "MODIFY_USER", "user" : self.user, "pass" : self.password, "new_pass" : new_password}

def comprobeResponse2(message):
    response = client_socket.recv(1024).decode()
    
    if message['Type']=="MODIFY_USER" and response == "OK":
        print("Usuario modificado correctamente")
        self.password=message['new_pass']
        self.new_password=""
        message=menu2()
        client_socket.send(json.dumps(message).encode())
        comprobeResponse2(message)
    elif message['Type']=="MODIFY_USER" and response == "ERROR":
        print("No se pudo modificar correctamente el usuario. Intente de nuevo")
        message = menu2()
        client_socket.send(json.dumps(message).encode())
        comprobeResponse2(message)
    elif message['Type']=="DELETE_USER" and response == "OK":
        print("Usuario eliminado correctamente")
        self.user=""
        self.password=""
        message = menu()
        client_socket.send(json.dumps(message).encode())
        comprobeResponse(message)
    elif message['Type']=="DELETE_USER" and response == "ERROR":
        print("No se pudo eliminar el usuario. Intente de nuevo")
        message = menu2()
        client_socket.send(json.dumps(message).encode())
        comprobeResponse2(message)
    elif message['Type']=="NEW_GAME" and response != "ERROR":
        print("Partida creada correctamente")
        #Partida creada, conexion con game?
    elif message['Type']=="NEW_GAME" and response == "ERROR":
        print("No se ha podido crear la partida")
        message = menu2()
        client_socket.send(json.dumps(message).encode())
        comprobeResponse2(message)
    elif message['Type']=="SEARCH_GAME" and response != "ERROR":
        print("Partida encontrada: " + response)
        #Unirse a una partida
        
    elif message['Type']=="SEARCH_GAME" and response == "ERROR":
        print("No se ha encontrado ninguna partida, pruebe a crear una nueva")
        message = menu2()
        client_socket.send(json.dumps(message).encode())
        comprobeResponse2(message)
    elif message['Type']=="LOG_OUT" and response == "OK":
        print("Sesión cerrada correctamente")
        self.user=""
        self.password=""
        message = menu()
        client_socket.send(json.dumps(message).encode())
        comprobeResponse(message)
    elif message['Type']=="LOG_OUT" and response == "ERROR":
        print("No se ha podido cerrar la sesión. Intente de nuevo")
        message = menu2()
        client_socket.send(json.dumps(message).encode())
        comprobeResponse2(message)


if __name__ =="__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('localhost', 8000)
    client_socket.connect(server_address)

    message = menu()
    client_socket.send(json.dumps(message).encode())

    comprobeResponse(message)

    client_socket.close()