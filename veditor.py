from moviepy import VideoFileClip, concatenate_videoclips, concatenate_audioclips, AudioArrayClip, vfx
from PIL import Image
import numpy as np

class VideoEditor:
    """A class to manage and apply video editing operations using MoviePy.

    This class provides methods to apply various video editing operations such as zooming,
    cropping (temporal and spatial), and muting audio segments. The operations are applied
    in a specific order when the `run` method is called.

    Order of operations applied in run():
        1. Apply all zoom transformations to the original video.
        2. Apply spatial crop (frame region).
        3. Apply mute ranges to the audio track.
        4. Extract and concatenate specific temporal segments (time crops).
    """

    def __init__(self):
        """Initializes the VideoEditor with empty zoom, crop, mute, and spatial crop lists."""
        self.zooms = []
        self.crops = []
        self.spatial_crop = None
        self.spatial_crop_normalized = False
        self.mutes = []

    def add_zoom(self, tstart, tend, w, h, zoom_factor):
        """Adds a gradual zoom operation to the video.

        The video will zoom in from 1.0 to `zoom_factor` and then back to 1.0 during the
        specified interval. The zoom effect uses a smoothstep function for smooth transitions.

        Args:
            tstart (float): The start time (in seconds) for the zoom effect.
            tend (float): The end time (in seconds) for the zoom effect.
            w (float): The relative horizontal center of the zoom (0.0 to 1.0).
            h (float): The relative vertical center of the zoom (0.0 to 1.0).
            zoom_factor (float): The peak magnification factor at the midpoint of the zoom.
        """
        self.zooms.append({
            'tstart': tstart,
            'tend': tend,
            'w': w,
            'h': h,
            'zoom_factor': zoom_factor
        })

    def add_time_crop(self, tstart, tend):
        """Adds a temporal cropping operation (segment to keep).

        This operation specifies a segment of the video to retain. Multiple segments can be
        added and they will be concatenated in the final output.

        Args:
            tstart (float): The start time (in seconds) of the segment to keep.
            tend (float): The end time (in seconds) of the segment to keep.
        """
        self.crops.append((tstart, tend))

    def add_spatial_crop(self, x1, y1, x2, y2, normalized=False):
        """Sets a spatial crop for the video frame.

        Crops the video frame to the given rectangle. Subsequent calls override the
        previous spatial crop (only one spatial crop is applied).

        Args:
            x1 (int or float): Left boundary (pixels if normalized=False, else 0–1).
            y1 (int or float): Top boundary (pixels if normalized=False, else 0–1).
            x2 (int or float): Right boundary (pixels if normalized=False, else 0–1).
            y2 (int or float): Bottom boundary (pixels if normalized=False, else 0–1).
            normalized (bool, optional): If True, x1, y1, x2, y2 are in 0–1. Defaults to False.
        """
        self.spatial_crop = (x1, y1, x2, y2)
        self.spatial_crop_normalized = normalized

    def add_mute(self, tstart=None, tend=None):
        """Adds a mute range to the video's audio track.

        Mutes the audio for a specified time range. Times refer to the original video
        timeline (before time crops). Calling with no arguments mutes the entire video.

        Args:
            tstart (float, optional): Start time in seconds. Defaults to 0.
            tend (float, optional): End time in seconds. Defaults to video end.
        """
        self.mutes.append((tstart, tend))

    def _apply_mutes(self, video):
        """Applies all queued mute ranges to the video's audio track.

        Merges overlapping mute ranges and builds a new audio clip from silent and original
        segments. If the entire duration is muted, the video is returned without audio.

        Args:
            video (VideoFileClip): The video clip whose audio will be muted.

        Returns:
            VideoFileClip: The same video with audio muted in the specified ranges.
        """
        audio = video.audio
        if audio is None:
            return video

        duration = video.duration

        mute_ranges = []
        for tstart, tend in self.mutes:
            t1 = float(tstart) if tstart is not None else 0.0
            t2 = float(tend) if tend is not None else duration
            t1 = max(0.0, min(t1, duration))
            t2 = max(0.0, min(t2, duration))
            if t1 < t2:
                mute_ranges.append([t1, t2])

        if not mute_ranges:
            return video

        mute_ranges.sort()
        merged = [mute_ranges[0]]
        for start, end in mute_ranges[1:]:
            if start <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], end)
            else:
                merged.append([start, end])

        if merged[0][0] <= 0.0 and merged[-1][1] >= duration:
            return video.without_audio()

        audio_fps = audio.fps
        nchannels = audio.nchannels if hasattr(audio, 'nchannels') else 2

        events = []
        prev = 0.0
        for t1, t2 in merged:
            if prev < t1:
                events.append((prev, t1, False))
            events.append((t1, t2, True))
            prev = t2
        if prev < duration:
            events.append((prev, duration, False))

        audio_segments = []
        for t1, t2, is_muted in events:
            seg_duration = t2 - t1
            if is_muted:
                n_samples = int(round(seg_duration * audio_fps))
                silence = np.zeros((n_samples, nchannels))
                audio_segments.append(AudioArrayClip(silence, fps=audio_fps))
            else:
                audio_segments.append(audio.subclipped(t1, t2))

        new_audio = concatenate_audioclips(audio_segments)
        return video.with_audio(new_audio)

    def run(self, input_path, output_path):
        """Processes the input video by applying all queued operations and writes the result.

        The operations are applied in the following order: zooms, spatial crop, mutes,
        and time crops. The processed video is then exported to the specified output path.

        Args:
            input_path (str): Path to the source video file.
            output_path (str): Path where the processed video will be written.
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

                def gradual_zoom_filter(get_frame, t, t1=t1, z_start=z_start, duration=duration, z_peak_factor=z_peak_factor, z_w=z_w, z_h=z_h):
                    """Applies a gradual zoom effect to a video frame.

                    This function is used as a transform filter for MoviePy. It calculates the
                    current zoom factor based on the time within the zoom effect and applies
                    the zoom to the frame.

                    Args:
                        get_frame (callable): A function that returns the frame at time t.
                        t (float): The time within the current segment.

                    Returns:
                        numpy.ndarray: The processed frame with zoom applied.
                    """
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

        # 2. Apply Spatial Crop
        if self.spatial_crop:
            x1, y1, x2, y2 = self.spatial_crop
            if self.spatial_crop_normalized:
                w, h = zoomed_video.size
                x1, y1 = int(x1 * w), int(y1 * h)
                x2, y2 = int(x2 * w), int(y2 * h)
            zoomed_video = zoomed_video.with_effects([vfx.Crop(x1=x1, y1=y1, x2=x2, y2=y2)])

        # 3. Apply Mutes
        if self.mutes:
            zoomed_video = self._apply_mutes(zoomed_video)

        # 4. Apply Crops (Temporal) — always last
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

        # 5. Export
        final_video.write_videofile(output_path, codec="libx264")
        video.close()
        final_video.close()