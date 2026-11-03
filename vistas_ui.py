# vistas_ui.py
import tkinter as tk
from config import Configuracion


class PantallaBienvenida(tk.Frame):
    def __init__(self, root, controlador, config_app):
        super().__init__(root)
        self.controlador = controlador
        self.config_app = config_app
        self.genero_var = tk.StringVar(value="M")
        self.construir_ui()

    def construir_ui(self):
        tk.Label(
            self, text="Experimento: Caza vs Recolección", font=("Arial", 20, "bold")
        ).pack(pady=40)

        tk.Label(self, text="Nombre o ID del Participante:", font=("Arial", 12)).pack()
        self.entry_nombre = tk.Entry(self, font=("Arial", 12))
        self.entry_nombre.pack(pady=10)

        frame_genero = tk.Frame(self)
        frame_genero.pack(pady=10)
        tk.Radiobutton(
            frame_genero,
            text="Femenino",
            variable=self.genero_var,
            value="F",
            font=("Arial", 12),
        ).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(
            frame_genero,
            text="Masculino",
            variable=self.genero_var,
            value="M",
            font=("Arial", 12),
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            self,
            text="Iniciar Experimento",
            font=("Arial", 14),
            bg="#4CAF50",
            fg="white",
            command=self.iniciar,
        ).pack(pady=20)
        tk.Button(
            self,
            text="Configuraciones",
            font=("Arial", 10),
            command=self.abrir_configuraciones,
        ).pack()

    def iniciar(self):
        nombre = self.entry_nombre.get().strip()
        genero = self.genero_var.get()
        if nombre:
            self.pack_forget()
            self.controlador.iniciar_participante(nombre, genero, self.config_app)

    def abrir_configuraciones(self):
        VentanaConfiguracion(self, self.config_app)


class VentanaConfiguracion(tk.Toplevel):
    def __init__(self, parent, config_app):
        super().__init__(parent)
        self.title("Configuraciones")
        self.geometry("300x420")  # Aumentado para que quepa la nueva opción
        self.config_app = config_app

        tk.Label(self, text="Intentos por bloque:").pack(pady=5)
        self.spin_intentos = tk.Spinbox(self, from_=2, to=100)
        self.spin_intentos.delete(0, tk.END)
        self.spin_intentos.insert(0, self.config_app.intentos_por_bloque)
        self.spin_intentos.pack()

        tk.Label(self, text="Pausa corta (segundos):").pack(pady=5)
        self.spin_corta = tk.Spinbox(self, from_=1, to=300)
        self.spin_corta.delete(0, tk.END)
        self.spin_corta.insert(0, int(self.config_app.pausa_corta_ms / 1000))
        self.spin_corta.pack()

        tk.Label(self, text="Pausa larga (segundos):").pack(pady=5)
        self.spin_larga = tk.Spinbox(self, from_=1, to=600)
        self.spin_larga.delete(0, tk.END)
        self.spin_larga.insert(0, int(self.config_app.pausa_larga_ms / 1000))
        self.spin_larga.pack()

        tk.Label(self, text="Tamaño pelotas Recolección:").pack(pady=5)
        self.spin_radio = tk.Spinbox(self, from_=5, to=100)
        self.spin_radio.delete(0, tk.END)
        self.spin_radio.insert(0, self.config_app.radio_pelota)
        self.spin_radio.pack()

        tk.Label(self, text="Tamaño objetivo Caza:").pack(pady=5)
        self.spin_ave = tk.Spinbox(self, from_=5, to=100)
        self.spin_ave.delete(0, tk.END)
        self.spin_ave.insert(0, self.config_app.tamaño_ave)
        self.spin_ave.pack()

        tk.Label(self, text="Velocidad de Caza:").pack(pady=5)
        self.spin_vel = tk.Spinbox(self, from_=1, to=30)
        self.spin_vel.delete(0, tk.END)
        self.spin_vel.insert(0, self.config_app.velocidad_pelota)
        self.spin_vel.pack()

        tk.Button(self, text="Guardar", command=self.guardar).pack(pady=15)

    def guardar(self):
        self.config_app.intentos_por_bloque = int(self.spin_intentos.get())
        self.config_app.pausa_corta_ms = int(self.spin_corta.get()) * 1000
        self.config_app.pausa_larga_ms = int(self.spin_larga.get()) * 1000
        self.config_app.radio_pelota = int(self.spin_radio.get())
        self.config_app.tamaño_ave = int(self.spin_ave.get())
        self.config_app.velocidad_pelota = int(self.spin_vel.get())
        self.destroy()


class PantallaDescanso(tk.Frame):
    def __init__(self, parent, milisegundos, callback_fin_pausa):
        super().__init__(parent)
        self.callback = callback_fin_pausa
        self.segundos_restantes = milisegundos // 1000

        tk.Label(self, text="Tiempo de Descanso", font=("Arial", 24, "bold")).pack(
            pady=50
        )
        self.label_tiempo = tk.Label(
            self, text=f"{self.segundos_restantes} s", font=("Arial", 40)
        )
        self.label_tiempo.pack()

        self.boton_continuar = tk.Button(
            self,
            text="Continuar",
            font=("Arial", 14),
            bg="#2196F3",
            fg="white",
            command=self.finalizar_pausa,
        )

        self.actualizar_reloj()

    def actualizar_reloj(self):
        if self.segundos_restantes > 0:
            self.label_tiempo.config(text=f"{self.segundos_restantes} s")
            self.segundos_restantes -= 1
            self.after(1000, self.actualizar_reloj)
        else:
            self.label_tiempo.config(text="¡Tiempo cumplido!", fg="#4CAF50")
            self.boton_continuar.pack(pady=30)

    def finalizar_pausa(self):
        self.pack_forget()
        self.callback()


class PantallaFin(tk.Frame):
    def __init__(self, parent, callback_reinicio, resumen):
        super().__init__(parent)
        tk.Label(
            self, text="¡Experimento Finalizado!", font=("Arial", 24, "bold")
        ).pack(pady=30)
        tk.Label(
            self,
            text="Los datos han sido guardados en formato CSV.",
            font=("Arial", 12),
        ).pack(pady=10)

        frame_stats = tk.Frame(self, bg="#f0f0f0", bd=2, relief=tk.GROOVE)
        frame_stats.pack(pady=20, padx=50, fill=tk.X)

        tk.Label(
            frame_stats,
            text="Resumen de Rendimiento",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
        ).pack(pady=10)

        for modo, stats in resumen.items():
            texto = f"{modo.capitalize()}: {stats['acc']:.1f}% aciertos | Media: {stats['avg_time']:.0f} ms"
            tk.Label(frame_stats, text=texto, font=("Arial", 14), bg="#f0f0f0").pack(
                pady=5
            )

        tk.Button(
            self,
            text="Volver al Menú Principal",
            font=("Arial", 14),
            bg="#2196F3",
            fg="white",
            command=callback_reinicio,
        ).pack(pady=30)
