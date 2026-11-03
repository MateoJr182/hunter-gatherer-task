# vistas_ui.py
import time
import tkinter as tk

import tema
from tema import Boton, CampoTexto, Segmentado, tarjeta


class PantallaBienvenida(tk.Frame):
    def __init__(self, root, controlador, config_app):
        super().__init__(root, bg=tema.FONDO)
        self.controlador = controlador
        self.config_app = config_app
        self.genero_var = tk.StringVar(value="M")
        self.construir_ui()

    def construir_ui(self):
        # Contenedor central: queda centrado aunque se redimensione la ventana
        centro = tk.Frame(self, bg=tema.FONDO)
        centro.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            centro, text="Caza vs Recolección", font=tema.fuente(30, "bold"),
            bg=tema.FONDO, fg=tema.TEXTO,
        ).pack()
        tk.Label(
            centro, text="Experimento de cognición visoespacial",
            font=tema.fuente(13), bg=tema.FONDO, fg=tema.TEXTO_SUAVE,
        ).pack(pady=(4, 26))

        card = tarjeta(centro)
        card.pack(ipadx=40, ipady=24)

        tk.Label(
            card, text="ID del participante", font=tema.fuente(11),
            bg=tema.TARJETA, fg=tema.TEXTO_SUAVE,
        ).pack(pady=(14, 2))
        self.campo_nombre = CampoTexto(card)
        self.campo_nombre.pack(pady=(0, 18))
        self.campo_nombre.entry.bind("<Return>", lambda e: self.iniciar())
        self.campo_nombre.focus()

        tk.Label(
            card, text="Género", font=tema.fuente(11),
            bg=tema.TARJETA, fg=tema.TEXTO_SUAVE,
        ).pack(pady=(0, 6))
        Segmentado(
            card, self.genero_var, [("Femenino", "F"), ("Masculino", "M")]
        ).pack(pady=(0, 22))

        Boton(card, "Iniciar experimento", self.iniciar).pack(pady=(0, 6))

        enlace = tk.Label(
            centro, text="Configuraciones", font=tema.fuente(10),
            bg=tema.FONDO, fg=tema.TEXTO_SUAVE, cursor="hand2",
        )
        enlace.pack(pady=(18, 0))
        enlace.bind("<Button-1>", lambda e: self.abrir_configuraciones())
        enlace.bind("<Enter>", lambda e: enlace.config(fg=tema.TEXTO))
        enlace.bind("<Leave>", lambda e: enlace.config(fg=tema.TEXTO_SUAVE))

    def iniciar(self):
        nombre = self.campo_nombre.get().strip()
        genero = self.genero_var.get()
        if not nombre:
            self.campo_nombre.marcar_error()
            return
        self.pack_forget()
        self.controlador.iniciar_participante(nombre, genero, self.config_app)

    def abrir_configuraciones(self):
        VentanaConfiguracion(self, self.config_app)


class VentanaConfiguracion(tk.Toplevel):
    # (etiqueta, atributo de Configuracion, mínimo, máximo, divisor ms -> s)
    CAMPOS = [
        ("Intentos por bloque", "intentos_por_bloque", 2, 100, None),
        ("Pausa corta (segundos)", "pausa_corta_ms", 1, 300, 1000),
        ("Pausa larga (segundos)", "pausa_larga_ms", 1, 600, 1000),
        ("Tamaño frutos · Recolección", "radio_pelota", 5, 100, None),
        ("Tamaño objetivo · Caza", "tamaño_ave", 5, 100, None),
        ("Velocidad · Caza", "velocidad_pelota", 1, 30, None),
    ]

    def __init__(self, parent, config_app):
        super().__init__(parent, bg=tema.FONDO)
        self.title("Configuraciones")
        self.resizable(False, False)
        self.config_app = config_app
        self.spins = {}

        tk.Label(
            self, text="Configuraciones", font=tema.fuente(18, "bold"),
            bg=tema.FONDO, fg=tema.TEXTO,
        ).pack(pady=(20, 12))

        card = tarjeta(self)
        card.pack(padx=28, fill=tk.X)
        card.columnconfigure(0, weight=1)

        for fila, (etiqueta, attr, minimo, maximo, factor) in enumerate(self.CAMPOS):
            tk.Label(
                card, text=etiqueta, font=tema.fuente(11), bg=tema.TARJETA,
                fg=tema.TEXTO, anchor="w",
            ).grid(row=fila, column=0, sticky="w", padx=(18, 10), pady=7)
            spin = tk.Spinbox(
                card, from_=minimo, to=maximo, width=6, font=tema.fuente(11),
                justify="center", relief=tk.FLAT, bg=tema.GRIS, buttonbackground=tema.GRIS,
            )
            spin.delete(0, tk.END)
            spin.insert(0, self._valor_visible(attr, factor))
            spin.grid(row=fila, column=1, padx=(0, 18), pady=7)
            self.spins[attr] = (spin, minimo, maximo, factor)

        Boton(self, "Guardar", self.guardar, tam=12, padx=28, pady=9).pack(pady=18)

        # Ventana modal centrada sobre la principal
        self.update_idletasks()
        raiz = parent.winfo_toplevel()
        x = raiz.winfo_x() + (raiz.winfo_width() - self.winfo_width()) // 2
        y = raiz.winfo_y() + (raiz.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(0, x)}+{max(0, y)}")
        self.transient(raiz)
        self.grab_set()

    def _valor_visible(self, attr, factor):
        valor = getattr(self.config_app, attr)
        return int(valor / factor) if factor else valor

    def guardar(self):
        for attr, (spin, minimo, maximo, factor) in self.spins.items():
            try:
                valor = int(spin.get())
            except ValueError:
                valor = self._valor_visible(attr, factor)  # entrada inválida: conserva el actual
            valor = max(minimo, min(maximo, valor))  # mantiene el valor dentro de rango
            setattr(self.config_app, attr, valor * factor if factor else valor)
        self.destroy()


class PantallaDescanso(tk.Frame):
    ANCHO_BARRA = 380

    def __init__(self, parent, milisegundos, callback_fin_pausa):
        super().__init__(parent, bg=tema.FONDO)
        self.callback = callback_fin_pausa
        self.segundos_restantes = milisegundos // 1000
        self.duracion_ms = max(1, milisegundos)

        centro = tk.Frame(self, bg=tema.FONDO)
        centro.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            centro, text="Tiempo de descanso", font=tema.fuente(26, "bold"),
            bg=tema.FONDO, fg=tema.TEXTO,
        ).pack()
        tk.Label(
            centro, text="Relájate y descansa la vista unos instantes",
            font=tema.fuente(13), bg=tema.FONDO, fg=tema.TEXTO_SUAVE,
        ).pack(pady=(4, 30))

        self.label_tiempo = tk.Label(
            centro, text=f"{self.segundos_restantes}", font=tema.fuente(64, "bold"),
            bg=tema.FONDO, fg=tema.VERDE,
        )
        self.label_tiempo.pack()
        self.label_unidad = tk.Label(
            centro, text="segundos", font=tema.fuente(12),
            bg=tema.FONDO, fg=tema.TEXTO_SUAVE,
        )
        self.label_unidad.pack()

        # Barra de progreso dibujada a mano (se llena de forma continua)
        self.barra = tk.Canvas(
            centro, width=self.ANCHO_BARRA, height=10, bg=tema.FONDO, highlightthickness=0
        )
        self.barra.pack(pady=26)
        self.barra.create_rectangle(0, 0, self.ANCHO_BARRA, 10, fill=tema.GRIS, outline="")
        self.relleno = self.barra.create_rectangle(0, 0, 0, 10, fill=tema.VERDE, outline="")

        self.boton_continuar = Boton(centro, "Continuar", self.finalizar_pausa, estilo="azul")

        self.t_inicio = time.time()
        self.animar_barra()
        self.actualizar_reloj()

    def animar_barra(self):
        if not self.winfo_exists():
            return
        frac = min(1.0, (time.time() - self.t_inicio) * 1000 / self.duracion_ms)
        self.barra.coords(self.relleno, 0, 0, self.ANCHO_BARRA * frac, 10)
        if frac < 1.0:
            self.after(33, self.animar_barra)

    def actualizar_reloj(self):
        if not self.winfo_exists():
            return
        if self.segundos_restantes > 0:
            self.label_tiempo.config(text=f"{self.segundos_restantes}")
            self.segundos_restantes -= 1
            self.after(1000, self.actualizar_reloj)
        else:
            self.label_tiempo.config(text="¡Listo!", font=tema.fuente(48, "bold"))
            self.label_unidad.config(text="")
            self.boton_continuar.pack(pady=(4, 0))

    def finalizar_pausa(self):
        self.pack_forget()
        self.callback()


class PantallaFin(tk.Frame):
    NOMBRES = {"recoleccion": "Recolección", "caza": "Caza"}

    def __init__(self, parent, callback_reinicio, resumen):
        super().__init__(parent, bg=tema.FONDO)

        centro = tk.Frame(self, bg=tema.FONDO)
        centro.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            centro, text="¡Experimento finalizado!", font=tema.fuente(28, "bold"),
            bg=tema.FONDO, fg=tema.TEXTO,
        ).pack()
        tk.Label(
            centro, text="Los datos fueron guardados en formato CSV. ¡Gracias por participar!",
            font=tema.fuente(12), bg=tema.FONDO, fg=tema.TEXTO_SUAVE,
        ).pack(pady=(4, 28))

        fila = tk.Frame(centro, bg=tema.FONDO)
        fila.pack()
        for modo, stats in resumen.items():
            card = tarjeta(fila)
            card.pack(side=tk.LEFT, padx=12, ipadx=34, ipady=16)
            tk.Label(
                card, text=self.NOMBRES.get(modo, modo.capitalize()),
                font=tema.fuente(14, "bold"), bg=tema.TARJETA, fg=tema.TEXTO,
            ).pack(pady=(10, 8))
            tk.Label(
                card, text=f"{stats['acc']:.0f}%", font=tema.fuente(40, "bold"),
                bg=tema.TARJETA, fg=tema.VERDE,
            ).pack()
            tk.Label(
                card, text="aciertos", font=tema.fuente(11),
                bg=tema.TARJETA, fg=tema.TEXTO_SUAVE,
            ).pack()
            tk.Frame(card, height=1, bg=tema.BORDE).pack(fill=tk.X, padx=14, pady=12)
            tk.Label(
                card, text=f"{stats['avg_time']:.0f} ms", font=tema.fuente(22, "bold"),
                bg=tema.TARJETA, fg=tema.AZUL,
            ).pack()
            tk.Label(
                card, text="tiempo medio", font=tema.fuente(11),
                bg=tema.TARJETA, fg=tema.TEXTO_SUAVE,
            ).pack(pady=(0, 6))

        Boton(centro, "Volver al menú principal", callback_reinicio, estilo="azul").pack(pady=34)
