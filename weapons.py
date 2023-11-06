import tkinter as tk
from PIL import Image, ImageTk
import random
import math

def rotate_image(image_dir, angle, is_below):
    image = Image.open(image_dir)
    rotated_image = ImageTk.PhotoImage(image.rotate(angle if not is_below else angle+180, expand=True))
    return rotated_image

class Bullet:
    def __init__(self, x, y, velx, vely, canvas, swidth, sheight):
        self.swidth, self.sheight = swidth, sheight
        self.x = x
        self.y = y
        self.velx = velx
        self.vely = vely
        self.canvas = canvas
        self.image = tk.PhotoImage(file="Images/bullet.png")

        self.damage = random.randint(12,18)

    def __del__(self):
        pass

    def update_bullet(self, player_movement):
        self.x += self.velx + player_movement
        self.y += self.vely

        if self.x > self.swidth or self.x < 0 or self.y > self.sheight-100 or self.y < 100:
            return -1

        self.canvas.create_image(self.x, self.y, image=self.image)

class Gun:
    def __init__(self, x, y, canvas):
        self.x = x
        self.y = y
        self.y_offset = 90
        self.canvas = canvas
        self.gun_image_dirs = {"gun_right":"Images/gun_right.png", "gun_left":"Images/gun_left.png"}
        self.current_image = self.gun_image_dirs["gun_right"]

        self.aiming_up = False

        self.angle = 0

        self.total_ammo = 12
        self.remaining_ammo = self.total_ammo

    def check_ammo(self):
        if self.remaining_ammo > 0:
            self.remaining_ammo -= 1
            return True
        return False
    
    def reload(self):
        self.remaining_ammo = self.total_ammo
    
    def display_ammo(self, swidth, sheight):
        self.canvas.create_text(swidth-100, sheight-30, text=f"{self.remaining_ammo}/{self.total_ammo}", justify="center", fill="white", font=("Courier", 20, "bold"))

    def update_gun(self, player, pointerx, pointery):
        self.x = player.x
        self.y = player.y-self.y_offset

        if pointery > self.y:
            self.aiming_up = True
        else:
            self.aiming_up = False

        if pointerx > self.x:
            self.current_image = self.gun_image_dirs["gun_right"]
        else:
            self.current_image = self.gun_image_dirs["gun_left"]

        try:
            self.angle = math.degrees(math.atan((pointerx-self.x)/(pointery-self.y)))
            self.current_image = rotate_image(self.current_image, self.angle, pointery>self.y)
        except:
            self.current_image = rotate_image(self.current_image, self.angle, pointery>self.y)

        self.canvas.create_image(self.x, self.y, image=self.current_image)
