from veditor import VideoEditor

editor = VideoEditor()

# Apply a zoom that overlaps with the crop
# Zoom from 1 to 4 seconds
editor.add_zoom(1, 4, 0.5, 0.5, 3.0)

# Keep segment from 0 to 5 seconds
editor.add_crop(0, 5)

input_video = "upload_file_2.mp4"
output_video = "debug_zoom_output.mp4"

print(f"Starting debug video processing: {input_video} -> {output_video}")
editor.run(input_video, output_video)
print("Debug processing complete.")
