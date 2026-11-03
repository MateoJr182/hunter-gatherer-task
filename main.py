# main.py
import tkinter as tk

import tema
from config import Configuracion
from controlador import ExperimentController
from vistas_ui import PantallaBienvenida

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Caza vs Recolección")
    root.configure(bg=tema.FONDO)
    # Mismo tamaño que antes (1000x700): el área de juego condiciona el estímulo.
    tema.centrar_ventana(root, 1000, 700)

    # Inicializar estado global y controlador
    config_app = Configuracion()
    controlador = ExperimentController(root)

    # Mostrar la primera pantalla
    pantalla_inicio = PantallaBienvenida(root, controlador, config_app)
    pantalla_inicio.pack(expand=True, fill=tk.BOTH)

    root.mainloop()
