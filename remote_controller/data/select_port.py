from tkinter import *
from tkinter import ttk
from tkinter import messagebox

import serial
import sys
import glob


class SelectPort(Toplevel):

    def __init__(self, parent):

        super(SelectPort, self).__init__()

        self.parent = parent
        self.transient(self.parent)

        width = 300
        height = 100

        pos_x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (width // 2)
        pos_y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

        self.resizable(False, False)
        self.title("Select Floppy port")

        """if sys.platform == "win32":
            self.iconbitmap("data/Floppy_icon.ico")
        elif sys.platform == "linux":
            self.icon = Image("photo", file="data/Floppy_icon.png")
            self.tk.call("wm", "iconphoto", self._w, self.icon)"""

        # region Port
        port = Frame(self, highlightthickness=1, highlightbackground="black")
        Label(port, text="Select port: ", anchor=W).grid(column=0, row=0, sticky=E, pady=5, padx=5)

        self.combo_box = ttk.Combobox(port, state="readonly", takefocus=0, width=10)
        self.serial_ports()

        self.combo_box.bind("<FocusIn>", self.connect_button)

        self.combo_box.grid(column=1, row=0, sticky=W)

        port.columnconfigure(0, weight=1)
        port.columnconfigure(1, weight=1)
        port.rowconfigure(0, weight=1)

        port.grid(column=0, row=0, columnspan=2, sticky=N+S+E+W, padx=10, pady=10)
        # endregion

        ttk.Button(self, text="Refresh", takefocus=False, command=self.serial_ports).grid(column=0, row=1, sticky=N+S+E+W, padx=10, pady=5)
        self.connect_button = ttk.Button(self, text="Connect", takefocus=False, state=DISABLED, command=self.connect)
        self.connect_button.grid(column=1, row=1, sticky=N+S+E+W, padx=10, pady=5)

        self.bind("<Return>", lambda e: self.connect())

        for i in range(2):
            self.columnconfigure(i, weight=1)
        self.rowconfigure(0, weight=1)

        self.protocol("WM_DELETE_WINDOW", self.close)

        self.focus_set()
        self.grab_set()

    def connect_button(self, event=None):

        """Enable connect button if port selected."""

        # Force focus to avoid blue selection on combobox.
        self.focus_set()

        if self.combo_box.get() != "":
            self.connect_button.config(state=NORMAL)

    def serial_ports(self):

        """Lists available serial port names."""

        if sys.platform == "win32":
            ports = ["COM%s" % (i + 1) for i in range(256)]
        elif sys.platform == "linux":
            ports = glob.glob("/dev/tty[A-Za-z]*")
        else:
            raise EnvironmentError("Unsupported platform")

        result = list()
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass

        self.combo_box.config(values=result)

    def connect(self):

        """If a port is selected, close this window and connect to the board."""

        if self.combo_box.get() == "":
            messagebox.showwarning("Warning", "No port selected. Please select one.")
        else:
            self.parent.connect(self.combo_box.get())
            self.destroy()

    def close(self):

        """If close button is pressed, destroy parent window"""

        self.parent.destroy()
