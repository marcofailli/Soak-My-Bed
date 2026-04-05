import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.interpolate import griddata
import matplotlib.gridspec as gridspec
import json
import argparse
import os

def generate_soak_plot(json_path):
    if not os.path.exists(json_path):
        print(f"Error: File {json_path} not found.")
        return

    with open(json_path, 'r') as f:
        data = json.load(f)

    if not data:
        print("Error: No data found in JSON.")
        return

    times_raw = [d['time'] for d in data]
    temps = [d['temp'] for d in data]
    z_frames = [np.array(d['matrix']) for d in data]
    
    mesh_min = data[0].get('mesh_min', [0.0, 0.0])
    mesh_max = data[0].get('mesh_max', [300.0, 300.0])
    
    min_x, min_y = float(mesh_min[0]), float(mesh_min[1])
    max_x, max_y = float(mesh_max[0]), float(mesh_max[1])
    
    rows, cols = z_frames[0].shape
    
    points_x = np.linspace(min_x, max_x, cols)
    points_y = np.linspace(min_y, max_y, rows)
    X, Y = np.meshgrid(points_x, points_y)
    grid_x, grid_y = np.mgrid[min_x:max_x:100j, min_y:max_y:100j]

    avg_var_vs_first = []
    avg_var_vs_prev = []
    first_mesh = z_frames[0]
    
    for i in range(len(z_frames)):
        curr = z_frames[i]
        avg_var_vs_first.append(np.mean(np.abs(curr - first_mesh)))
        avg_var_vs_prev.append(0 if i == 0 else np.mean(np.abs(curr - z_frames[i-1])))

    plt.style.use('bmh')
    fig = plt.figure(figsize=(12, 10), facecolor='#ffffff')
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
    
    ax3d = fig.add_subplot(gs[0], projection='3d')
    ax2d = fig.add_subplot(gs[1])
    ax_temp = ax2d.twinx() 

    z_min_abs = np.min(z_frames)
    z_max_abs = np.max(z_frames)

    def update(frame):
        ax3d.clear()
        ax2d.clear()
        ax_temp.clear()
        
        ax3d.set_facecolor((1.0, 1.0, 1.0, 1.0))
        ax2d.set_facecolor((1.0, 1.0, 1.0, 1.0))
        
        curr_z = z_frames[frame]
        z_interp = griddata((X.flatten(), Y.flatten()), curr_z.flatten(), 
                            (grid_x, grid_y), method='cubic')
        
        surf = ax3d.plot_surface(grid_x, grid_y, z_interp, cmap='turbo',
                                 vmin=z_min_abs, vmax=z_max_abs,
                                 edgecolor='k', linewidth=0.1, alpha=0.8)
        
        m, s = divmod(int(times_raw[frame]), 60)
        stats = (f"Time: {m:02d}:{s:02d} | Temp: {temps[frame]:.1f}Â°C\n"
                 f"Deformation: {avg_var_vs_first[frame]:.4f}mm")
        
        ax3d.text2D(0.02, 0.85, stats, transform=ax3d.transAxes, family='monospace', bbox=dict(facecolor='white', alpha=0.7))
        
        padding = 0.05
        ax3d.set_zlim(z_min_abs - padding, z_max_abs + padding)
        ax3d.set_title("Bed Surface Deformation", pad=30)
        ax3d.set_xlabel('X (mm)', labelpad=10)
        ax3d.set_ylabel('Y (mm)', labelpad=10)
        ax3d.set_box_aspect((1.3, 1, 0.5))
        ax3d.view_init(elev=25, azim=-45)

        ax3d.xaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
        ax3d.yaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
        ax3d.zaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))

        time_mins = [t / 60.0 for t in times_raw[:frame+1]]
        p1, = ax2d.plot(time_mins, avg_var_vs_first[:frame+1], color='#1f77b4', label='Total Shift (mm)', linewidth=2)
        p2, = ax2d.plot(time_mins, avg_var_vs_prev[:frame+1], color='#d62728', linestyle='--', label='Instant Stability (mm)')
        p3, = ax_temp.plot(time_mins, temps[:frame+1], color='#ff7f0e', label='Bed Temp (Â°C)', linewidth=1.5, alpha=0.6)
        
        ax2d.set_xlim(0, max(times_raw) / 60.0)
        ax2d.set_ylim(0, max(0.05, max(avg_var_vs_first) * 1.1))
        ax_temp.set_ylim(min(temps)-2, max(temps)+2)
        
        ax2d.set_xlabel("Time (minutes)")
        ax2d.set_ylabel("Variation (mm)", color='#1f77b4')
        ax_temp.yaxis.set_label_position("right")
        ax_temp.yaxis.tick_right()
        ax_temp.set_ylabel("Temperature (Â°C)", color='#ff7f0e')
        
        lines = [p1, p2, p3]
        ax2d.legend(lines, [l.get_label() for l in lines], loc='center right', fontsize='small')
        
        return surf,

    # Generation
    ani = FuncAnimation(fig, update, frames=len(z_frames), interval=200)
    output_gif = json_path.replace('.json', '.gif')
    ani.save(output_gif, writer='pillow', fps=8)
    
    update(len(z_frames) - 1)
    output_jpg = json_path.replace('.json', '.jpg')
    plt.savefig(output_jpg, dpi=150, bbox_inches='tight', facecolor='white')

    # --- FINAL SUMMARY LOGS ---
    print("\n" + "="*50)
    print("SUCCESS: Visualization files generated!")
    print(f"GIF: {os.path.abspath(output_gif)}")
    print(f"JPG: {os.path.abspath(output_jpg)}")
    print("="*50 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    args = parser.parse_args()
    generate_soak_plot(args.input)
