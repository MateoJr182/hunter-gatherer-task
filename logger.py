# logger.py
import csv
import os

class Logger:
    def __init__(self):
        self.filename = ""

    def set_participante(self, p_id):
        # Crea un archivo único para cada participante
        self.filename = f"resultados_{p_id}.csv"
        
        if not os.path.exists(self.filename):
            with open(self.filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                # Nueva columna: Semilla
                writer.writerow(["ID_Participante", "Genero", "Semilla", "Juego", "Bloque", "Intento", "Precision", "Latencia_ms"])

    def registrar(self, p_id, genero, semilla, juego, bloque, intento, precision, latencia):
        with open(self.filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([p_id, genero, semilla, juego, bloque, intento, precision, round(latencia, 2)])