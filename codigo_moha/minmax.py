from Variables_Globales import *

class arbolMin():
    def __init__(self,profundidad,jugadas):
        self.profundidadDeseada=profundidad
        self.profundidad=0
        self.jugadas=jugadas
        self.id=0
        self.profundidad=0
        self.nodos=[]
        self.iniciarArbol()

    def iniciarArbol(self):
        padre=None
        idN=self.id
        for i in self.jugadas:
            padre=nodo(self,self.id,self.profundidad,padre,i)
            self.nodos.append(padre)
            idN+=1

    def añadirNodo(self,nodo):
        self.nodos.append(nodo)
    
    def devolverJugada(self):
        self.calcularArbol()
        print(self.elegido)
        print(" Aquí es")
        return self.elegido.estado
    
    def calcularArbol(self):
        self.elegido=-1
        valor=-2
        print(str(self.nodos)+" nodos")
        for i in self.nodos:
            i.comprobarValor()
            print(i.valor)
            if i.valor>valor:
                valor=i.valor
                self.elegido=self.nodos

        
class nodo():
    def __init__(self,arbol,id,profundidad,padre,estado) -> None:
        self.arbol=arbol
        self.id=id
        self.profundidad=profundidad
        if profundidad%2==0:
            self.tipo="M"
        else:
            self.tipo  ="m"
        self.padre=padre
        self.hijos=[]
        self.estado=estado
        #print(self.profundidad)
        self.calcularValor()
        self.crearHijos()
    
    def calcularValor(self):
        self.estado=self.estado
        turn=self.estado['STATE']['TURN']
        chips=self.estado['STATE']['CHIPS']
        gamers=self.estado['STATE']['GAMER']
        free=self.estado['STATE']['FREE']
        if  comprobarVictoria(turn, chips, gamers, free): self.valor=1
        elif comprobarVictoria((turn+1)%2, chips, gamers, free): self.valor=-1
        else: self.valor=0
    
    def crearHijos(self):
        if self.profundidad!=self.arbol.profundidadDeseada:
            sucesores=generarSucesores(self.estado)
            for i in sucesores:
                self.arbol.id+=1
                self.hijos.append(nodo(self.arbol,self.arbol.id,self.profundidad+1,self,i))
        else:
            pass

    def comprobarValor(self):
        if len(self.hijos)!=0:
            for i in self.hijos:
                i.comprobarValor()
                i.asignarPadre()
        else:
            if self.padre!=None:
                self.asignarValorPadre()
                
  
    def asignarValorPadre(self):
        if(self.padre.tipo=="M" and self.padre.valor>self.valor):
            self.padre.valor=self.valor
        elif(self.padre.tipo=="m" and self.padre.valor<self.valor):
            self.padre.valor=self.valor


    

