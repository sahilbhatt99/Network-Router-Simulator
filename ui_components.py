import streamlit as st
import pandas as pd

class UIComponents:

    
    @staticmethod
    def render_quick_setup(simulator):
        """Render quick setup controls"""
        st.subheader("Quick Setup")
        col_setup1, col_setup2 = st.columns(2)
        
        with col_setup1:
            num_routers = st.number_input("Routers", min_value=2, max_value=50, value=5)
        
        with col_setup2:
            if st.button("🎲 Generate Random"):
                simulator.generate_random_network(num_routers)
                st.success(f"Generated random network with {num_routers} routers")
                st.rerun()
    
    @staticmethod
    def render_router_management(simulator):
        """Render router management controls"""
        st.subheader("Router Management")
        
        with st.expander("Add Router"):
            new_router = st.text_input("Router ID", key="new_router")
            if st.button("Add Router"):
                if new_router and new_router not in simulator.graph.nodes:
                    simulator.add_router(new_router)
                    st.success(f"Router {new_router} added")
                    st.rerun()
        
        with st.expander("Remove Router"):
            if simulator.graph.nodes:
                router_to_remove = st.selectbox("Select Router", list(simulator.graph.nodes), key="remove_router")
                if st.button("Remove Router"):
                    simulator.remove_router(router_to_remove)
                    st.success(f"Router {router_to_remove} removed")
                    st.rerun()
    
    @staticmethod
    def render_link_management(simulator):
        """Render link management controls"""
        st.subheader("Link Management")
        
        if len(simulator.graph.nodes) >= 2:
            with st.expander("Add Link"):
                routers = list(simulator.graph.nodes)
                router1 = st.selectbox("Router 1", routers, key="link_r1")
                router2 = st.selectbox("Router 2", routers, key="link_r2")
                latency = st.number_input("Latency (ms)", min_value=1, value=10)
                bandwidth = st.number_input("Bandwidth (Mbps)", min_value=1, value=100)
                
                if st.button("Add Link") and router1 != router2:
                    simulator.add_link(router1, router2, latency, bandwidth)
                    st.success(f"Link added: {router1} ↔ {router2}")
                    st.rerun()
            
            if simulator.graph.edges:
                with st.expander("Configure Links"):
                    edges = [(u, v) for u, v in simulator.graph.edges]
                    selected_edge = st.selectbox("Select Link", [f"{u} ↔ {v}" for u, v in edges])
                    
                    if selected_edge:
                        u, v = selected_edge.split(" ↔ ")
                        edge_data = simulator.graph[u][v]
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            new_latency = st.number_input("Latency", value=edge_data['latency'])
                            packet_loss = st.slider("Packet Loss %", 0, 100, edge_data['packet_loss'])
                        with col_b:
                            congestion = st.slider("Congestion %", 0, 100, edge_data['congestion'])
                            status = st.selectbox("Status", ['active', 'failed'], 
                                                index=0 if edge_data['status'] == 'active' else 1)
                        
                        if st.button("Update Link"):
                            simulator.update_link(u, v, latency=new_latency, 
                                              packet_loss=packet_loss, 
                                              congestion=congestion, 
                                              status=status)
                            st.success("Link updated")
                            st.rerun()
    
    @staticmethod
    def render_simulation_controls(simulator):
        """Render simulation controls"""
        st.subheader("Simulation")
        
        if len(simulator.graph.nodes) >= 2:
            routers = list(simulator.graph.nodes)
            start_router = st.selectbox("Start Router", routers, key="sim_start")
            end_router = st.selectbox("End Router", routers, key="sim_end")
            
            col_sim1, col_sim2 = st.columns(2)
            with col_sim1:
                if st.button("Send Packet"):
                    if start_router != end_router:
                        simulator.simulate_packet(start_router, end_router)
                        st.rerun()
            
            with col_sim2:
                if st.button("Clear Logs"):
                    simulator.logs.clear()
                    simulator.packet_path.clear()
                    simulator.packet_stats['status'] = 'idle'
                    st.rerun()
    
    @staticmethod
    def render_network_status(simulator):
        """Render network status tables"""
        if simulator.graph.nodes:
            st.subheader("Network Status")
            
            # Nodes table
            node_data = []
            for node in simulator.graph.nodes:
                node_data.append({
                    'Router': node,
                    'Status': simulator.graph.nodes[node]['status'],
                    'Connections': len(list(simulator.graph.neighbors(node)))
                })
            
            if node_data:
                st.write("**Routers:**")
                st.dataframe(pd.DataFrame(node_data), use_container_width=True)
            
            # Edges table
            if simulator.graph.edges:
                edge_data = []
                for u, v in simulator.graph.edges:
                    data = simulator.graph[u][v]
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
    
    @staticmethod
    def render_packet_analytics(packet_stats):
        """Render packet analytics section"""
        if packet_stats['status'] != 'idle':
            st.subheader("📈 Packet Analytics")
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            
            with col_stat1:
                st.metric("Packet ID", packet_stats.get('packet_id', 'N/A'))
                st.metric("Status", packet_stats.get('status', 'idle'))
            
            with col_stat2:
                st.metric("TTL Remaining", f"{packet_stats.get('ttl', 0):.0f}")
                st.metric("Hops", packet_stats.get('hops', 0))
            
            with col_stat3:
                st.metric("Total Latency", f"{packet_stats.get('total_latency', 0):.2f}ms")
                if packet_stats.get('end_time') and packet_stats.get('start_time'):
                    actual_time = (packet_stats['end_time'] - packet_stats['start_time']).total_seconds()
                    st.metric("Actual Time", f"{actual_time:.2f}s")
    
    @staticmethod
    def render_simulation_logs(logs):
        """Render simulation logs"""
        if logs:
            st.subheader("Simulation Logs")
            for i, log in enumerate(reversed(logs[-10:])):
                st.text(f"{len(logs)-i}: {log}")
    
    @staticmethod
    def render_legend():
        """Render network visualization legend"""
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