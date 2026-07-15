import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
import argparse
from datetime import datetime
import os


class DigitalEpidemicCA:
    """
    Cellular Automaton for Digital Epidemic Propagation
    
    States:
    0 = Susceptible (S)
    1 = Infected (I)
    2 = Recovered (R)
    """
    
    def __init__(self, grid_size=100, beta=0.3, gamma=0.1, 
                 neighborhood='moore', initial_infected=0.05,
                 seed=None):
        """
        Initialize the Digital Epidemic CA model.
        
        Parameters:
        -----------
        grid_size : int
            Size of the grid (grid_size x grid_size)
        beta : float
            Transmission rate (0-1)
        gamma : float
            Recovery rate (0-1)
        neighborhood : str
            'moore' (8 neighbors) or 'von_neumann' (4 neighbors)
        initial_infected : float
            Fraction of initially infected cells
        seed : int or None
            Random seed for reproducibility
        """
        self.grid_size = grid_size
        self.beta = beta
        self.gamma = gamma
        self.neighborhood = neighborhood
        self.initial_infected = initial_infected
        
        if seed is not None:
            np.random.seed(seed)
        
        # Initialize grid
        self.grid = np.zeros((grid_size, grid_size), dtype=int)
        self.initialize_infection()
        
        # Tracking variables
        self.time_step = 0
        self.history = {
            'susceptible': [],
            'infected': [],
            'recovered': [],
            'time': []
        }
        
        # Record initial state
        self.record_state()
    
    def initialize_infection(self):
        """Initialize the grid with random infected cells."""
        # Randomly infect initial cells
        infection_mask = np.random.random((self.grid_size, self.grid_size)) < self.initial_infected
        self.grid[infection_mask] = 1
        
        print(f"Initialized {self.grid_size}x{self.grid_size} grid")
        print(f"Initially infected: {np.sum(self.grid == 1)} cells")
        print(f"Parameters: β={self.beta}, γ={self.gamma}, neighborhood={self.neighborhood}")
    
    def get_neighbors(self, i, j):
        """
        Get the states of neighboring cells.
        Periodic boundary conditions.
        """
        if self.neighborhood == 'moore':
            # 8-neighbor Moore neighborhood
            neighbors = []
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    ni = (i + di) % self.grid_size
                    nj = (j + dj) % self.grid_size
                    neighbors.append(self.grid[ni, nj])
            return np.array(neighbors)
        
        elif self.neighborhood == 'von_neumann':
            # 4-neighbor von Neumann neighborhood
            neighbors = []
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ni = (i + di) % self.grid_size
                nj = (j + dj) % self.grid_size
                neighbors.append(self.grid[ni, nj])
            return np.array(neighbors)
    
    def count_infected_neighbors(self, i, j):
        """Count number of infected neighbors for cell (i,j)."""
        neighbors = self.get_neighbors(i, j)
        return np.sum(neighbors == 1)
    
    def update(self):
        """Perform one time step update of the cellular automaton."""
        new_grid = self.grid.copy()
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i, j] == 0:  # Susceptible
                    n_neighbors = 8 if self.neighborhood == 'moore' else 4
                    n_infected = self.count_infected_neighbors(i, j)
                    
                    # Probability of infection proportional to infected neighbors
                    infection_prob = self.beta * (n_infected / n_neighbors)
                    
                    if np.random.random() < infection_prob:
                        new_grid[i, j] = 1  # Become infected
                
                elif self.grid[i, j] == 1:  # Infected
                    # Probability of recovery
                    if np.random.random() < self.gamma:
                        new_grid[i, j] = 2  # Recover with immunity
        
        self.grid = new_grid
        self.time_step += 1
        self.record_state()
    
    def record_state(self):
        """Record current population statistics."""
        self.history['susceptible'].append(np.sum(self.grid == 0))
        self.history['infected'].append(np.sum(self.grid == 1))
        self.history['recovered'].append(np.sum(self.grid == 2))
        self.history['time'].append(self.time_step)
    
    def run_simulation(self, max_steps=200, verbose=True):
        """Run the simulation for a specified number of steps."""
        for step in range(max_steps):
            self.update()
            
            if verbose and step % 50 == 0:
                print(f"Step {self.time_step}: S={self.history['susceptible'][-1]}, "
                      f"I={self.history['infected'][-1]}, "
                      f"R={self.history['recovered'][-1]}")
            
            # Stop if no infected cells remain
            if self.history['infected'][-1] == 0:
                if verbose:
                    print(f"Epidemic ended at step {self.time_step}")
                break
    
    def visualize_grid(self, ax=None, title=None):
        """Visualize the current grid state."""
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))
        
        # Custom colormap: white=S, red=I, green=R
        cmap = ListedColormap(['white', 'red', 'green'])
        
        ax.imshow(self.grid, cmap=cmap, interpolation='nearest', vmin=0, vmax=2)
        ax.set_xlabel('X Position')
        ax.set_ylabel('Y Position')
        
        if title:
            ax.set_title(title)
        else:
            ax.set_title(f'Digital Epidemic Propagation (Step {self.time_step})')
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='white', edgecolor='black', label='Susceptible'),
            Patch(facecolor='red', label='Infected'),
            Patch(facecolor='green', label='Recovered')
        ]
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
        
        return ax
    
    def plot_epidemic_curve(self, save=True):
        """Plot the SIR epidemic curve over time."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Left plot: SIR populations
        ax1.plot(self.history['time'], self.history['susceptible'], 
                'b-', label='Susceptible', linewidth=2)
        ax1.plot(self.history['time'], self.history['infected'], 
                'r-', label='Infected', linewidth=2)
        ax1.plot(self.history['time'], self.history['recovered'], 
                'g-', label='Recovered', linewidth=2)
        ax1.set_xlabel('Time Step')
        ax1.set_ylabel('Population')
        ax1.set_title(f'Digital Epidemic Curve (β={self.beta}, γ={self.gamma})')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Right plot: Current grid state
        self.visualize_grid(ax2)
        
        plt.tight_layout()
        
        if save:
            plt.savefig('epidemic_results.png', dpi=150, bbox_inches='tight')
            print("Results saved to 'epidemic_results.png'")
        
        plt.show()
    
    def create_animation(self, max_frames=200, interval=100):
        """Create an animation of the epidemic spread."""
        # Reset the simulation
        self.__init__(self.grid_size, self.beta, self.gamma, 
                     self.neighborhood, self.initial_infected)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        cmap = ListedColormap(['white', 'red', 'green'])
        im = ax2.imshow(self.grid, cmap=cmap, interpolation='nearest', 
                       animated=True, vmin=0, vmax=2)
        
        # Initialize lines for epidemic curve
        line_s, = ax1.plot([], [], 'b-', label='Susceptible', linewidth=2)
        line_i, = ax1.plot([], [], 'r-', label='Infected', linewidth=2)
        line_r, = ax1.plot([], [], 'g-', label='Recovered', linewidth=2)
        
        ax1.set_xlim(0, max_frames)
        ax1.set_ylim(0, self.grid_size ** 2)
        ax1.set_xlabel('Time Step')
        ax1.set_ylabel('Population')
        ax1.set_title(f'Digital Epidemic Propagation (β={self.beta}, γ={self.gamma})')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        ax2.set_title('Spatial Distribution')
        
        def update_frame(frame):
            if frame > 0:
                self.update()
            
            im.set_array(self.grid)
            
            times = self.history['time']
            line_s.set_data(times, self.history['susceptible'])
            line_i.set_data(times, self.history['infected'])
            line_r.set_data(times, self.history['recovered'])
            
            return im, line_s, line_i, line_r
        
        anim = animation.FuncAnimation(fig, update_frame, frames=max_frames,
                                     interval=interval, blit=True)
        
        plt.tight_layout()
        plt.show()
        
        return anim


def main():
    """Main function to run the Digital Epidemic CA simulation."""
    parser = argparse.ArgumentParser(
        description='Digital Epidemic Propagation Cellular Automaton'
    )
    
    parser.add_argument('--grid-size', type=int, default=100,
                       help='Size of the grid (default: 100)')
    parser.add_argument('--beta', type=float, default=0.3,
                       help='Transmission rate (default: 0.3)')
    parser.add_argument('--gamma', type=float, default=0.1,
                       help='Recovery rate (default: 0.1)')
    parser.add_argument('--neighborhood', type=str, default='moore',
                       choices=['moore', 'von_neumann'],
                       help='Neighborhood type (default: moore)')
    parser.add_argument('--initial-infected', type=float, default=0.05,
                       help='Fraction of initially infected cells (default: 0.05)')
    parser.add_argument('--steps', type=int, default=200,
                       help='Maximum simulation steps (default: 200)')
    parser.add_argument('--animate', action='store_true',
                       help='Create animation instead of static plots')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility (default: 42)')
    
    args = parser.parse_args()
    
    # Create and run simulation
    print("=" * 60)
    print("Digital Epidemic Propagation - Cellular Automata")
    print("=" * 60)
    
    ca = DigitalEpidemicCA(
        grid_size=args.grid_size,
        beta=args.beta,
        gamma=args.gamma,
        neighborhood=args.neighborhood,
        initial_infected=args.initial_infected,
        seed=args.seed
    )
    
    if args.animate:
        # Create animation
        print("\nCreating animation...")
        ca.create_animation(max_frames=args.steps)
    else:
        # Run simulation and plot results
        print("\nRunning simulation...")
        ca.run_simulation(max_steps=args.steps)
        
        # Calculate statistics
        peak_infected = max(ca.history['infected'])
        peak_step = ca.history['infected'].index(peak_infected)
        total_infected = ca.history['recovered'][-1] + ca.history['infected'][-1]
        
        print("\n" + "=" * 60)
        print("Simulation Results:")
        print("=" * 60)
        print(f"Final state - S: {ca.history['susceptible'][-1]}, "
              f"I: {ca.history['infected'][-1]}, "
              f"R: {ca.history['recovered'][-1]}")
        print(f"Peak infected: {peak_infected} ({peak_infected/ca.grid_size**2:.1%}) at step {peak_step}")
        print(f"Total ever infected: {total_infected} ({total_infected/ca.grid_size**2:.1%})")
        print(f"Attack rate: {total_infected/ca.grid_size**2:.2%}")
        
        # Plot results
        print("\nGenerating plots...")
        ca.plot_epidemic_curve(save=True)
    
    print("\nSimulation completed!")


if __name__ == "__main__":
    main()