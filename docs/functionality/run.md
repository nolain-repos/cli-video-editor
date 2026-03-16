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
- Interprets special keys including:
  - Arrow keys (up/down) for navigation
  - Enter for selection
  - Escape for cancellation
  - Handles Ctrl+C as a keyboard interrupt

### Video Editing Workflow
- Presents a predefined set of video editing actions:
  - Zoom
  - Mute
  - Spatial Crop
  - Time Crop
- Integrates with the `VideoEditor` class for executing selected operations

## Key Components

### `read_key()`
**Purpose**: Low-level keyboard input handler
**Input**: None (reads directly from stdin)
**Output**: String representing the key pressed ("up", "down", "enter", "escape", or literal character)
**Behavior**:
- Temporarily configures terminal for raw input mode
- Handles multi-byte sequences for special keys
- Restores original terminal settings after reading

### `clear_screen()`
**Purpose**: Terminal screen management
**Input**: None
**Output**: None (direct terminal output)
**Behavior**:
- Clears all content from the terminal
- Resets cursor position to top-left corner

### `show_menu()`
**Purpose**: Interactive menu display and navigation
**Input**:
- `title`: Menu header text
- `options`: List of selectable menu items
- `header`: Optional text displayed above the title
**Output**: Integer representing the index of the selected option
**Behavior**:
- Renders a formatted menu with visual indicators for the selected item
- Handles keyboard navigation in a loop until selection is made
- Provides visual feedback for navigation controls

## Technical Implementation Details

### Terminal Control
- Uses Unix-specific terminal control modules (`tty`, `termios`)
- Implements proper resource management with try-finally blocks
- Handles terminal state restoration after operations

### User Experience
- Provides clear visual hierarchy with formatted text
- Includes navigation instructions in the interface
- Uses inverted colors to highlight the currently selected option
- Maintains consistent spacing and alignment

### Integration Points
- Designed to work with the `VideoEditor` class for actual video processing
- Menu options correspond to specific video editing operations
- Input handling supports both simple key presses and complex key sequences