""""
estado= {Free[int] lista posiciones libres en el tablero. Inicializado a [0,1,2....23] o array de tamaño 24 de boolea, true=libre
        Gamer [[int][int]] posiciones de las fichas del jugador 1 y 2. Inicializado a vacio
        Turn 0 o 1 indica a que jugador le toca el turno. Inicializado a 0
        chips int numero de fichas sin poner. inicializado a 18. 9 por jugador
    
    #en lugar de expecion podriamos crear la funcion etapaInicial que devuelva true o false en funcion de si es valida
    getAccion()
    if (accion.turno no igual a (estado.turno+1)%2) La accion esta intentado mover en un turno que no corresponde
        lanzar excepcion accion no valida
    if estado.chips > 0
        #Etapa inicial
        if(accion.origen no es -1) # si no es una ficha de fuera del tablero
            lanzar excepcion accion no valida
        if(accion.destino no esta en estado.Free) #No es una posicion valida
            lanzar excepcion accion no valida
        if(comprobarMolino(accion.destino)) #el jugador a formado un molino
            #Esto se podria meter en una funcion validarAccionKill
            if(accion.kill es igual a -1)# si  hay molino pero la accion no intenta comer una ficha
                lanzar excepcion accion no valida
            comprobar que la ficha que comemos es del rival y que esta en el tablero(que no esta libre)
            obtener las fichas que nos podemos comer(clonar la lista del jugador rival del estado)
            if(comprobarMolino(accion.kill)) #la ficha que intetamos comer es un molino
                fichasComibles.pop(accion.kill)
                foreach fichas comibles #Tambien se puede usar la funcion any( comprobarMolino(x) for x in fichasComibles)
                    if not comprobarmolino(i) #Una ficha comible no es molino
                        lanzar excepcion no valida #Solo se puede comer una ficha de un molino si no existe

        else
            if(accion.kill distino de -1)# si no hay molino pero la accion intenta comer una ficha
                lanzar excepcion accion no valida

        
    else
        #Etapa de movimiento
        if(estado.Free[accion.origen] = false) #Se esta intentado mover una ficha de una posicion vacia
            lanzar excepcion no valida
        if(accion.origen not in gamer[turno])#la ficha que se intenta mover no es tuya
            lanzar excepcion no valida
        movimientosDisponibles = MovimientosValidos(accion.origen)
        if(accion.destino not in movimientosDisponible)
            lanzar excepcion no valida
        if(comprobarMolino(accion.destino))
            #Esto se podria meter en una funcion validarAccionKill
            if(accion.kill es igual a -1)# si  hay molino pero la accion no intenta comer una ficha
                    lanzar excepcion accion no valida
                comprobar que la ficha que comemos es del rival y que esta en el tablero(que no esta libre)
                obtener las fichas que nos podemos comer(clonar la lista del jugador rival del estado)
                if(comprobarMolino(accion.kill)) #la ficha que intetamos comer es un molino
                    fichasComibles.pop(accion.kill)
                    foreach fichas comibles #Tambien se puede usar la funcion any( comprobarMolino(x) for x in fichasComibles)
                        if not comprobarmolino(i) #Una ficha comible no es molino
                            lanzar excepcion no valida #Solo se puede comer una ficha de un molino si no existe
        else
            if(accion.kill distino de -1)# si no hay molino pero la accion intenta comer una ficha
                lanzar excepcion accion no valida
    
    #Ejecutamos la accion
        estado.Free[accion.origen] = true
        estado.Free[accion.destino] = false
        gamer[turno].add = accion.origen
        if accion.kill distino a -1
            gamer[(turno+1)%2].pop(accion.kill) #eliminamos la ficha del jugador rival
            estado.Free[accion.kill] = true #Marcamos como libre la posicion de la ficha comida
        if(estado.chips>0)
            estado.chips--
        estado.turno = (estado.turno+1)%2
        PrintEstado()

    if(Gamer[0].count < 3 OR Gamer[1].count < 3) #Meter en un while que englobe todo
        Terminar juego


bool ComprobarMolino(int posicion,jugador){ #jugador tambien es el turno
    anillo = nivelAnillo(posicion)
    if(EsPasillo(posicion)) #Estamos en un pasillo

        if(anillo==0)
            if(estado.Gamer[jugador][poisicion+8] && estado.Free[posicion+8]
                && estado.Gamer[jugador][poisicion+16] && estado.Free[posicion+16])
                return true

        elif(anillo==1)
            if(estado.Gamer[jugador][poisicion-8] && estado.Free[posicion+8]
                && estado.Gamer[jugador][poisicion-8] && estado.Free[posicion+8])
                return true

        elif(anillo=2)
            if(estado.Gamer[jugador][poisicion-8] && estado.Free[posicion-16]
                && estado.Gamer[jugador][poisicion-8] && estado.Free[posicion-16])
                return true

        else
            Error
        if(estado.Gamer[jugador][mover(posicion,1)] && estado.Free[mover(posicion,1)]
            && estado.Gamer[jugador][(mover(posicion,-1)] && estado.Free[mover(posicion,-1)])
            return true;

    else #estamos en una esquina
        if(estado.Gamer[jugador][mover(posicion,1)] && estado.Free[mover(posicion,1)]
            && estado.Gamer[jugador][(mover(posicion,2)] && estado.Free[mover(posicion,2)])
            return true;
        elif(estado.Gamer[jugador][mover(posicion,-1)] && estado.Free[mover(posicion,-1)]
            && estado.Gamer[jugador][(mover(posicion,-2)] && estado.Free[mover(posicion,-2)])
            return true;


}
mover(int origen,int distancia)
    destino = origen%8 - distancia
    if(destino <=0)
        return destino+8
    return destino
moverPasillo(int origen,int distancia)
    destino = origen
#Devuelve 0,1 o 2 segun el anillo donde se encuentre la posicion
nivelAnillo(int posicion){
    return posicion%8
}
EsPasillo(int posicion)
    return posicion%2 == 0
#Devuelve una lista de posiciones de movimientos validas para una determinada posicion
int[] MovimientosValidos(int posiciones){

}
PrintEstado(){

}

"""