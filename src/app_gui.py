# app_gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import numpy as np
import threading
import time
import random
import math
import pyautogui

from perlin_noise import Perlin # Import from the local module

class App:
    """
    Main application class for the Perlin Noise Mouse Simulator.
    Handles GUI, configuration, and simulation logic.
    """
    # Constants for drawing
    POINT_RADIUS = 6
    POINT_OUTLINE_WIDTH = 3
    PATH_LINE_WIDTH = 2
    # Minimal distance (squared) to target for stopping, e.g., 0.5 pixels
    MIN_DISTANCE_TO_TARGET_SQUARED = 0.5 * 0.5


    def __init__(self, root: tk.Tk):
        """
        Initializes the application.
        Args:
            root: The main tkinter window.
        """
        self.root = root
        root.title("Perlin Noise Mouse Simulator")

        # --- Default Configs ---
        self.cfg = {
            "win_w": 1920, "win_h": 1080,
            "noise_scale": 100.0,
            "res_scale": 1,
            "speed_min": 30, "speed_max_mul": 1.5,
            "jitter_mul": 20,
            "dev_deg": 35.0,
            "sleep": 0.03
            # "target_threshold" is now removed
        }
        self.running = False
        self.perlin = Perlin()
        self.A: tuple[float, float] | None = None
        self.B: tuple[float, float] | None = None
        self.noise_arr: np.ndarray | None = None
        self.noise_img: ImageTk.PhotoImage | None = None
        self._resize_job: str | None = None


        self.mainframe = ttk.Frame(root)
        self.mainframe.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(self.mainframe, bg="white", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        cfgframe = ttk.LabelFrame(self.mainframe, text="Configurations")
        cfgframe.grid(row=0, column=1, sticky="ns", padx=10, pady=10)
        
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)

        self.entries: dict[str, tk.Variable] = {}
        self.config_widgets: list[ttk.Entry] = []

        # Define the order and presence of GUI configuration entries
        self.gui_config_order = [
            "win_w", "win_h", "noise_scale", "res_scale",
            "speed_min", "speed_max_mul", "jitter_mul", "dev_deg", "sleep"
        ]

        current_gui_row = 0
        for k in self.gui_config_order:
            if k not in self.cfg: continue 
            default_val = self.cfg[k]
            ttk.Label(cfgframe, text=k).grid(row=current_gui_row, column=0, sticky="w", pady=2, padx=5)
            var_type = tk.IntVar if k in ("win_w", "win_h") else tk.DoubleVar
            var = var_type(value=default_val)
            ent = ttk.Entry(cfgframe, textvariable=var, width=10)
            ent.grid(row=current_gui_row, column=1, pady=2, padx=5, sticky="ew")
            self.entries[k] = var
            self.config_widgets.append(ent)
            current_gui_row += 1

        # --- Buttons ---
        self.apply_btn = ttk.Button(cfgframe, text="Apply & Redraw All", command=self.apply_config_and_redraw)
        self.apply_btn.grid(row=current_gui_row, column=0, columnspan=2, pady=(10,5), sticky="ew")
        current_gui_row +=1

        self.new_ab_btn = ttk.Button(cfgframe, text="New A/B Points", command=self._generate_and_draw_new_ab_points)
        self.new_ab_btn.grid(row=current_gui_row, column=0, columnspan=2, pady=5, sticky="ew")
        current_gui_row +=1

        self.clear_path_btn = ttk.Button(cfgframe, text="Clear Drawn Path", command=self.clear_drawn_path)
        self.clear_path_btn.grid(row=current_gui_row, column=0, columnspan=2, pady=5, sticky="ew")
        current_gui_row +=1
        
        self.start_btn = ttk.Button(cfgframe, text="Start Simulation", command=self.start_simulation)
        self.start_btn.grid(row=current_gui_row, column=0, columnspan=2, pady=5, sticky="ew")
        current_gui_row +=1
        
        self.stop_btn = ttk.Button(cfgframe, text="Stop Simulation", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_btn.grid(row=current_gui_row, column=0, columnspan=2, pady=5, sticky="ew")

        self.simulation_control_buttons = [self.apply_btn, self.new_ab_btn, self.start_btn, self.clear_path_btn]

        root.bind("<Escape>", self.stop_simulation)
        root.bind("<Configure>", self.handle_resize)

        root.geometry(f"{int(self.cfg['win_w'])}x{int(self.cfg['win_h'])}")
        self.root.update_idletasks() 
        self._refresh_canvas_environment()
        self._update_ui_state()

    def _validate_config(self) -> bool:
        try:
            cfg_values = {}
            for k_entry in self.gui_config_order: # Validate only GUI entries
                cfg_values[k_entry] = self.entries[k_entry].get()

            if not (100 <= cfg_values["win_w"] <= 8000 and 100 <= cfg_values["win_h"] <= 8000):
                raise ValueError("Window dimensions out of reasonable range (e.g., 100-8000 W/H).")
            if not (0.0001 < cfg_values["noise_scale"]):
                raise ValueError("Noise scale must be positive and greater than a very small threshold.")
            if not (0.01 <= cfg_values["res_scale"] <= 1.0):
                raise ValueError("Resolution scale must be between 0.01 and 1.0.")
            if not (0 <= cfg_values["speed_min"]):
                raise ValueError("Speed min must be non-negative.")
            if not (0 <= cfg_values["speed_max_mul"]):
                raise ValueError("Speed max multiplier must be non-negative.")
            if not (0 <= cfg_values["jitter_mul"]):
                raise ValueError("Jitter multiplier must be non-negative.")
            if not (0.0 <= cfg_values["sleep"] < 1.0):
                raise ValueError("Sleep time must be non-negative and ideally < 1.0s.")
            # No target_threshold to validate
            return True
        except tk.TclError as e:
            messagebox.showerror("Validation Error", f"Invalid numeric input for a field: {e}")
            return False
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            return False

    def apply_config_and_redraw(self):
        if not self._validate_config():
            return

        for k, var in self.entries.items(): # self.entries only contains GUI editable cfgs
            self.cfg[k] = var.get()

        new_geo_w = int(self.cfg['win_w'])
        new_geo_h = int(self.cfg['win_h'])
        
        if new_geo_w != self.root.winfo_width() or new_geo_h != self.root.winfo_height():
             self.root.geometry(f"{new_geo_w}x{new_geo_h}")
        
        self.root.update_idletasks() 
        self._refresh_canvas_environment()

    def _refresh_canvas_environment(self):
        self.stop_simulation() 
        self.canvas.delete("all")
        
        self.root.update_idletasks()

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        if w <= 1 or h <= 1: 
            if hasattr(self, "_initial_refresh_retry_job") and self._initial_refresh_retry_job:
                self.root.after_cancel(self._initial_refresh_retry_job)
            self._initial_refresh_retry_job = self.root.after(50, self._refresh_canvas_environment)
            return

        self._generate_noise_texture(w, h)
        self._draw_noise_on_canvas()
        self._generate_and_draw_new_ab_points(specific_canvas_wh=(w,h))

    def _generate_noise_texture(self, canvas_w: int, canvas_h: int):
        rs = self.cfg["res_scale"]
        noise_map_w = max(1, int(canvas_w * rs))
        noise_map_h = max(1, int(canvas_h * rs))

        self.noise_arr = self.perlin.noise_array(noise_map_w, noise_map_h, self.cfg["noise_scale"])
        
        img_array = np.clip(self.noise_arr * 255, 0, 255).astype(np.uint8)
        img = Image.fromarray(img_array, mode="L")
        
        resized_img = img.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS if hasattr(Image.Resampling, 'LANCZOS') else Image.LANCZOS)
        self.noise_img = ImageTk.PhotoImage(resized_img)

    def _draw_noise_on_canvas(self):
        if self.noise_img:
            self.canvas.create_image(0, 0, anchor="nw", image=self.noise_img, tags="noise_background")

    def _generate_and_draw_new_ab_points(self, specific_canvas_wh: tuple[int, int] | None = None):
        self.stop_simulation() 

        self.canvas.delete("point_a_oval")
        self.canvas.delete("point_b_oval")
        self.clear_drawn_path() 

        if specific_canvas_wh:
            w, h = specific_canvas_wh
        else:
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
        
        if w <= 0 or h <= 0: return

        padding = self.POINT_RADIUS + 5 
        self.A = (random.uniform(padding, w - padding), random.uniform(padding, h - padding))
        self.B = (random.uniform(padding, w - padding), random.uniform(padding, h - padding))
        self._draw_ab_points()

    def _draw_ab_points(self):
        if self.A and self.B:
            r, lw = self.POINT_RADIUS, self.POINT_OUTLINE_WIDTH
            self.canvas.create_oval(self.A[0]-r, self.A[1]-r, self.A[0]+r, self.A[1]+r,
                                     outline="red", width=lw, tags="point_a_oval")
            self.canvas.create_oval(self.B[0]-r, self.B[1]-r, self.B[0]+r, self.B[1]+r,
                                     outline="blue", width=lw, tags="point_b_oval")
    
    def clear_drawn_path(self):
        self.canvas.delete("path_line")

    def handle_resize(self, event: tk.Event):
        if event.widget != self.root or self.running:
            return
        if self._resize_job:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(250, self._refresh_canvas_environment)

    def _update_ui_state(self):
        is_running = self.running
        for widget in self.config_widgets:
            widget.config(state=tk.DISABLED if is_running else tk.NORMAL)
        for btn in self.simulation_control_buttons:
            btn.config(state=tk.DISABLED if is_running else tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL if is_running else tk.DISABLED)
        self.clear_path_btn.config(state=tk.DISABLED if is_running else tk.NORMAL)

    def start_simulation(self):
        if self.running: return
        if not self.A or not self.B or self.noise_arr is None:
            messagebox.showinfo("Setup Needed", "A/B points & noise not ready. Try 'Apply & Redraw'.")
            return
            
        self.running = True
        self._update_ui_state()
        self.clear_drawn_path() 
        
        threading.Thread(target=self._simulate_mouse_movement, daemon=True).start()

    def stop_simulation(self, event=None):
        if self.running:
            self.running = False
            # Simulation thread will call _update_ui_state on exit.

    def _simulate_mouse_movement(self):
        if not self.A or not self.B or self.noise_arr is None:
            self.running = False
            self.root.after(0, self._update_ui_state)
            return

        cfg_copy = self.cfg.copy() 

        try:
            canvas_x_on_screen = self.root.winfo_rootx() + self.canvas.winfo_x()
            canvas_y_on_screen = self.root.winfo_rooty() + self.canvas.winfo_y()
            
            Ax_canvas, Ay_canvas = self.A
            Bx_canvas, By_canvas = self.B
            
            start_screen_x = canvas_x_on_screen + Ax_canvas
            start_screen_y = canvas_y_on_screen + Ay_canvas

            pyautogui.moveTo(start_screen_x, start_screen_y, duration=0)
            
            current_canvas_x, current_canvas_y = Ax_canvas, Ay_canvas
            
            self.canvas.create_line(current_canvas_x, current_canvas_y, current_canvas_x, current_canvas_y,
                                    fill="black", width=self.PATH_LINE_WIDTH, tags="path_line", capstyle=tk.ROUND)

            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            if canvas_width <=0 or canvas_height <=0 or self.noise_arr is None: # Check for valid state
                self.running = False
                self.root.after(0, self._update_ui_state)
                return

            noise_map_h, noise_map_w = self.noise_arr.shape

            while self.running:
                dx_to_target = Bx_canvas - current_canvas_x
                dy_to_target = By_canvas - current_canvas_y
                dist_to_target_sq = dx_to_target*dx_to_target + dy_to_target*dy_to_target

                # 1. Check if already at or very near target
                if dist_to_target_sq < self.MIN_DISTANCE_TO_TARGET_SQUARED:
                    next_cx, next_cy = Bx_canvas, By_canvas # Snap to target
                else:
                    # Calculate noise-influenced step
                    norm_x = np.clip(current_canvas_x / canvas_width, 0.0, 0.99999)
                    norm_y = np.clip(current_canvas_y / canvas_height, 0.0, 0.99999)
                    ix = int(norm_x * noise_map_w)
                    iy = int(norm_y * noise_map_h)
                    noise_val = float(self.noise_arr[iy, ix])

                    speed = cfg_copy["speed_min"] + noise_val * cfg_copy["speed_max_mul"]
                    jitter_x = (random.random() - 0.5) * noise_val * cfg_copy["jitter_mul"]
                    jitter_y = (random.random() - 0.5) * noise_val * cfg_copy["jitter_mul"]
                    deviation = (noise_val - 0.5) * math.radians(cfg_copy["dev_deg"])
                    
                    angle_to_target = math.atan2(dy_to_target, dx_to_target)
                    move_angle = angle_to_target + deviation

                    # Tentative step components
                    step_dx = math.cos(move_angle) * speed + jitter_x
                    step_dy = math.sin(move_angle) * speed + jitter_y
                    step_len_sq = step_dx*step_dx + step_dy*step_dy

                    # 2. Check if this step would overshoot
                    if step_len_sq >= dist_to_target_sq : # Overshoot or exact reach with this step
                        next_cx, next_cy = Bx_canvas, By_canvas # Snap to target
                    else:
                        # Take the calculated step
                        next_cx = current_canvas_x + step_dx
                        next_cy = current_canvas_y + step_dy
                
                # Move real mouse & draw segment
                pyautogui.moveTo(canvas_x_on_screen + next_cx, canvas_y_on_screen + next_cy, duration=0)
                
                # Only draw if there's a change in position to avoid zero-length lines
                if abs(current_canvas_x - next_cx) > 1e-6 or abs(current_canvas_y - next_cy) > 1e-6:
                    self.canvas.create_line(current_canvas_x, current_canvas_y, next_cx, next_cy,
                                            fill="black", width=self.PATH_LINE_WIDTH, tags="path_line", capstyle=tk.ROUND)
                
                current_canvas_x, current_canvas_y = next_cx, next_cy

                # 3. Check if we have arrived at B
                if current_canvas_x == Bx_canvas and current_canvas_y == By_canvas:
                    break 
                
                time.sleep(cfg_copy["sleep"])
                if not self.running: break # Allow external stop

        except pyautogui.PyAutoGUIException as e:
            print(f"PyAutoGUI Error during simulation: {e}")
            self.root.after(0, lambda: messagebox.showerror("Simulation Error", f"Mouse control error: {e}"))
        except Exception as e:
            import traceback
            print(f"Unexpected error in simulation: {e}\n{traceback.format_exc()}")
            self.root.after(0, lambda: messagebox.showerror("Simulation Error", f"An unexpected error occurred: {e}"))
        finally:
            self.running = False
            self.root.after(0, self._update_ui_state)