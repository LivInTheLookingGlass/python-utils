def file_dialog(*args, **kargs):
	import sys
	if sys.version_info[0] <= 2:
		import tkFileDialog, Tkinter
	else:
		import tkinter as Tkinter
		from tkinter import filedialog as tkFileDialog
	f = Tkinter.Tk()
	f.withdraw()
	ret = tkFileDialog.askopenfilename(*args, **kargs)
	f.destroy()
	return ret


def button_choice(choices, prompt=None):
	import sys, functools
	if sys.version_info[0] <= 2:
		import Tkinter as tk
	else:
		import tkinter as tk
	global choice
	choice = None

	def setchoice(c):
		global choice
		choice = c

	root = tk.Tk()
	if prompt:
		root.wm_title(str(prompt))
		text = tk.Label(root, text=str(prompt))
		text.pack(fill="x")
	buttons = [tk.Button(root, text=c, command=functools.partial(setchoice, c=c)) for c in choices]
	for button in buttons:
		button.pack(fill="x")

	def wait():
		if choice is None:
			root.after(5, wait)  # After five milliseconds, run the wait command
		else:
			root.destroy()

	root.after(5, wait)  # After five milliseconds, run the wait command
	root.mainloop()
	return choice


def prompt_warning(warn):
	import sys
	if sys.version_info[0] <= 2:
		import Tkinter as tk
	else:
		import tkinter as tk
	root = tk.Tk()
	root.wm_title("Warning")
	text = tk.Label(root, text=str(warn))
	text.pack(fill="x")
	cont = tk.Button(root, text="Continue", command=root.quit)
	cont.pack(fill="x")
	quit = tk.Button(root, text="Quit", command=exit)
	quit.pack(fill="x")
	root.mainloop()
	root.destroy()


def prompt(warn):
	import sys
	if sys.version_info[0] <= 2:
		import Tkinter as tk
	else:
		import tkinter as tk
	root = tk.Tk()
	root.wm_title("Warning")
	text = tk.Label(root, text=str(warn))
	text.pack(fill="x")
	cont = tk.Button(root, text="Continue", command=root.quit)
	cont.pack(fill="x")
	root.mainloop()
	root.destroy()
