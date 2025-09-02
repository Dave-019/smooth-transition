

A command-line tool that automatically analyzes, reorders, and mixes a collection of MP3 files into a single and seamless mix


## How It Works

The script operates in several distinct phases to create the final mix:

1.  **Analysis Phase**: The script first iterates through every MP3 in the `songs_to_mix` folder. Using the `librosa` library, it analyzes each track to determine its musical key (e.g., C Minor) and its corresponding Camelot wheel code (e.g., 5A).

2.  **Pre-processing Phase**: For each track in the new, intelligent order, the script uses `pydub` to perform two trimming operations:
    -   It removes any leading silence from the start of the track.
    -   It finds any long internal silences (e.g., >10 seconds) and shortens them to a consistent length (e.g., 5 seconds).

4.  **Mixing Phase**: The script iteratively mixes the pre-processed tracks. Each transition uses the advanced EQ fade algorithm to ensure sonic clarity. The tracks are mixed at their **original tempo** to preserve their natural feel.

5.  **Export Phase**: The final, single `AudioSegment` is exported to a high-quality MP3 file.

## Setup and Installation

### Prerequisites

-   **Python 3.7+**
-   **FFmpeg**: This is a critical system dependency that `pydub` relies on for handling audio formats.
   
    -   **Windows**: Download the binary from the [official FFmpeg website](https://ffmpeg.org/download.html), unzip it, and add the `bin` directory to your system's PATH.

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone <https://github.com/Dave-019/smooth-transition.git>
    cd python-dj-project
    ```

2.  **Create and activate a virtual environment:**
  
    -   On Windows:
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```

3.  **Install the required Python libraries:**
    Create a file named `requirements.txt` and add the following lines:
    ```
    pydub
    librosa
    numpy
    ```
    Then, install them with pip:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Add Your Music**: Place all the MP3 files you want to mix into the `songs_to_mix` folder. For best results, use at least 4-5 songs with a variety of musical keys.

2.  **Run the Mixer**: Execute the main script from your terminal:
    ```bash
    python main.py 
    ```

3.  **Listen**: The script will print its progress as it analyzes, reorders, and mixes the tracks. When it's finished, you will find your completed DJ set in the root directory, named `Your playlist.mp3` (or as configured in the script).

## Configuration

You can easily tweak the mixer's behavior by modifying the constants inside the script without needing to change the core logic.

Key parameters include:
-   `songs_folder`: The folder to read music from.
-   `intelligent_eq_mix()` parameters:
    -   `duration_ms`: The length of the crossfade in milliseconds.
    -   `crossover_freq`: The frequency that separates bass from mids/highs.
-   Silence trimming parameters inside the trimming functions.

## Future Improvements

-   **Command-Line Interface**: Implement `argparse` to allow users to specify folders, output names, and transition times via command-line arguments.

-   **Graphical User Interface (GUI)**: Build a simple front-end using a library like Tkinter or PyQt to allow users to drag-and-drop files and start the mix with a button click.

