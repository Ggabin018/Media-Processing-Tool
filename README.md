# Media-Processing-Tool

Web UI for editing videos.

## Operations:
* Cut video
* Compress video by bitrate
* Replace audio of video
* Combine audio of video
* Convert video to mp3
* Convert video to video

## Utils
Gradio as interface.

FFMPEG as editor.

# Table of Contents
* [Media-Processing-Tool](#media-processing-tool)
* [Table of Contents](#table-of-contents)
* [Installation](#installation)
  * [Windows](#windows)
    * [Pre-requirements](#windows-pre-requirements)
    * [Setup](#setup)
  * [Ubuntu](#ubuntu)
    * [Pre-requirements](#ubuntu-pre-requirements)
    * [Setup](#setup-1)
* [Updating](#updating)
* [Starting GUI](#starting-gui)
* [Codecs Information](#codecs-information)

## Installation

### Windows
#### Windows Pre-requirements
1. Install python 3.10 or more, and add it to the PATH
2. Install Git
3. [Install ffmpeg](https://github.com/BtbN/FFmpeg-Builds/releases)
    * Get ffmpeg-master-latest-win64-gpl-shared.zip
    * Add to the PATH the bin directory containing the exe files with dll

#### Setup
1. Open a terminal and go to the desired installation directory.
2. Clone the repository
    ```
    git clone https://github.com/Ggabin018/Media-Processing-Tool.git
    ```

3. Go in Media-Processing-Tool directory
    ```bat
    cd Media-Processing-Tool
    ```

4. Run install.bat
    ```bat
    .\install.bat
    ```

### Ubuntu

#### Ubuntu Pre-requirements
1. Install python 3.10 or more
2. Install ffmpeg
    * Update the repository
        ```
        sudo apt update && sudo apt upgrade
        ```
    * Install ffmpeg
        ```
        sudo apt install ffmpeg
        ```
    * Verify the installation
        ```
        ffmpeg
        ``` 

#### Setup
1. Open a terminal and go to the desired installation directory.
2. Clone the repository
    ```
    git clone https://github.com/Ggabin018/Media-Processing-Tool.git
    ```

3. Go in Media-Processing-Tool directory
    ```bat
    cd Media-Processing-Tool
    ```

4. Run install.bat
    ```bat
    ./install.sh
    ```

## Updating

    git pull

## Starting GUI

### Windows
    .\webui.bat

### ubuntu
    ./webui.sh

# Codecs Information
## Video Codecs:
- libx264 (H.264) - Best all-around browser compatibility
- libvpx-vp9 (VP9) - Good for web, slightly less universal than H.264
- h264_nvenc - If you need NVIDIA hardware acceleration with H.264
- hevc_nvenc (H.265/HEVC) - NVIDIA hardware acceleration, limited browser compatibility

# Audio Codecs:
- aac - Best browser compatibility
- libopus - Good quality at low bitrates, but less universal

# Container Format:
- mp4 extension for H.264/AAC
- webm extension for VP9/Opus