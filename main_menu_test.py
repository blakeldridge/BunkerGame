import tkinter as tk
from PIL import Image, ImageTk

WIDTH, HEIGHT = 960, 540

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

main_menu_frame = tk.Frame(width=WIDTH, height=HEIGHT, background="black")

main_menu_image = resize_image("Images/main_menu_image.png", WIDTH//2, HEIGHT)
for index, text in enumerate(["Play","Load","Leaderboard","Options","Exit"]):
    original_y = 3*HEIGHT//7
    menu_btn = tk.Label(master=main_menu_frame, text=text, fg="white", font=("Courier", 20, "bold"), background="black") 
    menu_btn.bind("<Button-1>", callback)
    menu_btn.bind("<Enter>", on_enter)
    menu_btn.bind("<Leave>", on_leave)
    menu_btn.place(x=3*WIDTH//4, y=original_y + 50*index, anchor="center")

title_label = tk.Label(master=main_menu_frame, text="Nuclear\nWhiskers", fg="white", background="black", font=("Courier", 40, "bold"))
title_label.place(x=3*WIDTH//4, y=HEIGHT//5, anchor="center")

main_menu_image_label = tk.Label(master=main_menu_frame, image=main_menu_image, background="black")
main_menu_image_label.place(x=0, y=0)

main_menu_frame.pack()
window.mainloop()