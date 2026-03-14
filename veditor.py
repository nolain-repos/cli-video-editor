from moviepy import VideoFileClip, concatenate_videoclips, vfx
from PIL import Image
import numpy as np

class VideoEditor:
    """
    A class to manage and apply video editing operations such as gradual zoom-in/out 
    and temporal cropping (trimming) using MoviePy.
    
    The editor follows a specific order of operations:
    1. Apply all zoom transformations to the original video.
    2. Extract and concatenate specific temporal segments (crops) from the zoomed video.
    """

    def __init__(self):
        """
        Initializes the VideoEditor with empty lists for zoom and crop operations.
        """
        self.zooms = []
        self.crops = []

    def add_zoom(self, tstart, tend, w, h, zoom_factor):
        """
        Adds a gradual zoom operation. The video will zoom in from 1.0 to zoom_factor 
        and then back to 1.0 during the specified interval.
        
        Args:
            tstart (float): The start time (in seconds) for the zoom effect.
            tend (float): The end time (in seconds) for the zoom effect.
            w (float): The relative horizontal center of the zoom (0.0 to 1.0).
            h (float): The relative vertical center of the zoom (0.0 to 1.0).
            zoom_factor (float): The peak magnification factor at the midpoint.
        """
        self.zooms.append({
            'tstart': tstart,
            'tend': tend,
            'w': w,
            'h': h,
            'zoom_factor': zoom_factor
        })

    def add_crop(self, tstart, tend):
        """
        Adds a temporal cropping operation (segment to keep).
        
        Args:
            tstart (float): The start time (in seconds) of the segment to keep.
            tend (float): The end time (in seconds) of the segment to keep.
        """
        self.crops.append((tstart, tend))

    def run(self, input_path, output_path):
        """
        Processes the input video by applying all queued zoom and crop operations.
        """
        video = VideoFileClip(input_path)
        original_w, original_h = video.size
        
        # 1. Apply Zooms
        # We split the video into segments based on zoom times.
        zoom_times = []
        for z in self.zooms:
            zoom_times.extend([z['tstart'], z['tend']])
        
        zoom_times.extend([0, video.duration])
        zoom_times = sorted(list(set(zoom_times)))
        
        segments = []
        for i in range(len(zoom_times) - 1):
            t1, t2 = zoom_times[i], zoom_times[i+1]
            if t1 >= t2: continue
            
            seg = video.subclipped(t1, t2)
            
            # Check if this segment has an active zoom
            mid_abs = (t1 + t2) / 2
            active_zoom = next((z for z in self.zooms if z['tstart'] <= mid_abs <= z['tend']), None)
            
            if active_zoom:
                z_start = active_zoom['tstart']
                z_end = active_zoom['tend']
                z_peak_factor = active_zoom['zoom_factor']
                z_w = active_zoom['w']
                z_h = active_zoom['h']
                duration = z_end - z_start
                midpoint = duration / 2

                def gradual_zoom_filter(get_frame, t, t1=t1, z_start=z_start, midpoint=midpoint, z_peak_factor=z_peak_factor, z_w=z_w, z_h=z_h):
                    # t is relative to the segment start
                    t_abs = t1 + t
                    t_rel_zoom = t_abs - z_start
                    
                    # Define phases: 30% ramp up, 40% plateau, 30% ramp down
                    ramp_up_end = duration * 0.3
                    plateau_end = duration * 0.7
                    
                    if t_rel_zoom <= ramp_up_end:
                        # Phase 1: Ramp Up (Smoothstep)
                        progress = t_rel_zoom / ramp_up_end
                        # Smoothstep formula: 3x^2 - 2x^3
                        smooth_progress = 3 * (progress**2) - 2 * (progress**3)
                        current_factor = 1.0 + (z_peak_factor - 1.0) * smooth_progress
                    elif t_rel_zoom <= plateau_end:
                        # Phase 2: Plateau
                        current_factor = z_peak_factor
                    else:
                        # Phase 3: Ramp Down (Smoothstep)
                        progress = (t_rel_zoom - plateau_end) / (duration - plateau_end)
                        # Inverse smoothstep
                        smooth_progress = 3 * (progress**2) - 2 * (progress**3)
                        current_factor = z_peak_factor - (z_peak_factor - 1.0) * smooth_progress
                    
                    current_factor = max(1.0, current_factor)
                    
                    # Get the original frame
                    frame = get_frame(t)
                    
                    if current_factor <= 1.0:
                        return frame

                    # Process frame with PIL
                    img = Image.fromarray(frame)
                    
                    # 1. Resize
                    new_w = int(original_w * current_factor)
                    new_h = int(original_h * current_factor)
                    
                    # Use a more compatible way to get the resampling filter
                    resample_filter = getattr(Image, 'Resampling', Image).LANCZOS
                    img = img.resize((new_w, new_h), resample_filter)
                    
                    # 2. Calculate Crop Box to keep target centered
                    target_x_px = original_w * z_w * current_factor
                    target_y_px = original_h * z_h * current_factor
                    
                    x1 = max(0, min(target_x_px - (original_w / 2), new_w - original_w))
                    y1 = max(0, min(target_y_px - (original_h / 2), new_h - original_h))
                    
                    img = img.crop((x1, y1, x1 + original_w, y1 + original_h))
                    
                    return np.array(img)

                seg = seg.transform(gradual_zoom_filter)
            
            segments.append(seg)
        
        zoomed_video = concatenate_videoclips(segments)
        
        # 2. Apply Crops (Temporal)
        if self.crops:
            final_segments = []
            for tstart, tend in self.crops:
                ts = min(tstart, zoomed_video.duration)
                te = min(tend, zoomed_video.duration)
                if ts < te:
                    final_segments.append(zoomed_video.subclipped(ts, te))
            
            if final_segments:
                final_video = concatenate_videoclips(final_segments)
            else:
                final_video = zoomed_video
        else:
            final_video = zoomed_video
            
        # 3. Export
        final_video.write_videofile(output_path, codec="libx264")
        video.close()
        final_video.close()