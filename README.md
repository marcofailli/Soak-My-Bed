<p align="center">
  <img src="https://raw.githubusercontent.com/marcofailli/Soak-My-Bed/main/banner.png?v=2" width="100%" alt="Soak My Bed Banner">
</p>

---

<h1 align="center"><strong>SOAK MY BED</strong></h1>

<p align="center">
  <strong>The definitive Klipper tool for thermal stability analysis.</strong>
</p>

---

### 📘 What is Soak My Bed?
All 3D printer beds and frames undergo physical deformation as they heat up (thermal drift). **Soak My Bed** eliminates the guessing game. Instead of relying on a random timer, this tool measures physical movement in real-time. It visualizes exactly when your printer reaches thermal equilibrium, ensuring a perfect Z-offset every time.

### ✨ Key Features
* **Full Automation:** Continuous `BED_MESH_CALIBRATE` loops with automated data logging.
* **Smart Naming:** Files are saved as `YYYYMMDD_HHMMSS_XXC_YYm` for easy tracking.
* **Real-time Feedback:** Live console updates showing elapsed time, scan count, and stabilization countdown.
* **Universal Compatibility:** Dynamic path detection for Pi, Biqu, Sovol, and Creality OS.
* **Visual Analytics:** Generates 3D animations (GIF) and stability curves automatically.
* **Instant Abort:** Use `ABORT_SOAK` to stop and instantly generate a report of the data collected so far.

---

### 🚀 Installation

1. **Clone the repository**:
    ```bash
    cd ~
    git clone [https://github.com/marcofailli/soak-my-bed.git](https://github.com/marcofailli/soak-my-bed.git)
    ```
2. **Run the installer**:
    ```bash
    cd soak-my-bed
    chmod +x install.sh
    ./install.sh
    ```
3. **Configure Klipper**: Add this to your `printer.cfg`:
    ```ini
    [soak_my_bed]
    ```
4. **Enable Updates**: Add this block to your `moonraker.conf` to see updates in Fluidd/Mainsail:
    ```ini
    [update_manager soak-my-bed]
    type: git_repo
    path: ~/soak-my-bed
    origin: [https://github.com/marcofailli/soak-my-bed.git](https://github.com/marcofailli/soak-my-bed.git)
    primary_branch: main
    install_script: install.sh
    managed_services: klipper
    ```

---

### 🛠️ Usage

Perform your standard homing routine (`G28`, `Z_TILT`, etc.) before starting. It is recommended to start with a **cold** printer to capture the full thermal expansion curve.

#### Commands
* `SOAK_MY_BED TEMPERATURE=100 DURATION=60`
  * Heats to 100°C and analyzes stability for 60 minutes after reaching target.
* `SOAK_MY_BED`
  * Default settings: 60°C for 10 minutes.
* `SOAK_MY_BED TEMPERATURE=110 DURATION=45 MESH_COMMAND="BED_MESH_CALIBRATE METHOD=rapid_scan"`
  * **Advanced:** Override temperature, duration, and the specific mesh macro.
* `ABORT_SOAK`
  * Halts the process, shuts down heaters, and triggers immediate plot generation.

---

### 🖼️ Understanding the Results
After completion, check your `printer_data/config/soak_data` folder for the `.gif` and `.jpg` files.

* **Red Dashed Line (Vs Prev Mesh):** Represents instant stability. When this line flattens near zero, your printer has stopped moving.
* **Blue Line (Total Shift):** Shows the cumulative deformation. This explains why a first layer might fail if the soak is skipped!

---
<p align="center">
  Released under the MIT License. Created by <b>marcofailli</b>.
</p>
