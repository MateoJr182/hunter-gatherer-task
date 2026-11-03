# juego_caza.py
import tkinter as tk
import random
import time
import math


class JuegoCaza(tk.Frame):
    def __init__(self, parent, controlador):
        super().__init__(parent)
        self.controlador = controlador

        self.canvas = tk.Canvas(self, bg="#87CEEB", cursor="crosshair")
        self.canvas.pack(expand=True, fill=tk.BOTH)

        self.start_time = 0
        self.ultimo_frame = 0
        self.animacion_id = None
        self.presa_activa = False

        self.intento_finalizado = False
        self.lanza_lanzada = False
        self.objetivo_lanza = (0, 0)
        self.resultado_tiro = None
        self.latencia_tiro = 0

        self.canvas.bind("<Button-1>", self.registrar_disparo)
        self.canvas.bind("<Motion>", self.apuntar_lanza)

    def iniciar(self):
        self.canvas.delete("all")
        self.canvas.update()

        self.ancho = self.canvas.winfo_width()
        self.alto = self.canvas.winfo_height()

        if self.ancho <= 1 or self.alto <= 1:
            self.ancho, self.alto = 800, 600

        self.dibujar_escenario()

        self.origen_lanza = (self.ancho / 2, self.alto)
        self.lanza_lanzada = False
        self.intento_finalizado = False

        self.canvas.create_line(
            self.origen_lanza[0],
            self.origen_lanza[1],
            self.origen_lanza[0],
            self.origen_lanza[1] - 80,
            width=5,
            fill="#4E342E",
            arrow=tk.LAST,
            arrowshape=(16, 20, 6),
            tags="lanza",
        )

        self.presa_activa = True

        margen_x = int(self.ancho * 0.2)
        x_inicial = random.randint(margen_x, self.ancho - margen_x)
        y_inicial = self.alto - 40

        vel_base = self.controlador.config.velocidad_pelota
        self.vel_x_sec = (
            random.choice([-vel_base, -(vel_base - 1), vel_base - 1, vel_base]) * 60
        )
        self.vel_y_sec = -random.uniform(vel_base + 2, vel_base + 6) * 60

        self.dibujar_sprite_nativo(x_inicial, y_inicial)
        self.canvas.tag_lower("presa", "pasto")

        self.start_time = time.time()
        self.ultimo_frame = time.time()
        self.mover_presa()

    def dibujar_escenario(self):
        altura_pasto = 80

        self.canvas.create_rectangle(
            50,
            self.alto - altura_pasto - 100,
            70,
            self.alto,
            fill="#5D4037",
            outline="#4E342E",
        )
        self.canvas.create_polygon(
            10,
            self.alto - altura_pasto - 50,
            60,
            self.alto - altura_pasto - 150,
            110,
            self.alto - altura_pasto - 50,
            fill="#2E7D32",
            outline="#1B5E20",
        )

        self.canvas.create_rectangle(
            self.ancho - 80,
            self.alto - altura_pasto - 120,
            self.ancho - 60,
            self.alto,
            fill="#5D4037",
            outline="#4E342E",
        )
        self.canvas.create_polygon(
            self.ancho - 130,
            self.alto - altura_pasto - 70,
            self.ancho - 70,
            self.alto - altura_pasto - 180,
            self.ancho - 10,
            self.alto - altura_pasto - 70,
            fill="#2E7D32",
            outline="#1B5E20",
        )

        self.canvas.create_rectangle(
            0,
            self.alto - altura_pasto,
            self.ancho,
            self.alto + 10,
            fill="#4CAF50",
            outline="#388E3C",
            tags="pasto",
        )

    def dibujar_sprite_nativo(self, x, y):
        s = self.controlador.config.tamaño_ave / 20.0
        puntos = [
            x,
            y,
            x - 15 * s,
            y - 10 * s,
            x - 20 * s,
            y - 5 * s,
            x - 40 * s,
            y - 15 * s,
            x - 30 * s,
            y + 5 * s,
            x - 50 * s,
            y + 10 * s,
            x - 25 * s,
            y + 15 * s,
            x - 10 * s,
            y + 5 * s,
        ]
        self.canvas.create_polygon(puntos, fill="black", outline="black", tags="presa")

    def apuntar_lanza(self, evento):
        if self.lanza_lanzada or not self.presa_activa:
            return

        dx = evento.x - self.origen_lanza[0]
        dy = evento.y - self.origen_lanza[1]
        angulo = math.atan2(dy, dx)

        largo = 90
        x_fin = self.origen_lanza[0] + math.cos(angulo) * largo
        y_fin = self.origen_lanza[1] + math.sin(angulo) * largo

        self.canvas.coords(
            "lanza", self.origen_lanza[0], self.origen_lanza[1], x_fin, y_fin
        )

    def mover_presa(self):
        if not self.presa_activa or self.intento_finalizado:
            return

        ahora = time.time()
        dt = ahora - self.ultimo_frame
        self.ultimo_frame = ahora

        dt = min(dt, 0.05)

        dx = self.vel_x_sec * dt
        dy = self.vel_y_sec * dt

        self.canvas.move("presa", dx, dy)
        coords = self.canvas.bbox("presa")

        if coords[0] <= 0 and self.vel_x_sec < 0:
            self.vel_x_sec = abs(self.vel_x_sec)
        elif coords[2] >= self.ancho and self.vel_x_sec > 0:
            self.vel_x_sec = -abs(self.vel_x_sec)

        if coords[1] < 0:
            self.registrar_escape_limite()
        else:
            self.animacion_id = self.after(8, self.mover_presa)

    def registrar_disparo(self, evento):
        if not self.presa_activa or self.lanza_lanzada or self.intento_finalizado:
            return

        self.lanza_lanzada = True
        # Guardamos el momento exacto de reacción del participante
        self.latencia_tiro = (time.time() - self.start_time) * 1000

        coords = self.canvas.bbox("presa")
        fue_acierto = False
        if coords:
            x1, y1, x2, y2 = coords
            s = self.controlador.config.tamaño_ave / 20.0
            margen = 15 * s

            if (x1 - margen) <= evento.x <= (x2 + margen) and (
                y1 - margen
            ) <= evento.y <= (y2 + margen):
                fue_acierto = True

        if fue_acierto:
            self.resultado_tiro = "acierto"
            self.objetivo_lanza = (evento.x, evento.y)
            # Solo detenemos al ave si el tiro es un acierto
            self.presa_activa = False
            if self.animacion_id:
                self.after_cancel(self.animacion_id)
        else:
            self.resultado_tiro = "fallo"
            # Proyectamos la lanza hacia el infinito para que pase de largo
            dx = evento.x - self.origen_lanza[0]
            dy = evento.y - self.origen_lanza[1]
            angulo = math.atan2(dy, dx)
            distancia_lejana = max(self.ancho, self.alto) * 2
            self.objetivo_lanza = (
                self.origen_lanza[0] + math.cos(angulo) * distancia_lejana,
                self.origen_lanza[1] + math.sin(angulo) * distancia_lejana,
            )
            # Nota: No detenemos a la presa, seguirá moviéndose en su ciclo.

        self.animar_vuelo_lanza()

    def animar_vuelo_lanza(self):
        coords_lanza = self.canvas.coords("lanza")
        if not coords_lanza:
            return
        x_base, y_base, x_punta, y_punta = coords_lanza

        dx = self.objetivo_lanza[0] - x_punta
        dy = self.objetivo_lanza[1] - y_punta
        distancia = math.hypot(dx, dy)

        velocidad_lanza = 60

        # Si acertó y la lanza llegó al objetivo
        if self.resultado_tiro == "acierto" and distancia < velocidad_lanza:
            self.finalizar_acierto()

        # Si falló y la lanza salió completamente de la pantalla
        elif self.resultado_tiro == "fallo" and (
            x_punta < -50
            or x_punta > self.ancho + 50
            or y_punta < -50
            or y_punta > self.alto + 50
        ):
            self.canvas.delete("lanza")
            # El intento sigue activo hasta que el pájaro escape por el cielo

        else:
            angulo = math.atan2(dy, dx)
            move_x = math.cos(angulo) * velocidad_lanza
            move_y = math.sin(angulo) * velocidad_lanza
            self.canvas.move("lanza", move_x, move_y)
            self.after(16, self.animar_vuelo_lanza)

    def finalizar_acierto(self):
        if self.intento_finalizado:
            return
        self.intento_finalizado = True

        self.canvas.itemconfig("presa", fill="red")
        self.canvas.tag_raise("presa")
        self.update()
        time.sleep(0.1)
        self.canvas.delete("lanza")

        self.controlador.registrar_resultado(1, self.latencia_tiro)

    def registrar_escape_limite(self):
        if self.intento_finalizado:
            return
        self.intento_finalizado = True

        self.presa_activa = False
        if self.animacion_id:
            self.after_cancel(self.animacion_id)

        if self.lanza_lanzada:
            # El usuario disparó y falló. Registramos el tiempo que demoró en disparar.
            self.controlador.registrar_resultado(0, self.latencia_tiro)
        else:
            # El usuario nunca disparó (se le escapó directo). Penalización máxima.
            self.controlador.registrar_resultado(0, 3000.0)
