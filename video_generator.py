import subprocess
import os
import streamlit as st

class VideoGenerator:
    def __init__(self):
        self.output_path = None
    
    def create_video_with_ffmpeg(self, frames, output_name='packet_simulation.mp4'):
        """Create video using FFmpeg"""
        if len(frames) < 2:
            return None
        
        # Check if ffmpeg is available
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True, shell=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            st.error("FFmpeg not found. Please install FFmpeg to generate videos.")
            return None
            
        try:
            self.output_path = output_name
            cmd = [
                'ffmpeg', '-y', '-framerate', '5',
                '-i', 'frames/frame_%04d.png',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                '-vf', 'scale=800:600',
                self.output_path
            ]
            subprocess.run(cmd, check=True, capture_output=True, shell=True)
            return self.output_path
        except Exception as e:
            st.error(f"Video generation failed: {e}")
            return None
    
    def create_manual_video(self, frames):
        """Create video from manual frames"""
        if not frames:
            return None
        
        # Check if ffmpeg is available
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True, shell=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            st.error("FFmpeg not found. Please install FFmpeg to generate videos.")
            return None
            
        try:
            output_path = 'manual_simulation.mp4'
            cmd = [
                'ffmpeg', '-y', '-framerate', '5',
                '-i', 'frames/manual_%04d.png',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                output_path
            ]
            subprocess.run(cmd, check=True, capture_output=True, shell=True)
            
            # Cleanup frames
            for frame in frames:
                if os.path.exists(frame):
                    os.remove(frame)
            
            return output_path
        except Exception as e:
            st.error(f"Video generation failed: {e}")
            return None
    
    def cleanup_frames(self, frames):
        """Clean up animation frames"""
        for frame in frames:
            if os.path.exists(frame):
                os.remove(frame)
        if os.path.exists('frames') and not os.listdir('frames'):
            os.rmdir('frames')
    
    def cleanup_videos(self):
        """Clean up generated videos"""
        for video_file in ['packet_simulation.mp4', 'manual_simulation.mp4']:
            if os.path.exists(video_file):
                os.remove(video_file)