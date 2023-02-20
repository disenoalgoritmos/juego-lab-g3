class Estado:
    def __init__(self):
        self.Free = [True] *24
        self.Gamer = [{},{}]
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
        
        if(accion.turno != (self.estado+1)%2):
            return False
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
        self.estado.Gamer[self.estado.Turn].remove(accion.origen)
        self.estado.Gamer[self.estado.Turn].add(accion.destino)
        if accion.kill != -1:
            self.estado.Gamer[(self.estado.Turn+1)%2].remove(accion.kill)
            self.estado.Free[accion.kill] = True
        if self.estado.chips > 0:
            self.estado.chips -= 1
        self.estado.Turn = (self.estado.Turn+1)%2

    def comprobarMolino(self,posicion):
        anillo = self.NivelAnillo(posicion)
        if self.EsPasillo(posicion): #Estamos en un pasillo

            if(anillo==0):
                if self.estado.Gamer[self.estado.Turn][posicion+8] and self.estado.Free[posicion+8] \
                and self.estado.Gamer[self.estado.Turn][posicion+16] and self.estado.Free[posicion+16]:
                    return True

            elif anillo==1:
                if self.estado.Gamer[self.estado.Turn][posicion-8] and self.estado.Free[posicion+8] \
                    and self.estado.Gamer[self.estado.Turn][posicion-8] and self.estado.Free[posicion+8]:
                    return True

            elif anillo==2:
                if self.estado.Gamer[self.estado.Turn][posicion-8] and self.estado.Free[posicion-16] \
                    and self.estado.Gamer[self.estado.Turn][posicion-8] and self.estado.Free[posicion-16]:
                    return True

            else:
                return False
            if self.estado.Gamer[self.estado.Turn][self.Mover(posicion,1)] and self.estado.Free[self.Mover(posicion,1)] \
                and self.estado.Gamer[self.estado.Turn][self.Mover(posicion,-1)] and self.estado.Free[self.Mover(posicion,-1)]:
                return True

        else: #estamos en una esquina
            if self.estado.Gamer[self.estado.Turn][self.Mover(posicion,1)] and self.estado.Free[self.Mover(posicion,1)] \
                and self.estado.Gamer[self.estado.Turn][self.Mover(posicion,2)] and self.estado.Free[self.Mover(posicion,2)]:
                return True
            elif self.estado.Gamer[self.estado.Turn][self.Mover(posicion,-1)] and self.estado.Free[self.Mover(posicion,-1)] \
                and self.estado.Gamer[self.estado.Turn][self.Mover(posicion,-2)] and self.estado.Free[self.Mover(posicion,-2)]:
                return True

        return False
    def EsPasillo(posicion):
        return posicion%2 == 0
    def NivelAnillo(posicion):
        return posicion%8
    def Mover(origen, distancia):
        destino = origen%8 - distancia
        if(destino <=0):
            return destino+8
        return destino
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