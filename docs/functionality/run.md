Here's a detailed documentation page in Markdown format for the `run.py` module:

```markdown
# `run.py` Module Documentation

## Overview

The `run.py` module provides a terminal-based interactive interface for video editing operations. It serves as the command-line frontend for the `VideoEditor` class (imported from `veditor`), allowing users to apply various video transformations through an intuitive menu system.

## Purpose

This module enables users to:
- Interactively select video editing operations
- Configure parameters for each operation
- Preview and apply transformations to video files
- Navigate through editing options using keyboard controls

## Key Components

### Core Functions

#### `read_key()`
```python
def read_key():
    """Reads a single keypress from stdin and returns its corresponding action.

    Returns:
        str: The detected key action ('up', 'down', 'enter', 'escape') or the character itself.

    Raises:
        KeyboardInterrupt: If Ctrl+C is pressed.
    """
```
- Captures single keypresses in raw terminal mode
- Handles special keys (arrow keys, Enter, Escape)
- Restores terminal settings after reading

#### `clear_screen()`
```python
def clear_screen():
    """Clears the terminal screen and moves cursor to home position."""
```
- Uses ANSI escape codes to clear terminal
- Ensures clean display for menu rendering

#### `show_menu(title, options, header="")`
```python
def show_menu(title, options, header=""):
    """Displays an interactive menu and handles user navigation.

    Args:
        title (str): The menu title to display.
        options (list): List of menu options to display.
        header (str, optional): Additional header text. Defaults to "".

    Returns:
        int: Index of the selected option.
    """
```
- Renders a navigable menu with highlighted selection
- Handles up/down arrow navigation
- Returns selected option index on Enter keypress

#### `get_input(prompt, type_fn=float, optional=False)`
```python
def get_input(prompt, type_fn=float, optional=False):
    """Gets validated user input from the command line.

    Args:
        prompt (str): The input prompt to display.
        type_fn (callable, optional): Function to convert input. Defaults to float.
        optional (bool, optional): Whether input can be empty. Defaults to False.

    Returns:
        type_fn return type or None: The converted input value or None if optional and empty.
    """
```
- Validates user input against expected type
- Supports optional inputs
- Provides error feedback for invalid inputs

### Constants

#### `ACTIONS`
```python
ACTIONS = ["Zoom", "Mute", "Spatial Crop", "Time Crop"]
```
- List of available video editing operations
- Used to populate the main menu

## Architecture

### Terminal Interaction Flow

1. **Initialization**:
   - Terminal is set to raw mode for single keypress reading
   - Screen is cleared for menu display

2. **Menu System**:
   - Main menu displays available actions
   - Sub-menus collect parameters for each action
   - Navigation uses arrow keys and Enter

3. **Parameter Collection**:
   - Each action has specific parameters
   - Input validation ensures correct data types
   - Optional parameters can be skipped

4. **Action Execution**:
   - Validated parameters are passed to VideoEditor
   - Results are displayed or saved

### Data Flow

```
User Input → read_key() → Menu Navigation → Parameter Collection → VideoEditor → Output
```

## Use Cases

### Basic Video Editing

1. Launch the script to display the main menu
2. Select an editing operation (e.g., "Zoom")
3. Enter required parameters when prompted
4. Apply the transformation to your video

### Batch Processing

```python
from run import VideoEditor

editor = VideoEditor("input.mp4")
actions = [
    ("Zoom", {"factor": 1.5}),
    ("Mute", {})
]
editor.apply_actions(actions)
editor.save("output.mp4")
```

### Custom Action Integration

1. Add new action to `ACTIONS` list
2. Implement parameter collection in the main loop
3. Add corresponding method to VideoEditor class

## Example Workflow

1. **Zoom Operation**:
   - Select "Zoom" from main menu
   - Enter zoom factor (e.g., 1.5)
   - Optionally specify duration and position

2. **Time Crop**:
   - Select "Time Crop" from main menu
   - Enter start time (e.g., 10.5 seconds)
   - Enter end time (e.g., 20.5 seconds)

## Error Handling

- Invalid numeric inputs are caught and prompt re-entry
- KeyboardInterrupt (Ctrl+C) exits the program
- Terminal settings are always restored on exit

## Dependencies

- `sys`: For terminal interaction
- `tty`/`termios`: For raw terminal mode
- `veditor.VideoEditor`: Core video editing functionality

## Best Practices

1. **Terminal Compatibility**:
   - Ensure terminal supports ANSI escape codes
   - Test with different terminal emulators

2. **Input Validation**:
   - Always validate user inputs
   - Provide clear error messages

3. **Resource Management**:
   - Restore terminal settings after use
   - Handle keyboard interrupts gracefully

## Future Enhancements

1. Add color support for better visual feedback
2. Implement undo/redo functionality
3. Add preview capability before applying changes
4. Support for additional video formats and codecs
```

This documentation provides comprehensive coverage of the module's functionality, architecture, and usage patterns while maintaining clarity and technical accuracy.