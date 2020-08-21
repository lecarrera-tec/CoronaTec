from typing import List

def derecha_igual(expresion : str, izq : str) -> str:
    """Extrae el expresion a la derecha de un igual.

    La expresión puede estar formada por varios iguales separados por 
    comas. Se busca el igual con el respectivo lado izquierdo.
    """
    # Separamos el expresion en cada una de las opciones.
    lista: List[str] = expresion.split(',')

    for elem in lista:
        # Buscamos el igual para separar el string.
        idx: int = elem.find('=')
        # No tiene igual; seguimos con el siguiente elemento.
        if idx == -1:
            continue
        # Extraemos el lado izquierdo.
        temp: str = elem[0:idx].strip()
        # Si el lado izquierdo no coincide, continuamos
        if temp != izq:
            continue
        # El lado izquierdo coincide. Devolvemos lo que hay al lado 
        # derecho del igual.
        temp = elem[idx+1:].strip()
        return temp
    # No se encontró nada.
    return ''
