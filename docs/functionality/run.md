# `run.py` Module Documentation

## Overview

The `run.py` module provides a terminal-based interactive menu system for controlling a video editing application. It enables users to navigate and select video editing actions through a text-based user interface (TUI) in a Unix-like terminal environment.

## Core Features

### Terminal-Based User Interface
- Implements a navigable menu system with visual feedback for selected options
- Supports keyboard navigation using arrow keys, Enter, and Escape
- Provides clear screen management and cursor positioning
- Displays formatted text with ANSI escape codes for styling (bold, inverted colors)

### Input Handling
- Captures single-key input in raw terminal mode
- Supports special key detection (arrow keys, Enter, Escape, Ctrl+C)
- Handles terminal state preservation (restores original terminal settings after input)

### Video Editing Workflow
- Presents a predefined set of video editing actions (Zoom, Mute, Spatial Crop, Time Crop)
- Serves as the entry point for the `VideoEditor` class functionality
- Designed to facilitate user selection of editing operations

## Key Components

### Input Processing
- **Key Reading Algorithm**: Interprets raw terminal input to detect special keys while maintaining compatibility with standard character input
- **Terminal State Management**: Temporarily modifies terminal settings for raw input while ensuring proper restoration

### Menu System
- **Navigation Logic**: Tracks currently selected menu option and handles user navigation commands
- **Visual Feedback**: Highlights the currently selected option using inverted colors
- **Information Display**: Presents clear navigation instructions and maintains consistent screen layout

## Inputs

### User Input
- Arrow keys (up/down) for navigation
- Enter key for selection
- Escape key for cancellation (where applicable)
- Standard character input (for future extensibility)

### Programmatic Inputs
- Menu title string
- List of option strings
- Optional header text

## Outputs

### User Interface Outputs
- Formatted menu display with:
  - Title (bold formatting)
  - List of options (with current selection highlighted)
  - Navigation instructions (dimmed formatting)

### Programmatic Outputs
- Integer representing the index of the selected menu option (0-based)
- Keyboard interrupt signals (propagated for application-level handling)

## Technical Characteristics

- **Terminal Compatibility**: Designed for Unix-like systems with termios support
- **State Management**: Maintains terminal state integrity through proper resource cleanup
- **Error Handling**: Propagates keyboard interrupts for graceful application termination
- **Extensibility**: Modular design allows for additional menu options and actions