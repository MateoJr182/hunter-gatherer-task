# juego_caza.py
import tkinter as tk
import random
import time

class JuegoCaza(tk.Frame):
    def __init__(self, parent, controlador):
        super().__init__(parent)
        self.controlador = controlador
        self.canvas = tk.Canvas(self, bg=self.controlador.config.color_fondo)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.start_time = 0
        self.activo = False
        
        # Usar la velocidad definida en la configuración
        v = self.controlador.config.velocidad_pelota
        opciones_vel = [-v, v]
        
        self.vx = random.choice(opciones_vel)
        self.vy = random.choice(opciones_vel)

    def iniciar(self):
        self.canvas.delete("all")
        self.canvas.update()
        self.ancho = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 800
        self.alto = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 600
        
        self.r = self.controlador.config.radio_pelota
        
        # Selección de color aleatorio para este intento
        colores = ["blue", "#ff33cc", "#00ffcc", "#ff9900", "#9900ff", "#33cc33", "red"]
        color_pelota = random.choice(colores)
        
        self.target_id = self.canvas.create_oval(
            self.ancho/2 - self.r, self.alto/2 - self.r, 
            self.ancho/2 + self.r, self.alto/2 + self.r, 
            fill=color_pelota, outline=color_pelota
        )
        
        # Velocidad inicial aleatoria constante (más rápido y suave)
        opciones_vel = [-6, -5, 5, 6]
        self.vx = random.choice(opciones_vel)
        self.vy = random.choice(opciones_vel)
        
        self.canvas.tag_bind(self.target_id, "<Button-1>", self.acierto)
        self.canvas.bind("<Button-1>", self.fallo)
        
        self.activo = True
        self.start_time = time.time()
        self.mover_objetivo()

    def mover_objetivo(self):
        if not self.activo:
            return
            
        # Mover la pelota un poco cada frame
        self.canvas.move(self.target_id, self.vx, self.vy)
        coords = self.canvas.coords(self.target_id)
        
        if len(coords) == 4:
            # Rebotar en los bordes horizontales (estilo protector de pantalla)
            if coords[0] <= 0 or coords[2] >= self.ancho:
                self.vx *= -1
                
            # Rebotar en los bordes verticales
            if coords[1] <= 0 or coords[3] >= self.alto:
                self.vy *= -1
                
        # Llamar a esta función cada 16 ms (aprox 60 FPS) para fluidez
        self.after(16, self.mover_objetivo)

    def acierto(self, event):
        if self.activo:
            latencia = (time.time() - self.start_time) * 1000
            self.activo = False
            self.controlador.registrar_resultado(1, latencia)

    def fallo(self, event):
        items = self.canvas.find_withtag("current")
        if not items and self.activo:
            latencia = (time.time() - self.start_time) * 1000
            self.activo = False
            self.controlador.registrar_resultado(0, latencia)