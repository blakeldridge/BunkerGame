import tkinter as tk
import random
from PIL import Image, ImageTk

WIDTH, HEIGHT = 960, 540

def rotate_image(image_dir, angle, is_below):
    image = Image.open(image_dir)
    rotated_image = ImageTk.PhotoImage(image.rotate(angle if not is_below else angle+180, expand=True))
    return rotated_image

class RatEnemy:
    def __init__(self, x, y, bunker_number, canvas):
        self.x = x
        self.y = y - 20
        self.hitbox_width = 50
        self.hitbox_height = 110
        self.canvas = canvas
        self.image = tk.PhotoImage(file="Images/rat_idle_right.png")
        lower, upper = self.calculate_health(bunker_number)
        self.health = random.randint(lower, upper)

        self.velx = 0
        self.speed = 3

        self.attack_ready = False
        self.attacking = 0
        self.attack_time = 60
        self.damage = 5

        self.direction = "right"
        self.current_frame = 1
        self.current_animation = 1

    # function to determine the range of enemy health based on the level of bunker they are on
    def calculate_health(self, bunker_number):
        # increase range by 1 for first 10 bunker and 1.5x for the rest
        if bunker_number < 10:
            lower_range = 20 + bunker_number
            upper_range = 40 + bunker_number
        else:
            lower_range = 20 + bunker_number*1.5
            upper_range = 20 + bunker_number*1.5
        
        return lower_range, upper_range

    # function to remove from memory
    def __del__(self):
        pass

    # function to take health from enemy and check whether they are dead
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return -1

    # function with logic for attacking the player
    def attack(self, player):
        hit = False
        if self.attack_ready:
            self.attacking += 1
            # attacking takes 60 frames (stand still to attacking)
            if self.attacking >= self.attack_time:
                # if player is closer than 50 pixels of enemy, take damage
                if self.x < player.x and self.x > player.x - 50 or self.x > player.x and self.x < player.x + 50:
                    player.take_damage(self.damage)
                    hit = True

                self.attack_ready = False
                self.attacking = 0
        # return status of attack
        if hit:
            return "hit_player"
        return ""

    # function to get the current frame of animation
    def get_current_image(self):
        # if player is not standing still, get walking animation
        # else get idle animation
        if self.velx != 0:
            current_image = tk.PhotoImage(file=f"Images/rat_{self.direction}_walking/frame_{self.current_animation}.png")
        else:
            current_image = tk.PhotoImage(file=f"Images/rat_idle_{self.direction}.png")

        # update the frame of animation every 3 frames
        # reset frame to 1 once animation is finished to repeat walking cycle
        if self.current_frame % 3 == 0:
            if self.current_animation >= 10:
                self.current_animation = 1
            else:
                self.current_animation += 1
            self.current_frame = 1
        self.current_frame += 1

        return current_image

    # function to handle all enemy processes
    def update_enemy(self, player, player_movement):
        # move towards the player if not attacking
        if not self.attack_ready:
            # move up to 50 pixels(attacking range) of the player
            if self.x > player.x + 50:
                self.direction = "left"
                self.velx = -self.speed
            elif self.x < player.x - 50:
                self.direction = "right"
                self.velx = self.speed
            else:
                self.attack_ready = True
                self.velx = 0
        else:
            self.velx = 0

        # move enemy by speed and player movement
        # get and create image
        self.image = self.get_current_image()
        self.x += self.velx + player_movement
        self.canvas.create_image(self.x, self.y, image=self.image, anchor="s")
        # return status of attack
        return self.attack(player)

class BatEnemy:
    def __init__(self, x, y, bunker_number, canvas):
        self.x = x
        self.y = y - 1.5*HEIGHT//5

        self.hitbox_width = 50
        self.hitbox_height = 60
        self.canvas = canvas
        self.image = tk.PhotoImage(file="Images/bat_right.png")
        lower, upper = self.calculate_health(bunker_number)
        self.health = random.randint(lower, upper)

        self.velx = 0
        self.speed = 3
        self.bob_speed = 1
        self.bob_dir = 1

        self.attack_ready = False
        self.attacking = 0
        self.attack_time = 60
        self.damage = 5

        self.current_animation = 1
        self.frame_change = 1

    # function to determine the range of enemy health based on the level of bunker they are on
    def calculate_health(self, bunker_number):
        # increase range by 1 for first 10 bunker and 1.5x for the rest
        if bunker_number < 10:
            lower_range = 20 + bunker_number
            upper_range = 25 + bunker_number
        else:
            lower_range = 20 + bunker_number*1.5
            upper_range = 25 + bunker_number*1.5
        
        return lower_range, upper_range

    # function to remove from memory
    def __del__(self):
        pass

    # function to take health from enemy and check whether they are dead
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return -1

    # function with logic for attacking the player
    def attack(self, player):
        hit = False
        if self.attack_ready:
            self.attacking += 1
            # attacking takes 60 frames (stand still to attacking)
            if self.attacking >= self.attack_time:
                # if player is closer than 50 pixels of enemy, take damage
                if self.x < player.x and self.x > player.x - 50 or self.x > player.x and self.x < player.x + 50:
                    player.take_damage(self.damage)
                    hit = True

                self.attack_ready = False
                self.attacking = 0
        # return status of attack
        if hit:
            return "hit_player"
        return ""

    # function to get the current frame of animation
    def get_current_image(self):
        # get next frame of animation 
        current_image = tk.PhotoImage(file=f"Images/bat_{self.direction}_flying/frame_{self.current_animation}.png")
        # update frame of animation every 2 frames
        # if animation reaches final frame repeat cycle
        if self.frame_change % 2 == 0:
            if self.current_animation >= 7:
                self.current_animation = 1
            else:
                self.current_animation += 1
        self.frame_change += 1

        return current_image

    # function that deals with all the processes of the enemy
    def update_enemy(self, player, player_movement):
        # if not attacking, move towards the player
        if not self.attack_ready:
            if self.x > player.x + 50:
                self.direction = "left"
                self.velx = -self.speed
            elif self.x < player.x - 50:
                self.direction = "right"
                self.velx = self.speed
            else:
                self.attack_ready = True
                self.velx = 0
        else:
            self.velx = 0

        self.image = self.get_current_image()
        # move towards player
        self.x += self.velx + player_movement
        # bob speed used to have bat move up and down
        self.y += self.bob_speed
        self.bob_dir += 1
        # every 15 frames, switch direction of bob
        if self.bob_dir % 15 == 0:
            self.bob_speed = -self.bob_speed
        self.canvas.create_image(self.x, self.y, image=self.image, anchor="s")
        return self.attack(player)

class MoleEnemy:
    def __init__(self, x, y, bunker_number, canvas, swidth):
        self.x = x
        self.y = y + 15
        self.swidth = swidth

        self.hitbox_width = 65
        self.hitbox_height = 75
        self.canvas = canvas
        self.image = None
        lower, upper = self.calculate_health(bunker_number)
        self.health = random.randint(lower, upper)

        self.spawning = True
        self.underground_y = y + 15
        self.final_y = y - 15
        self.burrowing_speed = 2

        self.attacking_frame = 1
        self.attack_rate = 60

    # function to determine the range of enemy health based on the level of bunker they are on
    def calculate_health(self, bunker_number):
        # increase range by 1 for first 10 bunker and 1.5x for the rest
        if bunker_number < 10:
            lower_range = 40 + bunker_number
            upper_range = 50 + bunker_number
        else:
            lower_range = 40 + bunker_number*1.5
            upper_range = 50 + bunker_number*1.5
        
        return lower_range, upper_range

    # function to remove from memory
    def __del__(self):
        pass

    # function to take health from enemy and check whether they are dead
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return -1

    # if mole goes too far off screen, have him return back on screen
    def respawn(self):
        self.y = self.underground_y
        self.spawning = True
        self.x = random.randint(0, self.swidth)

    # function containing all the processes of the enemy
    def update_enemy(self, player, player_movement):
        # if spawning in, have the mole raise from the ground
        if self.spawning:
            if self.y == self.final_y:
                self.spawning = False
            else:
                self.y -= self.burrowing_speed
        # move the enemy according to player movement
        self.x += player_movement
        # if off screen, respawn
        if self.x > self.swidth+200 or self.x < -200:
            self.respawn()
        # get correct image of enemy depending to face the player
        if self.x < player.x:
            self.direction = "right"
            self.image = tk.PhotoImage(file="Images/mole_idle_right.png")
        else:
            self.direction = "left"
            self.image = tk.PhotoImage(file="Images/mole_idle_left.png")
        self.canvas.create_image(self.x, self.y, image=self.image, anchor="s")
        # check whether ready to attack and return the status
        self.attacking_frame += 1
        if self.attacking_frame %  self.attack_rate == 0:
            self.attacking_frame = 1
            return f"mole_attack_{self.direction}"

class BladeTrap:
    def __init__(self, x, y, canvas):
        self.x = x
        self.attacking_y = y - 30
        self.y = y + 50
        self.canvas = canvas
        self.image = None

        self.current_frame = 1

        self.end_of_attack_frame = 60

        self.final_frame = 70

        self.angle = 0
        self.move_speed = 10
        self.hitbox_width = 0

    # function to remove from memory
    def __del__(self):
        pass

    # rotate the image by current angle so that it gives the effect that the blade is spinning
    def get_blade_image(self):
        return rotate_image("Images/blade_trap.png", self.angle, False)

    # if player is within the blades hitbox, take damage
    def attack(self, player):
        if player.x > self.x - self.hitbox_width//2 and player.x < self.x + self.hitbox_width//2:
            player.take_damage(20)

    # handles all the processes of the enemy
    def update_enemy(self, player, player_movement):
        # move the trap according to the players movement
        self.x += player_movement
        self.current_frame += 1
        # if the blade is currently attacking
        if self.current_frame < self.end_of_attack_frame:
            self.image = self.get_blade_image()
            self.angle += 20
            # move the blade upwards if it is spawning in
            if self.y > self.attacking_y:
                self.y -= self.move_speed
                self.hitbox_width += 22
        # if the blade has finished attacking, move the blade down and despawn
        elif self.current_frame >= self.end_of_attack_frame and self.current_frame < self.final_frame:
            self.image = self.get_blade_image()
            self.angle += 20
            self.y += self.move_speed
            self.hitbox_width -= 60
        else:
            return "remove"

        # attack and draw image
        self.attack(player)
        self.canvas.create_image(self.x, self.y, image=self.image)