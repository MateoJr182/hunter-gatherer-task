# config.py


class Configuracion:
    def __init__(self):
        # Valores por defecto
        self.intentos_por_bloque = 5
        self.pausa_corta_ms = 5 * 1000  # 1 minuto
        self.pausa_larga_ms = 5 * 1000  # 2 minutos
        self.color_fondo = "#FAFAFA"

        # Variables independientes de tamaño
        self.radio_pelota = 21  # Para Recolección
        self.tamaño_ave = 30  # Para Caza

        self.velocidad_pelota = 4  # velocidad base de movimiento

    @property
    def total_intentos_por_juego(self):
        return self.intentos_por_bloque * 2
