import streamlit as st
import matplotlib.pyplot as plt
import time
import os

from network_core import NetworkSimulator
from visualization import NetworkVisualizer
from video_generator import VideoGenerator
from gif_generator import GifGenerator
from ui_components import UIComponents

def main():
    st.set_page_config(page_title="Network Simulator", layout="wide")
    st.title("🌐 Network Router Simulator")
    
    # Initialize components
    if 'simulator' not in st.session_state:
        st.session_state.simulator = NetworkSimulator()
    if 'visualizer' not in st.session_state:
        st.session_state.visualizer = NetworkVisualizer()
    if 'video_gen' not in st.session_state:
        st.session_state.video_gen = VideoGenerator()
    if 'gif_gen' not in st.session_state:
        st.session_state.gif_gen = GifGenerator()
    
    sim = st.session_state.simulator
    viz = st.session_state.visualizer
    video_gen = st.session_state.video_gen
    gif_gen = st.session_state.gif_gen
    ui = UIComponents()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("Controls")
        
        # Render UI components
        ui.render_quick_setup(sim)
        ui.render_router_management(sim)
        ui.render_link_management(sim)
        ui.render_simulation_controls(sim)
        
        # Auto-refresh for animation
        if sim.animating:
            time.sleep(0.1)
            sim.animate_packet()
            st.rerun()
        
        # GIF and video generation
        if sim.packet_path:
            col_gen1, col_gen2 = st.columns(2)
            with col_gen1:
                if st.button("🎞️ Generate GIF"):
                    with st.spinner("Creating animated GIF..."):
                        gif_path = gif_gen.create_packet_gif(sim)
                        if gif_path:
                            st.success(f"GIF saved as {gif_path}")
                            with open(gif_path, "rb") as file:
                                st.download_button(
                                    label="📥 Download GIF",
                                    data=file.read(),
                                    file_name=gif_path,
                                    mime="image/gif"
                                )
            with col_gen2:
                if st.button("🎬 Generate Video"):
                    st.info("Video generation requires FFmpeg. Install FFmpeg or use the live animation above.")
    
    with col2:

        
        st.header("Network Visualization")
        
        if sim.graph.nodes:
            fig, ax = plt.subplots(figsize=(10, 8))
            viz.draw_network(sim, fig, ax)
            st.pyplot(fig)
            

            
            ui.render_legend()
        else:
            st.info("Add routers to start building your network")
        

        
        ui.render_network_status(sim)
        ui.render_simulation_logs(sim.logs)
        ui.render_packet_analytics(sim.packet_stats)

if __name__ == "__main__":
    main()