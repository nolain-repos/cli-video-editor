# Quickstart Guide

## Running the Video Editor

### Prerequisites
Ensure you have Python 3.6+ installed on your system.

### Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd video-editor
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Execution

#### Interactive Terminal Mode
To launch the interactive terminal interface:

1. Navigate to the project directory
2. Run the main script:
   ```
   python run.py <input_video_path> <output_video_path>
   ```

   Example:
   ```
   python run.py input.mp4 output.mp4
   ```

#### Command Line Arguments
- `<input_video_path>`: Path to the source video file (required)
- `<output_video_path>`: Path where the edited video will be saved (required)

### Using the Interactive Interface
1. After launching, you'll see a menu with available editing actions:
   - Zoom
   - Mute
   - Spatial Crop
   - Time Crop

2. Navigate the menu using:
   - Up/Down arrow keys to move selection
   - Enter to select an action
   - Escape to go back/cancel

3. Follow the on-screen prompts to configure each editing operation

4. When all desired edits are configured, select "Done" to process the video

### Processing
The editor will:
1. Apply all configured operations in the correct order
2. Display progress in the terminal
3. Save the final video to the specified output path