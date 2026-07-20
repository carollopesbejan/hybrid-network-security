from hybrid_security_ca import HybridSecurityCA
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap


def analyze_quorum_sensitivity():
    """Analisa sensibilidade ao quórum de votação."""
    print("\n🔍 Analisando sensibilidade ao quórum...")
    
    quorums = [2, 3, 4, 5, 6, 7, 8]
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    
    results = {}
    
    for idx, quorum in enumerate(quorums):
        ax = axes.flatten()[idx]
        
        ca = HybridSecurityCA(
            grid_size=50, beta=0.3, gamma=0.05,
            quorum=quorum, sensor_density=0.15,
            firewall_speed=0.3, patch_rate=0.05,
            seed=42
        )
        
        for _ in range(150):
            ca.update()
            if ca.history['infected'][-1] == 0 and ca.history['suspicious'][-1] == 0:
                break
        
        # Plot
        ax.plot(ca.history['time'], ca.history['infected'], 
               color='#e74c3c', label='Infectados', linewidth=2)
        ax.plot(ca.history['time'], ca.history['quarantined'], 
               color='#95a5a6', label='Quarentena', linewidth=2)
        ax.plot(ca.history['time'], ca.history['vaccinated'], 
               color='#3498db', label='Vacinados', linewidth=2)
        
        ax.set_title(f'Quórum = {quorum}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Passo')
        ax.set_ylabel('População')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        
        # Métricas
        peak_infected = max(ca.history['infected'])
        total_alarms = sum(ca.history['alarms_triggered'])
        total_false = sum(ca.history['false_alarms'])
        final_vaccinated = ca.history['vaccinated'][-1]
        
        results[quorum] = {
            'peak': peak_infected,
            'alarms': total_alarms,
            'false': total_false,
            'vaccinated': final_vaccinated
        }
        
        # Adicionar texto
        ax.text(0.95, 0.95, 
               f'Pico: {peak_infected}\nAlarmes: {total_alarms}\n'
               f'Falsos: {total_false}\nVacinas: {final_vaccinated}',
               transform=ax.transAxes, fontsize=8,
               verticalalignment='top', horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Remover último subplot vazio
    axes.flatten()[-1].remove()
    
    plt.suptitle('Análise de Sensibilidade ao Quórum de Votação',
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('quorum_analysis.png', dpi=200, bbox_inches='tight')
    print("✅ Análise de quórum salva como 'quorum_analysis.png'")
    plt.show()
    
    return results


def analyze_defense_strategies():
    """Compara diferentes estratégias de defesa."""
    print("\n🛡️ Comparando estratégias de defesa...")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    strategies = [
        {'name': 'Sem Defesa', 'sensors': 0, 'firewalls': False, 'patches': False},
        {'name': 'Apenas Sensores', 'sensors': 0.2, 'firewalls': False, 'patches': False},
        {'name': 'Sensores + Firewalls', 'sensors': 0.15, 'firewalls': True, 'patches': False},
        {'name': 'Sistema Híbrido Completo', 'sensors': 0.15, 'firewalls': True, 'patches': True}
    ]
    
    for idx, (ax, strategy) in enumerate(zip(axes.flatten(), strategies)):
        ca = HybridSecurityCA(
            grid_size=50, beta=0.3, gamma=0.05,
            quorum=4,
            sensor_density=strategy['sensors'],
            firewall_speed=0.3 if strategy['firewalls'] else 0,
            patch_rate=0.05 if strategy['patches'] else 0,
            seed=42
        )
        
        for _ in range(150):
            ca.update()
            if ca.history['infected'][-1] == 0:
                break
        
        ax.plot(ca.history['time'], ca.history['normal'], 
               color='#2ecc71', label='Normal', linewidth=2)
        ax.plot(ca.history['time'], ca.history['infected'], 
               color='#e74c3c', label='Infectado', linewidth=2)
        ax.plot(ca.history['time'], ca.history['vaccinated'], 
               color='#3498db', label='Vacinado', linewidth=2)
        
        ax.set_title(strategy['name'], fontsize=14, fontweight='bold')
        ax.set_xlabel('Passo Temporal')
        ax.set_ylabel('População')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Métricas
        peak = max(ca.history['infected'])
        final_vac = ca.history['vaccinated'][-1]
        ax.text(0.95, 0.5, f'Pico: {peak}\nVacinados: {final_vac}',
               transform=ax.transAxes, fontsize=10,
               verticalalignment='top', horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.suptitle('Comparação de Estratégias de Defesa',
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('defense_strategies.png', dpi=200, bbox_inches='tight')
    print("✅ Estratégias de defesa salvas como 'defense_strategies.png'")
    plt.show()


def create_spatial_evolution():
    """Cria evolução espacial com snapshots."""
    print("\n📸 Criando evolução espacial...")
    
    ca = HybridSecurityCA(
        grid_size=50, beta=0.3, gamma=0.05,
        quorum=4, sensor_density=0.15,
        firewall_speed=0.3, patch_rate=0.05,
        seed=42
    )
    
    snapshots = []
    times = [0, 10, 20, 30, 50, 80]
    
    for t in range(81):
        if t in times:
            snapshots.append((t, ca.grid.copy(), ca.firewalls.copy()))
        if t < 80:
            ca.update()
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    cmap = ListedColormap(['#2ecc71', '#e74c3c', '#f39c12', '#95a5a6', '#3498db'])
    
    for idx, (ax, (t, grid, firewalls)) in enumerate(zip(axes.flatten(), snapshots)):
        display = grid.copy()
        display[firewalls] = 5
        ax.imshow(display, cmap=cmap, interpolation='nearest', vmin=0, vmax=5)
        
        n_normal = np.sum(grid == 0)
        n_infected = np.sum(grid == 1)
        n_vaccinated = np.sum(grid == 4)
        
        ax.set_title(f'Passo {t}\nNormais:{n_normal} | Infectados:{n_infected} | '
                    f'Vacinados:{n_vaccinated}', fontsize=11, fontweight='bold')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
    
    plt.suptitle('Evolução Espacial do Sistema Híbrido de Segurança',
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('spatial_evolution_hybrid.png', dpi=200, bbox_inches='tight')
    print("✅ Evolução espacial salva como 'spatial_evolution_hybrid.png'")
    plt.show()


if __name__ == "__main__":
    print("="*60)
    print("🔬 Análise Avançada do Sistema Híbrido de Segurança")
    print("="*60)
    
    print("\n1️⃣  Analisando sensibilidade ao quórum...")
    results = analyze_quorum_sensitivity()
    
    print("\n2️⃣  Comparando estratégias de defesa...")
    analyze_defense_strategies()
    
    print("\n3️⃣  Criando evolução espacial...")
    create_spatial_evolution()
    
    print("\n" + "="*60)
    print("✅ Todas as análises completas!")
    print("="*60)
    print("\n📁 Arquivos gerados:")
    print("  1. quorum_analysis.png")
    print("  2. defense_strategies.png")
    print("  3. spatial_evolution_hybrid.png")
    print("\n💡 Execute também:")
    print("  python hybrid_security_ca.py --animate")
    print("="*60)