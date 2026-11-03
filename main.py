# main.py
import tkinter as tk
from config import Configuracion
from controlador import ExperimentController
from vistas_ui import PantallaBienvenida

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Caza vs Recolección")
    root.geometry("1000x700")
    
    # Inicializar estado global y controlador
    config_app = Configuracion()
    controlador = ExperimentController(root)
    
    # Mostrar la primera pantalla
    pantalla_inicio = PantallaBienvenida(root, controlador, config_app)
    pantalla_inicio.pack(expand=True, fill=tk.BOTH)
    
    root.mainloop()