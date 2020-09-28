from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from data.select_port import SelectPort

import serial
import time
import ast


class Floppy:

    def __init__(self):
        self._board = None

    def connect(self, port: str) -> None:
        self._board = serial.Serial(port, baudrate=115200)
        # self._board.flushInput()

    def flush(self) -> None:
        time.sleep(0.1)
        # self._board.flushInput()
        print(self.read_all())

    def send_command(self, command: str) -> None:
        self._board.flushInput()
        self._board.write((command + "\r").encode())

    def read_all(self) -> str:
        return self._board.read_all().decode()


class MainWindows(Tk):

    def __init__(self):

        super(MainWindows, self).__init__()

        self.title("Floppy Remote Controller - Alpha")
        self.geometry("375x325")
        self.resizable(False, False)

        self.move = Move(self)
        self.speed = Speed(self)
        self.grip = Grip(self)
        self.position = Position(self)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.update()
        # Start port popup
        SelectPort(self)

        self.mainloop()

    def connect(self, port: str) -> None:
        floppy.connect(port)

        self.move.stop()  # Prevent motors from moving.
        self.after(1000, self.update_position)

    def update_position(self):
        floppy.send_command("GET_POSITION")
        time.sleep(0.2)

        data = floppy.read_all()
        print(data)

        try:
            self.position.update_label(ast.literal_eval(data.split("\n")[1]))
        except:
            pass

        self.after(1000, self.update_position)


class Move(ttk.LabelFrame):

    def __init__(self, parent):

        super(Move, self).__init__(parent, labelwidget=ttk.Label(text="Move"))
        self.parent = parent

        axis_frame = Frame(self)

        ttk.Button(axis_frame, text="Homing", takefocus=False, command=self.homing).grid(column=0, row=0)
        ttk.Button(axis_frame, text="Reset", takefocus=False, command=self.reset).grid(column=1, row=0)

        for x, sign in enumerate(("-", "+")):
            for y, axis in enumerate(("X", "Y", "Z")):
                button = ttk.Button(axis_frame, text=axis + sign, takefocus=False)
                button.grid(column=x, row=y + 1)

                button.bind("<ButtonPress>", lambda _, a=axis + sign: self.moving(a))
                button.bind("<ButtonRelease>", self.stop)

        axis_frame.grid(column=0, row=0, padx=10, pady=10)

        mode_frame = Frame(self, highlightthickness=1, highlightbackground="black")
        self.mode = IntVar()

        ttk.Radiobutton(mode_frame, text="Jog", value=0, variable=self.mode, takefocus=False).grid(column=0, row=0, padx=3, pady=3, sticky=W)
        ttk.Radiobutton(mode_frame, text="Cartesian", value=1, variable=self.mode, takefocus=False).grid(column=0, row=1, padx=3, pady=3, sticky=W)

        mode_frame.grid(column=1, row=0, padx=10, pady=10)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.grid(column=0, row=0, columnspan=2, padx=5, pady=5, sticky=N+S+E+W)

    def homing(self):
        floppy.send_command(f"SET_SPEED={self.parent.speed.speed.get()}")
        floppy.send_command("HOMING")

    @staticmethod
    def reset():
        if messagebox.askokcancel("Warning", "Resetting position can produce unexpected moves. Especially for cartesian movements."):
            floppy.send_command("RESET_GRBL")

    def moving(self, axis):

        floppy.send_command(f"SET_SPEED={self.parent.speed.speed.get()}")

        if self.mode.get() == 0:
            # Jog mode
            if axis == "X+":
                floppy.send_command(f"JOG(10, 0, 0)")
            elif axis == "X-":
                floppy.send_command(f"JOG(-10, 0, 0)")
            elif axis == "Y+":
                floppy.send_command(f"JOG(0, 10, 0)")
            elif axis == "Y-":
                floppy.send_command(f"JOG(0, -10, 0)")
            elif axis == "Z+":
                floppy.send_command(f"JOG(0, 0, 10)")
            elif axis == "Z-":
                floppy.send_command(f"JOG(0, 0, -10)")
        elif self.mode.get() == 1:
            # Cartesian mode
            if axis == "X+":
                floppy.send_command(f"JOG_CART(-10, 0)")
            elif axis == "X-":
                floppy.send_command(f"JOG_CART(10, 0)")
            elif axis == "Y+":
                floppy.send_command(f"JOG_CART(0, 10)")
            elif axis == "Y-":
                floppy.send_command(f"JOG_CART(0, -10)")
            elif axis == "Z+":
                floppy.send_command(f"JOG(0, 0, 0.2)")
            elif axis == "Z-":
                floppy.send_command(f"JOG(0, 0, -0.2)")

        floppy.flush()

    def stop(self, _=None):
        if self.mode.get() == 0:
            floppy.send_command("JOG_CANCEL")
            floppy.flush()


class Speed(ttk.LabelFrame):

    def __init__(self, parent):
        super(Speed, self).__init__(parent, labelwidget=ttk.Label(text="Speed"))

        self.speed = IntVar()
        self.speed.set(50)

        Label(self, textvariable=self.speed).pack(expand=YES, fill=BOTH, padx=50)

        self.slider = ttk.Scale(self, from_=1, to=500, value=50, command=lambda s: self.speed.set(round(float(s))))
        self.slider.pack(expand=YES, fill=BOTH, padx=50, pady=5)

        self.grid(column=0, row=1, padx=5, pady=5, sticky=N+S+E+W)


class Grip(ttk.LabelFrame):

    def __init__(self, parent):
        super(Grip, self).__init__(parent, labelwidget=ttk.Label(text="Grip"))

        self.open = False

        self.grip_button = ttk.Button(self, text="CLOSE", takefocus=False, command=self.switch)
        self.grip_button.pack(expand=YES, fill=BOTH, padx=20, pady=5)

        self.spinbox = ttk.Spinbox(self, from_=1, to=100, width=5)
        self.spinbox.pack(padx=5, pady=5)

        self.grid(column=1, row=1, padx=5, pady=5, sticky=N+S+E+W)

    def switch(self) -> None:

        self.open = not self.open

        if not self.open:
            self.grip_button.config(text="CLOSE")
            floppy.send_command("GRIP=OPEN")
        else:
            self.grip_button.config(text="OPEN")
            print("GRIP=CLOSE" + str(self.spinbox.get()))
            floppy.send_command("GRIP=CLOSE" + str(self.spinbox.get()))

        floppy.flush()


class Position(ttk.LabelFrame):

    def __init__(self, parent):
        super(Position, self).__init__(parent, labelwidget=ttk.Label(text="Position"))

        self.position = (0.0, 0.0, 0.0)
        self.save_path = None
        self.point_nb = 0
        self.saving = False

        frame = Frame(self)
        self.label = Label(frame, text="X = 0.0 | Y = 0.0 | Z = 0.0")
        self.label.grid(column=0, row=0, padx=15, pady=5, sticky=N+S+E+W)

        ttk.Button(frame, text="Save Pos", takefocus=False, command=self.save_position).grid(column=1, row=0, pady=5, sticky=N+S+E+W)

        frame.pack()

        self.grid(column=0, row=2, columnspan=2, padx=5, pady=5, sticky=N+S+E+W)

    def update_label(self, pos: tuple) -> None:

        if self.saving and self.position != pos:
            self.label.config(fg="red")

        self.position = pos
        self.label.config(text=f"X = {self.position[0]} | Y = {self.position[1]} | Z = {self.position[2]}")

    def save_position(self) -> None:
        if self.save_path is None or len(self.save_path) < 1:
            self.save_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=(("Python file", "*.py"), ("All files", "*.*")))

        if len(self.save_path) > 0:
            self.point_nb += 1
            with open(self.save_path, "a") as file:
                file.write(f"joint{self.point_nb} = {self.position}\n")

            self.label.config(fg="blue")
            self.saving = True


if __name__ == "__main__":
    floppy = Floppy()
    MainWindows()
