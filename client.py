import socket
import json
import sys


class Client:

    def __init__(self):
        self.user = ""
        self.password = ""
        self.new_password = ""
        self.client_socket=None
    
    def run(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = ('localhost', 8888)
        self.client_socket.connect(server_address)

        message = self.menu()
        self.client_socket.send(json.dumps(message).encode())

        self.comprobeResponse(message)

        self.client_socket.close()

    def menu(self):
        print("Seleccione una opción: ")
        print("1. Iniciar sesión")
        print("2. Registrarme como nuevo usuario")
        print("3. Salir")
        opcion = input()

        if opcion.isdigit():
            opcion = int(opcion)
            if opcion == 1:
                return self.login()
            elif opcion == 2:
                return self.register()
            elif opcion == 3:
                exit()
            else:
                print("Opción inválida, opción no disponible")
                self.menu()
        else:
            print("Opción inválida, introduzca un número")
            self.menu()

    def login(self):
        username = input("Ingrese su nombre de usuario: ")
        password = input("Ingrese su contraseña: ")
        return {"TYPE": "LOG_IN", "USER": username, "PASSWORD": password}


    def register(self):
        username = input("Ingrese su nombre de usuario: ")
        password = input("Ingrese su contraseña: ")
        return {"TYPE": "ADD_USER", "USER": username, "PASSWORD": password}

    def comprobeResponse(self, message):
        response = json.loads(self.client_socket.recv(1024).decode())
        if message['TYPE'] == "ADD_USER" and response['MESSAGE'] == "OK":
            print("Usuario registrado correctamente. Puede iniciar sesión")
            message = self.login()
            self.client_socket.send(json.dumps(message).encode())
            self.comprobeResponse(message)
        elif message['TYPE'] == "ADD_USER" and response['MESSAGE'] == "ERROR":
            print("El usuario ya existe. Intente con otro nombre de usuario")
            message = self.menu()
            self.client_socket.send(json.dumps(message).encode())
            self.comprobeResponse(message)
        elif message['TYPE'] == "LOG_IN" and response['MESSAGE'] == "OK":
            print("\nBienvenido")
            self.user = message['USER']
            self.password = message['PASSWORD']
            message = self.menu2()
            self.client_socket.send(json.dumps(message).encode())
            self.comprobeResponse2(message)
        elif message['TYPE'] == "LOG_IN" and response['MESSAGE'] == "ERROR":
            print("Usuario o contraseña incorrectos. Intente de nuevo")
            message = self.menu()
            self.client_socket.send(json.dumps(message).encode())
            self.comprobeResponse(message)

    def menu2(self):
        print("Seleccione una opción: ")
        print("1. Modificar mi usuario")
        print("2. Eliminar mi usuario")
        print("3. Crear una partida")
        print("4. Buscar una partida")
        print("5. Cerrar sesión")
        opcion = input()

        if opcion.isdigit():
            opcion = int(opcion)
            if opcion == 1:
                return self.modifyUser()
            elif opcion == 2:
                return {"TYPE": "DELETE_USER", "USER": self.user, "PASSWORD": self.password}
            elif opcion == 3:
                return {"TYPE": "NEW_GAME"}
            elif opcion == 4:
                return {"TYPE": "SEARCH_GAME"}
            elif opcion == 5:
                return {"TYPE": "LOG_OUT"}
                message = self.menu()
                self.client_socket.send(json.dumps(message).encode())

                self.comprobeResponse(message)
            else:
                print("Opción inválida, opción no disponible")
                self.menu2()
        else:
            print("Opción inválida, introduzca un número")
            self.menu2()

    def modifyUser(self):
        new_password = input("Ingrese su nueva contraseña: ")
        return {"TYPE": "MODIFY_USER", "USER": self.user, "PASSWORD": self.password, "NEW_PASSWORD": new_password}

    def comprobeResponse2(self, message):
        response = json.loads(self.client_socket.recv(1024).decode())

        if message['TYPE'] == "MODIFY_USER" and response['MESSAGE'] == "OK":
            print("Usuario modificado correctamente")
            self.password = message['NEW_PASSWORD']
            self.new_password = ""
            message = self.menu2()
            self.client_socket.send(json.dumps(message).encode())
            self.comprobeResponse2(message)
        elif message['TYPE'] == "MODIFY_USER" and response['MESSAGE'] == "ERROR":
            print("No se pudo modificar correctamente el usuario. Intente de nuevo")
            message = self.menu2()
            self.client_socket.send(json.dumps(message).encode())
            self.comprobeResponse2(message)
        elif message['TYPE'] == "DELETE_USER" and response['MESSAGE'] == "OK":
            print("Usuario eliminado correctamente")
            self.user = ""
            self.password = ""
            message = self.menu()
            self.client_socket.send(json.dumps(message).encode())
            self.comprobeResponse(message)
        elif message['TYPE'] == "DELETE_USER" and response['MESSAGE'] == "ERROR":
            print("No se pudo eliminar el usuario. Intente de nuevo")
            message = self.menu2()
            self.client_socket.send(json.dumps(message).encode())
            self.comprobeResponse2(message)
        elif message['TYPE'] == "NEW_GAME" and response['MESSAGE'] != "ERROR":
            print("Partida creada correctamente")
            # Partida creada, conexion con game?
        elif message['TYPE'] == "NEW_GAME" and response['MESSAGE'] == "ERROR":
            print("No se ha podido crear la partida")
            message = self.menu2()
            self.client_socket.send(json.dumps(message).encode())
            self.comprobeResponse2(message)
        elif message['TYPE'] == "SEARCH_GAME" and len(response['MESSAGE']) > 0:
            print("Partidas encontrada: " + response['MESSAGE'], sep="\n")
            id(input("Seleccione una partida:"))
            while id not in response['MESSAGE']:
                print("Partida no encontrada")
                id = input("Seleccione una partida: " + response['MESSAGE'], sep="\n")

            print("Partida seleccionada correctamente")
            message = {"TYPE": "JOIN_GAME", "ID": id}
            self.client_socket.send(json.dumps(message).encode())
            # Unirse a una partida

        elif message['TYPE'] == "SEARCH_GAME" and len(response['MESSAGE']) == 0:
            print("No se ha encontrado ninguna partida, pruebe a crear una nueva")
            message = self.menu2()
            self.client_socket.send(json.dumps(message).encode())
            self.comprobeResponse2(message)
        elif message['TYPE'] == "LOG_OUT" and response['MESSAGE'] == "OK":
            print("Sesión cerrada correctamente")
            self.user = ""
            self.password = ""
            message = self.menu()
            self.client_socket.send(json.dumps(message).encode())
            self.comprobeResponse(message)
        elif message['TYPE'] == "LOG_OUT" and response['MESSAGE'] == "ERROR":
            print("No se ha podido cerrar la sesión. Intente de nuevo")
            message = self.menu2()
            self.client_socket.send(json.dumps(message).encode())
            self.comprobeResponse2(message)

if __name__ == "__main__":
    client = Client()
    client.run()
