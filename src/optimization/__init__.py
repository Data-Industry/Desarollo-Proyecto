"""Módulo de Optimización y Simulación Estocástica de Inventarios.

Basado en la metodología de simulación estocástica de sistemas de inventarios
de García Dunna, García Reyes & Cárdenas Barrón (2013).
"""

from .simulador_montecarlo_paciente import (
    SimuladorInventarioPaciente,
    ResultadoSimulacion,
    simular_cobertura_insulina,
)

__all__ = [
    "SimuladorInventarioPaciente",
    "ResultadoSimulacion",
    "simular_cobertura_insulina",
]
