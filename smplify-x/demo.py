import base64
import streamlit as st
import subprocess
import os
import time
import json
import cv2
import shutil
import warnings
from PIL import Image
import platform

warnings.filterwarnings("ignore")


def extract_frames(video_file, output_dir, max_frames=2):
    os.makedirs(output_dir, exist_ok=True)
    video_output_dir = "../openpose/DATA_FOLDER/video"
    os.makedirs(video_output_dir, exist_ok=True)

    temp_video_path = os.path.join(video_output_dir, "temp_video.mp4")
    with open(temp_video_path, "wb") as f:
        f.write(video_file.getbuffer())
    
    cap = cv2.VideoCapture(temp_video_path)
    frame_count = 0
    
    while frame_count < max_frames:
        success, frame = cap.read()
        if not success:
            break
        frame_filename = os.path.join(output_dir, f"frame_{frame_count}.jpg")
        cv2.imwrite(frame_filename, frame)
        frame_count += 1
    
    cap.release()
    return output_dir  # Return directory where frames are stored

def run_openpose(image_file=None, image_output_dir="../openpose/DATA_FOLDER/images", keypoints_output_dir="../openpose/DATA_FOLDER/keypoints", is_image=False):
    os.makedirs(image_output_dir, exist_ok=True)
    os.makedirs(keypoints_output_dir, exist_ok=True)

    if is_image:
        temp_image_path = os.path.join(image_output_dir, "temp_image.jpg")
        with open(temp_image_path, "wb") as f:
            f.write(image_file.getbuffer())
    
    openpose_root = os.path.join('..', 'openpose')
    # command = f"cd {openpose_root} && .\\build\\x64\\Release\\OpenPoseDemo.exe --image_dir {image_output_dir} --hand --face --write_json {keypoints_output_dir}"
    # command = f"cd {openpose_root} && ./build/examples/openpose/openpose.bin --image_dir {image_output_dir} --hand --face --write_json {keypoints_output_dir}"
    if platform.system() == "Windows":
        return f".\\build\\x64\\Release\\OpenPoseDemo.exe --image_dir {image_dir} --hand --face --write_json {keypoints_output_dir}"
    else:
        return f"./build/examples/openpose/openpose.bin --image_dir {image_dir} --hand --face --write_json {keypoints_output_dir}"

    subprocess.run(command, shell=True)

    return os.path.isdir(keypoints_output_dir) and os.listdir(keypoints_output_dir)

def run_smplifyx(data_folder, output_folder, model_folder, vposer_ckpt):
    smplifyx_root = "../smplify-x"
    os.makedirs(output_folder, exist_ok=True)
    command = f"cd {smplifyx_root} && python smplifyx/main.py --config cfg_files/fit_smplx.yaml --data_folder {data_folder} --output_folder {output_folder} --visualize=False --model_folder {model_folder} --vposer_ckpt {vposer_ckpt}"
    subprocess.run(command, shell=True)

st.title("RGB to 3D Demo.")

uploaded_file = st.file_uploader("Upload an image or video", type=["jpg", "png", "jpeg","webp", "mp4", "avi"])
num_frames = st.number_input("Number of frames to process", min_value=1, max_value=30, value=1)


if st.button("Run") and uploaded_file is not None:
    start = time.time()
    file_extension = uploaded_file.name.split(".")[-1].lower()
    image_output_dir = "../openpose/DATA_FOLDER/images/"
    keypoints_output_dir = "../openpose/DATA_FOLDER/keypoints"
    
    if file_extension in ["mp4", "avi"]:
        st.write("Extracting frames from video...")
        image_dir = extract_frames(uploaded_file, image_output_dir, max_frames=num_frames)
        json_output = run_openpose(image_file=image_dir, image_output_dir=image_dir, keypoints_output_dir=keypoints_output_dir, is_image=False)
    else:
        # st.write("Processing image...")
        with st.spinner("Processing..."):
            json_output = run_openpose(image_file=uploaded_file, image_output_dir=image_output_dir, keypoints_output_dir=keypoints_output_dir, is_image=True)
        
    if json_output:
        # st.write("Running SMPLify-X...")
        with st.spinner("Processing..."):
            run_smplifyx(data_folder="../openpose/DATA_FOLDER", output_folder="OUTPUT_FOLDER", model_folder="MODEL_FOLDER", vposer_ckpt="VPOSER_FOLDER")
            st.write("Processed successfully.")
    else:
        st.error("Failed to generate JSON output. Make sure OpenPose is correctly installed and configured.")
    end = time.time()
    execution_time = end - start
    st.write(f"It took {execution_time:.2f} seconds to run.")
    
# if st.button("3D-Demo"):
    mesh_dir = "./OUTPUT_FOLDER/meshes/"
    image_output_dir = "../openpose/DATA_FOLDER/images/"
    # Check if the mesh directory exists
    if not os.path.exists(mesh_dir):
        st.error("Mesh directory does not exist. Please run the SMPLify-X process first.")
        st.stop()
    
    # Build a mapping of folder name -> (obj_file_path, frame_file_path)
    match_dict = {}
    for subdir in os.listdir(mesh_dir):
        subdir_path = os.path.join(mesh_dir, subdir)
        if os.path.isdir(subdir_path):
            obj_file_path = os.path.join(subdir_path, "000.obj")
            frame_file_path = os.path.join(image_output_dir, f"{subdir}.jpg")
            if os.path.exists(obj_file_path) and os.path.exists(frame_file_path):
                match_dict[subdir] = (obj_file_path, frame_file_path)

    # Sort the keys to ensure a consistent order
    ordered_keys = sorted(match_dict.keys())
    obj_files = [match_dict[k][0] for k in ordered_keys]
    frame_files = [match_dict[k][1] for k in ordered_keys]

    obj_base64_list = []
    frame_base64_list = []
    
    for obj_file, frame_file in zip(obj_files, frame_files):
        with open(obj_file, "rb") as file:
            obj_data = file.read()
        obj_base64_list.append(base64.b64encode(obj_data).decode())
        
        with open(frame_file, "rb") as file:
            frame_data = file.read()
        frame_base64_list.append(base64.b64encode(frame_data).decode())
    
    obj_list_js = ", ".join(f'"{obj}"' for obj in obj_base64_list)
    frame_list_js = ", ".join(f'"{frame}"' for frame in frame_base64_list)
    # print(frame_list_js)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src=\"https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js\"></script>
        <script src=\"https://cdn.jsdelivr.net/npm/three/examples/js/loaders/OBJLoader.js\"></script>
        <script src=\"https://cdn.jsdelivr.net/npm/three/examples/js/controls/OrbitControls.js\"></script>
    </head>
    
    <body>
        <div style="display: flex; flex-direction: row; width: 100%;">
            <div id="viewer" style="width: 50%; height: 600px;"></div>
            <div style="width: 50%; height: 600px;">
                <img id="image" style="width: 100%; height: 100%;" />
            </div>
        </div>
        <script>
            var scene, camera, renderer, controls, currentObject;
            var objList = [{obj_list_js}];
            var frameList = [{frame_list_js}];  // Preloaded frames
            var currentIndex = 0;
            console.log(frameList);
            function init() {{
                scene = new THREE.Scene();
                var viewer = document.getElementById('viewer');
                var aspect = viewer.clientWidth / viewer.clientHeight;
                camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
                camera.position.set(0, 1, 5);
                renderer = new THREE.WebGLRenderer({{ antialias: true }});
                renderer.setSize(viewer.clientWidth, viewer.clientHeight);
                document.getElementById('viewer').appendChild(renderer.domElement);
                var ambientLight = new THREE.AmbientLight(0xffffff, 1.5);
                scene.add(ambientLight);
                var directionalLight = new THREE.DirectionalLight(0xffffff, 2);
                directionalLight.position.set(2, 2, 5);
                scene.add(directionalLight);
                controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.dampingFactor = 0.05;
                controls.screenSpacePanning = false;
                controls.maxDistance = 10;
                controls.minDistance = 1;
                loadObject(objList[currentIndex]);
                animate();
                setTimeout(function() {{
                    updateObject(); // Ensure the image updates initially after a delay
                    setInterval(updateObject, 100);
                }}, 1500);  // 1500ms delay (adjust as needed)
            }}
            function loadObject(objDataBase64) {{
                var loader = new THREE.OBJLoader();
                var objData = atob(objDataBase64);
                var objBlob = new Blob([objData], {{ type: 'text/plain' }});
                var objUrl = URL.createObjectURL(objBlob);
                loader.load(objUrl, function (object) {{
                    if (currentObject) scene.remove(currentObject);
                    currentObject = object;
                    scene.add(object);
                }});
            }}
            function updateObject() {{
                var imageElement = document.getElementById("image");
                // When the image finishes loading, load the corresponding 3D object
                imageElement.onload = function() {{
                     loadObject(objList[currentIndex]);
                     // prepare next index for the following cycle
                     currentIndex = (currentIndex + 1) % objList.length;
                }};
                // Update the image src (this triggers the onload event)
                imageElement.src = "data:image/jpeg;base64," + frameList[currentIndex];
            }}
            function animate() {{
                requestAnimationFrame(animate);
                controls.update();
                renderer.render(scene, camera);
            }}
            init();
        </script>
    </body>
    </html>
    """
    st.components.v1.html(html_code, height=650)
    
if st.button("End"):
    print(os.getcwd())
    smplifyx_root = "OUTPUT_FOLDER/"
    openpose_root = os.path.join('..', 'openpose/DATA_FOLDER/')
    shutil.rmtree(smplifyx_root)
    shutil.rmtree(openpose_root)
    # st.write("All files have been deleted.")
