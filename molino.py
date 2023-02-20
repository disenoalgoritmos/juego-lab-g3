class Estado:
    def __init__(self):
        self.Free = [True] *24
        self.Gamer = [[],[]]
        self.Turn = 0
        self.chips = 18
class Accion:
    def __init__(self,origen,destino,kill):
        self.origen=origen
        self.destino = destino
        self.kill = kill
        pass
class Tablero:
    def __init__(self,estado):
        self.estado = estado

    def validarAccion(self,accion:Accion):
        
        """if(accion.turno != (self.estado+1)%2):
            return False"""
        if self.estado.chips > 0:
            #Etapa inicial
            if accion.origen != -1:
                return False
            if (self.estado.Free[accion.destino] ==False):
                return False
            if self.validarAccionKill(accion) == False:
                return False
        else:
            #Etapa de movimiento
            if self.estado.Free[accion.origen]==False:
                return False
            if accion.origen not in self.estado.Gamer[self.estado.Turn]:
                return False
            movimientosDisponibles = self.MovimientosValidos(accion.origen)
            if accion.destino not in movimientosDisponibles:
                return False
            if self.validarAccionKill(accion) == False:
                return False
        

        return True

                



    def validarAccionKill(self,accion:Accion):
        if self.comprobarMolino(accion.destino) == True:
                if accion.kill == -1:
                    return False
                if accion.kill not in self.estado.Gamer[(self.estado.Turn+1)%2]:
                    return False
                fichasComibles = self.estado.Gamer[(self.estado.Turn+1)%2].copy()
                if self.comprobarMolino(accion.kill):
                
                    fichasComibles.remove(accion.kill)
                    for ficha in fichasComibles:
                        if not self.comprobarMolino(ficha):
                            return False
                
        else:
            if accion.kill != -1:
                return False
        return True

    def ejecutarAccion(self,accion:Accion):
        self.estado.Free[accion.origen] = True
        self.estado.Free[accion.destino] = False
        if(self.estado.chips<=0):
            self.estado.Gamer[self.estado.Turn].remove(accion.origen)
        self.estado.Gamer[self.estado.Turn].append(accion.destino)
        if accion.kill != -1:
            self.estado.Gamer[(self.estado.Turn+1)%2].remove(accion.kill)
            self.estado.Free[accion.kill] = True
        if self.estado.chips > 0:
            self.estado.chips -= 1
        print (f"Accion: origen={accion.origen}, destino={accion.destino}, kill={accion.kill}, turno={self.estado.Turn}")
        #self.Print()
        self.estado.Turn = (self.estado.Turn+1)%2

    def comprobarMolino(self,posicion):
        anillo = self.NivelAnillo(posicion)
        if self.EsPasillo(posicion): #Estamos en un pasillo

            if(anillo==0):
                if posicion+8 in self.estado.Gamer[self.estado.Turn] and not self.estado.Free[posicion+8] \
                and posicion+16 in self.estado.Gamer[self.estado.Turn] and not self.estado.Free[posicion+16]:
                    return True

            elif anillo==1:
                if posicion+8 in self.estado.Gamer[self.estado.Turn] and not self.estado.Free[posicion+8] \
                    and posicion-8 in self.estado.Gamer[self.estado.Turn] and not self.estado.Free[posicion+8]:
                    return True

            elif anillo==2:
                if posicion-8 in self.estado.Gamer[self.estado.Turn] and not self.estado.Free[posicion-16] \
                    and posicion-8 in self.estado.Gamer[self.estado.Turn] and not self.estado.Free[posicion-16]:
                    return True

            else:
                return False
            if self.Mover(posicion,1) in self.estado.Gamer[self.estado.Turn] and not self.estado.Free[self.Mover(posicion,1)] \
                and self.Mover(posicion,-1) in self.estado.Gamer[self.estado.Turn] and not self.estado.Free[self.Mover(posicion,-1)]:
                return True

        else: #estamos en una esquina
            if self.Mover(posicion,1) in self.estado.Gamer[self.estado.Turn] and not self.estado.Free[self.Mover(posicion,1)] \
                and self.Mover(posicion,2) in self.estado.Gamer[self.estado.Turn] and not self.estado.Free[self.Mover(posicion,2)]:
                return True
            elif self.Mover(posicion,-1) in self.estado.Gamer[self.estado.Turn] and not self.estado.Free[self.Mover(posicion,-1)] \
                and self.Mover(posicion,-2) in self.estado.Gamer[self.estado.Turn]and not self.estado.Free[self.Mover(posicion,-2)]:
                return True

        return False
    def EsPasillo(self,posicion):
        return posicion%2 == 1
    def NivelAnillo(self,posicion):
        return posicion//8
    def Mover(self,origen, distancia):
        destino = origen + distancia
        
        return destino%8+8*(self.NivelAnillo(origen))
    def MovimientosValidos(self,posicion):
        movimientosValidos = {}
        movimientosValidos.add(self.Mover(posicion,-1))
        movimientosValidos.add(self.Mover(posicion,+1))
        if self.EsPasillo(posicion): #estamos en un pasillo
            anillo = self.nivelAnillo()
            if anillo==0:
                movimientosValidos.add(posicion+8)

            elif anillo==1:
                movimientosValidos.add(posicion+8)
                movimientosValidos.add(posicion-8)
                    
            elif anillo==2:
                movimientosValidos.add(posicion-8)
        return movimientosValidos
    def Print(self):
        matriz = [["0","—","—","—","—","—","1","—","—","—","—","—","2"],
            ["|"," "," "," "," "," ","|"," "," "," "," "," ","|"],
            ["|"," ","8","—","—","—","9","—","—","—","10"," ","|"],
            ["|"," ","|"," "," "," ","|"," "," "," ","|"," ","|"],
            ["|"," ","|"," ","16","—","17","—","18"," ","|"," ","|"],
            ["|"," ","|"," ","|"," "," "," ","|"," ","|"," ","|"],
            ["7","—","15","—","23"," "," "," ","19","—","11","—","3"],
            ["|"," ","|"," ","|"," "," "," ","|"," ","|"," ","|"],
            ["|"," ","|"," ","22","—","21","—","20"," ","|"," ","|"],
            ["|"," ","|"," "," "," ","|"," "," "," ","|"," ","|"],
            ["|"," ","14","—","—","—","13","—","—","—","12"," ","|"],
            ["|"," "," "," "," "," ","|"," "," "," "," "," ","|"],
            ["6","—","—","—","—","—","5","—","—","—","—","—","4"]]


        indice = {0: (0, 0), 1: (0, 6), 2: (0, 12), 8: (2, 2), 9: (2, 6), 10: (2, 10), 16: (4, 4), 17: (4, 6), 18: (4, 8), 7: (6, 0), 15: (6, 2), 23: (6, 4), 19: (6, 8), 11: (6, 10), 3: (6, 12), 22: (8, 4), 21: (8, 6), 20: (8, 8), 14: (10, 2), 13: (10, 6), 12: (10, 10), 6: (12, 0), 5: (12, 6), 4: (12, 12)}
        for x in self.estado.Gamer[0]:
            matriz[indice[x][0]][indice[x][1]] = f"J{0}({x})"
        for x in self.estado.Gamer[1]:
             matriz[indice[x][0]][indice[x][1]] = f"J{1}({x})"

        for x in matriz:
            print (x)
        



def getAccion():
    origen = int(input("Introduce un número entero de origen(-1 si no esta en el tablero): "))
    destino = int(input("Introduce un número entero de destino: "))
    kill = int(input("Introduce un número entero como kill(-1 si no hay kill): "))
    return Accion(origen,destino,kill)

if __name__ =="__main__":
    tablero = Tablero(Estado())#tablero y estado inicial
    while tablero.estado.chips > 0 or (tablero.estado.Gamer[0].count() >= 3 and tablero.estado.Gamer[1].count() >= 3):
        tablero.Print()
        accion = getAccion()
        if tablero.validarAccion(accion): 
            tablero.ejecutarAccion(accion)
        else:
            print("Accion no valida")
    print ("partida terminada")
