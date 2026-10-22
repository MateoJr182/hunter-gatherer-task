# controlador.py
import random
import tkinter as tk
from logger import Logger
from vistas_ui import PantallaDescanso, PantallaFin
from juego_recoleccion import JuegoRecoleccion
from juego_caza import JuegoCaza

class ExperimentController:
    def __init__(self, root):
        self.root = root
        self.participante_id = None
        self.genero = None
        self.config = None
        self.logger = Logger()
        
        self.orden_juegos = []
        self.juego_actual_idx = 0
        self.intento_actual = 0
        self.bloque_actual = 1
        
    def iniciar_participante(self, nombre, genero, config_app):
        self.participante_id = nombre
        self.genero = genero
        self.config = config_app
        
        self.semilla_actual = hash(self.participante_id)
        random.seed(self.semilla_actual)
        self.logger.set_participante(self.participante_id)
        
        self.orden_juegos = ["recoleccion", "caza"]
        random.shuffle(self.orden_juegos)
        
        self.juego_actual_idx = 0
        self.intento_actual = 0
        self.bloque_actual = 1
        
        # Diccionario para calcular promedios al final
        self.resultados_memoria = {"recoleccion": [], "caza": []}
        
        self.lanzar_siguiente_intento()

    def registrar_resultado(self, precision, latencia):
        juego = self.orden_juegos[self.juego_actual_idx]
        
        # Guardar en CSV
        self.logger.registrar(
            self.participante_id, self.genero, self.semilla_actual, 
            juego, self.bloque_actual, self.intento_actual + 1, 
            precision, latencia
        )
        
        # Guardar en memoria para el resumen final
        self.resultados_memoria[juego].append({"precision": precision, "latencia": latencia})
        
        self.intento_actual += 1
        self.evaluar_flujo()

    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.pack_forget()

    def evaluar_flujo(self):
        if self.intento_actual == self.config.total_intentos_por_juego:
            self.juego_actual_idx += 1
            if self.juego_actual_idx < len(self.orden_juegos):
                self.intento_actual = 0
                self.bloque_actual += 1
                self.disparar_pausa(self.config.pausa_larga_ms)
            else:
                self.finalizar_experimento()
                
        elif self.intento_actual == self.config.intentos_por_bloque:
            self.bloque_actual += 1
            self.disparar_pausa(self.config.pausa_corta_ms)
            
        else:
            self.lanzar_siguiente_intento()

    def disparar_pausa(self, duracion_ms):
        self.limpiar_pantalla()
        pantalla_pausa = PantallaDescanso(self.root, duracion_ms, self.lanzar_siguiente_intento)
        pantalla_pausa.pack(expand=True, fill=tk.BOTH)
        
    def lanzar_siguiente_intento(self):
        self.limpiar_pantalla()
        juego_actual = self.orden_juegos[self.juego_actual_idx]
        
        if juego_actual == "recoleccion":
            vista = JuegoRecoleccion(self.root, self)
        else:
            vista = JuegoCaza(self.root, self)
            
        vista.pack(expand=True, fill=tk.BOTH)
        vista.iniciar()

    def reiniciar_experimento(self):
        self.limpiar_pantalla()
        self.participante_id = None
        self.genero = None
        self.intento_actual = 0
        self.bloque_actual = 1
        self.resultados_memoria = {"recoleccion": [], "caza": []}
        
        from vistas_ui import PantallaBienvenida
        pantalla_inicio = PantallaBienvenida(self.root, self, self.config)
        pantalla_inicio.pack(expand=True, fill=tk.BOTH)

    def finalizar_experimento(self):
        self.limpiar_pantalla()
        
        # Calcular estadísticas
        resumen = {}
        for modo, datos in self.resultados_memoria.items():
            if datos:
                acc = sum(d["precision"] for d in datos) / len(datos) * 100
                avg_time = sum(d["latencia"] for d in datos) / len(datos)
            else:
                acc, avg_time = 0, 0
            resumen[modo] = {"acc": acc, "avg_time": avg_time}
            
        pantalla_final = PantallaFin(self.root, self.reiniciar_experimento, resumen)
        pantalla_final.pack(expand=True, fill=tk.BOTH)