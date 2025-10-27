# Network Router Simulator

A modular Streamlit application for creating and visualizing network topologies with real-time packet routing simulation.

## Features

- **Router Management**: Add/remove routers dynamically (2-50 routers)
- **Link Configuration**: Create connections with customizable latency, bandwidth, congestion, and packet loss
- **Real-time Animation**: Live packet routing visualization using Dijkstra's algorithm
- **Vector Graphics**: Professional router representations with antennas and LED indicators
- **Random Networks**: Generate random topologies with configurable parameters
- **Packet Analytics**: Track routing decisions, TTL, hops, and delivery times

## Installation

```bash
pip install -r requirements.txt
```

## Usage

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

**Windows:**
```bash
run.bat
```

**Manual:**
```bash
streamlit run main.py
```

## File Structure

- `main.py` - Main application entry point
- `network_core.py` - Network simulation and routing logic
- `visualization.py` - Vector graphics and packet animation
- `video_generator.py` - FFmpeg video operations (optional)
- `ui_components.py` - Streamlit interface components

## Controls

1. **Quick Setup**: Generate random networks (2-50 routers)
2. **Add/Remove Routers**: Create network nodes manually
3. **Configure Links**: Adjust latency, congestion, packet loss, and status
4. **Send Packets**: Simulate routing between any two routers
5. **Live Animation**: Watch packets move along calculated paths

## Network Indicators

- **Green Routers**: Current packet path
- **Blue Routers**: Active routers
- **Gray Edges**: Normal links
- **Orange Edges**: Congested links (>50%)
- **Red Dashed Edges**: Failed links
- **Red Vector Packet**: Moving data with trail effect

## Requirements

- Python 3.8+
- Streamlit
- NetworkX
- Matplotlib
- Pandas
- NumPy
- Pillow (PIL)

## Optional

- FFmpeg (for video export - not required for core functionality)