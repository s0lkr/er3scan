#! /usr/bin/env python3
"""
Sistema de Monitoramento de OPSEC
"""

from dataclasses import dataclass
import time
import asyncio
from dataclasses import dataclass
from typing import Dict, List
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.text import Text
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

@dataclass
class OPSECCheck:
    """Classe para representar um check de OPSEC"""
    max_rps: float = 0.8  # Requisições por segundo
    warning_threshold: float = 0.5  # Limite de alerta
    critical_threshold: float = 1.0  # Limite crítico
    sample_window: int = 10  # Janela de amostragem em segundos
    adaptive_limit: bool = True  # Limite adaptativo baseado em média móvel
    
class OPSECMonitor:
    """Classe para monitorar e exibir métricas de OPSEC"""
    
    def __init__(self, config: OPSECCheck = None):
        self.config = config or OPSECCheck()
        self.rps_samples: List[float] = []
        self.timestamps: List[float] = []
        self.console = Console()
        self.start_time = time.time()
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], 'b-')
        self.ax.set_ylim(0, self.config.max_rps * 1.5)
        self.ax.set_xlim(0, self.config.sample_window)
        self.ax.set_xlabel('Tempo (s)')
        self.ax.set_ylabel('Requisições por segundo (RPS)')
        self.ax.set_title('Monitoramento de OPSEC')
        plt.ion()
        plt.show()
    
    async def track_request(self):
        async with self.semaphore:
            now = time.time()
            self.request_timestamps.append(now)
            self.cleanup_old_requests(now)
            self.update_status()
            await self.__apply_rate_limit()
            
    def cleanup_old_requests(self, current_time: float):
        """Remove timestamps antigos fora da janela de amostragem"""
        self.request_timestamps = [t for t in self.request_timestamps if current_time - t <= self.config.sample_window]
            