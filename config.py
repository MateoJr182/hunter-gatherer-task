# config.py

class Configuracion:
    def __init__(self):
        # Valores por defecto
        self.intentos_por_bloque = 25
        self.pausa_corta_ms = 60 * 1000   # 1 minuto
        self.pausa_larga_ms = 120 * 1000  # 2 minutos
        self.color_fondo = "#FAFAFA"
        self.radio_pelota = 20
        self.velocidad_pelota = 6         # velocidad de movimiento
        
    @property
    def total_intentos_por_juego(self):
        return self.intentos_por_bloque * 2