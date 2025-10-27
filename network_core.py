import networkx as nx
import random
import heapq
from datetime import datetime

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
            'status': 'idle',
            'num_packets': 1,
            'packet_size': 64
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
            
        if start == end:
            return [start], 0
            
        distances = {start: 0}
        previous = {}
        visited = set()
        pq = [(0, start)]
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current in visited:
                continue
            visited.add(current)
            
            if current == end:
                break
                
            for neighbor in self.graph.neighbors(current):
                if neighbor in visited:
                    continue
                    
                edge_data = self.graph[current][neighbor]
                if edge_data['status'] == 'failed':
                    continue
                    
                weight = edge_data['latency']
                distance = current_dist + weight
                
                if neighbor not in distances or distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current
                    heapq.heappush(pq, (distance, neighbor))
        
        if end not in distances:
            return [], float('inf')
            
        path = []
        current = end
        while current in previous:
            path.append(current)
            current = previous[current]
        path.append(start)
        path.reverse()
            
        return path, distances[end]
    
    def simulate_packet(self, start, end, num_packets=1, packet_size=64):
        path, total_cost = self.dijkstra(start, end)
        if path:
            self.packet_path = path
            self.packet_position = 0
            self.animating = True
            
            self.packet_stats = {
                'start_time': datetime.now(),
                'end_time': None,
                'ttl': 64,
                'hops': len(path) - 1,
                'total_latency': total_cost,
                'packet_id': f"PKT_{random.randint(1000, 9999)}",
                'status': 'transmitting',
                'source': start,
                'destination': end,
                'num_packets': num_packets,
                'packet_size': packet_size
            }
            
            log_entry = f"{num_packets} packet(s) ({packet_size}KB each) {self.packet_stats['packet_id']} routed from {start} to {end}: {' -> '.join(path)} (Cost: {total_cost:.2f}ms)"
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
                
                if self.packet_stats['start_time']:
                    time_taken = (self.packet_stats['end_time'] - self.packet_stats['start_time']).total_seconds()
                    self.logs.append(f"Packet {self.packet_stats['packet_id']} delivered in {time_taken:.2f}s")
    
    def generate_random_network(self, num_routers=5):
        self.graph.clear()
        self.packet_path = []
        self.logs = []
        self.packet_stats['status'] = 'idle'
        
        for i in range(num_routers):
            self.add_router(f"R{i+1}")
        
        routers = list(self.graph.nodes)
        for i in range(1, len(routers)):
            r1 = routers[random.randint(0, i-1)]
            r2 = routers[i]
            latency = random.randint(5, 50)
            bandwidth = random.choice([10, 50, 100, 1000])
            self.add_link(r1, r2, latency, bandwidth)
        
        for _ in range(random.randint(0, num_routers)):
            r1, r2 = random.sample(routers, 2)
            if not self.graph.has_edge(r1, r2):
                latency = random.randint(5, 50)
                bandwidth = random.choice([10, 50, 100, 1000])
                self.add_link(r1, r2, latency, bandwidth)
        
        for u, v in list(self.graph.edges):
            if random.random() < 0.3:
                self.update_link(u, v, congestion=random.randint(20, 80))
            if random.random() < 0.1:
                self.update_link(u, v, status='failed')