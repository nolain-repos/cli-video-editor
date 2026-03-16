# Video Editor Quickstart Guide

## Prerequisites

1. Python 3.8 or higher
2. pip package manager

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

### Main Entry Point

Execute the interactive video editor:
```
python run.py <input_video_path>
```

### Command Line Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `input_video_path` | Path to the input video file | Yes |

## Interactive Controls

Once the application is running:

1. Use **↑** and **↓** arrow keys to navigate the menu
2. Press **Enter** to select an action
3. Follow on-screen prompts for each editing operation:
   - **Zoom**: Enter zoom factor and duration
   - **Mute**: Specify time ranges to mute
   - **Spatial Crop**: Define frame region to keep
   - **Time Crop**: Select temporal segments to include
4. Press **Esc** to cancel current operation
5. After completing edits, the final video will be saved as `output.mp4` in the current directory

## Output

The edited video will be saved as:
```
./output.mp4
```