import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import shutil

def upload():
    file = filedialog.askopenfilename(
        title="Upload"
    )

    if not file:
        return

    source = Path(file)
    destination = Path("music") / source.name

    destination.parent.mkdir(exist_ok=True)
    shutil.copy2(source, destination)

root = tk.Tk()
root.title("osu!megamix")

tk.Button(
    root,
    text="Upload",
    command=upload
).pack(padx=40, pady=40)

root.mainloop()