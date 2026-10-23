# juego_recoleccion.py
import tkinter as tk
import random
import time
import math


class JuegoRecoleccion(tk.Frame):
    def __init__(self, parent, controlador):
        super().__init__(parent)
        self.controlador = controlador
        self.canvas = tk.Canvas(self, bg="#F5F2EB")
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.start_time = 0
        self.posiciones_ramas = []

    def iniciar(self):
        self.canvas.delete("all")
        self.canvas.update()
        ancho = self.canvas.winfo_width()
        alto = self.canvas.winfo_height()

        if ancho <= 1 or alto <= 1:
            ancho, alto = 800, 600

        self.posiciones_ramas = []

        # 1. Generar 2 arbustos masivos que se expandan por toda la pantalla
        posiciones_base = [
            ancho * 0.3,
            ancho * 0.7,
        ]  # Distribuidos a la izquierda y derecha

        for x_base in posiciones_base:
            y_base = alto + 50
            angulo_base = -math.pi / 2 + random.uniform(-0.1, 0.1)

            self.dibujar_rama_fractal(
                x_base,
                y_base,
                angulo=angulo_base,
                longitud=alto * 0.28,  # Ramas iniciales muy largas
                profundidad=6,  # Mayor profundidad para más ramas
                grosor=14,  # Base gruesa
            )

        r = self.controlador.config.radio_pelota
        d = r * 2

        colores_disponibles = [
            ("red", "#fa5555"),
            ("blue", "#005dbb"),
            ("#4A148C", "#7B1FA2"),
            ("#E65100", "#FFB74D"),
            ("#1B5E20", "#4CAF50"),
        ]

        color_distractor, color_target = random.choice(colores_disponibles)

        # 2. Filtrado espacial para evitar superposición de los frutos
        posiciones_elegidas = []
        random.shuffle(self.posiciones_ramas)
        distancia_minima = d + 5  # Diámetro del fruto + 5px de separación obligatoria

        for pos in self.posiciones_ramas:
            # Evitar que se generen fuera de los límites visibles de la pantalla
            if pos[0] < d or pos[0] > ancho - d or pos[1] < d or pos[1] > alto - d:
                continue

            superpone = False
            for elegida in posiciones_elegidas:
                if (
                    math.hypot(pos[0] - elegida[0], pos[1] - elegida[1])
                    < distancia_minima
                ):
                    superpone = True
                    break

            if not superpone:
                posiciones_elegidas.append(pos)
                if len(posiciones_elegidas) >= 51:
                    break

        # Fallback de seguridad: Si la pantalla es muy pequeña o el radio muy grande,
        # forzar posiciones que no se superpongan demasiado
        intentos = 0
        while len(posiciones_elegidas) < 51 and intentos < 2000:
            nx = random.randint(d, ancho - d)
            ny = random.randint(d, alto - d)
            superpone = False
            for elegida in posiciones_elegidas:
                if math.hypot(nx - elegida[0], ny - elegida[1]) < distancia_minima:
                    superpone = True
                    break
            if not superpone:
                posiciones_elegidas.append((nx, ny))
            intentos += 1

        # Último recurso extremo si los parámetros del usuario son imposibles matemáticamente
        while len(posiciones_elegidas) < 51:
            posiciones_elegidas.append(
                (random.randint(d, ancho - d), random.randint(d, alto - d))
            )

        # 3. Distribuir los frutos incorrectos (distractores)
        for i in range(50):
            cx, cy = posiciones_elegidas[i]
            x = cx - r
            y = cy - r
            self.canvas.create_oval(
                x,
                y,
                x + d,
                y + d,
                fill=color_distractor,
                outline="#2E2E2E",
                width=2,
                tags="distractor",
            )

        # 4. Posicionar el fruto objetivo (Target)
        cx_obj, cy_obj = posiciones_elegidas[50]
        x_obj = cx_obj - r
        y_obj = cy_obj - r
        self.canvas.create_oval(
            x_obj,
            y_obj,
            x_obj + d,
            y_obj + d,
            fill=color_target,
            outline="#2E2E2E",
            width=2,
            tags="target",
        )

        self.canvas.tag_raise("distractor")
        self.canvas.tag_raise("target")

        self.canvas.tag_bind("target", "<Button-1>", self.acierto)
        self.canvas.tag_bind("distractor", "<Button-1>", self.fallo)
        self.canvas.bind("<Button-1>", self.clic_fondo)

        self.start_time = time.time()

    def dibujar_rama_fractal(self, x, y, angulo, longitud, profundidad, grosor):
        if profundidad == 0:
            return

        x_fin = x + longitud * math.cos(angulo)
        y_fin = y + longitud * math.sin(angulo)

        color_rama = random.choice(["#5D4037", "#4E342E", "#6D4C41", "#8D6E63"])
        self.canvas.create_line(
            x,
            y,
            x_fin,
            y_fin,
            fill=color_rama,
            width=grosor,
            tags="arbusto",
            capstyle=tk.ROUND,
        )

        # Extraemos múltiples puntos a lo largo de la rama para tener más opciones viables
        self.posiciones_ramas.append((x_fin, y_fin))
        self.posiciones_ramas.append((x + (x_fin - x) * 0.33, y + (y_fin - y) * 0.33))
        self.posiciones_ramas.append((x + (x_fin - x) * 0.66, y + (y_fin - y) * 0.66))

        # Ramificación: 2 a 3 ramas asegurando apertura expansiva
        num_sub_ramas = random.randint(2, 3)
        for _ in range(num_sub_ramas):
            # Ángulo muy ancho para cubrir toda la pantalla horizontalmente
            nuevo_angulo = angulo + random.uniform(-math.pi / 2.1, math.pi / 2.1)
            # Retención de longitud muy alta para llegar al techo
            nueva_longitud = longitud * random.uniform(0.65, 0.85)
            nuevo_grosor = max(1, grosor - 2)

            self.dibujar_rama_fractal(
                x_fin,
                y_fin,
                nuevo_angulo,
                nueva_longitud,
                profundidad - 1,
                nuevo_grosor,
            )

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
        if not items or "arbusto" in self.canvas.gettags(items[0]):
            self.fallo(event)
