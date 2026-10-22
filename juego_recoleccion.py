# juego_recoleccion.py
import tkinter as tk
import random
import time

class JuegoRecoleccion(tk.Frame):
    def __init__(self, parent, controlador):
        super().__init__(parent)
        self.controlador = controlador
        self.canvas = tk.Canvas(self, bg=self.controlador.config.color_fondo)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.start_time = 0

    def iniciar(self):
        self.canvas.delete("all")
        self.canvas.update()
        ancho = self.canvas.winfo_width()
        alto = self.canvas.winfo_height()
        
        if ancho <= 1 or alto <= 1:
            ancho, alto = 800, 600

        r = self.controlador.config.radio_pelota
        d = r * 2 # diámetro

        # Definir pares de colores: (Color Distractor, Color Objetivo)
        colores_disponibles = [
            ("red", "#fa5555"),       # Rojo / Rojo claro
            ("blue", "#005dbb"),      # Azul / Azul claro
            ("green", "#339e33"),     # Verde / Verde claro
            ("purple", "#9b52e4"),    # Morado / Morado claro
            ("#ff8c00", "#ffb366")    # Naranja / Naranja claro
        ]
        
        # Seleccionar una paleta al azar para este intento
        color_distractor, color_target = random.choice(colores_disponibles)

        # Crear distractores
        for _ in range(50):
            x = random.randint(d, ancho - d)
            y = random.randint(d, alto - d)
            self.canvas.create_oval(x, y, x+d, y+d, fill=color_distractor, outline=color_distractor, tags="distractor")
            
        # Crear objetivo
        x_obj = random.randint(d, ancho - d)
        y_obj = random.randint(d, alto - d)
        self.canvas.create_oval(x_obj, y_obj, x_obj+d, y_obj+d, fill=color_target, outline=color_target, tags="target")
        
        self.canvas.tag_bind("target", "<Button-1>", self.acierto)
        self.canvas.tag_bind("distractor", "<Button-1>", self.fallo)
        self.canvas.bind("<Button-1>", self.clic_fondo)
        
        self.start_time = time.time()

    def acierto(self, event):
        latencia = (time.time() - self.start_time) * 1000
        self.canvas.unbind("<Button-1>")
        self.controlador.registrar_resultado(1, latencia)

    def fallo(self, event):
        latencia = (time.time() - self.start_time) * 1000
        self.canvas.unbind("<Button-1>")
        self.controlador.registrar_resultado(0, latencia)
        
    def clic_fondo(self, event):
        items = self.canvas.find_withtag("current")
        if not items:
            self.fallo(event)