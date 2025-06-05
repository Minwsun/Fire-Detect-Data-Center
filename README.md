

Fire Alarm Simulation Project

This project simulates a fire detection system using **SimulIDE** for the Arduino circuit and a **Python** GUI for the user interface. Communication is handled via a virtual COM port created by **VSPE**.

Prerequisites

Ensure you have the following software installed:

1.  VSPE (Virtual Serial Ports Emulator):** To create a virtual COM port pair.
2.  SimulIDE: To run the Arduino simulation file (`Fire.sim1`).
3.  Python 3: Along with required libraries (`PyQt5`, `pyserial`).
    bash
    pip install PyQt5 pyserial


How to Run

Follow these steps in order to run the project:

1. Create Virtual COM Port

Open VSPE.
Load the provided `brige.vspe` configuration file, which creates a COM port pair (e.g., COM1 <=> COM2).
Click the **Start Emulation** (green Play button).

2. Run the SimulIDE Simulation

Open SimulIDE.
Load the circuit file `Fire.sim1`.
Click the Power On Circuit** button.
IMPORTANT: After starting the simulation, right-click the serial port component in the circuit and select **"Open"** to enable the connection.

3. Launch the GUI

Open your terminal or command prompt.
Navigate to the project directory.
Run the main GUI script:
    bash
    python fire_detect_GUI.py

In the application, select the other virtual COM port (e.g., COM2) and click **"Connect"**.

The system is now operational. The GUI will display an alert when a fire is detected in the simulation.



Note

You must open the port connection in SimulIDE** after powering on the simulation for the application to work correctly.
