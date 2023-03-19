import asyncio
import json
import subprocess
import socket
import platform
import random


class Client:

    def __init__(self):
        self.ip = '127.0.0.1'
        self.user = ""
        self.password = ""
        self.new_password = ""
        self.writer=None
        self.reader=None
        self.salir=False
        self.jugador=None
    
    async def run(self):
        self.reader, self.writer = await asyncio.open_connection(
        self.ip, 8908)

        print(  "  _______     _____  _____ \n"+
                " |__   __|   |  ___|/  _  \ \n"+
                "    | |_    _| |_  |  (_)  |___\n"+
                "    | | |  | |  _|  \___   / _ \ \n"+
                " ___| | |__| | |___  ___| | (_)   \n"+
                "|_____|______|_____||_____|\___/  \n"+


                "      _____  _____ _   \n" +     
                "     |  __ \|  ___| |  \n" + 
                "     | |  | | |_  | |  \n" + 
                "     | |  | |  _| | |  \n" +     
                "     | |__| | |___| |____ \n" +
                "     |_____/|_____|______|  \n"+

                " ___    ___       _ _     \n"+
                "|   \  /   |     | |_|     \n"+
                "| |\ \/ /| | ___ | |_ ______  ___  \n"+
                "| | \__/ | |/ _ \| | |  __  |/ _ \  \n"+
                "| |      | | (_) | | | |  | | (_)    \n"+
                "|_|      |_|\___/|_|_|_|  |_|\___/   ")

        message = await self.menu()

        self.writer.write(json.dumps(message).encode())
        await self.writer.drain()

        await self.comprobeResponse(message)

    async def run2(self):
        message = await self.menu2()
        self.writer.write(json.dumps(message).encode())
        await self.writer.drain()
        await self.comprobeResponse2(message)

    async def menu(self):
        print("\nSeleccione una opción: ")
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
                self.salir=True
                print('\nClose the connection')
                self.writer.close()
                await self.writer.wait_closed()
                exit()
            else:
                print("\nOpción inválida, opción no disponible")
                message = await self.menu()
                self.writer.write(json.dumps(message).encode())
                await self.writer.drain()

                await self.comprobeResponse(message)
        else:
            print("\nOpción inválida, introduzca un número")
            message = await self.menu()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()

            await self.comprobeResponse(message)

    def login(self):
        username = input("\nIngrese su nombre de usuario: ")
        password = input("Ingrese su contraseña: ")
        return {"TYPE": "LOGIN", "USER": username, "PASSWORD": password}


    def register(self):
        username = input("\nIngrese su nombre de usuario: ")
        password = input("Ingrese su contraseña: ")
        return {"TYPE": "ADD_USER", "USER": username, "PASSWORD": password}

    async def comprobeResponse(self, message):
        response = await self.reader.read(100)
        response = json.loads(response.decode())
        if message['TYPE'] == "ADD_USER" and response['MESSAGE'] == "OK":
            print("\nUsuario registrado correctamente. Puede iniciar sesión")
            message = self.login()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse(message)
        elif message['TYPE'] == "ADD_USER" and response['MESSAGE'] == "ERROR":
            print("\nEl usuario ya existe. Intente con otro nombre de usuario")
            message = await self.menu()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse(message)
        elif message['TYPE'] == "LOGIN" and response['MESSAGE'] == "OK":
            print("\nBienvenido")
            self.user = message['USER']
            self.password = message['PASSWORD']
            message = await self.menu2()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)
        elif message['TYPE'] == "LOGIN" and response['MESSAGE'] == "ERROR":
            print("\nUsuario o contraseña incorrectos. Intente de nuevo")
            message = await self.menu()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse(message)

    async def menu2(self):
        print("\nSeleccione una opción: ")
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
                return {"TYPE": "DELETE", "USER": self.user, "PASSWORD": self.password}
            elif opcion == 3:
                return self.new_game()
            elif opcion == 4:
                return {"TYPE": "SEARCH_GAME"}
            elif opcion == 5:
                return {"TYPE": "LOG_OUT", "USER": self.user, "PASSWORD": self.password}
                message = self.menu()
                self.writer.write(json.dumps(message).encode())
                await self.writer.drain()

                await self.comprobeResponse(message)
            else:
                print("Opción inválida, opción no disponible")
                message = await self.menu2()
                self.writer.write(json.dumps(message).encode())
                await self.writer.drain()
                await self.comprobeResponse2(message)
        else:
            print("Opción inválida, introduzca un número")
            message = await self.menu2()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)

    def modifyUser(self):
        new_password = input("\nIngrese su nueva contraseña: ")
        return {"TYPE": "MODIFY_USER", "USER": self.user, "PASSWORD": self.password, "NEW_PASSWORD": new_password}

    def new_game(self):
        id_game = input("\nIngrese el id de la partida: ")
        return {"TYPE": "NEW_GAME", "ID_GAME": id_game}

    async def comprobeResponse2(self, message):
        response = await self.reader.read(100)
        response = json.loads(response.decode())

        if message['TYPE'] == "MODIFY_USER" and response['MESSAGE'] == "OK":
            print("\nUsuario modificado correctamente")
            self.password = message['NEW_PASSWORD']
            self.new_password = ""
            message = await self.menu2()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)
        elif message['TYPE'] == "MODIFY_USER" and response['MESSAGE'] == "ERROR":
            print("\nNo se pudo modificar correctamente el usuario. Intente de nuevo")
            message = await self.menu2()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)
        elif message['TYPE'] == "DELETE" and response['MESSAGE'] == "OK":
            print("\nUsuario eliminado correctamente")
            self.user = ""
            self.password = ""
            message = await self.menu()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse(message)
        elif message['TYPE'] == "DELETE" and response['MESSAGE'] == "ERROR":
            print("\nNo se pudo eliminar el usuario. Intente de nuevo")
            message = await self.menu2()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)
        elif message['TYPE'] == "NEW_GAME" and response['MESSAGE'] == "OK":
            print("\nPartida creada correctamente. Búsquela y pruebe a unirse a ella.")
            message = await self.menu2()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)

        elif message['TYPE'] == "NEW_GAME" and response['MESSAGE'] == "ERROR":
            print("\nNo se ha podido crear la partida")
            message = await self.menu2()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)

        elif message['TYPE'] == "SEARCH_GAME" and len(response['MESSAGE']) > 0:
            print("\nPartidas encontradas: ")
            for item in response['MESSAGE']:
                print(item)
            id=input("\nSeleccione una partida:")
            while id not in response['MESSAGE']:
                print("\nError al introducir el id de la partida")
                print("Partidas encontradas: ")
                for item in response['MESSAGE']:
                    print(item)
                id=input("\nSeleccione una partida:")

            print("\nPartida seleccionada correctamente")
            
            puertos = range(49153, 65535)
            puerto=random.choice(puertos)

            correcto = False
            while correcto == False:
                print("\nSeleccione una opción: ")
                print("1. Jugador manual")
                print("2. Jugador torpe (al azar)")
                #print("3. Jugador perfecto (algortimo minimax)")
                opcion = input()

                if opcion.isdigit():
                    opcion = int(opcion)
                    if opcion in [1,2]:
                        self.jugador=opcion
                        correcto=True
                    else:
                        print("Opción inválida, opción no disponible")
                else:
                    print("Opción inválida, introduzca un número")

            
            message = {"TYPE": "JOIN_GAME", "ID_GAME": id, "ADDR":[self.ip, str(puerto)]}
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)

        elif message['TYPE'] == "SEARCH_GAME" and len(response['MESSAGE']) == 0:
            print("\nNo se ha encontrado ninguna partida, pruebe a crear una nueva")
            message = await self.menu2()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)

        elif message['TYPE'] == "JOIN_GAME" and response['MESSAGE'] == "OK":
            print("\nPartida unida correctamente")
            argumentos = [str(message.get('ADDR')[0]), str(message.get('ADDR')[1]), str(self.jugador)]
            comando = ["python", ".\clienteGAME_socket.py"] + argumentos
            if(platform.system()=="Windows"):
                subprocess.Popen(comando, creationflags =subprocess.CREATE_NEW_CONSOLE)
            else:
                print(f"Ejecute el siguiente comando en otra terminal: python3 clienteGAME_socket.py  {str(message.get('ADDR')[0])} {str(message.get('ADDR')[1])} {str(self.jugador)} ")    
            # Unirse a una partida
            message = await self.menu2()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)
        
        elif message['TYPE'] == "JOIN_GAME" and response['MESSAGE'] == "ERROR":
            print("\nNo se ha podido unir a la partida")
            message = await self.menu2()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)
        
        elif message['TYPE'] == "LOG_OUT" and response['MESSAGE'] == "OK":
            print("\nSesión cerrada correctamente")
            self.user = ""
            self.password = ""
            message = await self.menu()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse(message)
        elif message['TYPE'] == "LOG_OUT" and response['MESSAGE'] == "ERROR":
            print("\nNo se ha podido cerrar la sesión. Intente de nuevo")
            message = await self.menu2()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)

if __name__ == "__main__":
    client = Client()
    asyncio.run(client.run())
