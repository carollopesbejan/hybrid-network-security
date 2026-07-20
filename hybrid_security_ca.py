"""
Estados:
  0 = Normal (Saudável, vulnerável)
  1 = Infectado (Propagando malware)
  2 = Sob Suspeita (Sensor detectou anomalia)
  3 = Em Quarentena (Isolado por firewall)
  4 = Vacinado (Patch aplicado, imune)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
import argparse
from datetime import datetime
import os


class HybridSecurityCA:
    """
    Autômato Celular Híbrido para Segurança de Redes
    
    Combina detecção por consenso distribuído com
    contenção ativa por firewalls móveis.
    """
    
    def __init__(self, grid_size=100, beta=0.3, gamma=0.1,
                 quorum=4, sensor_density=0.15, firewall_speed=0.3,
                 patch_rate=0.05, neighborhood='moore',
                 initial_infected=0.03, seed=None):
        """
        Inicializa o modelo híbrido de segurança.
        
        Parâmetros:
        -----------
        grid_size : int
            Tamanho da grade (grid_size × grid_size)
        beta : float
            Taxa de propagação do malware (0-1)
        gamma : float
            Taxa de recuperação natural (0-1)
        quorum : int
            Número mínimo de votos para confirmar ameaça
        sensor_density : float
            Fração de células que são sensores (0-1)
        firewall_speed : float
            Velocidade de movimentação dos firewalls (0-1)
        patch_rate : float
            Taxa de aplicação de patches em quarentena (0-1)
        neighborhood : str
            'moore' (8 vizinhos) ou 'von_neumann' (4 vizinhos)
        initial_infected : float
            Fração inicial de células infectadas
        seed : int or None
            Semente aleatória para reprodutibilidade
        """
        self.grid_size = grid_size
        self.beta = beta
        self.gamma = gamma
        self.quorum = quorum
        self.sensor_density = sensor_density
        self.firewall_speed = firewall_speed
        self.patch_rate = patch_rate
        self.neighborhood = neighborhood
        self.initial_infected = initial_infected
        
        if seed is not None:
            np.random.seed(seed)
        
        # Inicializar grade
        self.grid = np.zeros((grid_size, grid_size), dtype=int)
        
        # Matriz de sensores (fixa - quais células são sensores)
        self.sensors = np.random.random((grid_size, grid_size)) < sensor_density
        
        # Matriz de firewalls (dinâmica - posição dos firewalls)
        self.firewalls = np.zeros((grid_size, grid_size), dtype=bool)
        
        # Inicializar infecção e defesas
        self.initialize_infection()
        self.initialize_defenses()
        
        # Tracking
        self.time_step = 0
        self.history = {
            'normal': [],
            'infected': [],
            'suspicious': [],
            'quarantined': [],
            'vaccinated': [],
            'alarms_triggered': [],
            'false_alarms': [],
            'time': []
        }
        
        self.record_state()
    
    def initialize_infection(self):
        """Inicializa a grade com células infectadas aleatoriamente."""
        infection_mask = np.random.random((self.grid_size, self.grid_size)) < self.initial_infected
        self.grid[infection_mask] = 1
        
        print(f"╔══════════════════════════════════════════════╗")
        print(f"║   SISTEMA HÍBRIDO DE SEGURANÇA DE REDE      ║")
        print(f"╚══════════════════════════════════════════════╝")
        print(f"📊 Grade: {self.grid_size}×{self.grid_size} ({self.grid_size**2} nós)")
        print(f"🦠 Infectados iniciais: {np.sum(self.grid == 1)}")
        print(f"🔍 Sensores: {np.sum(self.sensors)} ({self.sensor_density*100:.0f}%)")
        print(f"⚙️  Parâmetros: β={self.beta}, γ={self.gamma}")
        print(f"🗳️  Quórum de votação: {self.quorum}")
        print(f"🛡️  Velocidade firewall: {self.firewall_speed}")
    
    def initialize_defenses(self):
        """Posiciona firewalls iniciais em células vacinadas."""
        # Alguns firewalls começam em posições aleatórias
        num_firewalls = int(self.grid_size * 0.05)  # 5% da grade
        positions = np.random.choice(self.grid_size**2, num_firewalls, replace=False)
        for pos in positions:
            i, j = pos // self.grid_size, pos % self.grid_size
            if self.grid[i, j] == 0:  # Só em células normais
                self.firewalls[i, j] = True
    
    def get_neighbors(self, i, j):
        """Obtém coordenadas dos vizinhos com condições periódicas."""
        if self.neighborhood == 'moore':
            offsets = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        else:
            offsets = [(-1,0), (1,0), (0,-1), (0,1)]
        
        neighbors = []
        for di, dj in offsets:
            ni = (i + di) % self.grid_size
            nj = (j + dj) % self.grid_size
            neighbors.append((ni, nj))
        
        return neighbors
    
    def count_neighbors_by_state(self, i, j):
        """Conta vizinhos por estado."""
        neighbors = self.get_neighbors(i, j)
        states = [self.grid[ni, nj] for ni, nj in neighbors]
        
        counts = {
            'normal': states.count(0),
            'infected': states.count(1),
            'suspicious': states.count(2),
            'quarantined': states.count(3),
            'vaccinated': states.count(4)
        }
        return counts
    
    def detect_anomalies(self):
        """Fase 1: Sensores analisam vizinhança e marcam suspeitos."""
        new_grid = self.grid.copy()
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i, j] == 0:  # Célula normal
                    if self.sensors[i, j]:  # Se for sensor
                        counts = self.count_neighbors_by_state(i, j)
                        # Se há infectados na vizinhança, marca como suspeito
                        if counts['infected'] > 0:
                            if np.random.random() < 0.8:  # 80% de chance de detectar
                                new_grid[i, j] = 2  # Marca como suspeito
        
        # Células suspeitas podem "voltar ao normal" se ameaça passou
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i, j] == 2:  # Suspeito
                    counts = self.count_neighbors_by_state(i, j)
                    if counts['infected'] == 0:
                        if np.random.random() < 0.3:  # 30% de chance de limpar
                            new_grid[i, j] = 0
        
        self.grid = new_grid
    
    def vote_and_consensus(self):
        """Fase 2: Sistema de votação entre vizinhos."""
        new_grid = self.grid.copy()
        alarms = 0
        false_alarms = 0
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i, j] == 2:  # Célula suspeita
                    counts = self.count_neighbors_by_state(i, j)
                    
                    # Sistema de votação ponderada
                    vote_score = (counts['suspicious'] * 1.0 + 
                                 counts['infected'] * 1.5 +
                                 counts['quarantined'] * 0.5)
                    
                    if vote_score >= self.quorum:
                        # ALARME CONFIRMADO!
                        alarms += 1
                        # Isolar esta célula
                        new_grid[i, j] = 3  # Quarentena
                        
                        # Isolar vizinhos infectados também
                        neighbors = self.get_neighbors(i, j)
                        for ni, nj in neighbors:
                            if self.grid[ni, nj] == 1:  # Infectado
                                new_grid[ni, nj] = 3  # Quarentena
                            elif self.grid[ni, nj] == 0 and np.random.random() < 0.3:
                                new_grid[ni, nj] = 2  # Alerta preventivo
                    else:
                        # Falso alarme (por enquanto)
                        if counts['infected'] == 0:
                            false_alarms += 1
        
        self.grid = new_grid
        
        if alarms > 0:
            self.history['alarms_triggered'].append(alarms)
            self.history['false_alarms'].append(false_alarms)
        else:
            self.history['alarms_triggered'].append(0)
            self.history['false_alarms'].append(0)
    
    def deploy_firewalls(self):
        """Fase 3: Firewalls se movem para conter ameaças."""
        new_firewalls = self.firewalls.copy()
        
        # Firewalls existentes se movem em direção a ameaças
        firewall_positions = np.argwhere(self.firewalls)
        
        for fi, fj in firewall_positions:
            if np.random.random() < self.firewall_speed:
                neighbors = self.get_neighbors(fi, fj)
                
                # Priorizar movimento para perto de infectados/suspeitos
                best_move = (fi, fj)  # Fica parado por padrão
                best_score = -1
                
                for ni, nj in neighbors:
                    if self.grid[ni, nj] in [0, 2]:  # Normal ou suspeito
                        counts = self.count_neighbors_by_state(ni, nj)
                        score = counts['infected'] * 3 + counts['suspicious'] * 1
                        
                        if score > best_score:
                            best_score = score
                            best_move = (ni, nj)
                
                # Mover firewall
                if best_move != (fi, fj):
                    new_firewalls[fi, fj] = False
                    new_firewalls[best_move[0], best_move[1]] = True
        
        # Firewalls aplicam quarentena em vizinhos infectados
        new_grid = self.grid.copy()
        firewall_positions = np.argwhere(new_firewalls)
        
        for fi, fj in firewall_positions:
            neighbors = self.get_neighbors(fi, fj)
            for ni, nj in neighbors:
                if self.grid[ni, nj] == 1:  # Infectado
                    new_grid[ni, nj] = 3  # Quarentena
                elif self.grid[ni, nj] == 2:  # Suspeito
                    new_grid[ni, nj] = 3  # Quarentena preventiva
        
        self.firewalls = new_firewalls
        self.grid = new_grid
    
    def apply_patches(self):
        """Fase 4: Aplicar patches em células em quarentena."""
        new_grid = self.grid.copy()
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i, j] == 3:  # Em quarentena
                    # Chance de ser vacinado
                    if np.random.random() < self.patch_rate:
                        new_grid[i, j] = 4  # Vacinado
                        # Recrutar firewall se houver vizinho vacinado
                        counts = self.count_neighbors_by_state(i, j)
                        if counts['vaccinated'] > 0 and np.random.random() < 0.2:
                            self.firewalls[i, j] = True
                
                elif self.grid[i, j] == 4:  # Vacinado
                    # Vacinados podem "curar" vizinhos em quarentena
                    neighbors = self.get_neighbors(i, j)
                    for ni, nj in neighbors:
                        if self.grid[ni, nj] == 3:  # Quarentena
                            if np.random.random() < self.patch_rate * 1.5:
                                new_grid[ni, nj] = 4  # Também vacinado
        
        self.grid = new_grid
    
    def spread_malware(self):
        """Fase 5: Malware tenta se propagar."""
        new_grid = self.grid.copy()
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i, j] == 1:  # Infectado
                    # Pode se recuperar naturalmente
                    if np.random.random() < self.gamma:
                        new_grid[i, j] = 4  # Vacinado naturalmente
                    else:
                        # Tentar infectar vizinhos
                        neighbors = self.get_neighbors(i, j)
                        for ni, nj in neighbors:
                            if self.grid[ni, nj] == 0:  # Normal (vulnerável)
                                n_neighbors = 8 if self.neighborhood == 'moore' else 4
                                infection_prob = self.beta / n_neighbors
                                if np.random.random() < infection_prob:
                                    new_grid[ni, nj] = 1  # Infectado!
        
        self.grid = new_grid
    
    def update(self):
        """Executa um passo completo da simulação."""
        # Ordem das operações é crucial!
        self.detect_anomalies()      # Fase 1: Detecção
        self.vote_and_consensus()    # Fase 2: Consenso
        self.deploy_firewalls()      # Fase 3: Contenção
        self.apply_patches()         # Fase 4: Recuperação
        self.spread_malware()        # Fase 5: Propagação
        
        self.time_step += 1
        self.record_state()
    
    def record_state(self):
        """Registra estatísticas atuais."""
        total = self.grid_size ** 2
        self.history['normal'].append(np.sum(self.grid == 0))
        self.history['infected'].append(np.sum(self.grid == 1))
        self.history['suspicious'].append(np.sum(self.grid == 2))
        self.history['quarantined'].append(np.sum(self.grid == 3))
        self.history['vaccinated'].append(np.sum(self.grid == 4))
        self.history['time'].append(self.time_step)
    
    def run_simulation(self, max_steps=200, verbose=True):
        """Executa a simulação completa."""
        for step in range(max_steps):
            self.update()
            
            if verbose and step % 50 == 0:
                print(f"Passo {self.time_step}: N={self.history['normal'][-1]}, "
                      f"I={self.history['infected'][-1]}, "
                      f"S={self.history['suspicious'][-1]}, "
                      f"Q={self.history['quarantined'][-1]}, "
                      f"V={self.history['vaccinated'][-1]}")
            
            # Parar se não há mais ameaças
            if (self.history['infected'][-1] == 0 and 
                self.history['suspicious'][-1] == 0 and
                self.history['quarantined'][-1] == 0):
                if verbose:
                    print(f"✅ Rede segura no passo {self.time_step}!")
                break
    
    def visualize_grid(self, ax=None):
        """Visualiza o estado atual da grade."""
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 10))
        
        # Mapa de cores: Normal=verde, Infectado=vermelho, Suspeito=amarelo,
        #                Quarentena=cinza, Vacinado=azul
        cmap = ListedColormap(['#2ecc71', '#e74c3c', '#f39c12', '#95a5a6', '#3498db'])
        
        # Criar overlay para firewalls
        display_grid = self.grid.copy()
        display_grid[self.firewalls] = 5  # Estado especial para firewalls
        
        ax.imshow(display_grid, cmap=cmap, interpolation='nearest', vmin=0, vmax=5)
        ax.set_title(f'Passo {self.time_step}', fontsize=14, fontweight='bold')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        
        # Legenda
        legend_elements = [
            Patch(facecolor='#2ecc71', label='Normal'),
            Patch(facecolor='#e74c3c', label='Infectado'),
            Patch(facecolor='#f39c12', label='Sob Suspeita'),
            Patch(facecolor='#95a5a6', label='Quarentena'),
            Patch(facecolor='#3498db', label='Vacinado')
        ]
        ax.legend(handles=legend_elements, loc='upper left', 
                 bbox_to_anchor=(1.02, 1), fontsize=10)
        
        return ax
    
    def plot_results(self, save=True):
        """Plota resultados completos da simulação."""
        fig = plt.figure(figsize=(18, 12))
        gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
        
        # Gráfico 1: Populações ao longo do tempo
        ax1 = fig.add_subplot(gs[0, :2])
        ax1.plot(self.history['time'], self.history['normal'], 
                color='#2ecc71', label='Normal', linewidth=2)
        ax1.plot(self.history['time'], self.history['infected'], 
                color='#e74c3c', label='Infectado', linewidth=2)
        ax1.plot(self.history['time'], self.history['suspicious'], 
                color='#f39c12', label='Sob Suspeita', linewidth=2)
        ax1.plot(self.history['time'], self.history['quarantined'], 
                color='#95a5a6', label='Quarentena', linewidth=2)
        ax1.plot(self.history['time'], self.history['vaccinated'], 
                color='#3498db', label='Vacinado', linewidth=2)
        ax1.set_xlabel('Passo Temporal', fontsize=12)
        ax1.set_ylabel('População', fontsize=12)
        ax1.set_title('Evolução do Sistema de Segurança', fontsize=14, fontweight='bold')
        ax1.legend(loc='center right', fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Alarmes ao longo do tempo
        ax2 = fig.add_subplot(gs[0, 2])
        ax2.bar(self.history['time'][1:], self.history['alarms_triggered'][1:], 
               color='#e74c3c', alpha=0.7, label='Alarmes Verdadeiros')
        ax2.bar(self.history['time'][1:], self.history['false_alarms'][1:], 
               color='#f39c12', alpha=0.7, label='Falsos Alarmes')
        ax2.set_xlabel('Passo Temporal', fontsize=12)
        ax2.set_ylabel('Número de Alarmes', fontsize=12)
        ax2.set_title('Sistema de Alarmes', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Gráfico 3: Estado final da grade
        ax3 = fig.add_subplot(gs[1, :2])
        self.visualize_grid(ax3)
        
        # Gráfico 4: Métricas de eficácia
        ax4 = fig.add_subplot(gs[1, 2])
        
        # Calcular métricas
        total_infected = max(self.history['infected'])
        total_quarantined = max(self.history['quarantined'])
        total_vaccinated = self.history['vaccinated'][-1]
        total_alarms = sum(self.history['alarms_triggered'])
        total_false = sum(self.history['false_alarms'])
        
        metrics = ['Pico\nInfectados', 'Máx.\nQuarentena', 'Total\nVacinados', 
                  'Alarmes\nReais', 'Falsos\nAlarmes']
        values = [total_infected, total_quarantined, total_vaccinated, 
                 total_alarms, total_false]
        colors = ['#e74c3c', '#95a5a6', '#3498db', '#2ecc71', '#f39c12']
        
        bars = ax4.bar(metrics, values, color=colors, alpha=0.8)
        ax4.set_ylabel('Contagem', fontsize=12)
        ax4.set_title('Métricas de Eficácia', fontsize=14, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Adicionar valores nas barras
        for bar, val in zip(bars, values):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, 
                    str(val), ha='center', fontweight='bold')
        
        plt.suptitle('Sistema Híbrido de Detecção e Contenção de Ameaças\n'
                    f'(β={self.beta}, γ={self.gamma}, Quórum={self.quorum})',
                    fontsize=16, fontweight='bold')
        
        if save:
            plt.savefig('hybrid_security_results.png', dpi=200, 
                       bbox_inches='tight', facecolor='white')
            print("📊 Resultados salvos como 'hybrid_security_results.png'")
        
        plt.show()
    
    def create_animation(self, max_frames=200, interval=100):
        """Cria animação da simulação."""
        # Reset
        self.__init__(self.grid_size, self.beta, self.gamma,
                     self.quorum, self.sensor_density, self.firewall_speed,
                     self.patch_rate, self.neighborhood, self.initial_infected)
        
        fig = plt.figure(figsize=(16, 8))
        gs = fig.add_gridspec(1, 2, wspace=0.3)
        
        # Subplot esquerdo: Grade
        ax_grid = fig.add_subplot(gs[0, 0])
        cmap = ListedColormap(['#2ecc71', '#e74c3c', '#f39c12', '#95a5a6', '#3498db'])
        
        display_grid = self.grid.copy()
        display_grid[self.firewalls] = 5
        im = ax_grid.imshow(display_grid, cmap=cmap, interpolation='nearest',
                           animated=True, vmin=0, vmax=5)
        ax_grid.set_title('Rede', fontsize=14, fontweight='bold')
        
        # Subplot direito: Gráfico de linhas
        ax_plot = fig.add_subplot(gs[0, 1])
        lines = {}
        lines['normal'], = ax_plot.plot([], [], color='#2ecc71', label='Normal', linewidth=2)
        lines['infected'], = ax_plot.plot([], [], color='#e74c3c', label='Infectado', linewidth=2)
        lines['suspicious'], = ax_plot.plot([], [], color='#f39c12', label='Suspeito', linewidth=2)
        lines['quarantined'], = ax_plot.plot([], [], color='#95a5a6', label='Quarentena', linewidth=2)
        lines['vaccinated'], = ax_plot.plot([], [], color='#3498db', label='Vacinado', linewidth=2)
        
        ax_plot.set_xlim(0, max_frames)
        ax_plot.set_ylim(0, self.grid_size ** 2)
        ax_plot.set_xlabel('Passo Temporal', fontsize=12)
        ax_plot.set_ylabel('População', fontsize=12)
        ax_plot.set_title('Evolução Temporal', fontsize=14, fontweight='bold')
        ax_plot.legend(loc='upper right', fontsize=10)
        ax_plot.grid(True, alpha=0.3)
        
        def update_frame(frame):
            if frame > 0:
                self.update()
            
            display = self.grid.copy()
            display[self.firewalls] = 5
            im.set_array(display)
            
            times = self.history['time']
            for key in ['normal', 'infected', 'suspicious', 'quarantined', 'vaccinated']:
                lines[key].set_data(times, self.history[key])
            
            ax_plot.set_xlim(0, max(frame + 10, max_frames))
            
            return im, *lines.values()
        
        anim = animation.FuncAnimation(fig, update_frame, frames=max_frames,
                                      interval=interval, blit=True)
        
        plt.suptitle('Sistema Híbrido de Segurança - Detecção e Contenção',
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
        
        return anim


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description='Sistema Híbrido de Detecção e Contenção de Ameaças'
    )
    
    parser.add_argument('--grid-size', type=int, default=100,
                       help='Tamanho da grade (default: 100)')
    parser.add_argument('--beta', type=float, default=0.3,
                       help='Taxa de propagação do malware (default: 0.3)')
    parser.add_argument('--gamma', type=float, default=0.05,
                       help='Taxa de recuperação natural (default: 0.05)')
    parser.add_argument('--quorum', type=int, default=4,
                       help='Quórum mínimo para alarme (default: 4)')
    parser.add_argument('--sensor-density', type=float, default=0.15,
                       help='Densidade de sensores (default: 0.15)')
    parser.add_argument('--firewall-speed', type=float, default=0.3,
                       help='Velocidade dos firewalls (default: 0.3)')
    parser.add_argument('--patch-rate', type=float, default=0.05,
                       help='Taxa de aplicação de patches (default: 0.05)')
    parser.add_argument('--neighborhood', type=str, default='moore',
                       choices=['moore', 'von_neumann'])
    parser.add_argument('--initial-infected', type=float, default=0.03,
                       help='Fração inicial infectada (default: 0.03)')
    parser.add_argument('--steps', type=int, default=200,
                       help='Passos máximos (default: 200)')
    parser.add_argument('--animate', action='store_true',
                       help='Criar animação')
    parser.add_argument('--seed', type=int, default=42,
                       help='Semente aleatória (default: 42)')
    
    args = parser.parse_args()
    
    # Criar e executar simulação
    ca = HybridSecurityCA(
        grid_size=args.grid_size,
        beta=args.beta,
        gamma=args.gamma,
        quorum=args.quorum,
        sensor_density=args.sensor_density,
        firewall_speed=args.firewall_speed,
        patch_rate=args.patch_rate,
        neighborhood=args.neighborhood,
        initial_infected=args.initial_infected,
        seed=args.seed
    )
    
    if args.animate:
        print("🎬 Criando animação...")
        ca.create_animation(max_frames=args.steps)
    else:
        print("\n🔄 Executando simulação...")
        ca.run_simulation(max_steps=args.steps)
        
        # Estatísticas finais
        print(f"\n{'='*50}")
        print(f"📊 RESULTADOS FINAIS")
        print(f"{'='*50}")
        print(f"✅ Normais: {ca.history['normal'][-1]}")
        print(f"🦠 Infectados: {ca.history['infected'][-1]}")
        print(f"⚠️  Suspeitos: {ca.history['suspicious'][-1]}")
        print(f"🚫 Quarentena: {ca.history['quarantined'][-1]}")
        print(f"🛡️  Vacinados: {ca.history['vaccinated'][-1]}")
        print(f"🚨 Total alarmes: {sum(ca.history['alarms_triggered'])}")
        print(f"❌ Falsos alarmes: {sum(ca.history['false_alarms'])}")
        
        # Resultados
        ca.plot_results(save=True)
    
    print(f"\n✨ Simulação concluída!")


if __name__ == "__main__":
    main()