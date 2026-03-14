from veditor import VideoEditor

# --- CONFIGURATION ---

editor = VideoEditor()

# Define zoom events
# (tstart, tend, w, h, zoom_factor)
editor.add_zoom(3.7, 5, 0.25, 0.6, 2.0)
editor.add_zoom(16, 18, 0.5, 0.8, 2.0)
editor.add_zoom(24, 26, 0.25, 0.8, 2.0)

# Define segments to keep (start, end)
editor.add_crop(0, 5) # Changed from (0, 3) to include the zoom at 3.7-5
editor.add_crop(6, 7)
editor.add_crop(9, 11)
editor.add_crop(19, 23)
editor.add_crop(27, 33)

# --- EXECUTION ---

input_video = "upload_file_2.mp4"
output_video = "multi_edit_output.mp4"

print(f"Starting video processing: {input_video} -> {output_video}")
editor.run(input_video, output_video)
print("Processing complete.")