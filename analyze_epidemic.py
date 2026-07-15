from epidemic_ca import DigitalEpidemicCA
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

def run_parameter_sweep():
    """Varredura de parâmetros para encontrar transições de fase"""
    betas = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    gammas = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
    
    results = np.zeros((len(betas), len(gammas)))
    
    # Criar figura com GridSpec para controle preciso
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(2, 3, hspace=0.35, wspace=0.3)
    
    # ===== SUBPLOT 1: MAPA DE CALOR (Superior Esquerdo) =====
    ax_heatmap = fig.add_subplot(gs[0, 0])
    
    print("Executando 48 simulações para o mapa de calor...")
    for i, beta in enumerate(betas):
        for j, gamma in enumerate(gammas):
            ca = DigitalEpidemicCA(
                grid_size=50, 
                beta=beta, 
                gamma=gamma, 
                neighborhood='moore',
                initial_infected=0.05,
                seed=42
            )
            
            # Executar simulação silenciosamente
            for _ in range(200):
                ca.update()
                if ca.history['infected'][-1] == 0:
                    break
            
            attack_rate = (ca.history['recovered'][-1] + ca.history['infected'][-1]) / (50*50)
            results[i, j] = attack_rate
    
    # Plot do mapa de calor
    im = ax_heatmap.imshow(results, cmap='YlOrRd', aspect='auto', origin='lower')
    ax_heatmap.set_xticks(range(len(gammas)))
    ax_heatmap.set_xticklabels([f'{g:.2f}' for g in gammas], fontsize=10)
    ax_heatmap.set_yticks(range(len(betas)))
    ax_heatmap.set_yticklabels([f'{b:.2f}' for b in betas], fontsize=10)
    ax_heatmap.set_xlabel('Taxa de Recuperação (γ)', fontsize=12, fontweight='bold')
    ax_heatmap.set_ylabel('Taxa de Transmissão (β)', fontsize=12, fontweight='bold')
    ax_heatmap.set_title('Taxa de Ataque por Parâmetros', fontsize=13, fontweight='bold')
    
    # Adicionar barra de cores
    cbar = plt.colorbar(im, ax=ax_heatmap)
    cbar.set_label('Taxa de Ataque', fontsize=11, fontweight='bold')
    
    # Adicionar valores numéricos nas células
    for i in range(len(betas)):
        for j in range(len(gammas)):
            if results[i, j] > 0.7:
                color = 'white'
            else:
                color = 'black'
            ax_heatmap.text(j, i, f'{results[i,j]:.2f}', 
                          ha='center', va='center', color=color, fontsize=8, fontweight='bold')
    
    # ===== SUBPLOTS 2-4: CENÁRIOS ESPECÍFICOS =====
    scenarios = [
        {'beta': 0.2, 'gamma': 0.3, 'title': 'Epidemia Contida (R₀<1)', 'pos': (0, 1)},
        {'beta': 0.3, 'gamma': 0.15, 'title': 'Limiar Crítico (R₀≈2)', 'pos': (0, 2)},
        {'beta': 0.5, 'gamma': 0.1, 'title': 'Epidemia Explosiva (R₀=5)', 'pos': (1, 0)}
    ]
    
    for scenario in scenarios:
        ax = fig.add_subplot(gs[scenario['pos']])
        ca = DigitalEpidemicCA(
            grid_size=50, 
            beta=scenario['beta'], 
            gamma=scenario['gamma'], 
            neighborhood='moore',
            seed=42
        )
        
        for _ in range(200):
            ca.update()
            if ca.history['infected'][-1] == 0:
                break
        
        # Plot com cores melhoradas
        ax.plot(ca.history['time'], ca.history['susceptible'], 
                color='#3498db', label='Suscetíveis', linewidth=2.5)
        ax.plot(ca.history['time'], ca.history['infected'], 
                color='#e74c3c', label='Infectados', linewidth=2.5)
        ax.plot(ca.history['time'], ca.history['recovered'], 
                color='#2ecc71', label='Recuperados', linewidth=2.5)
        
        # Preenchimento da área de infectados
        ax.fill_between(ca.history['time'], 0, ca.history['infected'], 
                        color='#e74c3c', alpha=0.15)
        
        ax.set_xlabel('Passo Temporal', fontsize=11)
        ax.set_ylabel('População', fontsize=11)
        ax.set_title(scenario['title'], fontsize=13, fontweight='bold')
        ax.legend(loc='best', fontsize=10, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Adicionar estatísticas
        peak = max(ca.history['infected'])
        peak_step = ca.history['infected'].index(peak)
        final_attack = (ca.history['recovered'][-1] + ca.history['infected'][-1]) / 2500 * 100
        r0 = scenario['beta'] / scenario['gamma']
        
        stats_text = f'Pico: {peak} infectados\n'
        stats_text += f'({peak/2500*100:.1f}% no passo {peak_step})\n'
        stats_text += f'Ataque Final: {final_attack:.1f}%\n'
        stats_text += f'R₀ = {r0:.1f}'
        
        ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
                fontsize=9, verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # ===== SUBPLOT 5: COMPARAÇÃO DE VIZINHANÇAS (Inferior Central) =====
    ax_neigh = fig.add_subplot(gs[1, 1])
    
    neighborhoods = [
        ('moore', '#e74c3c', 'Moore (8 vizinhos)'),
        ('von_neumann', '#3498db', 'von Neumann (4 vizinhos)')
    ]
    
    for neigh, color, label in neighborhoods:
        ca = DigitalEpidemicCA(
            grid_size=50, 
            beta=0.3, 
            gamma=0.1, 
            neighborhood=neigh,
            seed=42
        )
        
        for _ in range(200):
            ca.update()
            if ca.history['infected'][-1] == 0:
                break
        
        ax_neigh.plot(ca.history['time'], ca.history['infected'], 
                     color=color, label=label, linewidth=2.5)
        
        # Adicionar marcador no pico
        peak_idx = ca.history['infected'].index(max(ca.history['infected']))
        ax_neigh.plot(ca.history['time'][peak_idx], ca.history['infected'][peak_idx], 
                     'o', color=color, markersize=10)
    
    ax_neigh.set_xlabel('Passo Temporal', fontsize=11)
    ax_neigh.set_ylabel('Número de Infectados', fontsize=11)
    ax_neigh.set_title('Impacto da Topologia de Rede', fontsize=13, fontweight='bold')
    ax_neigh.legend(fontsize=11)
    ax_neigh.grid(True, alpha=0.3, linestyle='--')
    
    # ===== SUBPLOT 6: ESPAÇO DE FASE (Inferior Direito) =====
    ax_phase = fig.add_subplot(gs[1, 2])
    
    # Usar cenário explosivo para diagrama de fase
    ca = DigitalEpidemicCA(
        grid_size=50, 
        beta=0.5, 
        gamma=0.1, 
        neighborhood='moore',
        seed=42
    )
    
    for _ in range(200):
        ca.update()
        if ca.history['infected'][-1] == 0:
            break
    
    # Plot trajetória no espaço de fase S-I
    points = np.array([ca.history['susceptible'], ca.history['infected']])
    ax_phase.plot(points[0], points[1], 'o-', color='#8e44ad', 
                 markersize=2, linewidth=1.5, alpha=0.7)
    
    # Destacar pontos importantes
    ax_phase.plot(points[0][0], points[1][0], 'go', markersize=12, 
                 label='Início', alpha=0.8)
    
    peak_idx = ca.history['infected'].index(max(ca.history['infected']))
    ax_phase.plot(points[0][peak_idx], points[1][peak_idx], 'ro', markersize=12, 
                 label='Pico', alpha=0.8)
    
    ax_phase.plot(points[0][-1], points[1][-1], 'ko', markersize=12, 
                 label='Fim', alpha=0.8)
    
    # Adicionar seta de direção
    mid = len(points[0]) // 2
    ax_phase.annotate('', xy=(points[0][mid+2], points[1][mid+2]),
                     xytext=(points[0][mid], points[1][mid]),
                     arrowprops=dict(arrowstyle='->', color='black', lw=2))
    
    ax_phase.set_xlabel('Suscetíveis', fontsize=11)
    ax_phase.set_ylabel('Infectados', fontsize=11)
    ax_phase.set_title('Espaço de Fase (S-I)', fontsize=13, fontweight='bold')
    ax_phase.legend(fontsize=10)
    ax_phase.grid(True, alpha=0.3, linestyle='--')
    
    # Título geral
    fig.suptitle('Análise Completa de Propagação de Epidemias Digitais\n'
                'Modelo de Autômato Celular SIR em Rede Social',
                fontsize=16, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    plt.savefig('parameter_analysis.png', dpi=200, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print("✅ Análise de parâmetros salva como 'parameter_analysis.png'")
    plt.show()

def compare_neighborhoods():
    """Compara vizinhanças Moore vs von Neumann com detalhes"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    neighborhoods = ['moore', 'von_neumann']
    titles = ['Vizinhança de Moore (8 conexões)', 'Vizinhança de von Neumann (4 conexões)']
    colors = ['#e74c3c', '#3498db']
    
    for idx, (neigh, title) in enumerate(zip(neighborhoods, titles)):
        ca = DigitalEpidemicCA(
            grid_size=50, 
            beta=0.3, 
            gamma=0.1, 
            neighborhood=neigh,
            seed=42
        )
        
        for _ in range(200):
            ca.update()
            if ca.history['infected'][-1] == 0:
                break
        
        # Curva epidêmica completa
        axes[idx].plot(ca.history['time'], ca.history['susceptible'], 
                      color='#2ecc71', label='Suscetíveis', linewidth=2, alpha=0.7)
        axes[idx].plot(ca.history['time'], ca.history['infected'], 
                      color=colors[idx], label='Infectados', linewidth=3)
        axes[idx].plot(ca.history['time'], ca.history['recovered'], 
                      color='#f39c12', label='Recuperados', linewidth=2, alpha=0.7)
        
        # Preencher área de infectados
        axes[idx].fill_between(ca.history['time'], 0, ca.history['infected'], 
                               color=colors[idx], alpha=0.2)
        
        axes[idx].set_xlabel('Passo Temporal', fontsize=12)
        axes[idx].set_ylabel('População', fontsize=12)
        axes[idx].set_title(title, fontsize=14, fontweight='bold')
        axes[idx].legend(fontsize=10)
        axes[idx].grid(True, alpha=0.3, linestyle='--')
        
        # Adicionar linha vertical no pico
        peak_idx = ca.history['infected'].index(max(ca.history['infected']))
        axes[idx].axvline(x=ca.history['time'][peak_idx], color='gray', 
                         linestyle=':', alpha=0.5)
        
        # Calcular e exibir métricas
        peak = max(ca.history['infected'])
        peak_time = ca.history['time'][peak_idx]
        attack = (ca.history['recovered'][-1] + ca.history['infected'][-1]) / 2500 * 100
        duration = len(ca.history['time'])
        
        metrics_text = (
            f'📊 Métricas:\n'
            f'• Pico: {peak} infectados ({peak/2500*100:.1f}%)\n'
            f'• Tempo do pico: passo {peak_time}\n'
            f'• Taxa de ataque: {attack:.1f}%\n'
            f'• Duração: {duration} passos'
        )
        
        axes[idx].text(0.02, 0.98, metrics_text, transform=axes[idx].transAxes,
                      fontsize=10, verticalalignment='top',
                      bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    plt.suptitle('Comparação do Impacto da Topologia de Rede na Propagação Digital',
                fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('neighborhood_comparison.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("✅ Comparação de vizinhanças salva como 'neighborhood_comparison.png'")
    plt.show()

def create_publication_plots():
    """Cria visualizações da evolução espacial prontas para publicação"""
    ca = DigitalEpidemicCA(
        grid_size=50, 
        beta=0.4, 
        gamma=0.1, 
        neighborhood='moore',
        initial_infected=0.05,
        seed=42
    )
    
    # Capturar estados em momentos chave
    snapshots = []
    times = [0, 5, 10, 20, 50, 100]
    
    for t in range(101):
        if t in times:
            snapshots.append((t, ca.grid.copy()))
        if t < 100:
            ca.update()
    
    # Criar figura com snapshots
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    
    for idx, (ax, (t, grid)) in enumerate(zip(axes.flatten(), snapshots)):
        cmap = ListedColormap(['#ecf0f1', '#e74c3c', '#2ecc71'])
        ax.imshow(grid, cmap=cmap, interpolation='nearest', vmin=0, vmax=2)
        
        # Adicionar borda
        for spine in ax.spines.values():
            spine.set_edgecolor('black')
            spine.set_linewidth(1)
        
        # Contar estados
        n_s = np.sum(grid == 0)
        n_i = np.sum(grid == 1)
        n_r = np.sum(grid == 2)
        
        ax.set_title(f'Passo {t}\nS={n_s} | I={n_i} | R={n_r}', 
                    fontsize=12, fontweight='bold')
        ax.set_xlabel('X', fontsize=10)
        ax.set_ylabel('Y', fontsize=10)
    
    # Adicionar legenda
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#ecf0f1', edgecolor='black', label='Suscetível'),
        Patch(facecolor='#e74c3c', label='Infectado'),
        Patch(facecolor='#2ecc71', label='Recuperado')
    ]
    fig.legend(handles=legend_elements, loc='upper right', 
              bbox_to_anchor=(1.12, 0.92), fontsize=12, framealpha=0.9)
    
    plt.suptitle('Evolução Espacial da Epidemia Digital\n'
                '(β=0.4, γ=0.1, Rede com 2.500 nós)',
                fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('spatial_evolution.png', dpi=200, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("✅ Evolução espacial salva como 'spatial_evolution.png'")
    plt.show()

if __name__ == "__main__":
    print("="*60)
    print("🔬 Análise Avançada de Epidemias Digitais")
    print("   Modelo de Autômato Celular para Redes Sociais")
    print("="*60)
    
    print("\n1️⃣  Executando varredura de parâmetros (48 simulações)...")
    print("   Isto pode levar alguns segundos...")
    run_parameter_sweep()
    
    print("\n2️⃣  Comparando tipos de vizinhança...")
    compare_neighborhoods()
    
    print("\n3️⃣  Criando visualizações espaciais para publicação...")
    create_publication_plots()
    
    print("\n" + "="*60)
    print("✅ Todas as análises completas com sucesso!")
    print("="*60)
    print("\n📁 Arquivos gerados:")
    print("  1. parameter_analysis.png - Dashboard completo (6 gráficos)")
    print("  2. neighborhood_comparison.png - Comparação de topologias")
    print("  3. spatial_evolution.png - Evolução espacial temporal")
    print("\n💡 Dica: Use estas imagens no seu artigo!")
    print("="*60)