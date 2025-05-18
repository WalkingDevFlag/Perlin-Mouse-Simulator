# Perlin-Mouse-Simulator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python application that simulates human-like mouse movement from a starting point (A) to an ending point (B) on the screen. The movement is influenced by Perlin noise to create a more natural, less robotic path. The application features a Tkinter-based GUI for real-time visualization of the noise field, the path, and for configuring simulation parameters. The actual system mouse cursor is controlled using PyAutoGUI.

![Screenshot Placeholder](https://via.placeholder.com/700x400.png?text=Add+a+Screenshot+or+GIF+of+the+App+Here!)

## Features

*   **Perlin Noise-Based Movement:** Generates smooth, natural-looking random paths.
*   **Real-time Mouse Control:** Uses `pyautogui` to move the system mouse cursor.
*   **Interactive Tkinter GUI:**
    *   Visualize the Perlin noise field.
    *   Display start (A) and end (B) points.
    *   Draw the simulated mouse path in real-time.
    *   Configure parameters like noise scale, speed, jitter, deviation, and window size.
*   **Modular Code Structure:** Organized into `perlin_noise.py`, `app_gui.py`, and `main.py` within an `src/` directory for better maintainability.
*   **Configurable Parameters:** Adjust various aspects of the simulation via the GUI.
*   **Non-Blocking Simulation:** Mouse movement simulation runs in a separate thread to keep the GUI responsive.

## Requirements

*   Python 3.7+
*   Conda (for environment management)
*   Tkinter (usually included with Python standard library)
*   Pillow (PIL)
*   NumPy
*   PyAutoGUI

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/WalkingDevFlag/Perlin-Mouse-Simulator.git
    cd Perlin-Mouse-Simulator
    ```

2.  **Create and activate a Conda virtual environment (recommended):**
    ```bash
    conda create -n pms_env python=10
    conda activate pms_env
    ```

3.  **Install dependencies:**
    It's recommended to install PyAutoGUI via pip even in a Conda environment for the latest versions or if Conda channels are problematic. Other packages can be installed via Conda or pip.
    ```bash
    pip install -r requirements.txt
    # Or, if you prefer to install main packages via conda:
    # pip install pyautogui pillow numpy
    ```

## Usage

Run the main application script from the root directory of the project:

```bash
python src/main.py
```

This will launch the Tkinter GUI.
1.  Adjust configuration parameters on the right-hand panel if needed.
2.  Click "**Apply & Redraw All**" to apply new configurations and regenerate the noise field and A/B points.
3.  Click "**New A/B Points**" to randomly select new start and end points on the current noise field.
4.  Click "**Start Simulation**" to begin the mouse movement.
5.  Click "**Stop Simulation**" or press the **`Esc`** key to halt an ongoing simulation.
6.  Click "**Clear Drawn Path**" to remove the black path lines from the canvas.

## Project Structure

```
Perlin-Mouse-Simulato/
├── src/
│   ├── perlin_noise.py     # Contains the Perlin class for noise generation
│   ├── app_gui.py          # Contains the App class for GUI and simulation logic
│   └── main.py             # Main script to launch the application
├── requirements.txt        # Project dependencies
├── LICENSE                 # Project license (MIT)
└── README.md               # This file
```

## Configuration Parameters

The following parameters can be configured through the GUI:

*   **`win_w`, `win_h`**: Width and height of the application window.
*   **`noise_scale`**: Scale of the Perlin noise (higher values mean more zoomed-out/smoother noise).
*   **`res_scale`**: Resolution scale for generating the noise map (0.01 to 1.0). Lower values are faster to compute but less detailed.
*   **`speed_min`**: Minimum pixels moved per step.
*   **`speed_max_mul`**: Multiplier for additional speed derived from noise value.
*   **`jitter_mul`**: Multiplier for random jitter strength.
*   **`dev_deg`**: Maximum angular deviation (in degrees) influenced by noise.
*   **`sleep`**: Sleep time (in seconds) between mouse movement steps.

## Future Ideas / Improvements

*   [ ] Option to save/load configurations.
*   [ ] Click on canvas to set A and B points.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
