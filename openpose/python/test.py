import os

# Define the relative paths
exe_path = os.path.join("build", "x64", "Release", "OpenPoseDemo.exe")
video_path = os.path.join("examples", "media", "video.avi")

# Check if the executable exists
if os.path.isfile(exe_path):
    print(f"Executable exists: {exe_path}")
else:
    print(f"Executable does NOT exist: {exe_path}")

# Check if the video file exists
if os.path.isfile(video_path):
    print(f"Video file exists: {video_path}")
else:
    print(f"Video file does NOT exist: {video_path}")



"C:\Users\Oyinloluwa Olatunji\Desktop\pose\openpose\build\x64\Release\OpenPoseDemo.exe"