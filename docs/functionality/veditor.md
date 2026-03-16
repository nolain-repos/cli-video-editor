# Video Editor Module (`veditor.py`)

## Overview

The `veditor.py` module provides a high-level interface for performing complex video editing operations using the MoviePy library. It encapsulates common video manipulation tasks into a reusable `VideoEditor` class, enabling users to apply multiple transformations in a controlled sequence without directly managing low-level video processing details.

## Core Features

### Multi-Stage Video Processing Pipeline

The module implements a structured editing pipeline that applies transformations in a specific, optimized order:
1. **Zoom transformations** - Dynamic scaling effects applied to the original footage
2. **Spatial cropping** - Frame region selection (fixed or normalized coordinates)
3. **Audio muting** - Selective audio track silencing
4. **Temporal segmentation** - Time-based clip extraction and concatenation

This ordered approach ensures predictable results and prevents transformation conflicts.

### Zoom Effects

The editor supports sophisticated zoom operations with:
- **Gradual magnification** - Smooth transitions between zoom levels
- **Custom focal points** - Precise control over zoom center coordinates
- **Smoothstep interpolation** - Natural acceleration/deceleration of zoom speed
- **Multiple zoom sequences** - Ability to stack several zoom effects

Zoom parameters are specified in relative coordinates (0.0-1.0 range) for resolution independence.

### Temporal Editing

The module provides two distinct temporal editing capabilities:
1. **Time cropping** - Extracting specific time segments from the source video
2. **Audio muting** - Silencing portions of the audio track while preserving video

These operations maintain frame-perfect synchronization between audio and video streams.

### Spatial Manipulation

The editor supports:
- **Fixed-coordinate cropping** - Pixel-based frame region selection
- **Normalized cropping** - Resolution-independent frame region specification
- **Non-destructive operations** - All transformations are applied to the original source

## Technical Implementation

### Input Requirements

The module accepts:
- **Video files** - Any format supported by MoviePy/FFmpeg
- **Transformation parameters** - Time values in seconds, spatial coordinates in relative or absolute units
- **Effect specifications** - Zoom factors, crop dimensions, mute ranges

### Processing Algorithms

The editor employs:
- **Smoothstep interpolation** for natural zoom transitions
- **Frame-accurate concatenation** for temporal segmentation
- **Non-linear audio processing** for precise muting
- **Resolution-independent coordinate systems** for spatial operations

### Output Characteristics

The module produces:
- **Edited video files** - Maintaining original quality and format
- **Synchronized audio/video streams** - With frame-perfect alignment
- **Consistent aspect ratios** - Regardless of applied transformations

## Use Cases

The module is particularly suited for:
- Creating dynamic video presentations with zoom effects
- Extracting specific segments from long recordings
- Preparing video content with selective audio muting
- Applying consistent transformations across multiple video files
- Building automated video processing pipelines