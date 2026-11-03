# tema.py
"""Paleta, tipografías y widgets reutilizables para toda la interfaz.

Los botones están hechos con tk.Label porque en macOS tk.Button ignora
los colores de fondo/texto; así se ven igual en Windows, macOS y Linux.
"""
import tkinter as tk
from tkinter import font as tkfont

# --- Paleta -----------------------------------------------------------------
FONDO = "#F4F1EA"        # crema cálido (pantallas de menú)
TARJETA = "#FFFFFF"
TEXTO = "#2B2B2B"
TEXTO_SUAVE = "#7A7468"
BORDE = "#E2DDD0"

VERDE = "#4C8C4A"
VERDE_HOVER = "#3F763D"
AZUL = "#3B7DD8"
AZUL_HOVER = "#2F68B8"
GRIS = "#E9E5DA"
GRIS_HOVER = "#DCD7C9"

_FAMILIAS_PREFERIDAS = (
    "Segoe UI", "SF Pro Text", "Helvetica Neue", "Inter", "Ubuntu", "DejaVu Sans", "Arial",
)
_familia = None


def familia():
    """Primera tipografía disponible de la lista (se resuelve una sola vez)."""
    global _familia
    if _familia is None:
        disponibles = set(tkfont.families())
        _familia = next((f for f in _FAMILIAS_PREFERIDAS if f in disponibles), "Arial")
    return _familia


def fuente(tam=12, estilo="normal"):
    return (familia(), tam, estilo)


# --- Widgets ----------------------------------------------------------------
class Boton(tk.Label):
    """Botón plano con efecto hover. `estilo`: 'primario', 'azul' o 'suave'."""

    ESTILOS = {
        "primario": (VERDE, VERDE_HOVER, "white"),
        "azul": (AZUL, AZUL_HOVER, "white"),
        "suave": (GRIS, GRIS_HOVER, TEXTO),
    }

    def __init__(self, parent, texto, comando, estilo="primario", tam=14, padx=34, pady=12):
        bg, hover, fg = self.ESTILOS[estilo]
        super().__init__(
            parent, text=texto, bg=bg, fg=fg, font=fuente(tam, "bold"),
            padx=padx, pady=pady, cursor="hand2",
        )
        self._bg, self._hover, self._comando = bg, hover, comando
        self.bind("<Enter>", lambda e: self.config(bg=self._hover))
        self.bind("<Leave>", lambda e: self.config(bg=self._bg))
        self.bind("<Button-1>", lambda e: self._comando())


class Segmentado(tk.Frame):
    """Selector de opciones excluyentes (reemplaza a los Radiobutton)."""

    def __init__(self, parent, variable, opciones, bg=TARJETA):
        super().__init__(parent, bg=bg)
        self.variable = variable
        self.botones = {}
        for texto, valor in opciones:
            lbl = tk.Label(
                self, text=texto, font=fuente(12), padx=22, pady=8,
                cursor="hand2", bd=0,
            )
            lbl.pack(side=tk.LEFT, padx=3)
            lbl.bind("<Button-1>", lambda e, v=valor: self.variable.set(v))
            self.botones[valor] = lbl
        self.variable.trace_add("write", lambda *a: self._pintar())
        self._pintar()

    def _pintar(self):
        for valor, lbl in self.botones.items():
            if self.variable.get() == valor:
                lbl.config(bg=VERDE, fg="white")
            else:
                lbl.config(bg=GRIS, fg=TEXTO)


class CampoTexto(tk.Frame):
    """Entry con subrayado que se resalta al enfocarlo."""

    def __init__(self, parent, ancho=24, bg=TARJETA):
        super().__init__(parent, bg=bg)
        self.entry = tk.Entry(
            self, font=fuente(14), width=ancho, relief=tk.FLAT, bd=0,
            bg=bg, fg=TEXTO, insertbackground=TEXTO, justify="center",
            highlightthickness=0,
        )
        self.entry.pack(ipady=6)
        self.linea = tk.Frame(self, height=2, bg=BORDE)
        self.linea.pack(fill=tk.X)
        self.entry.bind("<FocusIn>", lambda e: self.linea.config(bg=VERDE))
        self.entry.bind("<FocusOut>", lambda e: self.linea.config(bg=BORDE))
        # al escribir se limpia el estado de error (la línea vuelve al color de foco)
        self.entry.bind("<Key>", lambda e: self.linea.config(bg=VERDE))

    def get(self):
        return self.entry.get()

    def focus(self):
        self.entry.focus_set()

    def marcar_error(self):
        self.linea.config(bg="#D9534F")


def tarjeta(parent, **kw):
    """Frame blanco con borde fino, para agrupar contenido sobre el fondo crema."""
    return tk.Frame(
        parent, bg=TARJETA, highlightbackground=BORDE, highlightcolor=BORDE,
        highlightthickness=1, **kw,
    )


def centrar_ventana(root, ancho, alto):
    root.update_idletasks()
    x = (root.winfo_screenwidth() - ancho) // 2
    y = max(0, (root.winfo_screenheight() - alto) // 2 - 20)
    root.geometry(f"{ancho}x{alto}+{x}+{y}")
