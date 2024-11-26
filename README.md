# Media-Processing-Tool

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