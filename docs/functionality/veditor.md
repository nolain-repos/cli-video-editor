Here's a detailed documentation page in Markdown format for the `veditor.py` module:

```markdown
# Video Editor Module (`veditor.py`)

## Overview

The `veditor.py` module provides a Python class `VideoEditor` for performing non-linear video editing operations using the [MoviePy](https://zulko.github.io/moviepy/) library. This module enables programmatic video manipulation including zooming, cropping (both temporal and spatial), and audio muting.

## Purpose

The `VideoEditor` class serves as a high-level interface for common video editing tasks, abstracting the complexity of direct MoviePy operations. It's designed for:

- Automating video editing workflows
- Batch processing of video files
- Creating dynamic video effects through code
- Integrating video editing capabilities into larger Python applications

## Architecture

### Core Class

#### `VideoEditor`

The main class that manages and applies video editing operations in a specific order.

**Operation Order (applied in `run()` method):**
1. Zoom transformations (applied to original video)
2. Spatial crop (frame region selection)
3. Audio mute ranges
4. Temporal segments concatenation (time crops)

### Key Components

1. **Zoom Operations**
   - Gradual zoom effects with configurable center points and magnification factors
   - Multiple zoom operations can be stacked

2. **Temporal Cropping**
   - Select specific time segments to keep
   - Segments are concatenated in the order they were added

3. **Spatial Cropping**
   - Pixel-level frame region selection
   - Only one spatial crop can be active (subsequent calls override previous ones)

4. **Audio Muting**
   - Time ranges where audio should be silenced
   - Multiple mute ranges can be specified

## API Reference

### `VideoEditor` Class

```python
class VideoEditor:
    """A class to manage and apply video editing operations using MoviePy."""
```

#### Methods

##### `__init__(self)`
Initializes a new video editor instance with empty operation queues.

##### `add_zoom(self, tstart, tend, w, h, zoom_factor)`
Adds a gradual zoom operation to the video.

**Args:**
- `tstart` (float): Start time in seconds for the zoom effect
- `tend` (float): End time in seconds for the zoom effect
- `w` (float): Relative horizontal center of zoom (0.0 to 1.0)
- `h` (float): Relative vertical center of zoom (0.0 to 1.0)
- `zoom_factor` (float): Peak magnification factor at midpoint

**Behavior:**
- Zooms in from 1.0 to `zoom_factor` then back to 1.0 during the specified interval
- Multiple zoom operations can be added and will be applied sequentially

##### `add_time_crop(self, tstart, tend)`
Adds a temporal cropping operation (segment to keep).

**Args:**
- `tstart` (float): Start time in seconds of segment to keep
- `tend` (float): End time in seconds of segment to keep

**Behavior:**
- Segments are concatenated in the order they were added
- Overlapping segments will be merged

##### `add_spatial_crop(self, x1, y1, x2, y2)`
Sets a spatial crop for the video frame.

**Args:**
- `x1` (int): Left coordinate of crop rectangle (pixels)
- `y1` (int): Top coordinate of crop rectangle (pixels)
- `x2` (int): Right coordinate of crop rectangle (pixels)
- `y2` (int): Bottom coordinate of crop rectangle (pixels)

**Behavior:**
- Only one spatial crop can be active (subsequent calls override previous ones)
- Coordinates are in pixel units from the top-left corner

##### `add_mute(self, tstart, tend)`
Adds a time range where audio should be muted.

**Args:**
- `tstart` (float): Start time in seconds for mute range
- `tend` (float): End time in seconds for mute range

**Behavior:**
- Multiple mute ranges can be added
- Overlapping ranges will be merged

##### `run(self, input_path, output_path, fps=None, audio_codec='aac')`
Executes all queued operations and generates the output video.

**Args:**
- `input_path` (str): Path to input video file
- `output_path` (str): Path to save output video file
- `fps` (float, optional): Frames per second for output video. If None, uses input fps.
- `audio_codec` (str, optional): Audio codec to use for output. Defaults to 'aac'.

**Returns:**
- None

**Raises:**
- `ValueError`: If no operations have been queued
- Various MoviePy exceptions for file operations

## Use Cases

### 1. Creating a Zoom Effect Video

```python
from veditor import VideoEditor

editor = VideoEditor()
editor.add_zoom(tstart=2.0, tend=5.0, w=0.5, h=0.5, zoom_factor=1.5)
editor.run("input.mp4", "zoomed_output.mp4")
```

### 2. Extracting Specific Segments

```python
editor = VideoEditor()
editor.add_time_crop(10.0, 20.0)  # First 10 seconds
editor.add_time_crop(30.0, 45.0)  # Middle 15 seconds
editor.run("input.mp4", "segments_output.mp4")
```

### 3. Creating a Picture-in-Picture Effect

```python
editor = VideoEditor()
editor.add_spatial_crop(100, 100, 500, 400)  # Crop to center region
editor.add_zoom(tstart=5.0, tend=15.0, w=0.5, h=0.5, zoom_factor=2.0)
editor.run("input.mp4", "pip_output.mp4")
```

### 4. Muting Specific Audio Segments

```python
editor = VideoEditor()
editor.add_mute(15.0, 20.0)  # Mute from 15-20 seconds
editor.add_mute(30.0, 35.0)  # Mute from 30-35 seconds
editor.run("input.mp4", "muted_output.mp4")
```

### 5. Complex Editing Workflow

```python
editor = VideoEditor()
# Add multiple zoom effects
editor.add_zoom(2.0, 5.0, 0.5, 0.5, 1.5)
editor.add_zoom(8.0, 12.0, 0.3, 0.7, 2.0)

# Select specific time segments
editor.add_time_crop(0.0, 15.0)
editor.add_time_crop(20.0, 30.0)

# Crop to 16:9 aspect ratio
editor.add_spatial_crop(0, 0, 1920, 1080)

# Mute some audio
editor.add_mute(5.0, 7.0)

# Process the video
editor.run("input.mp4", "complex_output.mp4", fps=30)
```

## Dependencies

- [MoviePy](https://zulko.github.io/moviepy/) (>= 1.0.0)
- [Pillow](https://python-pillow.org/) (PIL)
- [NumPy](https://numpy.org/)

## Best Practices

1. **Operation Order**: Remember that operations are applied in a specific order (zooms → spatial crop → mutes → time crops)

2. **Performance**: For large videos, consider:
   - Processing in chunks
   - Using lower resolution previews
   - Running on machines with sufficient RAM

3. **Error Handling**: Wrap `run()` calls in try-except blocks to handle potential file operation errors

4. **Temporal Precision**: Be aware that some operations may slightly affect timing due to frame rate conversions

5. **Memory Management**: Large video files can consume significant memory - consider processing in segments if memory is constrained

## Limitations

1. **Single Spatial Crop**: Only one spatial crop can be active at a time

2. **Operation Order**: The fixed operation order may limit some editing workflows

3. **Performance**: Complex operations on high-resolution videos may be slow

4. **Audio Processing**: Limited to muting - no advanced audio effects

5. **Video Formats**: Output format depends on MoviePy's supported codecs

## Future Enhancements

Potential future improvements could include:

1. Support for multiple spatial crops (picture-in-picture)
2. Additional audio effects (volume adjustment, fade in/out)
3. Color correction and filtering
4. Text and image overlays
5. Transition effects between segments
6. Support for variable frame rate videos
7. Parallel processing for improved performance
```

This documentation provides comprehensive information about the module's purpose, architecture, API, use cases, and best practices while maintaining clarity and technical accuracy.