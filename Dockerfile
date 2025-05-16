# # Base image with CUDA and Python support
# FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# # Set environment variables
# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONIOENCODING=utf-8 \
#     DEBIAN_FRONTEND=noninteractive

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     python3.10 python3.10-venv python3-pip \
#     cmake git libglib2.0-0 libsm6 libxrender1 libxext6 \
#     libgl1 \
#     && rm -rf /var/lib/apt/lists/*

# # Set Python 3.10 as default
# RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# # Create working directory
# WORKDIR /workspace

# # Copy the full project
# COPY . /workspace

# # Set OpenPose build path in PATH
# ENV PATH="/workspace/openpose/build/bin:${PATH}"

# # Install Python dependencies
# WORKDIR /workspace/smplify-x
# RUN pip install --upgrade pip && pip install -r requirements.txt

# # Default command to run your script
# CMD ["python", "demo.py"]



# Base image with CUDA and Python (adjust for your CUDA version)
# FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# # Set up environment
# ENV DEBIAN_FRONTEND=noninteractive

# # Install dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential cmake git curl wget \
#     libopencv-dev libatlas-base-dev \
#     libboost-all-dev libprotobuf-dev protobuf-compiler \
#     libgoogle-glog-dev libgflags-dev \
#     libhdf5-dev python3-dev python3-pip \
#     python3-opencv ffmpeg \
#     && rm -rf /var/lib/apt/lists/*

# # Python and pip
# RUN ln -s /usr/bin/python3 /usr/bin/python && pip3 install --upgrade pip

# # Install Python packages
# COPY requirements.txt /tmp/
# RUN pip install -r /tmp/requirements.txt

# # Clone OpenPose (you can copy it from your local directory if preferred)
# WORKDIR /workspace
# RUN git clone https://github.com/CMU-Perceptual-Computing-Lab/openpose.git
# WORKDIR /workspace/openpose

# # Build OpenPose for Linux
# RUN mkdir -p build && cd build && \
#     cmake -DBUILD_PYTHON=OFF -DBUILD_CAFFE=OFF .. && \
#     make -j$(nproc)

# # Add SMPLify-X
# WORKDIR /workspace
# COPY ./smplify-x ./smplify-x

# # Add your Streamlit demo
# COPY ./demo.py ./smplify-x/demo.py

# # Expose Streamlit port
# EXPOSE 8501

# # Default command to run Streamlit
# CMD ["streamlit", "run", "smplify-x/demo.py", "--server.port=8501", "--server.address=0.0.0.0"]


FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=utf-8 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 python3.10-venv python3-pip \
    cmake git curl wget ffmpeg \
    libopencv-dev libatlas-base-dev \
    libboost-all-dev libprotobuf-dev protobuf-compiler \
    libgoogle-glog-dev libgflags-dev \
    libhdf5-dev libglib2.0-0 libsm6 libxrender1 libxext6 libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Create working directory
WORKDIR /workspace

# Copy project
COPY . /workspace

# Install Python requirements
WORKDIR /workspace/smplify-x
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

# Clone and build OpenPose
WORKDIR /workspace
RUN git clone https://github.com/CMU-Perceptual-Computing-Lab/openpose.git
WORKDIR /workspace/openpose
RUN mkdir build && cd build && \
    cmake -DBUILD_PYTHON=OFF -DBUILD_CAFFE=OFF .. && \
    make -j$(nproc)

# Add OpenPose to PATH
ENV PATH="/workspace/openpose/build/bin:${PATH}"

# Expose Streamlit
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "smplify-x/demo.py", "--server.port=8501", "--server.address=0.0.0.0"]
