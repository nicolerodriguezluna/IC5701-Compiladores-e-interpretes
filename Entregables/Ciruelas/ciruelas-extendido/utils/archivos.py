# Utilitarios para manejar archivos

def cargar_archivo(ruta_archivo):
    """
    Carga un archivo y lo retorna cómo un solo string pero línea por línea
    en caso de que el archivo 
    """

    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
        for linea in archivo:
            yield linea.strip("\n")

   
