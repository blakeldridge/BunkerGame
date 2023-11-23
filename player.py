import tkinter as tk
from tkinter import ttk
import weapons
import random
import math

# contains all the player's items / weapons and processes to use and display the ui
class Inventory:
    def __init__(self, player, canvas):
        self.player = player
        self.canvas = canvas
        self.ammo = 24
        self.bandages = 2

        self.weapon = weapons.Gun(self.player.x, self.player.y, self.canvas)
        # images for the ui
        self.bullet_image = tk.PhotoImage(file="Images/bullet_ui.png")
        self.bandages_image = tk.PhotoImage(file="Images/bandages_ui.png")

    def get_gun_angle(self):
        return self.weapon.angle

    def check_ammo(self):
        return self.weapon.check_ammo()

    def use_bandage(self):
        # if the player has bandages, increase their health by 15
        if self.bandages > 0:
            self.player.increase_health(15)
            self.bandages -= 1

    def use_weapon(self):
        self.weapon.remaining_ammo -= 1

    def reload_weapon(self):
        # if the player has ammo in inventory left
        # increase the ammo to max ammo
        if self.ammo > 0:
            weapon_mag_size = self.weapon.get_mag_size()
            if self.ammo >= weapon_mag_size:
                extra = self.weapon.reload(weapon_mag_size)
                self.ammo -= weapon_mag_size - extra
            # if not enough ammo for full clip, only fill up to max possible
            else:
                extra = self.weapon.reload(self.ammo)
                self.ammo = extra

    def collect_item(self, item_type):
        # if item is collected, check type and add to inventory
        if item_type == "ammo":
            self.ammo += self.weapon.get_mag_size()
        elif item_type == "bandage":
            self.bandages += 1

    def display_ui(self, swidth, sheight):
        # display current magazine, image of shotgun shell, remaining total bullets {bottom right}
        self.weapon.display_ammo(swidth, sheight)
        self.canvas.create_image(swidth-65, sheight-30, image=self.bullet_image, anchor="center")
        self.canvas.create_text(swidth-30, sheight-30, text=str(self.ammo), justify="right", fill="gray", font=("Courier", 20, "bold"))
        # display current weapon equiped (melee or gun) slot and bandages slot {bottom left}
        self.canvas.create_image(70, sheight-50, image=self.bandages_image, anchor="center")
        self.canvas.create_text(35, sheight-50, text=str(self.bandages), font=("Courier", 20, "bold"), fill="white", anchor="center")

    def update_weapon(self, pointerx, pointery):
        self.weapon.update_gun(self.player, pointerx, pointery)

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

        self.speed = 10
        self.bullet_speed = 50

        self.shoot_frame = 100
        self.shoot_available = True
        self.damage_lower = 12
        self.damage_upper = 18 

        self.damage_buffer = 0

        self.melee_attack = False
        self.melee_damage = 15

        self.health = 100
        self.healthbar_value = tk.IntVar()
        style = ttk.Style()
        style.theme_use('clam') 
        style.configure("2.Horizontal.TProgressbar", background='red')
        self.healthbar = ttk.Progressbar(variable=self.healthbar_value, mode="determinate", style="2.Horizontal.TProgressbar")
        self.healthbar.place(x=self.swidth//2 - self.swidth//8, y=self.sheight-30, width=self.swidth//4)

        self.inventory = Inventory(self, self.canvas)

    def get_save_info(self):
        return [self.health, self.inventory.weapon.remaining_ammo, self.inventory.ammo, self.inventory.bandages]

    def get_damage(self):
        return random.randint(self.damage_lower, self.damage_upper)

    def check_ammo(self):
        return self.inventory.check_ammo()

    def increase_health(self, health):
        # increases health (not over max health)
        self.health += health
        if self.health > 100:
            self.health = 100

    def collect_item(self, item_type):
        self.inventory.collect_item(item_type)
    
    def load_save_info(self, saved_info):
        self.health = saved_info[0]
        self.inventory.weapon.remaining_ammo = saved_info[1]
        self.inventory.ammo = saved_info[2]
        self.inventory.bandages = saved_info[3]

    # check for all keys pressed
    def key_pressed(self, event, bindings):
        char = event.char
        # move character right if right is pressed
        if char == bindings["Move Right"] and not self.melee_attack:
            self.direction = "right"
            self.velx = self.speed
        # move character left if left is pressed
        elif char == bindings["Move Left"] and not self.melee_attack:
            self.direction = "left"
            self.velx = -self.speed
        # if reload is pressed, reload the weapon
        elif char == bindings["Reload"]:
            self.inventory.reload_weapon()
        # if bandage is used, heal player
        elif char == bindings["Heal"]:
            self.inventory.use_bandage()
        # if player presses melee attack, make player melee
        elif char == bindings["Melee"] and not self.melee_attack:
            # make player stand still
            #starts melee attack
            self.melee_attack = True
            self.velx = 0
            self.current_animation_frame = 6
            self.frame_change = 1

    # when key is released handle movement so that player stops
    def key_released(self, event, bindings):
        char = event.keysym
        # if player was moving right and right is released
        if char == bindings["Move Right"] and self.direction == "right":
            # stop movement
            self.direction = None
            self.velx = 0
            self.current_animation_frame = 1
        # if player was moving left and left is released
        elif char == bindings["Move Left"] and self.direction == "left":
            # stop movement
            self.direction = None
            self.velx = 0
            self.current_animation_frame = 1
        # give infinite ammo if user presses cheats button
        elif char == bindings["Cheats"]:
            self.inventory.ammo = 1000

    # get arguements for when shooting bullets (based on the angle that the gun is facing)
    def get_bullet_args(self):
        # get angle of gun
        angle = math.radians(self.inventory.get_gun_angle())
        # calculate the velocity of the bullet (so that it is always constant)
        bullet_velx = self.bullet_speed * math.sin(angle)
        bullet_vely = self.bullet_speed * math.cos(angle)
        # check which direction the gun is aiming
        # alter the bullet velocity to the opposite
        # otherwise does not shoot in a full circle
        if self.inventory.weapon.aiming_up:
            return self.x, self.inventory.weapon.y, bullet_velx, bullet_vely, self.shoot_available
        else:
            return self.x, self.inventory.weapon.y, -bullet_velx, -bullet_vely, self.shoot_available
        
    def take_damage(self, damage):
        # check if player has recently taken damage
        # if so, dont take damage
        # if they havent, take damage and begin the damage buffer
        if self.damage_buffer <= 0:
            self.health -= damage
            if self.health < 0:
                self.health = 0

            self.damage_buffer = 8

    def check_dead(self):
        return self.health == 0

    def get_player_movement(self):
        return self.velx

    # updates healthbar each time player is healed or damaged
    def update_healthbar(self):
        self.healthbar_value.set(self.health)

    def taken_shot(self):
        self.shoot_available = False
        self.inventory.use_weapon()

    # movement code for when player moves past the edge boundary (stops moving in the center of screen)
    def move(self, edge_status):
        # if player is at the right edge
        if edge_status == "right":
            # move right (unless at the edge of the screen)
            if self.x < self.swidth-100:
                self.x += self.speed
        else:
            # move left (unless at edge of screen)
            if self.x > 100:
                self.x -= self.speed

    def display_inventory(self, swidth, sheight):
        self.inventory.display_ui(swidth, sheight)

    # function that gets the current animation image to play
    def get_current_image(self, pointer_dir, spawner):
        # if player is currently doing a melee attack
        if self.melee_attack:
            # get the current frame in the animtaion
            current_image = tk.PhotoImage(file=f"Images/player_{pointer_dir}_attack/frame_{self.current_animation_frame}.png")
            # change the frame to the next one every 3 game loops
            if self.frame_change % 3 == 0:
                self.current_animation_frame += 1
                # if in the current attack frame (peak of animation) check if hit any enemies
                if self.current_animation_frame == 7:
                    spawner.melee_attack(pointer_dir)
                # if animation has finished, reset variables and allow player to move again
                if self.current_animation_frame >= 11:
                    self.melee_attack = False
                    self.current_animation_frame = 1
                    self.frame_change = 1
                else:
                    self.frame_change += 1
        # if player is currently moving (right or left)
        elif self.direction == "right" or self.direction == "left":#
            # get the current imgae of the animation
            current_image = tk.PhotoImage(file=f"Images/player_{pointer_dir}_walking/frame_{self.current_animation_frame}.png")
            # if player is moving backwards, move animation backwards
            if self.direction == "right" and pointer_dir == "left" or self.direction == "left" and pointer_dir == "right":
                if self.frame_change % 4 == 0:
                    if self.current_animation_frame <= 1:                
                        self.current_animation_frame = 8
                    else:
                        self.current_animation_frame -= 1
                    self.frame_change = 1
            # if player is moving forwards, move animation forwards
            else:
                if self.frame_change % 4 == 0:
                    if self.current_animation_frame >= 8:                
                        self.current_animation_frame = 1
                    else:
                        self.current_animation_frame += 1
                    self.frame_change = 1
        # if not moving at all, current image is the idle image
        else:
            current_image = tk.PhotoImage(file=f"Images/player_{pointer_dir}_idle.png")

        return current_image

    def update_player(self, pointerx, pointery, spawner):
        # increases damage buffer and timing for when the animation changes
        self.damage_buffer -= 1
        self.frame_change += 1
        # if mouse is on the right of the player, set the direction for the images
        # get the current animation image
        if pointerx > self.x:
            pointer_dir = "right"
            self.current_image = self.get_current_image(pointer_dir, spawner)
        # if mouse is on left, set direction for images
        # get current animation images
        else:
            pointer_dir = "left"
            self.current_image = self.get_current_image(pointer_dir, spawner)
        # if melees attack, change x (as animation images have larger width) by offset
        if self.melee_attack and pointer_dir == "right":
            x = self.x + 50
        elif self.melee_attack and pointer_dir == "left":
            x = self.x - 50
        else:
            x = self.x
        # draw player image onto screen.
        self.canvas.create_image(x, self.y, image=self.current_image, anchor="s")
        # increase the shoot frame so that the gun only shoots once every few frames (simulates fire rate)
        if not self.shoot_available:
            self.shoot_frame += 1
            if self.shoot_frame % 10 == 0:
                self.shoot_available = True
                self.shoot_frame = 1

        # if melee, dont update the gun (so its not drawn on the screen)
        if not self.melee_attack:
            self.inventory.update_weapon(pointerx, pointery)