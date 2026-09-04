import json
import os
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILENAME = os.path.join(BASE_DIR, "levels.json")

def load_levels():
    if not os.path.exists(FILENAME):
        return []
    if os.path.getsize(FILENAME) == 0:
        return []
    try:
        with open(FILENAME, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_levels(levels):
    for i, lvl in enumerate(levels):
        lvl["position"] = i + 1
    with open(FILENAME, "w", encoding="utf-8") as f:
        json.dump(levels, f, indent=4)

class TVLAdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TVL Admin Panel (Desktop GUI)")
        self.root.geometry("780x540")
        self.root.minsize(700, 480)
        
        self.levels = load_levels()

        # --- Layout Frames ---
        left_frame = ttk.Frame(root, padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_frame = ttk.Frame(root, padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Left Side: Level List & Reordering ---
        ttk.Label(left_frame, text="Current Levels (List Order)", font=("Fira Sans", 11, "bold")).pack(anchor="w", pady=5)
        
        self.listbox = tk.Listbox(left_frame, font=("Fira Sans", 10), height=18, selectmode=tk.SINGLE)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        # Reorder / Delete buttons frame
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="▲ Move Up", command=self.move_up).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(btn_frame, text="▼ Move Down", command=self.move_down).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(btn_frame, text="+ Add Record", command=self.open_record_window).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(btn_frame, text="🗑 Delete", command=self.delete_level).pack(side=tk.LEFT, expand=True, padx=2)

        # --- GitHub Sync Button at bottom left ---
        git_frame = ttk.Frame(left_frame)
        git_frame.pack(fill=tk.X, pady=5)
        ttk.Button(git_frame, text="☁️ Push / Publish to GitHub", command=self.push_to_github).pack(fill=tk.X)

        # --- Right Side: Add Level Form ---
        ttk.Label(right_frame, text="Add New Level", font=("Fira Sans", 11, "bold")).pack(anchor="w", pady=5)

        ttk.Label(right_frame, text="Level Name:").pack(anchor="w")
        self.name_entry = ttk.Entry(right_frame, width=28)
        self.name_entry.pack(anchor="w", pady=2)

        ttk.Label(right_frame, text="Creator:").pack(anchor="w")
        self.creator_entry = ttk.Entry(right_frame, width=28)
        self.creator_entry.pack(anchor="w", pady=2)

        ttk.Label(right_frame, text="Verifier:").pack(anchor="w")
        self.verifier_entry = ttk.Entry(right_frame, width=28)
        self.verifier_entry.pack(anchor="w", pady=2)

        ttk.Label(right_frame, text="YouTube Video Link:").pack(anchor="w")
        self.video_entry = ttk.Entry(right_frame, width=28)
        self.video_entry.pack(anchor="w", pady=2)

        ttk.Label(right_frame, text="Difficulty:").pack(anchor="w")
        self.diff_combobox = ttk.Combobox(right_frame, values=[
            "Extreme Demon", "Insane Demon", "Hard Demon", "Medium Demon", "Easy Demon"
        ], state="readonly", width=25)
        self.diff_combobox.set("Extreme Demon")
        self.diff_combobox.pack(anchor="w", pady=2)

        ttk.Button(right_frame, text="Save New Level", command=self.add_level).pack(anchor="w", pady=15)

        self.refresh_listbox()

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for i, lvl in enumerate(self.levels):
            display_text = f"#{i+1} - {lvl['name']} by {lvl['creator']} ({lvl['difficulty']})"
            self.listbox.insert(tk.END, display_text)

    def add_level(self):
        name = self.name_entry.get().strip()
        creator = self.creator_entry.get().strip()
        verifier = self.verifier_entry.get().strip()
        video = self.video_entry.get().strip()
        difficulty = self.diff_combobox.get()

        if not name or not creator:
            messagebox.showerror("Error", "Level Name and Creator cannot be empty!")
            return

        new_level = {
            "position": len(self.levels) + 1,
            "name": name,
            "creator": creator,
            "verifier": verifier if verifier else "Unknown",
            "video": video,
            "difficulty": difficulty,
            "records": []
        }

        self.levels.append(new_level)
        save_levels(self.levels)
        self.refresh_listbox()

        # Clear inputs
        self.name_entry.delete(0, tk.END)
        self.creator_entry.delete(0, tk.END)
        self.verifier_entry.delete(0, tk.END)
        self.video_entry.delete(0, tk.END)
        messagebox.showinfo("Success", "Level added locally!")

    def move_up(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Select a level to move.")
            return
        idx = selected[0]
        if idx > 0:
            self.levels[idx], self.levels[idx - 1] = self.levels[idx - 1], self.levels[idx]
            save_levels(self.levels)
            self.refresh_listbox()
            self.listbox.selection_set(idx - 1)

    def move_down(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Select a level to move.")
            return
        idx = selected[0]
        if idx < len(self.levels) - 1:
            self.levels[idx], self.levels[idx + 1] = self.levels[idx + 1], self.levels[idx]
            save_levels(self.levels)
            self.refresh_listbox()
            self.listbox.selection_set(idx + 1)

    def delete_level(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Select a level to delete.")
            return
        idx = selected[0]
        lvl_name = self.levels[idx]['name']
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{lvl_name}'?"):
            self.levels.pop(idx)
            save_levels(self.levels)
            self.refresh_listbox()

    def push_to_github(self):
        try:
            subprocess.run(["git", "add", "levels.json"], cwd=BASE_DIR, check=True)
            subprocess.run(["git", "commit", "-m", "Auto-update levels.json via TVL Admin GUI"], cwd=BASE_DIR, capture_output=True, text=True)
            
            push_result = subprocess.run(["git", "push"], cwd=BASE_DIR, capture_output=True, text=True)
            
            if push_result.returncode != 0 and "no upstream branch" in push_result.stderr:
                branch_res = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=BASE_DIR, capture_output=True, text=True, check=True)
                branch_name = branch_res.stdout.strip()
                subprocess.run(["git", "push", "--set-upstream", "origin", branch_name], cwd=BASE_DIR, check=True)
                messagebox.showinfo("Success", f"Linked branch '{branch_name}' and successfully published levels.json to GitHub!")
            elif push_result.returncode != 0:
                raise subprocess.CalledProcessError(push_result.returncode, push_result.args, push_result.stdout, push_result.stderr)
            else:
                messagebox.showinfo("Success", "Successfully published levels.json to GitHub! Your live site will update shortly.")
                
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            messagebox.showerror("Git Error", f"Failed to push to GitHub:\n{error_msg}")
        except FileNotFoundError:
            messagebox.showerror("Error", "Git is not installed or not found in your system PATH.")

    def open_record_window(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Select a level to add a record to.")
            return
        idx = selected[0]
        
        rec_win = tk.Toplevel(self.root)
        rec_win.title(f"Add Record to #{idx+1} {self.levels[idx]['name']}")
        rec_win.geometry("320x280")
        rec_win.grab_set()

        ttk.Label(rec_win, text="Player Name:").pack(anchor="w", padx=10, pady=2)
        player_entry = ttk.Entry(rec_win, width=35)
        player_entry.pack(padx=10, pady=2)

        ttk.Label(rec_win, text="Proof Video Link:").pack(anchor="w", padx=10, pady=2)
        video_entry = ttk.Entry(rec_win, width=35)
        video_entry.pack(padx=10, pady=2)

        ttk.Label(rec_win, text="Refresh Rate (e.g. 360Hz):").pack(anchor="w", padx=10, pady=2)
        hz_entry = ttk.Entry(rec_win, width=35)
        hz_entry.insert(0, "360Hz")
        hz_entry.pack(padx=10, pady=2)

        mobile_var = tk.BooleanVar()
        ttk.Checkbutton(rec_win, text="Mobile Player", variable=mobile_var).pack(anchor="w", padx=10, pady=8)

        def save_record():
            player = player_entry.get().strip()
            if not player:
                messagebox.showerror("Error", "Player name cannot be empty!")
                return
            
            new_record = {
                "player": player,
                "video": video_entry.get().strip(),
                "hz": hz_entry.get().strip() or "Unknown",
                "mobile": mobile_var.get()
            }

            if "records" not in self.levels[idx]:
                self.levels[idx]["records"] = []
            
            self.levels[idx]["records"].append(new_record)
            save_levels(self.levels)
            messagebox.showinfo("Success", "Record added locally!")
            rec_win.destroy()

        ttk.Button(rec_win, text="Save Record", command=save_record).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = TVLAdminApp(root)
    root.mainloop()