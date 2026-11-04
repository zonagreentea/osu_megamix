import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import shutil

music = Path("music")

def upload():
    file = filedialog.askopenfilename(title="Upload")

    if file:
        source = Path(file)
        music.mkdir(exist_ok=True)
        shutil.copy2(source, music / source.name)

def download():
    file = filedialog.askopenfilename(
        title="Download",
        initialdir=music
    )

    if file:
        destination = filedialog.asksaveasfilename(
            title="Save as",
            initialfile=Path(file).name
        )

        if destination:
            shutil.copy2(file, destination)

root = tk.Tk()
root.title("osu!megamix")

tk.Button(root, text="Upload", command=upload).pack(
    padx=40, pady=10
)

tk.Button(root, text="Download", command=download).pack(
    padx=40, pady=10
)

root.mainloop()