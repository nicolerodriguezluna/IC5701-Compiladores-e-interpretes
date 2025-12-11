# Clases para el manejo de un árbol de sintáxis abstracta

from enum import Enum, auto

class TipoNodo(Enum):
    """
    Describe el tipo de nodo del árbol
    """
    PROGRAMA              = auto()
    ASIGNACIÓN            = auto()
    EXPRESIÓN_MATEMÁTICA  = auto()
    EXPRESIÓN             = auto()
    FUNCIÓN               = auto()
    INVOCACIÓN            = auto()
    PARÁMETROS_FUNCIÓN    = auto()
    PARÁMETROS_INVOCACIÓN = auto()
    INSTRUCCIÓN           = auto()
    REPETICIÓN            = auto()
    BIFURCACIÓN           = auto()
    DIAYSI                = auto()
    SINO                  = auto()
    OPERADOR_LÓGICO       = auto()
    CONDICIÓN             = auto()
    COMPARACIÓN           = auto()
    RETORNO               = auto()
    ERROR                 = auto()
    PRINCIPAL             = auto()
    BLOQUE_INSTRUCCIONES  = auto()
    OPERADOR              = auto()
    VALOR_VERDAD          = auto()
    COMPARADOR            = auto()
    TEXTO                 = auto()
    ENTERO                = auto()
    FLOTANTE              = auto()
    IDENTIFICADOR         = auto()
    SWITCH_CASE = auto()
    MOVIDA = auto()
    DELE_VUELTA = auto()
    TRY_CATCH = auto()

import copy

class NodoÁrbol:

    tipo      : TipoNodo
    contenido : str
    atributos : dict

    def __init__(self, tipo, linea = None, columna = None, contenido = None, nodos = [], atributos = {}):

        self.tipo      = tipo
        self.contenido = contenido
        self.nodos     = nodos
        self.atributos = copy.deepcopy(atributos)
        self.linea = linea
        self.columna = columna

    def visitar(self, visitador):
        return visitador.visitar(self)


    def __str__(self):

        # Coloca la información del nodo
        resultado = '{:30}\t'.format(self.tipo)
        
        if self.contenido is not None:
            resultado += '{:10}\t'.format(self.contenido)
        else:
            resultado += '{:10}\t'.format('')


        if self.atributos != {}:
            resultado += '{:38}'.format(str(self.atributos))
        else:
            resultado += '{:38}\t'.format('')

        if self.nodos != []:
            resultado += '<'

            # Imprime los tipos de los nodos del nivel siguiente
            for nodo in self.nodos[:-1]:
                if nodo is not None:
                    resultado += '{},'.format(nodo.tipo)

            resultado += '{}'.format(self.nodos[-1].tipo)
            resultado += '>'

        return resultado


class ÁrbolSintáxisAbstracta:

    raiz : NodoÁrbol

    def imprimir_preorden(self):
        self.__preorden(self.raiz)

    def __preorden(self, nodo):

        print(nodo)

        if nodo is not None:
            for nodo in nodo.nodos:
                self.__preorden(nodo)
