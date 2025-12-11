# Implementa el veficador de ciruelas

import sys
from typing import List, Dict

from utils.árbol import ÁrbolSintáxisAbstracta, NodoÁrbol, TipoNodo
from utils.tipo_datos import TipoDatos
from explorador.explorador import ErrorCompilacion

class TablaSímbolos:
    """ 
    Almacena información auxiliar para decorar el árbol de sintáxis
    abstracta con información de tipo y alcance.

    La estructura de símbolos es una lista de diccionarios 
    """

    profundidad : int  = 0
    símbolos : List[Dict] = []

    def abrir_bloque(self):
        """
        Inicia un bloque de alcance (scope)
        """
        self.profundidad += 1

    def cerrar_bloque(self):
        """
        Termina un bloque de alcance y al acerlo elimina todos los
        registros de la tabla que estan en ese bloque
        """

        for registro in self.símbolos:
            if registro['profundidad'] == self.profundidad:
                self.símbolos.remove(registro)

        self.profundidad -= 1

    def nuevo_registro(self, nodo, nombre_registro=''):
        """
        Introduce un nuevo registro a la tabla de símbolos
        """
        # El nombre del identificador + el nivel de profundidad 

        """
        Los atributos son: nombre, profundidad, referencia

        referencia es una referencia al nodo dentro del árbol
        (Técnicamente todo lo 'modificable (mutable)' en python es una
        referencia siempre y cuando use la POO... meh... más o menos.
        """

        diccionario = {}

        diccionario['nombre']      = nodo.contenido 
        diccionario['profundidad'] = self.profundidad
        diccionario['referencia']  = nodo

        self.símbolos.append(diccionario)

    def verificar_existencia(self, nombre):
        """
        Verficia si un identificador existe cómo variable/función global o local
        """
        for registro in self.símbolos:

            # si es local
            if registro['nombre'] == nombre and \
                    registro['profundidad'] <= self.profundidad:

                return registro

        return None

    def __str__(self):

        resultado = 'TABLA DE SÍMBOLOS\n\n'
        resultado += 'Profundidad: ' + str(self.profundidad) +'\n\n'
        for registro in self.símbolos:
            resultado += str(registro) + '\n'

        return resultado


class Visitante:

    tabla_símbolos: TablaSímbolos

    def __init__(self, nueva_tabla_símbolos, errores):
        self.tabla_símbolos = nueva_tabla_símbolos 
        self.errores = errores

    def visitar(self, nodo: NodoÁrbol):
        """
        Realiza el despacho dinámico para procesar un nodo del árbol.

        Parámetros:
            nodo (NodoÁrbol): El nodo AST que se va a visitar.

        Retorna:
            El resultado de invocar el método específico para el tipo de nodo.

        Imprime el error y detiene el programa: 
            Si no existe un método asociado al tipo de nodo.
        """
        # Construye nombre del método a partir del tipo de nodo
        method_name = f"_Visitante__visitar_{nodo.tipo.name.lower()}"
        method = getattr(self, method_name, None)
        if method is None:
            print(f"FATAL: no existe un método para visitar nodo de tipo {nodo.tipo} en línea {nodo.linea} columna {nodo.columna}")
            sys.exit(1)
        return method(nodo)

    def __visitar_programa(self, nodo_actual):
        """
        Programa ::= (Comentario | Asignación | Función)* Principal
        """
        for nodo in nodo_actual.nodos:
            # acá 'self' quiere decir que al método 'visitar' le paso el
            # objetto visitante que estoy usando (o sea, este mismo...
            # self)
            nodo.visitar(self)

    def __visitar_switch_case(self, nodo_actual: NodoÁrbol):
        """
        SwitchCase ::= como está la vara ( Identificador ) { Movida+ (sino ni modo Bloque)? }

        Nodo SWITCH_CASE:
        - nodo_actual.nodos[0]: expresión de control
        - nodo_actual.nodos[1:]: nodos MOVIDA o SINO (default)
        """
        tipo_control = nodo_actual.nodos[0].visitar(self)
        # Procesar cada caso
        for caso in nodo_actual.nodos[1:]:
            if caso.tipo is TipoNodo.MOVIDA:
                valor = caso.nodos[0].visitar(self)
                if valor != tipo_control:
                    self.errores.append(
                        ErrorCompilacion(
                            mensaje=f"Tipo de case {valor} != control {tipo_control}",
                            texto=str(caso.nodos[0].contenido),
                            linea=caso.nodos[0].linea,
                            columna=caso.nodos[0].columna
                        )
                    )
                for inst in caso.nodos[1].nodos:
                    inst.visitar(self)
            elif caso.tipo is TipoNodo.SINO:
                for inst in caso.nodos[0].nodos:
                    inst.visitar(self)
            else:
                print(f"FATAL: Nodo inesperado en switch-case: {caso.tipo} en línea {caso.linea} columna {caso.columna}")
                sys.exit(1)
        # El switch-case no produce un valor específico, asignamos CUALQUIERA
        nodo_actual.atributos['tipo'] = TipoDatos.CUALQUIERA
        return TipoDatos.CUALQUIERA

    def __visitar_movida(self, nodo_actual: NodoÁrbol):
        """
        Movida ::= movida ~ Valor ~ { Instrucción+ }

        Nodo MOVIDA (caso de switch):
        - nodo_actual.nodos[0]: valor del case
        - nodo_actual.nodos[1]: bloque de instrucciones
        """
        return nodo_actual.nodos[0].visitar(self)
    
    def __visitar_try_catch(self, nodo_actual: NodoÁrbol):
        """
        TryCatch ::= juéguesela { BloqueInstrucciones } tortón { BloqueInstrucciones }

        Nodo TRY_CATCH (juéguesela-tortón):
        - nodo_actual.nodos[0]: bloque try (BloqueInstrucciones)
        - nodo_actual.nodos[1]: bloque catch (BloqueInstrucciones)
        """
        # Visitar bloque try
        for inst in nodo_actual.nodos[0].nodos:
            inst.visitar(self)
        # Visitar bloque catch
        for inst in nodo_actual.nodos[1].nodos:
            inst.visitar(self)
        # Semánticamente, el try-catch como instrucción no devuelve un tipo concreto,
        # usamos CUALQUIERA para indicar que puede manejar múltiples tipos.
        nodo_actual.atributos['tipo'] = TipoDatos.CUALQUIERA
        return TipoDatos.CUALQUIERA
    
    def __visitar_dele_vuelta(self, nodo_actual: NodoÁrbol):
        """
        DeleVuelta ::= dele vuelta ( Inicialización / Condición / Incremento ) BloqueInstrucciones

        Nodo DELE_VUELTA (bucle for):
        nodos:
          [0] = inicialización (Asignación u otra instrucción que setea la variable)
          [1] = condición (Condición)
          [2] = incremento (Asignación o Expresión matemética)
          [3] = bloque de instrucciones (BloqueInstrucciones)
        """
        # Abrir nuevo scope para variables del for
        self.tabla_símbolos.abrir_bloque()
        # Visitar inicialización
        nodo_actual.nodos[0].visitar(self)
        # Evaluar condición
        nodo_actual.nodos[1].visitar(self)
        # Ejecutar cuerpo del bucle
        for inst in nodo_actual.nodos[3].nodos:
            inst.visitar(self)
        # Aplicar incremento
        nodo_actual.nodos[2].visitar(self)
        # Cerrar scope del for
        self.tabla_símbolos.cerrar_bloque()
        # El for no devuelve un valor concreto, usamos CUALQUIERA
        nodo_actual.atributos['tipo'] = TipoDatos.CUALQUIERA
        return TipoDatos.CUALQUIERA
    
    def __visitar_asignación(self, nodo_actual):
        """
        Asignación ::= Identificador metale (Identificador | Literal | ExpresiónMatemática | Invocación )
        """
        lado_izquierdo = nodo_actual.nodos[0]
        lado_derecho = nodo_actual.nodos[1]

        # Meto la información en la tabla de símbolos (IDENTIFICACIÓN)
        self.tabla_símbolos.nuevo_registro(lado_izquierdo)

        if lado_derecho.tipo is TipoNodo.IDENTIFICADOR:
            registro = self.tabla_símbolos.verificar_existencia(lado_derecho.contenido)
            if registro is None:
                self.errores.append(
                    ErrorCompilacion(
                        mensaje=f"Identificador no declarado '{lado_derecho.contenido}'",
                        texto=lado_derecho.contenido,
                        linea=lado_derecho.linea,
                        columna=lado_derecho.columna
                    )
                )

        lado_izquierdo.visitar(self)
        lado_derecho.visitar(self)

        # Si es una función verifico el tipo que retorna para incluirlo en
        # la asignación y si es un literal puedo anotar el tipo (TIPO) 

        tipo_lado_derecho = lado_derecho.atributos.get('tipo', TipoDatos.CUALQUIERA)
        nodo_actual.atributos['tipo'] = tipo_lado_derecho
        lado_izquierdo.atributos['tipo'] = tipo_lado_derecho


    def __visitar_expresión_matemática(self, nodo_actual):
        """
        ExpresiónMatemática ::= (Expresión) | Número | Identificador

        Ojo esto soportaría un texto
        """
        for nodo in nodo_actual.nodos:

            # Verifico que exista si es un identificador (IDENTIFICACIÓN)
            if nodo.tipo == TipoNodo.IDENTIFICADOR:
                registro = self.tabla_símbolos.verificar_existencia(nodo.contenido)
                if registro is None:
                    self.errores.append(
                        ErrorCompilacion(
                            mensaje=f"Identificador no declarado '{nodo.contenido}'",
                            texto=nodo.contenido,
                            linea=nodo.linea,
                            columna=nodo.columna
                        )
                    )

            nodo.visitar(self)

        # Anoto el tipo de datos 'NÚMERO' (TIPO)
        nodo_actual.atributos['tipo'] = TipoDatos.NÚMERO

    def __visitar_expresión(self, nodo_actual):
        """
        Expresión ::= ExpresiónMatemática Operador ExpresiónMatemática
        """
        for nodo in nodo_actual.nodos:
            nodo.visitar(self)

        # Anoto el tipo de datos 'NÚMERO' (TIPO)
        nodo_actual.atributos['tipo'] = TipoDatos.NÚMERO

    def __visitar_función(self, nodo_actual):
        """
        Función ::= (Comentario)? mae Identificador (ParámetrosFunción) BloqueInstrucciones
        """

        # Meto la función en la tabla de símbolos (IDENTIFICACIÓN)
        self.tabla_símbolos.nuevo_registro(nodo_actual)

        self.tabla_símbolos.abrir_bloque()

        for nodo in nodo_actual.nodos:
            nodo.visitar(self)

        self.tabla_símbolos.cerrar_bloque()

        # Anoto el tipo de retorno (TIPO)
        nodo_actual.atributos['tipo'] = nodo_actual.nodos[2].atributos['tipo']


    def __visitar_invocación(self, nodo_actual):
        """
        Invocación ::= Identificador ( ParámetrosInvocación )
        """

        # Verfica que el 'Identificador' exista (IDENTIFICACIÓN) y que sea
        registro = self.tabla_símbolos.verificar_existencia(nodo_actual.nodos[0].contenido)
        if registro is None:
            print(f"FATAL: Función {nodo_actual.nodos[0].contenido} no declarada en línea {nodo_actual.nodos[0].linea} columna {nodo_actual.nodos[0].columna}")
            sys.exit(1)

        if registro['referencia'].tipo != TipoNodo.FUNCIÓN:
            self.errores.append(
                ErrorCompilacion(
                    mensaje="Esa vara es una variable...",
                    texto=nodo_actual.nodos[0].contenido,
                    linea=nodo_actual.linea,
                    columna=nodo_actual.columna
                )
            )

        for nodo in nodo_actual.nodos:
            nodo.visitar(self)

        # El tipo resultado de la invocación es el tipo inferido de una
        # función previamente definida
        nodo_actual.atributos['tipo'] = registro['referencia'].atributos['tipo']


    def __visitar_parámetros_invocación(self, nodo_actual):
        """
        ParámetrosInvocación ::= Valor (/ Valor)+
        """

        # Recordemos que 'Valor' no existe en el árbol...

        # Si es 'Identificador' verifico que exista (IDENTIFICACIÓN)
        for nodo in nodo_actual.nodos:

            # Si existe y no es función ya viene con el tipo por que
            # fue producto de una asignación
            if nodo.tipo == TipoNodo.IDENTIFICADOR:
                registro = self.tabla_símbolos.verificar_existencia(nodo.contenido)
                if registro is None:
                    self.errores.append(
                        ErrorCompilacion(
                            mensaje=f"Identificador no declarado '{nodo.contenido}'",
                            texto=nodo.contenido,
                            linea=nodo.linea,
                            columna=nodo.columna
                        )
                    )

            elif nodo.tipo == TipoNodo.FUNCIÓN:
                self.errores.append(
                    ErrorCompilacion(
                        mensaje="Esa vara es una función...",
                        texto=nodo.contenido,
                        linea=nodo_actual.linea,
                        columna=nodo_actual.columna
                    )
                )

            # Si es número o texto nada más los visito
            nodo.visitar(self)

        # No hay tipos en los parámetros... se sabe en tiempo de ejecución


    def __visitar_parámetros_función(self, nodo_actual):
        """
        ParámetrosFunción ::= Identificador (/ Identificador)+
        """

        # Registro cada 'Identificador' en la tabla
        for nodo in nodo_actual.nodos:
                self.tabla_símbolos.nuevo_registro(nodo)
                nodo.visitar(self)


    def __visitar_instrucción(self, nodo_actual):
        """
        Instrucción ::= (Repetición | Bifurcación | (Asignación | Invocación) | Retorno | Error | Comentario )
        """
        # Por alguna razón no me volé este nivel.. así que lo visitamos... 
        # Esto es un desperdicio de memoria y de cpu

        # Visita la instrucción 

        # Lo pongo así por copy/paste... pero puede ser como el comentario
        # de más abajo.
        for nodo in nodo_actual.nodos:
            nodo.visitar(self)
            nodo_actual.atributos['tipo'] = nodo.atributos['tipo']

        # nodo_actual.nodos[0].visitar(self)

    def __visitar_repetición(self, nodo_actual):
        """
        Repetición ::= upee ( Condición ) BloqueInstrucciones
        """
        # Visita la condición


        # Visita el bloque de instrucciones

        # Lo pongo así por copy/paste... pero puede ser como el comentario
        # de más abajo.
        self.tabla_símbolos.abrir_bloque()

        for nodo in nodo_actual.nodos:
            nodo.visitar(self)

        # nodo_actual.nodos[0].visitar(self)

        self.tabla_símbolos.cerrar_bloque()

        # Anoto el tipo de retorno (TIPO)
        nodo_actual.atributos['tipo'] = nodo_actual.nodos[1].atributos['tipo']


    def __visitar_bifurcación(self, nodo_actual):
        """
        Bifurcación ::= DiaySi (Sino)?
        """

        # Visita los dos nodos en el siguiente nivel si los hay
        for nodo in nodo_actual.nodos:
            nodo.visitar(self)

        nodo_actual.atributos['tipo'] = TipoDatos.CUALQUIERA 

    def __visitar_diaysi(self, nodo_actual):
        """
        DiaySi ::= diay siii ( Condición ) BloqueInstrucciones
        """


        # Visita la condición


        # Visita el bloque de instrucciones

        # Lo pongo así por copy/paste... pero puede ser como el comentario
        # de más abajo.
        self.tabla_símbolos.abrir_bloque()

        for nodo in nodo_actual.nodos:
            nodo.visitar(self)

        # nodo_actual.nodos[0].visitar(self)

        self.tabla_símbolos.cerrar_bloque()

        # Anoto el tipo de retorno (TIPO)
        nodo_actual.atributos['tipo'] = nodo_actual.nodos[1].atributos['tipo']

    def __visitar_sino(self, nodo_actual):
        """
        Sino ::= sino ni modo BloqueInstrucciones
        """
        # Visita el bloque de instrucciones

        # Lo pongo así por copy/paste... pero puede ser como el comentario
        # de más abajo.
        self.tabla_símbolos.abrir_bloque()

        for nodo in nodo_actual.nodos:
            nodo.visitar(self)

        # nodo_actual.nodos[0].visitar(self)

        self.tabla_símbolos.cerrar_bloque()

        # Anoto el tipo de retorno (TIPO)
        nodo_actual.atributos['tipo'] = nodo_actual.nodos[0].atributos['tipo']

    def __visitar_condición(self, nodo_actual):
        """
        Condición ::= Comparación ((divorcio|casorio) Comparación)?
        """

        for nodo in nodo_actual.nodos:
            nodo.visitar(self)

        # Comparación retorna un valor de verdad (TIPO)
        nodo_actual.atributos['tipo'] = TipoDatos.VALOR_VERDAD


    def __visitar_comparación(self, nodo_actual):
        """
        Comparación ::= Valor Comparador Valor
        """

        # Si los 'Valor' son identificadores se asegura que existan (IDENTIFICACIÓN)
        for nodo in nodo_actual.nodos:
            if nodo.tipo == TipoNodo.IDENTIFICADOR:
                registro = self.tabla_símbolos.verificar_existencia(nodo.contenido)
                if registro is None:
                    self.errores.append(
                        ErrorCompilacion(
                            mensaje=f"Identificador no declarado '{nodo.contenido}'",
                            texto=nodo.contenido,
                            linea=nodo.linea,
                            columna=nodo.columna
                        )
                    )

            nodo.visitar(self)


        # Verifico que los tipos coincidan (TIPO)
        valor_izq      = nodo_actual.nodos[0]
        comparador  = nodo_actual.nodos[1]
        valor_der      = nodo_actual.nodos[2]

        tipo_izq = valor_izq.atributos['tipo']
        tipo_der = valor_der.atributos['tipo']
        # Ya se que eso se ve sueltelefeo... pero ya el cerebro se me apagó...

        if tipo_izq == tipo_der:
            comparador.atributos['tipo'] = tipo_izq

            # Una comparación siempre tiene un valor de verdad
            nodo_actual.atributos['tipo'] = TipoDatos.VALOR_VERDAD

        # Caso especial loco: Si alguno de los dos es un identificador de
        # un parámetro de función no puedo saber que tipo tiene o va a
        # tener por que este lenguaje no es tipado... tons vamos a poner
        # que la comparación puede ser cualquiera
        elif tipo_izq == TipoDatos.CUALQUIERA or \
                tipo_der == TipoDatos.CUALQUIERA:

            comparador.atributos['tipo'] = TipoDatos.CUALQUIERA

            # Todavía no estoy seguro.
            nodo_actual.atributos['tipo'] = TipoDatos.CUALQUIERA

        else:
            self.errores.append(
                ErrorCompilacion(        
                    mensaje=(
                        f"Tipo incompatible en comparación: "
                        f"'{valor_izq.contenido}' ({tipo_izq}) vs '{valor_der.contenido}' ({tipo_der})"
                    ),
                    texto=comparador.contenido,
                    linea=nodo_actual.linea,
                    columna=nodo_actual.columna
                )
            )
            # Para poder seguir, le damos un tipo neutro
            nodo_actual.atributos['tipo'] = TipoDatos.CUALQUIERA


    def __visitar_valor(self, nodo_actual):
        """
        Valor ::= (Identificador | Literal)
        """
        # En realidad núnca se va a visitar por que lo saqué del árbol
        # duránte la etapa de análisiss

    def __visitar_retorno(self, nodo_actual):
        """
        Retorno :: sarpe (Valor)?
        """

        for nodo in nodo_actual.nodos:
            nodo.visitar(self)
        
        if nodo_actual.nodos == []:
            # Si no retorna un valor no retorna un tipo específico 
            nodo_actual.atributos['tipo'] = TipoDatos.NINGUNO

        else:

            for nodo in nodo_actual.nodos:

                nodo.visitar(self)

                if nodo.tipo == TipoNodo.IDENTIFICADOR:
                    # Verifico si valor es un identificador que exista (IDENTIFICACIÓN)
                    registro = self.tabla_símbolos.verificar_existencia(nodo.contenido)
                    if registro is None:
                        self.errores.append(
                            ErrorCompilacion(
                                mensaje=f"Identificador no declarado '{nodo.contenido}'",
                                texto=nodo.contenido,
                                linea=nodo.linea,
                                columna=nodo.columna
                            )
                        )

                    # le doy al sarpe el tipo de retorno del identificador encontrado
                    nodo_actual.atributos['tipo'] = registro['referencia'].atributos['tipo']

                else:
                    # Verifico si es un Literal de que tipo es (TIPO)
                    nodo_actual.atributos['tipo'] = nodo.atributos['tipo']

    def __visitar_error(self, nodo_actual):
        """
        Error ::= safis Valor
        """
        # Verifico si 'Valor' es un identificador que exista (IDENTIFICACIÓN)
        for nodo in nodo_actual.nodos:
            if nodo.tipo == TipoNodo.IDENTIFICADOR:
                registro = self.tabla_símbolos.verificar_existencia(nodo.contenido)
                if registro is None:
                    self.errores.append(
                        ErrorCompilacion(
                            mensaje=f"Identificador no declarado '{nodo.contenido}'",
                            texto=nodo.contenido,
                            linea=nodo.linea,
                            columna=nodo.columna
                        )
                    )

        # Un safis imprime a stderr y sigue sin retornar nada
        nodo_actual.atributos['tipo'] = TipoDatos.NINGUNO 


    def __visitar_principal(self, nodo_actual):
        """
        Principal ::= (Comentario)?  (jefe | jefa) mae BloqueInstrucciones
        """
        # Este mae solo va a tener un bloque de instrucciones que tengo que
        # ir a visitar

        # Lo pongo así por copy/paste... pero puede ser como el comentario
        # de más abajo.
        for nodo in nodo_actual.nodos:
            nodo.visitar(self)

        # nodo_actual.nodos[0].visitar(self)

        # Anoto el tipo de retorno (TIPO)
        nodo_actual.atributos['tipo'] = nodo_actual.nodos[0].atributos['tipo']

    def __visitar_literal(self, nodo_actual):
        """
        Literal ::= (Número | Texto | ValorVerdad)
        """
        # En realidad núnca se va a visitar por que lo saqué del árbol
        # duránte la etapa de análisiss

    def __visitar_número(self, nodo_actual):
        """
        Número ::= (Entero | Flotante)
        """
        # En realidad núnca se va a visitar por que lo saqué del árbol
        # duránte la etapa de análisiss

    def __visitar_bloque_instrucciones(self, nodo_actual):
        """
        BloqueInstrucciones ::= { Instrucción+ }
        """
        # Visita todas las instrucciones que contiene
        for nodo in nodo_actual.nodos:
            nodo.visitar(self)

        # Acá yo debería agarrar el tipo de datos del Retorno si lo hay
        nodo_actual.atributos['tipo'] = TipoDatos.NINGUNO 

        for nodo in nodo_actual.nodos:
            if nodo.atributos['tipo'] != TipoDatos.NINGUNO:
                nodo_actual.atributos['tipo'] = nodo.atributos['tipo']

    def __visitar_operador(self, nodo_actual):
        """
        Operador ::= (hechele | quitele | chuncherequee | desmadeje)
        """
        # Operador para trabajar con números (TIPO)
        nodo_actual.atributos['tipo'] = TipoDatos.NÚMERO

    def __visitar_valor_verdad(self, nodo_actual):
        """
        ValorVerdad ::= (True | False)
        """
        # Valor de verdad (TIPO)
        nodo_actual.atributos['tipo'] = TipoDatos.VALOR_VERDAD

    def __visitar_comparador(self, nodo_actual):
        """
        Comparador ::= (cañazo | poquitico | misma vara | otra vara | menos o igualitico | más o igualitico)
        """
        # Estos comparadores son numéricos  (TIPO) 
        # (cañazo | poquitico | misma vara | otra vara | menos o igualitico | más o igualitico)
        if nodo_actual.contenido not in ['misma vara', 'otra vara' ]:
            nodo_actual.atributos['tipo'] = TipoDatos.NÚMERO

        else:
            nodo_actual.atributos['tipo'] = TipoDatos.CUALQUIERA
            # Si no es alguno de esos puede ser Numérico o texto y no lo puedo
            # inferir todavía


    def __visitar_texto(self, nodo_actual):
        """
        Texto ::= ~/\w(\s\w)*)?~
        """
        # Texto (TIPO)
        nodo_actual.atributos['tipo'] = TipoDatos.TEXTO

    def __visitar_entero(self, nodo_actual):
        """
        Entero ::= (-)?\d+
        """
        # Entero (TIPO) 
        nodo_actual.atributos['tipo'] = TipoDatos.NÚMERO

    def __visitar_flotante(self, nodo_actual):
        """
        Flotante ::= (-)?\d+.(-)?\d+
        """
        # Flotante (TIPO) 
        nodo_actual.atributos['tipo'] = TipoDatos.NÚMERO

    def __visitar_identificador(self, nodo_actual):
        """
        Identificador ::= [a-z][a-zA-Z0-9]+
        """
        nodo_actual.atributos['tipo'] = TipoDatos.CUALQUIERA
        # No hace nada


class Verificador:

    asa            : ÁrbolSintáxisAbstracta
    visitador      : Visitante
    tabla_símbolos : TablaSímbolos

    def __init__(self, nuevo_asa: ÁrbolSintáxisAbstracta):

        self.asa            = nuevo_asa

        self.tabla_símbolos = TablaSímbolos()
        self.errores: list[ErrorCompilacion] = []
        self.__cargar_ambiente_estándar()

        self.visitador      = Visitante(self.tabla_símbolos, self.errores)

    def imprimir_asa(self):
        """
        Imprime el árbol de sintáxis abstracta
        """
            
        if self.asa.raiz is None:
            print([])
        else:
            self.asa.imprimir_preorden()

    def __cargar_ambiente_estándar(self):

        funciones_estandar = [ 
                ('hacer_menjunje', TipoDatos.NINGUNO),
                ('viene_bolita', TipoDatos.TEXTO),
                ('trome', TipoDatos.NÚMERO),
                ('sueltele', TipoDatos.NINGUNO),
                ('echandi_jiménez', TipoDatos.TEXTO),
                ('grítele', TipoDatos.TEXTO), # recibe un texto y lo retorna en mayúsculas
                ('susúrrele', TipoDatos.TEXTO), # recibe un texto y lo retorna en minúsculas
                ('déjelo_parejo', TipoDatos.ENTERO) # recibe un número flotante, lo redondea y lo retorna como entero
            ]

        for nombre, tipo in  funciones_estandar:
            nodo = NodoÁrbol(TipoNodo.FUNCIÓN, contenido=nombre, atributos= {'tipo': tipo})
            self.tabla_símbolos.nuevo_registro(nodo)

    def verificar(self):
        self.visitador.visitar(self.asa.raiz)
        if self.errores:
            for err in self.errores:
                print(err)
            sys.exit(1)
