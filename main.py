import sys
import tkinter as tk
from gui import AutoMinerGUI

def main():
    root = tk.Tk()
    app = AutoMinerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
