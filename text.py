import tkinter as tk

WIDTH, HEIGHT = 500, 500

def main_menu_screen():
    canvas.config(background="white")
    canvas.create_image(0, 0, image=player_right)
    canvas.create_image(WIDTH//2, 0, image=foreground)

window = tk.Tk()
player_right = tk.PhotoImage(file="Images/player_right.png")
foreground = tk.PhotoImage(file="Images/foreground.png")
menu_options = tk.Frame()
for index, text in enumerate(["Play","Load","Options","Exit"]):
    original_y = HEIGHT//3
    menu_btn = tk.Button(text=text)
    menu_btn.place(x=2*WIDTH//3, y=original_y + 50*index)

window.geometry(f"{WIDTH}x{HEIGHT}")
#canvas = tk.Canvas(width=WIDTH, height=HEIGHT, background="white")
#canvas.pack()
menu_options.pack()
window.mainloop()