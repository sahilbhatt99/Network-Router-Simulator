import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import time
import random
from collections import defaultdict
import heapq
import threading
import numpy as np
import matplotlib.patches as patches
import matplotlib.animation as animation
from datetime import datetime
import subprocess
import os

class NetworkSimulator:
    def __init__(self):
        self.graph = nx.Graph()
        self.simulation_running = False
        self.logs = []
        self.packet_path = []
        self.packet_position = 0
        self.animating = False
        self.packet_stats = {
            'start_time': None,
            'end_time': None,
            'ttl': 64,
            'hops': 0,
            'total_latency': 0,
            'packet_id': None,
            'status': 'idle'
        }
        self.animation_frames = []
        
    def add_router(self, router_id):
        self.graph.add_node(router_id, status='active')
        
    def remove_router(self, router_id):
        if router_id in self.graph.nodes:
            self.graph.remove_node(router_id)
            
    def add_link(self, router1, router2, latency=10, bandwidth=100):
        self.graph.add_edge(router1, router2, 
                          latency=latency, 
                          bandwidth=bandwidth, 
                          status='active',
                          packet_loss=0,
                          congestion=0)
        
    def remove_link(self, router1, router2):
        if self.graph.has_edge(router1, router2):
            self.graph.remove_edge(router1, router2)
            
    def update_link(self, router1, router2, **kwargs):
        if self.graph.has_edge(router1, router2):
            for key, value in kwargs.items():
                self.graph[router1][router2][key] = value
                
    def dijkstra(self, start, end):
        if start not in self.graph.nodes or end not in self.graph.nodes:
            return [], float('inf')
            
        distances = {node: float('inf') for node in self.graph.nodes}
        distances[start] = 0
        previous = {}
        pq = [(0, start)]
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current == end:
                break
                
            if current_dist > distances[current]:
                continue
                
            for neighbor in self.graph.neighbors(current):
                edge_data = self.graph[current][neighbor]
                if edge_data['status'] == 'failed':
                    continue
                    
                weight = edge_data['latency'] * (1 + edge_data['congestion']/100)
                distance = current_dist + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current
                    heapq.heappush(pq, (distance, neighbor))
        
        path = []
        current = end
        while current in previous:
            path.append(current)
            current = previous[current]
        if distances[end] != float('inf'):
            path.append(start)
            path.reverse()
            
        return path, distances[end]
    
    def simulate_packet(self, start, end):
        path, total_cost = self.dijkstra(start, end)
        if path:
            self.packet_path = path
            self.packet_position = 0
            self.animating = True
            
            # Initialize packet stats
            self.packet_stats = {
                'start_time': datetime.now(),
                'end_time': None,
                'ttl': 64,
                'hops': len(path) - 1,
                'total_latency': total_cost,
                'packet_id': f"PKT_{random.randint(1000, 9999)}",
                'status': 'transmitting',
                'source': start,
                'destination': end
            }
            
            log_entry = f"Packet {self.packet_stats['packet_id']} routed from {start} to {end}: {' -> '.join(path)} (Cost: {total_cost:.2f}ms)"
            self.logs.append(log_entry)
            return True
        else:
            log_entry = f"No path found from {start} to {end}"
            self.logs.append(log_entry)
            return False
    
    def animate_packet(self):
        if self.animating and self.packet_path:
            self.packet_position += 0.1
            self.packet_stats['ttl'] = max(0, self.packet_stats['ttl'] - 0.1)
            
            if self.packet_position >= len(self.packet_path) - 1:
                self.animating = False
                self.packet_position = 0
                self.packet_stats['end_time'] = datetime.now()
                self.packet_stats['status'] = 'delivered'
                
                # Calculate actual time taken
                if self.packet_stats['start_time']:
                    time_taken = (self.packet_stats['end_time'] - self.packet_stats['start_time']).total_seconds()
                    self.logs.append(f"Packet {self.packet_stats['packet_id']} delivered in {time_taken:.2f}s")
    
    def generate_random_network(self, num_routers=5):
        self.graph.clear()
        self.packet_path = []
        self.logs = []
        self.packet_stats['status'] = 'idle'
        
        # Add routers
        for i in range(num_routers):
            self.add_router(f"R{i+1}")
        
        # Add random links ensuring connectivity
        routers = list(self.graph.nodes)
        for i in range(1, len(routers)):
            r1 = routers[random.randint(0, i-1)]
            r2 = routers[i]
            latency = random.randint(5, 50)
            bandwidth = random.choice([10, 50, 100, 1000])
            self.add_link(r1, r2, latency, bandwidth)
        
        # Add additional random links
        for _ in range(random.randint(0, num_routers)):
            r1, r2 = random.sample(routers, 2)
            if not self.graph.has_edge(r1, r2):
                latency = random.randint(5, 50)
                bandwidth = random.choice([10, 50, 100, 1000])
                self.add_link(r1, r2, latency, bandwidth)
        
        # Add random congestion and failures
        for u, v in list(self.graph.edges):
            if random.random() < 0.3:
                self.update_link(u, v, congestion=random.randint(20, 80))
            if random.random() < 0.1:
                self.update_link(u, v, status='failed')
    
    def create_packet_vector(self, ax, x, y):
        """Create a vector packet representation"""
        # Packet body (rectangle)
        packet_body = patches.Rectangle((x-0.03, y-0.02), 0.06, 0.04, 
                                      facecolor='red', edgecolor='darkred', linewidth=2)
        ax.add_patch(packet_body)
        
        # Packet header (smaller rectangle on top)
        packet_header = patches.Rectangle((x-0.025, y+0.01), 0.05, 0.015, 
                                        facecolor='darkred', edgecolor='black', linewidth=1)
        ax.add_patch(packet_header)
        
        # Data bits representation
        for i in range(3):
            bit_x = x - 0.02 + i * 0.02
            ax.plot([bit_x, bit_x], [y-0.015, y+0.005], 'white', linewidth=1)
        
        return [packet_body, packet_header]
    
    def save_animation_frame(self, fig):
        """Save current frame for FFmpeg animation"""
        if not os.path.exists('frames'):
            os.makedirs('frames')
        
        frame_path = f'frames/frame_{len(self.animation_frames):04d}.png'
        fig.savefig(frame_path, dpi=100, bbox_inches='tight')
        self.animation_frames.append(frame_path)
    
    def create_video_with_ffmpeg(self):
        """Create video using FFmpeg"""
        if len(self.animation_frames) < 2:
            return None
            
        try:
            output_path = 'packet_simulation.mp4'
            cmd = [
                'ffmpeg', '-y', '-framerate', '5',
                '-i', 'frames/frame_%04d.png',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                '-vf', 'scale=800:600',
                output_path
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except Exception as e:
            st.error(f"FFmpeg error: {e}")
            return None
    
    def cleanup_frames(self):
        """Clean up animation frames"""
        for frame in self.animation_frames:
            if os.path.exists(frame):
                os.remove(frame)
        if os.path.exists('frames') and not os.listdir('frames'):
            os.rmdir('frames')
        self.animation_frames = []

def main():
    st.set_page_config(page_title="Network Simulator", layout="wide")
    st.title("🌐 Network Router Simulator")
    
    if 'simulator' not in st.session_state:
        st.session_state.simulator = NetworkSimulator()
    
    sim = st.session_state.simulator
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("Controls")
        
        # Quick Setup
        st.subheader("Quick Setup")
        col_setup1, col_setup2 = st.columns(2)
        with col_setup1:
            num_routers = st.selectbox("Routers", [3, 5, 8, 10], index=1)
        with col_setup2:
            if st.button("🎲 Generate Random"):
                sim.generate_random_network(num_routers)
                st.success(f"Generated random network with {num_routers} routers")
                st.rerun()
        
        # Router Management
        st.subheader("Router Management")
        with st.expander("Add Router"):
            new_router = st.text_input("Router ID", key="new_router")
            if st.button("Add Router"):
                if new_router and new_router not in sim.graph.nodes:
                    sim.add_router(new_router)
                    st.success(f"Router {new_router} added")
                    st.rerun()
        
        with st.expander("Remove Router"):
            if sim.graph.nodes:
                router_to_remove = st.selectbox("Select Router", list(sim.graph.nodes), key="remove_router")
                if st.button("Remove Router"):
                    sim.remove_router(router_to_remove)
                    st.success(f"Router {router_to_remove} removed")
                    st.rerun()
        
        # Link Management
        st.subheader("Link Management")
        if len(sim.graph.nodes) >= 2:
            with st.expander("Add Link"):
                routers = list(sim.graph.nodes)
                router1 = st.selectbox("Router 1", routers, key="link_r1")
                router2 = st.selectbox("Router 2", routers, key="link_r2")
                latency = st.number_input("Latency (ms)", min_value=1, value=10)
                bandwidth = st.number_input("Bandwidth (Mbps)", min_value=1, value=100)
                
                if st.button("Add Link") and router1 != router2:
                    sim.add_link(router1, router2, latency, bandwidth)
                    st.success(f"Link added: {router1} ↔ {router2}")
                    st.rerun()
            
            # Link Configuration
            if sim.graph.edges:
                with st.expander("Configure Links"):
                    edges = [(u, v) for u, v in sim.graph.edges]
                    selected_edge = st.selectbox("Select Link", 
                                               [f"{u} ↔ {v}" for u, v in edges])
                    
                    if selected_edge:
                        u, v = selected_edge.split(" ↔ ")
                        edge_data = sim.graph[u][v]
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            new_latency = st.number_input("Latency", value=edge_data['latency'])
                            packet_loss = st.slider("Packet Loss %", 0, 100, edge_data['packet_loss'])
                        with col_b:
                            congestion = st.slider("Congestion %", 0, 100, edge_data['congestion'])
                            status = st.selectbox("Status", ['active', 'failed'], 
                                                index=0 if edge_data['status'] == 'active' else 1)
                        
                        if st.button("Update Link"):
                            sim.update_link(u, v, latency=new_latency, 
                                          packet_loss=packet_loss, 
                                          congestion=congestion, 
                                          status=status)
                            st.success("Link updated")
                            st.rerun()
        
        # Simulation Controls
        st.subheader("Simulation")
        if len(sim.graph.nodes) >= 2:
            routers = list(sim.graph.nodes)
            start_router = st.selectbox("Start Router", routers, key="sim_start")
            end_router = st.selectbox("End Router", routers, key="sim_end")
            
            col_sim1, col_sim2 = st.columns(2)
            with col_sim1:
                if st.button("Send Packet"):
                    if start_router != end_router:
                        sim.simulate_packet(start_router, end_router)
                        st.rerun()
            
            # Auto-refresh for animation
            if sim.animating:
                time.sleep(0.1)
                sim.animate_packet()
                st.rerun()
            
            with col_sim2:
                if st.button("Clear Logs"):
                    sim.logs.clear()
                    sim.packet_path.clear()
                    sim.packet_stats['status'] = 'idle'
                    st.rerun()
        
        # Manual video generation
        if st.button("🎬 Generate Video") and sim.packet_path:
            with st.spinner("Creating simulation video..."):
                # Create frames for current packet path
                if not os.path.exists('frames'):
                    os.makedirs('frames')
                
                pos = nx.spring_layout(sim.graph, seed=42)
                for frame_num in range(20):
                    fig_temp, ax_temp = plt.subplots(figsize=(8, 6))
                    
                    # Draw network
                    for node in sim.graph.nodes:
                        x, y = pos[node]
                        color = 'lightgreen' if node in sim.packet_path else 'lightblue'
                        circle = plt.Circle((x, y), 0.1, color=color, alpha=0.8)
                        ax_temp.add_patch(circle)
                        ax_temp.text(x, y, '🌐', ha='center', va='center', fontsize=20)
                    
                    # Draw packet at different positions
                    if len(sim.packet_path) > 1:
                        progress = frame_num / 19.0 * (len(sim.packet_path) - 1)
                        path_idx = int(progress)
                        if path_idx < len(sim.packet_path) - 1:
                            t = progress - path_idx
                            start_pos = pos[sim.packet_path[path_idx]]
                            end_pos = pos[sim.packet_path[path_idx + 1]]
                            packet_x = start_pos[0] + t * (end_pos[0] - start_pos[0])
                            packet_y = start_pos[1] + t * (end_pos[1] - start_pos[1])
                            sim.create_packet_vector(ax_temp, packet_x, packet_y)
                    
                    nx.draw_networkx_edges(sim.graph, pos, ax=ax_temp, edge_color='gray')
                    ax_temp.set_title(f"Packet Simulation - Frame {frame_num+1}")
                    ax_temp.axis('off')
                    
                    # Save frame
                    frame_path = f'frames/manual_{frame_num:04d}.png'
                    fig_temp.savefig(frame_path, dpi=100, bbox_inches='tight')
                    plt.close(fig_temp)
                
                # Create video
                try:
                    cmd = [
                        'ffmpeg', '-y', '-framerate', '5',
                        '-i', 'frames/manual_%04d.png',
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                        'manual_simulation.mp4'
                    ]
                    subprocess.run(cmd, check=True, capture_output=True)
                    st.success("Video generated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Video generation failed: {e}")
    
    with col2:
        # Stats tracker in top right
        if sim.packet_stats['status'] != 'idle':
            with st.container():
                st.markdown("""
                <div style="position: fixed; top: 10px; right: 10px; background: rgba(255,255,255,0.9); 
                           padding: 10px; border-radius: 5px; border: 2px solid #333; z-index: 1000;">
                <h4>📊 Packet Stats</h4>
                <p><strong>ID:</strong> {}</p>
                <p><strong>Status:</strong> {}</p>
                <p><strong>TTL:</strong> {:.0f}</p>
                <p><strong>Hops:</strong> {}</p>
                <p><strong>Latency:</strong> {:.2f}ms</p>
                <p><strong>Route:</strong> {} → {}</p>
                </div>
                """.format(
                    sim.packet_stats.get('packet_id', 'N/A'),
                    sim.packet_stats.get('status', 'idle'),
                    sim.packet_stats.get('ttl', 0),
                    sim.packet_stats.get('hops', 0),
                    sim.packet_stats.get('total_latency', 0),
                    sim.packet_stats.get('source', ''),
                    sim.packet_stats.get('destination', '')
                ), unsafe_allow_html=True)
        
        st.header("Network Visualization")
        
        if sim.graph.nodes:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Position nodes
            pos = nx.spring_layout(sim.graph, seed=42)
            
            # Draw router icons
            for node in sim.graph.nodes:
                x, y = pos[node]
                if node in sim.packet_path:
                    icon = '🖥️'  # Server icon for active path
                    color = 'lightgreen'
                else:
                    icon = '🌐'  # Router icon for normal state
                    color = 'lightblue'
                
                # Draw background circle
                circle = plt.Circle((x, y), 0.1, color=color, alpha=0.8, zorder=2)
                ax.add_patch(circle)
                
                # Draw router/server icon
                ax.text(x, y, icon, ha='center', va='center', fontsize=24, zorder=3)
            
            # Draw animated packet with vector representation
            if sim.animating and sim.packet_path and len(sim.packet_path) > 1:
                path_idx = int(sim.packet_position)
                if path_idx < len(sim.packet_path) - 1:
                    # Calculate packet position between nodes
                    start_node = sim.packet_path[path_idx]
                    end_node = sim.packet_path[path_idx + 1]
                    
                    start_pos = pos[start_node]
                    end_pos = pos[end_node]
                    
                    # Linear interpolation for packet position
                    t = sim.packet_position - path_idx
                    packet_x = start_pos[0] + t * (end_pos[0] - start_pos[0])
                    packet_y = start_pos[1] + t * (end_pos[1] - start_pos[1])
                    
                    # Draw vector packet
                    sim.create_packet_vector(ax, packet_x, packet_y)
                    
                    # Add packet trail
                    trail_length = min(5, len(sim.packet_path))
                    for i in range(1, trail_length):
                        if sim.packet_position - i * 0.1 >= 0:
                            trail_idx = int(sim.packet_position - i * 0.1)
                            if trail_idx < len(sim.packet_path) - 1:
                                trail_t = (sim.packet_position - i * 0.1) - trail_idx
                                trail_x = pos[sim.packet_path[trail_idx]][0] + trail_t * (pos[sim.packet_path[trail_idx + 1]][0] - pos[sim.packet_path[trail_idx]][0])
                                trail_y = pos[sim.packet_path[trail_idx]][1] + trail_t * (pos[sim.packet_path[trail_idx + 1]][1] - pos[sim.packet_path[trail_idx]][1])
                                ax.scatter(trail_x, trail_y, c='orange', s=20, alpha=0.7 - i*0.1, zorder=4)
                
                # Save frame for FFmpeg
                sim.save_animation_frame(fig)
            
            # Draw edges
            edge_colors = []
            edge_styles = []
            for u, v in sim.graph.edges:
                edge_data = sim.graph[u][v]
                if edge_data['status'] == 'failed':
                    edge_colors.append('red')
                    edge_styles.append('--')
                elif edge_data['congestion'] > 50:
                    edge_colors.append('orange')
                    edge_styles.append('-')
                else:
                    edge_colors.append('gray')
                    edge_styles.append('-')
            
            nx.draw_networkx_edges(sim.graph, pos, edge_color=edge_colors, 
                                 style=edge_styles, ax=ax)
            
            # Draw labels below routers
            for node in sim.graph.nodes:
                x, y = pos[node]
                ax.text(x, y-0.15, node, ha='center', va='center', fontsize=10, 
                       fontweight='bold', zorder=3)
            
            # Draw edge labels
            edge_labels = {}
            for u, v in sim.graph.edges:
                edge_data = sim.graph[u][v]
                label = f"{edge_data['latency']}ms"
                if edge_data['congestion'] > 0:
                    label += f"\n{edge_data['congestion']}%"
                edge_labels[(u, v)] = label
            
            nx.draw_networkx_edge_labels(sim.graph, pos, edge_labels, 
                                       font_size=8, ax=ax)
            
            ax.set_title("Network Topology")
            ax.axis('off')
            st.pyplot(fig)
            
            # Generate and display video when animation completes
            if not sim.animating and len(sim.animation_frames) > 5:
                with st.spinner("Generating simulation video..."):
                    video_path = sim.create_video_with_ffmpeg()
                    if video_path and os.path.exists(video_path):
                        st.subheader("📹 Packet Simulation Video")
                        st.video(video_path)
                        sim.cleanup_frames()
            
            # Legend
            st.markdown("""
            **Legend:**
            - 🟢 Green routers: Current packet path
            - 🔵 Blue routers: Active routers  
            - Gray edges: Normal links
            - Orange edges: Congested links (>50%)
            - Red dashed edges: Failed links
            - 🔴 Red vector: Moving data packet
            - 🟠 Orange trail: Packet movement history
            """)
        else:
            st.info("Add routers to start building your network")
        
        # Network Status
        if sim.graph.nodes:
            st.subheader("Network Status")
            
            # Nodes table
            node_data = []
            for node in sim.graph.nodes:
                node_data.append({
                    'Router': node,
                    'Status': sim.graph.nodes[node]['status'],
                    'Connections': len(list(sim.graph.neighbors(node)))
                })
            
            if node_data:
                st.write("**Routers:**")
                st.dataframe(pd.DataFrame(node_data), use_container_width=True)
            
            # Edges table
            if sim.graph.edges:
                edge_data = []
                for u, v in sim.graph.edges:
                    data = sim.graph[u][v]
                    edge_data.append({
                        'Link': f"{u} ↔ {v}",
                        'Latency': f"{data['latency']}ms",
                        'Bandwidth': f"{data['bandwidth']}Mbps",
                        'Congestion': f"{data['congestion']}%",
                        'Packet Loss': f"{data['packet_loss']}%",
                        'Status': data['status']
                    })
                
                st.write("**Links:**")
                st.dataframe(pd.DataFrame(edge_data), use_container_width=True)
        
        # Display generated videos
        for video_file in ['packet_simulation.mp4', 'manual_simulation.mp4']:
            if os.path.exists(video_file):
                st.subheader("📹 Simulation Video")
                st.video(video_file)
                break
        
        # Simulation Logs
        if sim.logs:
            st.subheader("Simulation Logs")
            for i, log in enumerate(reversed(sim.logs[-10:])):  # Show last 10 logs
                st.text(f"{len(sim.logs)-i}: {log}")
        
        # Packet Statistics Summary
        if sim.packet_stats['status'] != 'idle':
            st.subheader("📈 Packet Analytics")
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            
            with col_stat1:
                st.metric("Packet ID", sim.packet_stats.get('packet_id', 'N/A'))
                st.metric("Status", sim.packet_stats.get('status', 'idle'))
            
            with col_stat2:
                st.metric("TTL Remaining", f"{sim.packet_stats.get('ttl', 0):.0f}")
                st.metric("Hops", sim.packet_stats.get('hops', 0))
            
            with col_stat3:
                st.metric("Total Latency", f"{sim.packet_stats.get('total_latency', 0):.2f}ms")
                if sim.packet_stats.get('end_time') and sim.packet_stats.get('start_time'):
                    actual_time = (sim.packet_stats['end_time'] - sim.packet_stats['start_time']).total_seconds()
                    st.metric("Actual Time", f"{actual_time:.2f}s")

if __name__ == "__main__":
    main()