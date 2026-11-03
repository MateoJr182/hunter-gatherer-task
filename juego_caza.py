# juego_caza.py
import math
import random
import time
import tkinter as tk


def _mezclar(c1, c2, t):
    """Interpola linealmente entre dos colores hex (t en [0, 1])."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


class JuegoCaza(tk.Frame):
    VELOCIDAD_LANZA = 3750  # px/s (equivale a los 60 px por frame de ~16 ms originales)
    DURACION_IMPACTO_MS = 120  # pausa visual tras un acierto (antes: time.sleep(0.1))

    def __init__(self, parent, controlador):
        super().__init__(parent)
        self.controlador = controlador

        self.canvas = tk.Canvas(self, bg="#87CEEB", cursor="crosshair", highlightthickness=0)
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
        self.ultimo_vuelo = 0

        self.canvas.bind("<Button-1>", self.registrar_disparo)
        self.canvas.bind("<Motion>", self.apuntar_lanza)

    # ------------------------------------------------------------------ setup
    def iniciar(self):
        self.canvas.delete("all")
        self.canvas.update_idletasks()

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
            capstyle=tk.ROUND,
            tags="lanza",
        )

        self.presa_activa = True

        # IMPORTANTE: el orden y la cantidad de llamadas al RNG global se mantienen
        # idénticos a la versión original para no alterar las secuencias por semilla.
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

    # --------------------------------------------------------------- escenario
    def dibujar_escenario(self):
        """Escenario estático. Usa un RNG propio (fijo) para que la decoración
        no consuma números del RNG global que determina los ensayos."""
        rng = random.Random(2024)
        c = self.canvas
        w, h = self.ancho, self.alto
        altura_pasto = 80
        y_pasto = h - altura_pasto

        # Cielo: degradado vertical en franjas
        franjas = 36
        for i in range(franjas):
            color = _mezclar("#6DB6E8", "#D6EEF8", i / (franjas - 1))
            c.create_rectangle(
                0, i * y_pasto / franjas, w, (i + 1) * y_pasto / franjas + 1,
                fill=color, outline="",
            )
        c.create_rectangle(0, y_pasto, w, h, fill="#D6EEF8", outline="")

        # Sol con halo
        sx, sy = w * 0.84, h * 0.17
        for radio, color in ((70, "#DDF1FA"), (52, "#EAF6FB"), (36, "#FFF3C4")):
            c.create_oval(sx - radio, sy - radio, sx + radio, sy + radio, fill=color, outline="")
        c.create_oval(sx - 26, sy - 26, sx + 26, sy + 26, fill="#FFE27A", outline="")

        # Colinas lejanas
        for amp, fase, color in (
            (38, 0.0, "#A9D8A4"),
            (30, 1.7, "#8FCB86"),
        ):
            pts = [0, h]
            pasos = 14
            for k in range(pasos + 1):
                x = w * k / pasos
                y = y_pasto - amp * (0.5 + 0.5 * math.sin(k * 0.7 + fase)) - 18
                pts += [x, y]
            pts += [w, h]
            c.create_polygon(pts, fill=color, outline="", smooth=True)

        # Árboles (mismas posiciones aproximadas que antes)
        self._arbol(60, y_pasto, 100, rng)
        self._arbol(w - 70, y_pasto, 120, rng)

        # Pasto: base + franjas más oscuras hacia abajo + briznas
        c.create_rectangle(0, y_pasto, w, h + 10, fill="#58B85C", outline="", tags="pasto")
        for i in range(8):
            y0 = y_pasto + altura_pasto * i / 8
            c.create_rectangle(
                0, y0, w, y0 + altura_pasto / 8 + 1,
                fill=_mezclar("#5CBF60", "#3F9446", i / 7), outline="", tags="pasto",
            )
        for _ in range(int(w / 5)):
            x = rng.uniform(0, w)
            y = y_pasto + rng.uniform(-2, altura_pasto)
            largo = rng.uniform(7, 15)
            inclin = rng.uniform(-4, 4)
            c.create_line(
                x, y, x + inclin, y - largo,
                fill=rng.choice(["#4CAF50", "#3F9446", "#6BC96F", "#357F3B"]),
                width=2, capstyle=tk.ROUND, tags="pasto",
            )

    def _arbol(self, x, y_suelo, alto_tronco, rng):
        c = self.canvas
        # Sombra
        c.create_oval(x - 55, y_suelo - 6, x + 55, y_suelo + 12, fill="#6FB46A", outline="")
        # Tronco cónico
        c.create_polygon(
            x - 12, y_suelo, x + 12, y_suelo,
            x + 7, y_suelo - alto_tronco, x - 7, y_suelo - alto_tronco,
            fill="#6D4C41", outline="#4E342E",
        )
        # Copa en capas (circulos solapados, de oscuro a claro)
        cy = y_suelo - alto_tronco - 22
        for dx, dy, r, col in (
            (-26, 16, 40, "#2E7D32"), (26, 16, 40, "#2E7D32"), (0, 0, 48, "#388E3C"),
            (-14, -14, 32, "#43A047"), (14, -18, 28, "#4CAF50"),
        ):
            c.create_oval(x + dx - r, cy + dy - r, x + dx + r, cy + dy + r, fill=col, outline="")

    def dibujar_sprite_nativo(self, x, y):
        # Silueta idéntica a la original: es el estímulo experimental y no debe cambiar.
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

    # ------------------------------------------------------------------ lanza
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

    # ------------------------------------------------------------------- presa
    def mover_presa(self):
        if not self.winfo_exists() or not self.presa_activa or self.intento_finalizado:
            return

        ahora = time.time()
        dt = ahora - self.ultimo_frame
        self.ultimo_frame = ahora

        dt = min(dt, 0.05)

        dx = self.vel_x_sec * dt
        dy = self.vel_y_sec * dt

        self.canvas.move("presa", dx, dy)
        coords = self.canvas.bbox("presa")
        if not coords:
            return

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

        self.ultimo_vuelo = time.time()
        self.animar_vuelo_lanza()

    def animar_vuelo_lanza(self):
        if not self.winfo_exists():
            return
        coords_lanza = self.canvas.coords("lanza")
        if not coords_lanza:
            return
        x_base, y_base, x_punta, y_punta = coords_lanza

        # Paso dependiente del tiempo real: la lanza vuela igual de rápido en cualquier equipo
        ahora = time.time()
        dt = min(ahora - self.ultimo_vuelo, 0.05)
        self.ultimo_vuelo = ahora
        paso = self.VELOCIDAD_LANZA * dt

        dx = self.objetivo_lanza[0] - x_punta
        dy = self.objetivo_lanza[1] - y_punta
        distancia = math.hypot(dx, dy)

        # Si acertó y la lanza llegó al objetivo
        if self.resultado_tiro == "acierto" and distancia <= max(paso, 1):
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
            self.canvas.move("lanza", math.cos(angulo) * paso, math.sin(angulo) * paso)
            self.after(10, self.animar_vuelo_lanza)

    # ---------------------------------------------------------------- impacto
    def finalizar_acierto(self):
        if self.intento_finalizado:
            return
        self.intento_finalizado = True

        self.canvas.itemconfig("presa", fill="#E53935", outline="#E53935")
        self.canvas.tag_raise("presa")

        # Destello de impacto: anillo que se expande + chispas. No bloquea la interfaz.
        x, y = self.objetivo_lanza
        self._t_impacto = time.time()
        self._impacto = (x, y)
        self.canvas.create_oval(x, y, x, y, outline="#FFFFFF", width=3, tags="impacto_anillo")
        self.animar_impacto()

    def animar_impacto(self):
        if not self.winfo_exists():
            return
        frac = (time.time() - self._t_impacto) * 1000 / self.DURACION_IMPACTO_MS
        x, y = self._impacto
        if frac < 1.0:
            r = 6 + 34 * frac
            self.canvas.coords("impacto_anillo", x - r, y - r, x + r, y + r)
            self.canvas.itemconfig("impacto_anillo", width=max(1, round(4 * (1 - frac))))
            self.after(10, self.animar_impacto)
        else:
            self.canvas.delete("lanza")
            self.canvas.delete("impacto_anillo")
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
