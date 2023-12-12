import tkinter as tk
import numpy as np
import random
from tkinter import messagebox

# Constantes para el juego
FILAS, COLUMNAS = 6, 7
JUGADOR, IA = 1, 2
PROFUNDIDAD_ALFA_BETA = 5  # Puedes ajustar la profundidad según la dificultad deseada

# Funciones de utilidad para el juego
def crear_tablero():
    return np.zeros((FILAS, COLUMNAS))

def soltar_ficha(tablero, fila, columna, ficha):
    tablero[fila][columna] = ficha

def es_posicion_valida(tablero, columna):
    if 0 <= columna < COLUMNAS:
        return tablero[FILAS - 1][columna] == 0
    return False


def obtener_siguiente_fila_libre(tablero, columna):
    for r in range(FILAS):
        if tablero[r][columna] == 0:
            return r

def verificar_victoria(tablero, ficha):
    # Verificar horizontales
    for c in range(COLUMNAS - 3):
        for r in range(FILAS):
            if tablero[r][c] == ficha and tablero[r][c + 1] == ficha and tablero[r][c + 2] == ficha and tablero[r][c + 3] == ficha:
                return True

    # Verificar verticales
    for c in range(COLUMNAS):
        for r in range(FILAS - 3):
            if tablero[r][c] == ficha and tablero[r + 1][c] == ficha and tablero[r + 2][c] == ficha and tablero[r + 3][c] == ficha:
                return True

    # Verificar diagonales positivas
    for c in range(COLUMNAS - 3):
        for r in range(FILAS - 3):
            if tablero[r][c] == ficha and tablero[r + 1][c + 1] == ficha and tablero[r + 2][c + 2] == ficha and tablero[r + 3][c + 3] == ficha:
                return True

    # Verificar diagonales negativas
    for c in range(COLUMNAS - 3):
        for r in range(3, FILAS):
            if tablero[r][c] == ficha and tablero[r - 1][c + 1] == ficha and tablero[r - 2][c + 2] == ficha and tablero[r - 3][c + 3] == ficha:
                return True

    return False
def obtener_movimientos_validos(tablero):
    movimientos_validos = []
    for col in range(COLUMNAS):
        if es_posicion_valida(tablero, col):
            movimientos_validos.append(col)
    return movimientos_validos

# Función para evaluar el tablero
def evaluar_tablero(tablero, ficha):
    puntuacion = 0

    # Evaluar horizontales
    for r in range(FILAS):
        fila_array = [int(i) for i in list(tablero[r, :])]
        for c in range(COLUMNAS - 3):
            ventana = fila_array[c:c + 4]
            puntuacion += evaluar_ventana(ventana, ficha)

    # Evaluar verticales
    for c in range(COLUMNAS):
        col_array = [int(i) for i in list(tablero[:, c])]
        for r in range(FILAS - 3):
            ventana = col_array[r:r + 4]
            puntuacion += evaluar_ventana(ventana, ficha)

    # Evaluar diagonales positivas
    for r in range(FILAS - 3):
        for c in range(COLUMNAS - 3):
            ventana = [tablero[r + i][c + i] for i in range(4)]
            puntuacion += evaluar_ventana(ventana, ficha)

    # Evaluar diagonales negativas
    for r in range(FILAS - 3):
        for c in range(COLUMNAS - 3):
            ventana = [tablero[r + 3 - i][c + i] for i in range(4)]
            puntuacion += evaluar_ventana(ventana, ficha)

    return puntuacion

def evaluar_ventana(ventana, ficha):
    puntuacion = 0
    opuesto = JUGADOR if ficha == IA else IA

    if ventana.count(ficha) == 4:
        puntuacion += 100
    elif ventana.count(ficha) == 3 and ventana.count(0) == 1:
        puntuacion += 5
    elif ventana.count(ficha) == 2 and ventana.count(0) == 2:
        puntuacion += 2

    if ventana.count(opuesto) == 3 and ventana.count(0) == 1:
        puntuacion -= 4

    return puntuacion

# Algoritmo de Poda Alfa-Beta
def alfa_beta(tablero, profundidad, alfa, beta, maximizando):
    es_terminal = verificar_victoria(tablero, JUGADOR) or verificar_victoria(tablero, IA) or len(obtener_movimientos_validos(tablero)) == 0
    if profundidad == 0 or es_terminal:
        if es_terminal:
            if verificar_victoria(tablero, IA):
                return (None, 100000000000000)
            elif verificar_victoria(tablero, JUGADOR):
                return (None, -10000000000000)
            else: # Juego es un empate
                return (None, 0)
        else: # Profundidad es cero
            return (None, evaluar_tablero(tablero, IA))

    if maximizando:
        valor = float('-inf')
        columna = random.choice(obtener_movimientos_validos(tablero))
        for col in obtener_movimientos_validos(tablero):
            fila = obtener_siguiente_fila_libre(tablero, col)
            b_copy = tablero.copy()
            soltar_ficha(b_copy, fila, col, IA)
            nuevo_puntaje = alfa_beta(b_copy, profundidad - 1, alfa, beta, False)[1]
            if nuevo_puntaje > valor:
                valor = nuevo_puntaje
                columna = col
            alfa = max(alfa, valor)
            if alfa >= beta:
                break
        return columna, valor

    else: # Minimizando jugador
        valor = float('inf')
        columna = random.choice(obtener_movimientos_validos(tablero))
        for col in obtener_movimientos_validos(tablero):
            fila = obtener_siguiente_fila_libre(tablero, col)
            b_copy = tablero.copy()
            soltar_ficha(b_copy, fila, col, JUGADOR)
            nuevo_puntaje = alfa_beta(b_copy, profundidad - 1, alfa, beta, True)[1]
            if nuevo_puntaje < valor:
                valor = nuevo_puntaje
                columna = col
            beta = min(beta, valor)
            if alfa >= beta:
                break
        return columna, valor
    
class ConnectFourUI:
    def __init__(self, master):
        self.master = master
        master.title("Connect Four")

        # Crear un frame para la cuadrícula
        self.grid_frame = tk.Frame(master)
        self.grid_frame.grid(row=0, column=0)

        # Crear labels para la cuadrícula y configurar eventos de clic
        self.labels = [[None] * COLUMNAS for _ in range(FILAS)]
        for fila in range(FILAS):
            for columna in range(COLUMNAS):
                label = tk.Label(self.grid_frame, text="", bg="white", width=4, height=2, font=("Arial", 24))
                label.grid(row=fila, column=columna, padx=5, pady=5, sticky="nsew")
                label.bind("<Button-1>", lambda event, col=columna: self.hacer_movimiento(col))
                self.labels[fila][columna] = label  # Almacena el label en la matriz

        # Configurar pesos de las filas y columnas para que se ajusten al tamaño de la ventana
        for i in range(FILAS):
            self.grid_frame.grid_rowconfigure(i, weight=1)
        for i in range(COLUMNAS):
            self.grid_frame.grid_columnconfigure(i, weight=1)

        # Crear el botón "Reiniciar" con el nuevo comando
        self.boton_reiniciar = tk.Button(master, text="Reiniciar", command=self.reiniciar)
        self.boton_reiniciar.grid(row=FILAS, columnspan=COLUMNAS)

        # Inicializar el juego
        self.tablero = crear_tablero()
        self.turno_juego = JUGADOR


    def actualizar_interfaz(self):
    # Recorre el tablero y actualiza los labels en función de las fichas en el tablero
        for fila in range(FILAS):
            for columna in range(COLUMNAS):
                label = self.labels[fila][columna]
                ficha = self.tablero[fila][columna]
                if ficha == JUGADOR:
                    label.config(text="X", bg="red")  # Puedes personalizar el aspecto de la ficha del jugador
                elif ficha == IA:
                    label.config(text="O", bg="yellow")  # Puedes personalizar el aspecto de la ficha de la IA
                else:
                    label.config(text="", bg="light gray")  # Fondo gris claro para casilla vacía

        # Actualiza la ventana principal para reflejar los cambios en la interfaz
        self.master.update_idletasks()

    def reiniciar(self):
        # Reiniciar el tablero y el turno del jugador
        self.tablero = crear_tablero()
        self.turno_juego = JUGADOR

        # Limpiar la interfaz (borrar las fichas en la cuadrícula)
        for fila in range(FILAS):
            for columna in range(COLUMNAS):
                self.labels[fila][columna]["text"] = ""
                self.labels[fila][columna]["bg"] = "white"  # También puedes restablecer el fondo a blanco

    def hacer_movimiento(self, columna):
        if es_posicion_valida(self.tablero, columna):
            fila_libre = obtener_siguiente_fila_libre(self.tablero, columna)
            if fila_libre is not None:
                soltar_ficha(self.tablero, fila_libre, columna, self.turno_juego)
                self.actualizar_interfaz()
                if verificar_victoria(self.tablero, self.turno_juego):
                    self.fin_del_juego(f"Jugador {self.turno_juego} gana!")
                else:
                    self.cambiar_turno()
                    # Llama a la función para que la IA haga su movimiento
                    self.mover_IA()

    def mover_IA(self):
        # Obtener las columnas válidas donde la IA puede hacer un movimiento
        movimientos_validos = obtener_movimientos_validos(self.tablero)

        if movimientos_validos:
            # La IA selecciona una columna al azar de las columnas válidas
            columna_ia = random.choice(movimientos_validos)

            # Realizar el movimiento de la IA en la columna seleccionada
            fila_libre = obtener_siguiente_fila_libre(self.tablero, columna_ia)
            soltar_ficha(self.tablero, fila_libre, columna_ia, IA)
            self.actualizar_interfaz()

            # Verificar si la IA ganó
            if verificar_victoria(self.tablero, IA):
                self.fin_del_juego("La IA gana.")
            else:
                self.cambiar_turno()


    def cambiar_turno(self):
        if self.turno_juego == JUGADOR:
            self.turno_juego = IA
        else:
            self.turno_juego = JUGADOR

    def fin_del_juego(self, mensaje):
        for fila in range(FILAS):
            for columna in range(COLUMNAS):
                self.labels[fila][columna]["text"] = ""
        tk.messagebox.showinfo("Fin del Juego", mensaje)
        self.reiniciar()

# Iniciar la interfaz gráfica
root = tk.Tk()
gui = ConnectFourUI(root)
root.mainloop()