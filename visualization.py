import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx
import numpy as np
import os

class NetworkVisualizer:
    def __init__(self):
        self.animation_frames = []
    
    def create_packet_vector(self, ax, x, y):
        """Create a vector packet representation"""
        packet_body = patches.Rectangle((x-0.03, y-0.02), 0.06, 0.04, 
                                      facecolor='red', edgecolor='darkred', linewidth=2)
        ax.add_patch(packet_body)
        
        packet_header = patches.Rectangle((x-0.025, y+0.01), 0.05, 0.015, 
                                        facecolor='darkred', edgecolor='black', linewidth=1)
        ax.add_patch(packet_header)
        
        for i in range(3):
            bit_x = x - 0.02 + i * 0.02
            ax.plot([bit_x, bit_x], [y-0.015, y+0.005], 'white', linewidth=1)
        
        return [packet_body, packet_header]
    
    def draw_network(self, simulator, fig, ax):
        """Draw the complete network visualization"""
        pos = nx.spring_layout(simulator.graph, seed=42)
        
        # Draw router vectors
        for node in simulator.graph.nodes:
            x, y = pos[node]
            color = 'lightgreen' if node in simulator.packet_path else 'lightblue'
            
            # Router body (rectangle)
            router_body = patches.Rectangle((x-0.08, y-0.05), 0.16, 0.1, 
                                          facecolor=color, edgecolor='black', linewidth=2)
            ax.add_patch(router_body)
            
            # Antenna lines
            ax.plot([x-0.04, x+0.04], [y+0.06, y+0.06], 'k-', linewidth=2)
            ax.plot([x-0.02, x+0.02], [y+0.08, y+0.08], 'k-', linewidth=1)
            
            # LED indicators
            ax.scatter([x-0.05, x, x+0.05], [y, y, y], c=['red', 'green', 'blue'], s=20)
        
        # Draw animated packet
        if simulator.animating and simulator.packet_path and len(simulator.packet_path) > 1:
            path_idx = int(simulator.packet_position)
            if path_idx < len(simulator.packet_path) - 1:
                start_node = simulator.packet_path[path_idx]
                end_node = simulator.packet_path[path_idx + 1]
                
                start_pos = pos[start_node]
                end_pos = pos[end_node]
                
                t = simulator.packet_position - path_idx
                packet_x = start_pos[0] + t * (end_pos[0] - start_pos[0])
                packet_y = start_pos[1] + t * (end_pos[1] - start_pos[1])
                
                self.create_packet_vector(ax, packet_x, packet_y)
                
                # Add packet trail
                trail_length = min(5, len(simulator.packet_path))
                for i in range(1, trail_length):
                    if simulator.packet_position - i * 0.1 >= 0:
                        trail_idx = int(simulator.packet_position - i * 0.1)
                        if trail_idx < len(simulator.packet_path) - 1:
                            trail_t = (simulator.packet_position - i * 0.1) - trail_idx
                            trail_x = pos[simulator.packet_path[trail_idx]][0] + trail_t * (pos[simulator.packet_path[trail_idx + 1]][0] - pos[simulator.packet_path[trail_idx]][0])
                            trail_y = pos[simulator.packet_path[trail_idx]][1] + trail_t * (pos[simulator.packet_path[trail_idx + 1]][1] - pos[simulator.packet_path[trail_idx]][1])
                            ax.scatter(trail_x, trail_y, c='orange', s=20, alpha=0.7 - i*0.1, zorder=4)
            
            if simulator.animating:
                self.save_animation_frame(fig)
        
        # Draw edges
        edge_colors = []
        edge_styles = []
        for u, v in simulator.graph.edges:
            edge_data = simulator.graph[u][v]
            if edge_data['status'] == 'failed':
                edge_colors.append('red')
                edge_styles.append('--')
            elif edge_data['congestion'] > 50:
                edge_colors.append('orange')
                edge_styles.append('-')
            else:
                edge_colors.append('gray')
                edge_styles.append('-')
        
        nx.draw_networkx_edges(simulator.graph, pos, edge_color=edge_colors, 
                             style=edge_styles, ax=ax)
        
        # Draw labels
        nx.draw_networkx_labels(simulator.graph, pos, ax=ax, font_size=10, font_weight='bold')
        
        # Draw edge labels
        edge_labels = {}
        for u, v in simulator.graph.edges:
            edge_data = simulator.graph[u][v]
            label = f"{edge_data['latency']}ms"
            if edge_data['congestion'] > 0:
                label += f"\n{edge_data['congestion']}%"
            edge_labels[(u, v)] = label
        
        nx.draw_networkx_edge_labels(simulator.graph, pos, edge_labels, 
                                   font_size=8, ax=ax)
        
        ax.set_title("Network Topology")
        ax.axis('off')
        
        return pos
    
    def save_animation_frame(self, fig):
        """Save current frame for FFmpeg animation"""
        if not os.path.exists('frames'):
            os.makedirs('frames')
        
        frame_path = f'frames/frame_{len(self.animation_frames):04d}.png'
        fig.savefig(frame_path, dpi=100, bbox_inches='tight')
        self.animation_frames.append(frame_path)
    
    def generate_manual_frames(self, simulator):
        """Generate frames for manual video creation"""
        if not simulator.packet_path:
            return []
        
        if not os.path.exists('frames'):
            os.makedirs('frames')
        
        pos = nx.spring_layout(simulator.graph, seed=42)
        frames = []
        
        for frame_num in range(20):
            fig_temp, ax_temp = plt.subplots(figsize=(8, 6))
            
            # Draw router vectors
            for node in simulator.graph.nodes:
                x, y = pos[node]
                color = 'lightgreen' if node in simulator.packet_path else 'lightblue'
                
                # Router body
                router_body = patches.Rectangle((x-0.06, y-0.04), 0.12, 0.08, 
                                              facecolor=color, edgecolor='black', linewidth=1)
                ax_temp.add_patch(router_body)
                
                # Antenna
                ax_temp.plot([x-0.03, x+0.03], [y+0.05, y+0.05], 'k-', linewidth=1)
                
                # LED
                ax_temp.scatter(x, y, c='green', s=15)
            
            # Draw packet at different positions
            if len(simulator.packet_path) > 1:
                progress = frame_num / 19.0 * (len(simulator.packet_path) - 1)
                path_idx = int(progress)
                if path_idx < len(simulator.packet_path) - 1:
                    t = progress - path_idx
                    start_pos = pos[simulator.packet_path[path_idx]]
                    end_pos = pos[simulator.packet_path[path_idx + 1]]
                    packet_x = start_pos[0] + t * (end_pos[0] - start_pos[0])
                    packet_y = start_pos[1] + t * (end_pos[1] - start_pos[1])
                    self.create_packet_vector(ax_temp, packet_x, packet_y)
            
            nx.draw_networkx_edges(simulator.graph, pos, ax=ax_temp, edge_color='gray')
            ax_temp.set_title(f"Packet Simulation - Frame {frame_num+1}")
            ax_temp.axis('off')
            
            frame_path = f'frames/manual_{frame_num:04d}.png'
            fig_temp.savefig(frame_path, dpi=100, bbox_inches='tight')
            frames.append(frame_path)
            plt.close(fig_temp)
        
        return frames