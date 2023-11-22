import tkinter as tk
from PIL import Image, ImageTk
import random
import math

# rotates an image by an angle
def rotate_image(image_dir, angle, is_below):
    image = Image.open(image_dir)
    rotated_image = ImageTk.PhotoImage(image.rotate(angle if not is_below else angle+180, expand=True))
    return rotated_image

# projectile thrown by the mole enemy 
class PickaxeProjectile:
    def __init__(self, x, y, sheight, direction, canvas):
        self.x = x
        self.y = y
        self.canvas = canvas

        self.sheight = sheight
        self.damage = 15
        self.angle = 0

        self.hitbox_width = 25
        self.hitbox_height = 35

        self.image = tk.PhotoImage(file="Images/pickaxe_projectile.png")
        self.direction = direction
        if self.direction == "left":
            self.velx, self.vely = -18, -25
        else:
            self.velx, self.vely = 18, -25

        self.gravity = 2
        self.rotation_speed = 20

    # function to remove the object from memory
    def __del__(self):
        pass

    # rotates and gets the image
    def get_image(self):
        return rotate_image("Images/pickaxe_projectile.png", self.angle, False)

    # called each frame ofthe game loop holding all logic for the projectile
    def update_projectile(self, player_movement):
        # adjust by both the velocity and player movement
        # thrown in an arc and therefore applies gravity
        self.x += self.velx + player_movement
        self.y += self.vely
        self.vely += self.gravity

        # if the projectile goes off screen
        # indicate it must be removed
        if self.y >= 4*self.sheight//5 or self.y <= self.sheight//5:
            return -1

        # rotates the pickaxe in the same direction as it was thrown (to give a realistic effect)
        if self.direction == "left":
            self.angle += self.rotation_speed
        else:
            self.angle -= self.rotation_speed

        if self.angle >= 360:
            self.angle = 0

        # get and place the image
        self.image = self.get_image()
        self.canvas.create_image(self.x, self.y, image=self.image, anchor="s")

# bullet class used by the gun (weapon for the player)
class Bullet:
    def __init__(self, x, y, velx, vely, damage, canvas, swidth, sheight):
        self.swidth, self.sheight = swidth, sheight
        self.x = x
        self.y = y
        self.velx = velx
        self.vely = vely
        self.canvas = canvas
        self.image = tk.PhotoImage(file="Images/bullet.png")

        self.damage = damage

    # function used to remove the bullet from memory
    def __del__(self):
        pass

    # called each frame of the game loop to handle all bullet logic
    def update_bullet(self, player_movement):
        # continues moving the bullet in the correct direction
        # also affected by player movement
        self.x += self.velx + player_movement
        self.y += self.vely

        # if player moves outside of the bunker (hits ceiling or floor or too far right or left), remove from scene
        if self.x > self.swidth or self.x < 0 or self.y > 4*self.sheight//5 or self.y < self.sheight//5:
            return -1

        # create image onto screen
        self.canvas.create_image(self.x, self.y, image=self.image)

# class for the weapon used by the player
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

    def get_mag_size(self):
        return self.total_ammo

    # function to check if ammo is empty
    def check_ammo(self):
        if self.remaining_ammo > 0:
            return True
        return False
    
    # function used to reload the gun
    # takes in ammo that will be added
    def reload(self, ammo):
        # addes ammo to mag
        self.remaining_ammo += ammo
        # if this is greater than the mag size
        if self.remaining_ammo > self.total_ammo:
            # return the extra ammo (greater than the total mag)
            extra = self.remaining_ammo - self.total_ammo
            self.remaining_ammo = self.total_ammo
            return extra
        return 0
    
    # function to display the ammo ui on screen
    def display_ammo(self, swidth, sheight):
        # highlight text as red if out of ammo, else white
        if self.remaining_ammo == 0:
            colour = "red"
        else:
            colour = "white"
        # draw text on the screen
        self.canvas.create_text(swidth-100, sheight-30, text=str(self.remaining_ammo), justify="center", fill=colour, font=("Courier", 20, "bold"))

    # called each frame of the game loop handling all the logic of the weapon
    def update_gun(self, player, pointerx, pointery):
        # places the gun on the screen in the correct place
        self.x = player.x
        self.y = player.y-self.y_offset

        # checks whether the mouse is above the gun or not
        if pointery > self.y:
            self.aiming_up = True
        else:
            self.aiming_up = False

        # checks which direction the mouse is on
        # determines which image to use
        if pointerx > self.x:
            self.current_image = self.gun_image_dirs["gun_right"]
        else:
            self.current_image = self.gun_image_dirs["gun_left"]

        # calculate the angle (try statement just incase division by 0 error)
        # rotate the image
        try:
            self.angle = math.degrees(math.atan((pointerx-self.x)/(pointery-self.y)))
            self.current_image = rotate_image(self.current_image, self.angle, pointery>self.y)
        except:
            self.current_image = rotate_image(self.current_image, self.angle, pointery>self.y)

        # draw gun to the screen
        self.canvas.create_image(self.x, self.y, image=self.current_image)