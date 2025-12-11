# Implementa el veficador de ciruelas

from utils.árbol import ÁrbolSintáxisAbstracta, NodoÁrbol, TipoNodo
from generador.visitadores import VisitantePython

import os

class Generador:

    asa            : ÁrbolSintáxisAbstracta
    visitador      : VisitantePython

    ambiente_estandar = """import sys

def hacer_menjunje(texto1, texto2):
    return texto1 + texto2

def viene_bolita(texto, indice):
    return texto[indice]

def trome(texto):
    return len(texto)

def sueltele(texto):
    print(texto)

def echandi_jiménez():
    return input()

def grítele(texto):
    return texto.upper()

def susúrrele(texto):
    return texto.lower()

def déjelo_parejo(flotante):
    return round(flotante)
"""

    def __init__(self, nuevo_asa: ÁrbolSintáxisAbstracta):

        self.asa            = nuevo_asa
        self.visitador      = VisitantePython() 

    def imprimir_asa(self):
        """
        Imprime el árbol de sintáxis abstracta
        """
            
        if self.asa.raiz is None:
            print([])
        else:
            self.asa.imprimir_preorden()

    def generar(self, nombre_archivo, directorio="transpilados"):
        """
        Genera el código Python y lo guarda en un archivo .py dentro de un directorio
        
        Args:
            nombre_archivo (str): Nombre del archivo a crear (por defecto: "programa_generado.py")
            directorio (str): Directorio donde crear el archivo (por defecto: "transpilados")
        """
        resultado = self.visitador.visitar(self.asa.raiz)
        codigo_completo = self.ambiente_estandar + "\n" + resultado
        
        try:
            # Crear el directorio si no existe
            if not os.path.exists(directorio):
                os.makedirs(directorio)
                print(f"Directorio '{directorio}' creado.")
            
            # Crear la ruta completa del archivo
            ruta_completa = os.path.join(directorio, nombre_archivo)
            
            # Crear el archivo Python
            with open(ruta_completa, 'w', encoding='utf-8') as archivo:
                archivo.write(codigo_completo)
            
            print(f"Archivo '{ruta_completa}' generado exitosamente.")
            
            # Hacer el archivo ejecutable en Linux
            os.chmod(ruta_completa, 0o755)
            
        except IOError as e:
            print(f"Error al crear el archivo: {e}")
        except Exception as e:
            print(f"Error inesperado: {e}")



