"""
vectores.py

Implementación de las propiedades algebraicas de vectores en R^n.
Las operaciones se realizan en Python puro sin librerías externas.
Un vector se representa como una lista de floats (asumiendo formato de columna).
"""

def sumar_vectores(v1, v2):
    """Suma dos vectores de la misma dimensión en R^n."""
    if len(v1) != len(v2):
        raise ValueError("Los vectores deben tener la misma dimensión para sumarse.")
    return [a + b for a, b in zip(v1, v2)]

def multiplicar_escalar(c, v):
    """Multiplica un vector v por un escalar c."""
    return [c * a for a in v]

def combinacion_lineal(vectores, escalares):
    """
    Calcula la combinación lineal de una lista de vectores y sus pesos (escalares).
    v_resultante = c1*v1 + c2*v2 + ... + cp*vp
    """
    if len(vectores) != len(escalares):
        raise ValueError("Debe haber exactamente un escalar (peso) por cada vector.")
    if not vectores:
        raise ValueError("La lista de vectores no puede estar vacía.")

    n = len(vectores[0])
    for v in vectores:
        if len(v) != n:
            raise ValueError("Todos los vectores deben pertenecer al mismo R^n (misma dimensión).")

    # Iniciar el vector resultante con ceros
    resultado = [0.0] * n

    # Sumar el aporte de cada vector multiplicado por su escalar
    for escalar, vector in zip(escalares, vectores):
        vector_escalado = multiplicar_escalar(escalar, vector)
        resultado = sumar_vectores(resultado, vector_escalado)

    return resultado