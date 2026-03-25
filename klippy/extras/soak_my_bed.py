import logging
import time
import math
import os
import json
import subprocess

class SoakMyBed:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        self.reactor = self.printer.get_reactor()
        
        # --- Internal State ---
        self.is_running = False
        self.target_temp = 0.0
        self.duration_sec = None
        self.start_time = None
        self.temp_reached_time = None
        self.results = []
        
        # Register the timer in the Klipper reactor
        self.timer = self.reactor.register_timer(self._soak_tick)

        # Register G-Code commands for the user
        self.gcode.register_command("SOAK_MY_BED", self.cmd_SOAK_MY_BED,
                                    help="Start bed thermal profiling")
        self.gcode.register_command("CANCEL_SOAK", self.cmd_CANCEL_SOAK,
                                    help="Stop profiling and generate results")

    def cmd_SOAK_MY_BED(self, gcmd):
        """Start the automated soaking process."""
        if self.is_running:
            gcmd.respond_info("Soak My Bed is already running!")
            return

        # Fetch parameters from G-code command
        self.target_temp = gcmd.get_float('TEMP', 0.0)
        duration_min = gcmd.get_float('DURATION', -1.0)
        
        # Convert duration to seconds if provided
        self.duration_sec = duration_min * 60 if duration_min > 0 else None
        self.start_time = time.time()
        self.temp_reached_time = None
        self.results = []
        self.is_running = True

        gcmd.respond_info(f"Soak My Bed: Process started. Target: {self.target_temp}C")
        
        # Set bed temperature (M140 does not wait, allowing the loop to start)
        if self.target_temp > 0:
            self.gcode.run_script_from_command(f"M140 S{self.target_temp}")

        # Trigger the first tick immediately
        self.reactor.update_timer(self.timer, self.reactor.NOW)

    def _soak_tick(self, eventtime):
        """Main loop executed by the Klipper reactor timer."""
        if not self.is_running:
            return self.reactor.NEVER

        current_time = time.time()
        heater_bed = self.printer.lookup_object('heater_bed')
        bed_status = heater_bed.get_status(current_time)
        current_temp = bed_status['temperature']

        # --- CHECK COMPLETION CONDITIONS ---
        
        # Case A: Fixed duration reached
        if self.duration_sec and (current_time - self.start_time) >= self.duration_sec:
            self._finalize_soak("Target duration reached.")
            return self.reactor.NEVER
        
        # Case B: Smart stability (Target reached + 30 mins)
        if self.target_temp > 0 and self.temp_reached_time is None:
            if current_temp >= (self.target_temp - 0.5):
                self.temp_reached_time = current_time
                self.gcode.respond_info("Target temperature reached. Stability timer started (30m).")
        
        if self.temp_reached_time and (current_time - self.temp_reached_time) >= 1800:
            self._finalize_soak("Thermal stability achieved (30m soak).")
            return self.reactor.NEVER

        # --- EXECUTE BED MESH ---
        
        # Measure mesh duration to optimize the next interval
        mesh_start = time.time()
        self.gcode.run_script_from_command("BED_MESH_CALIBRATE")
        mesh_duration = time.time() - mesh_start

        # --- DATA CAPTURE ---
        
        # Access the bed_mesh object to retrieve the last probed matrix
        bed_mesh = self.printer.lookup_object('bed_mesh')
        try:
            # z_mesh contains the last captured matrix in Klipper
            z_matrix = bed_mesh.z_mesh
            self.results.append({
                'time': current_time - self.start_time,
                'temp': current_temp,
                'matrix': z_matrix
            })
        except Exception as e:
            logging.error(f"SoakMyBed Error: Could not retrieve mesh data. {str(e)}")

        # --- SCHEDULE NEXT TICK ---
        
        # Interval = Mesh duration + 10s safety buffer, rounded up to nearest 5s
        next_interval = math.ceil((mesh_duration + 10) / 5.0) * 5
        
        return eventtime + next_interval

    def _finalize_soak(self, reason):
        """Clean up state and trigger post-processing."""
        self.is_running = False
        self.gcode.respond_info(f"Soak My Bed: {reason}")
        
        # Safety: Turn off the bed heater
        self.gcode.run_script_from_command("M140 S0")
        
        self._save_and_plot()

    def cmd_CANCEL_SOAK(self, gcmd):
        """Manually stop the process and generate partial results."""
        if self.is_running:
            self._finalize_soak("Interrupted by user.")
        else:
            gcmd.respond_info("Soak My Bed: No process currently running.")

    def _save_and_plot(self):
        """Export data to JSON and launch the external Python plotter."""
        # Save JSON to the standard Klipper log directory
        log_path = os.path.expanduser("~/printer_data/logs/soak_my_bed_data.json")
        
        try:
            with open(log_path, 'w') as f:
                json.dump(self.results, f)
            
            # Paths for the external plotter and the Klipper virtualenv
            plotter_script = os.path.expanduser("~/soak-my-bed/scripts/plotter.py")
            venv_python = os.path.expanduser("~/klippy-env/bin/python")
            
            # Launch plotter in background to avoid blocking Klipper
            subprocess.Popen([venv_python, plotter_script, log_path])
            self.gcode.respond_info("Soak My Bed: Data saved. Generating animation...")
            
        except Exception as e:
            logging.error(f"SoakMyBed: Failed to save or plot results. {str(e)}")

def load_config(config):
    return SoakMyBed(config)
