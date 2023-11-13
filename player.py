import tkinter as tk
from tkinter import ttk
import weapons
import random
import math

class Player:
    def __init__(self, swidth, sheight, canvas):
        self.x = swidth//2
        self.y = 4*sheight//5 - 20

        self.swidth = swidth
        self.sheight = sheight

        self.dimensions = 15
        self.current_image = tk.PhotoImage(file="Images/player_right_idle.png")
        self.current_animation_frame = 1
        self.frame_change = 1
        self.canvas = canvas
        self.image = self.canvas.create_image(self.x, self.y, image=self.current_image, anchor="s")
        self.direction = None
        self.velx = 0

        self.hitbox_width = 60
        self.hitbox_height = 150

        self.speed = 8
        self.bullet_speed = 25

        self.shoot_frame = 100
        self.shoot_available = True
        self.damage_lower = 12
        self.damage_upper = 18 

        self.health = 1
        self.healthbar_value = tk.IntVar()
        style = ttk.Style()
        style.theme_use('clam') 
        style.configure("2.Horizontal.TProgressbar", background='red')
        self.healthbar = ttk.Progressbar(variable=self.healthbar_value, mode="determinate", style="2.Horizontal.TProgressbar")
        self.healthbar.place(x=self.swidth//2 - self.swidth//8, y=self.sheight-30, width=self.swidth//4)

        self.gun = weapons.Gun(self.x, self.y, self.canvas)

    def get_save_info(self):
        return [self.health]

    def get_damage(self):
        return random.randint(self.damage_lower, self.damage_upper)
    
    def load_save_info(self, saved_info):
        self.health = saved_info[0]

    def key_pressed(self, event, bindings):
        char = event.char
        if char == bindings["Move Right"]:
            self.direction = "right"
            self.velx = self.speed
        elif char == bindings["Move Left"]:
            self.direction = "left"
            self.velx = -self.speed
        elif char == bindings["Reload"]:
            self.gun.reload()

    def key_released(self, event, bindings):
        char = event.char
        if char == bindings["Move Right"] and self.direction == "right":
            self.direction = None
            self.velx = 0
            self.current_animation_frame = 1

        elif char == bindings["Move Left"] and self.direction == "left":
            self.direction = None
            self.velx = 0
            self.current_animation_frame = 1

    def get_bullet_args(self):
        angle = math.radians(self.gun.angle)
        bullet_velx = self.bullet_speed * math.sin(angle)
        bullet_vely = self.bullet_speed * math.cos(angle)
        if self.gun.aiming_up:
            return self.x, self.gun.y, bullet_velx, bullet_vely, self.shoot_available
        else:
            return self.x, self.gun.y, -bullet_velx, -bullet_vely, self.shoot_available
        
    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def check_dead(self):
        return self.health == 0

    def get_player_movement(self):
        return self.velx

    def update_healthbar(self):
        self.healthbar_value.set(self.health)

    def taken_shot(self):
        self.shoot_available = False
        self.gun.remaining_ammo -= 1

    def move(self, edge_status):
        if edge_status == "right":
            if self.x < self.swidth-100:
                self.x += self.speed
        else:
            if self.x > 100:
                self.x -= self.speed

    def get_current_image(self, pointer_dir):
        if self.direction == "right" or self.direction == "left":
            current_image = tk.PhotoImage(file=f"Images/player_{pointer_dir}_walking/frame_{self.current_animation_frame}.png")
            if self.direction == "right" and pointer_dir == "left" or self.direction == "left" and pointer_dir == "right":
                if self.frame_change % 4 == 0:
                    if self.current_animation_frame <= 1:                
                        self.current_animation_frame = 8
                    else:
                        self.current_animation_frame -= 1
                    self.frame_change = 1

            else:
                if self.frame_change % 4 == 0:
                    if self.current_animation_frame >= 8:                
                        self.current_animation_frame = 1
                    else:
                        self.current_animation_frame += 1
                    self.frame_change = 1
        else:
            current_image = tk.PhotoImage(file=f"Images/player_{pointer_dir}_idle.png")

        return current_image

    def update_player(self, pointerx, pointery):
        self.frame_change += 1
        if pointerx > self.x:
            self.current_image = self.get_current_image("right")
        else:
            self.current_image = self.get_current_image("left")

        self.canvas.create_image(self.x, self.y, image=self.current_image, anchor="s")
        if not self.shoot_available:
            self.shoot_frame += 1
            if self.shoot_frame % 10 == 0:
                self.shoot_available = True
                self.shoot_frame = 1

        self.gun.update_gun(self, pointerx, pointery)