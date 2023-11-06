import tkinter as tk
from PIL import Image, ImageTk

WIDTH, HEIGHT = 960, 540
SCORE = 1230

def resize_image(image_dir, width, height):
    image = Image.open(image_dir)
    return ImageTk.PhotoImage(image.resize((width, height), Image.NEAREST))

def callback(event):
    pass

def on_enter(event):
    event.widget.config(fg="yellow", font=("Courier", 25, "bold"))

def on_leave(event):
    event.widget.config(fg="white", font=("Courier", 20, "bold"))

window = tk.Tk()
window.geometry(f"{WIDTH}x{HEIGHT}")

game_over_frame = tk.Frame(width=WIDTH, height=HEIGHT, background="black")

game_over_image = resize_image("Images/main_menu_image.png", WIDTH//2, HEIGHT)
for index, text in enumerate(["Play Again", "Main Menu"]):
    original_y = 5*HEIGHT//7
    menu_btn = tk.Label(master=game_over_frame, text=text, fg="white", font=("Courier", 20, "bold"), background="black") 
    menu_btn.bind("<Button-1>", callback)
    menu_btn.bind("<Enter>", on_enter)
    menu_btn.bind("<Leave>", on_leave)
    menu_btn.place(x=3*WIDTH//4, y=original_y + 50*index, anchor="center")

title_label = tk.Label(master=game_over_frame, text="Game Over", fg="white", background="black", font=("Courier", 40, "bold"))
title_label.place(x=3*WIDTH//4, y=HEIGHT//5, anchor="center")

score_label = tk.Label(master=game_over_frame, text=f"Final Score: {SCORE}", fg="white", background="black", font=("Courier", 20, "bold"))
score_label.place(x=3*WIDTH//4, y=3*HEIGHT//7, anchor="center")

game_over_image_label = tk.Label(master=game_over_frame, image=game_over_image, background="black")
game_over_image_label.place(x=0, y=0)

game_over_frame.pack()
window.mainloop()