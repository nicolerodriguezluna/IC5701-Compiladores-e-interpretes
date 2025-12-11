# Explorador para el lenguaje Ciruelas (scanner)
from enum import Enum, auto
import sys

import re

class TipoComponente(Enum):
    """
    Enum con los tipos de componentes disponibles

    Esta clase tiene mayormente un propósito de validación
    """
    COMENTARIO = auto()
    PALABRA_CLAVE = auto()
    CONDICIONAL = auto()
    REPETICION = auto()
    ASIGNACION = auto()
    OPERADOR = auto()
    COMPARADOR = auto()
    TEXTO = auto()
    IDENTIFICADOR = auto()
    ENTERO = auto()
    FLOTANTE = auto()
    VALOR_VERDAD = auto()
    PUNTUACION = auto()
    BLANCOS = auto()
    NINGUNO = auto()
    SWITCHCASE = auto()
    CASE = auto()
    TRY = auto()
    CATCH = auto()
    INVOCACION = auto()
    FOR = auto()


class ComponenteLéxico:
    """
    Clase que almacena la información de un componente léxico

    Almacena información auxiliar para mostrar errores (lina y columna)
    """

    tipo    : TipoComponente
    texto   : str 
    linea   : int
    columna : int

    def __init__(self, tipo_nuevo: TipoComponente, texto_nuevo: str, linea: int, columna):
        self.tipo = tipo_nuevo
        self.texto = texto_nuevo
        self.linea = linea
        self.columna = columna

    def __str__(self):
        """
        Da una representación en texto de la instancia actual usando un
        string de formato de python (ver 'python string formatting' en
        google)
        """

        resultado = f'{self.tipo:30} <{self.texto}> Línea: {self.linea} Columna: {self.columna}'
        return resultado

class ErrorCompilacion:
    """
        Clase que almacena errores encontrados durante la compilación
    """
    def __init__(self, mensaje, texto, linea, columna):
        self.mensaje = mensaje
        self.texto = texto
        self.linea = linea
        self.columna = columna
    
    def __str__(self):
        return f"ERROR: {self.mensaje} en línea {self.linea}, columna {self.columna} - Texto: '{self.texto}'"

class Explorador:
    """
    Clase que lleva el proceso principal de exploración y deja listos los 
    los componentes léxicos usando para ello los descriptores de
    componente.

    Un descriptor de componente es una tupla con dos elementos:
        - El tipo de componente
        - Un string de regex que describe los textos que son generados para
          ese componente
    """

    descriptores_componentes = [ (TipoComponente.COMENTARIO, r'^Bomba:.*'),
            (TipoComponente.PALABRA_CLAVE, r'^(mae|sarpe|jefe|jefa|safis)'),
            (TipoComponente.SWITCHCASE, r'^(como está la vara)'),
            (TipoComponente.CASE, r'^(movida)'),
            (TipoComponente.TRY, r'^(juéguesela)'),
            (TipoComponente.CATCH, r'^(tortón)'),
            (TipoComponente.INVOCACION, r'^(llamese)'),
            (TipoComponente.FOR, r'^(dele vuelta)'),
            (TipoComponente.CONDICIONAL, r'^(diay siii|sino ni modo)'),
            (TipoComponente.REPETICION, r'^(upee)'),
            (TipoComponente.ASIGNACION, r'^(metale)'),
            (TipoComponente.OPERADOR, r'^(echele|quitele|chuncherequee|desmadeje|divorcio|casorio)'),
            (TipoComponente.COMPARADOR, r'^(cañazo|poquitico|misma vara|otra vara|menos o igualitico|más o igualitico)'),
            (TipoComponente.TEXTO, r'^(~.?[^~]*)~'),
            (TipoComponente.IDENTIFICADOR, r'^([a-záéíóúüñ_]([a-záéíóúüñA-ZÁÉÍÓÚÑ0-9_])*)'),
            (TipoComponente.FLOTANTE, r'^(-?[0-9]+\.[0-9]+)'), # Detectar los flotantes antes para que no se confundan con enteros
            (TipoComponente.ENTERO, r'^(-?[0-9]+)'),
            (TipoComponente.VALOR_VERDAD, r'^(True|False)'),
            (TipoComponente.PUNTUACION, r'^([/{}()])'),
            (TipoComponente.BLANCOS, r'^(\s+)')]

    def __init__(self, contenido_archivo):
        self.texto = contenido_archivo
        self.componentes = []

        # Lista de errores encontrados
        self.errores = []

        # Se asegura que regex funcione en modo unicode para soportar caracteres especiales
        re.UNICODE

    def explorar(self):
        """
        Itera sobre cada una de las líneas y las va procesando de forma que
        se generan los componentes lexicos necesarios en la etapa de
        análisis
        """
        indice_linea = 1

        for linea in self.texto:
            resultado = self.procesar_linea(linea, indice_linea)
            self.componentes = self.componentes + resultado
            indice_linea += 1

        # Si se encontró 1 o más errores se imprimen y se detiene el programa
        if len(self.errores) > 0:
            self.imprimir_errores()
            sys.exit()

    def imprimir_componentes(self):
        """
        Imprime en pantalla en formato amigable al usuario los componentes
        léxicos creados a partir del archivo de entrada
        """

        for componente in self.componentes:
            print(componente) # Esto funciona por que el print llama al
                              # método __str__ de la instancia 

    def imprimir_errores(self):
        """
        Imprime todos los errores encontrados por el explorador en una estructura legible para el programador
        """
        print("\n==== ERRORES ENCONTRADOS ====")
        for error in self.errores:
            print(error)
        print(f"Total de errores: {len(self.errores)}")

    def registrar_error(self, mensaje, texto, linea, columna):
        """
        Registra un error para ser mostrado al final de la exploración
        """
        error = ErrorCompilacion(mensaje, texto, linea, columna)
        self.errores.append(error)

    def procesar_linea(self, linea, indice_linea):
        """
        Toma cada línea y la procesa extrayendo los componentes léxicos.

        Acá se deberían generar los errores y almacenar la información
        adicional necesaria para tener errores inteligentes
        """

        componentes = []
        indice_columna = 1

        # Toma una línea y le va cortando pedazos hasta que se acaba
        while(linea !=  ""):

            # Bandera para saber si hubo match o no
            match_encontrado = False

            # Separa los descriptores de componente en dos variables
            for tipo_componente, regex in self.descriptores_componentes:


                # Trata de hacer match con el descriptor actual
                respuesta = re.match(regex, linea)

                # Si no es nulo significa que hubo coincidencia
                match_encontrado = respuesta is not None

                # Si hay coincidencia se procede a generar el componente
                # léxico final
                if match_encontrado:
                    texto_coindicencia = respuesta.group()
                    # Se actualiza el índice de la columna que corresponde al componente
                    indice_columna_componente = indice_columna
                    # Para los espacios en blanco, se cuentan los caracteres individualmente
                    if tipo_componente is TipoComponente.BLANCOS:
                        for caracter in texto_coindicencia:
                            # En el caso de los tabuladores se asume que equivalen a 4 espacios
                            if caracter == '\t':
                                indice_columna += 4
                            else:
                                indice_columna += 1
                    else:
                        indice_columna += len(texto_coindicencia)

                    # si la coincidencia corresponde a un BLANCO o un
                    # COMENTARIO se ignora por que no se ocupa
                    if tipo_componente is not TipoComponente.BLANCOS and \
                            tipo_componente is not TipoComponente.COMENTARIO:

                        #Crea el componente léxico y lo guarda
                        nuevo_componente = ComponenteLéxico(tipo_componente, respuesta.group(), indice_linea, indice_columna_componente) 
                        componentes.append(nuevo_componente)


                    # Se elimina el pedazo que hizo match
                    linea = linea[respuesta.end():]
                    break;
            
            # Si no hubo match con nada
            if not match_encontrado:
                caracter_desconocido = linea[0]
                self.registrar_error("Caracter desconocido", caracter_desconocido, indice_linea, indice_columna)

                # Se avanza un caracter para continuar la exploración
                linea = linea[1:]
                indice_columna += 1

        return componentes

