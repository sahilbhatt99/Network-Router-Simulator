import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx
import numpy as np
import os
from PIL import Image
import io
import warnings

# Suppress font warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

class GifGenerator:
    def __init__(self):
        self.frames = []
    
    def create_packet_gif(self, simulator, duration=2.0, fps=10):
        """Generate animated GIF for packet transfer"""
        if not simulator.packet_path or len(simulator.packet_path) < 2:
            return None
        
        self.frames = []
        total_frames = int(duration * fps)
        pos = nx.spring_layout(simulator.graph, seed=42)
        
        for frame_num in range(total_frames):
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Calculate packet position
            progress = frame_num / (total_frames - 1) * (len(simulator.packet_path) - 1)
            path_idx = int(progress)
            t = progress - path_idx
            
            # Draw routers
            for node in simulator.graph.nodes:
                x, y = pos[node]
                color = 'lightgreen' if node in simulator.packet_path else 'lightblue'
                
                router_body = patches.Rectangle((x-0.06, y-0.04), 0.12, 0.08, 
                                              facecolor=color, edgecolor='black', linewidth=1)
                ax.add_patch(router_body)
                
                # Antenna
                ax.plot([x-0.03, x+0.03], [y+0.05, y+0.05], 'k-', linewidth=1)
                ax.scatter(x, y, c='green', s=15)
            
            # Draw edges
            for u, v in simulator.graph.edges:
                edge_data = simulator.graph[u][v]
                color = 'red' if edge_data['status'] == 'failed' else 'orange' if edge_data['congestion'] > 50 else 'gray'
                style = '--' if edge_data['status'] == 'failed' else '-'
                nx.draw_networkx_edges(simulator.graph, pos, [(u, v)], edge_color=color, style=style, ax=ax)
            
            # Draw packet
            if path_idx < len(simulator.packet_path) - 1:
                start_pos = pos[simulator.packet_path[path_idx]]
                end_pos = pos[simulator.packet_path[path_idx + 1]]
                packet_x = start_pos[0] + t * (end_pos[0] - start_pos[0])
                packet_y = start_pos[1] + t * (end_pos[1] - start_pos[1])
                
                # Packet body
                packet_body = patches.Rectangle((packet_x-0.02, packet_y-0.015), 0.04, 0.03, 
                                              facecolor='red', edgecolor='darkred', linewidth=1)
                ax.add_patch(packet_body)
                
                # Trail effect
                for i in range(1, min(5, frame_num + 1)):
                    trail_progress = max(0, progress - i * 0.3)
                    trail_idx = int(trail_progress)
                    if trail_idx < len(simulator.packet_path) - 1:
                        trail_t = trail_progress - trail_idx
                        trail_x = pos[simulator.packet_path[trail_idx]][0] + trail_t * (pos[simulator.packet_path[trail_idx + 1]][0] - pos[simulator.packet_path[trail_idx]][0])
                        trail_y = pos[simulator.packet_path[trail_idx]][1] + trail_t * (pos[simulator.packet_path[trail_idx + 1]][1] - pos[simulator.packet_path[trail_idx]][1])
                        ax.scatter(trail_x, trail_y, c='orange', s=10, alpha=0.7 - i*0.1)
            
            # Labels
            nx.draw_networkx_labels(simulator.graph, pos, ax=ax, font_size=8)
            
            # Add packet stats text
            stats_text = f"Packet ID: {simulator.packet_stats.get('packet_id', 'N/A')}\n"
            stats_text += f"Packets: {simulator.packet_stats.get('num_packets', 1)} x {simulator.packet_stats.get('packet_size', 64)}KB\n"
            stats_text += f"Hops: {simulator.packet_stats.get('hops', 0)} | Latency: {simulator.packet_stats.get('total_latency', 0):.1f}ms"
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=9, 
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            ax.set_title(f"Packet Transfer Animation - Frame {frame_num+1}/{total_frames}")
            ax.axis('off')
            
            # Save frame to memory
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=80, bbox_inches='tight')
            buf.seek(0)
            self.frames.append(Image.open(buf))
            plt.close(fig)
        
        return self.save_gif()
    
    def save_gif(self, filename='packet_animation.gif'):
        """Save frames as animated GIF"""
        if not self.frames:
            return None
        
        self.frames[0].save(
            filename,
            save_all=True,
            append_images=self.frames[1:],
            duration=100,  # 100ms per frame = 10fps
            loop=0
        )
        return filename