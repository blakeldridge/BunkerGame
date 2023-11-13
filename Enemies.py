import tkinter as tk
import random

WIDTH, HEIGHT = 960, 540

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

    def calculate_health(self, bunker_number):
        if bunker_number < 10:
            lower_range = 20 + bunker_number
            upper_range = 40 + bunker_number
        else:
            lower_range = 20 + bunker_number*1.5
            upper_range = 20 + bunker_number*1.5
        
        return lower_range, upper_range

    def __del__(self):
        pass

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return -1

    def attack(self, player):
        hit = False
        if self.attack_ready:
            self.attacking += 1
            if self.attacking >= self.attack_time:
                if self.x < player.x and self.x > player.x - 50 or self.x > player.x and self.x < player.x + 50:
                    player.take_damage(self.damage)
                    hit = True

                self.attack_ready = False
                self.attacking = 0

        if hit:
            return "hit_player"
        return ""

    def get_current_image(self):
        if self.velx != 0:
            current_image = tk.PhotoImage(file=f"Images/rat_{self.direction}_walking/frame_{self.current_animation}.png")
        else:
            current_image = tk.PhotoImage(file=f"Images/rat_idle_{self.direction}.png")

        if self.current_frame % 3 == 0:
            if self.current_animation >= 10:
                self.current_animation = 1
            else:
                self.current_animation += 1
            self.current_frame = 1
        self.current_frame += 1

        return current_image

    def update_enemy(self, player, player_movement):
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
        self.x += self.velx + player_movement
        self.canvas.create_image(self.x, self.y, image=self.image, anchor="s")
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

    def calculate_health(self, bunker_number):
        if bunker_number < 10:
            lower_range = 20 + bunker_number
            upper_range = 25 + bunker_number
        else:
            lower_range = 20 + bunker_number*1.5
            upper_range = 25 + bunker_number*1.5
        
        return lower_range, upper_range

    def __del__(self):
        pass

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return -1

    def attack(self, player):
        hit = False
        if self.attack_ready:
            self.attacking += 1
            if self.attacking >= self.attack_time:
                if self.x < player.x and self.x > player.x - 50 or self.x > player.x and self.x < player.x + 50:
                    player.take_damage(self.damage)
                    hit = True

                self.attack_ready = False
                self.attacking = 0
        if hit:
            return "hit_player"
        return ""

    def get_current_image(self):
        current_image = tk.PhotoImage(file=f"Images/bat_{self.direction}_flying/frame_{self.current_animation}.png")
        if self.frame_change % 2 == 0:
            if self.current_animation >= 7:
                self.current_animation = 1
            else:
                self.current_animation += 1
        self.frame_change += 1

        return current_image


    def update_enemy(self, player, player_movement):
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

        self.x += self.velx + player_movement
        self.y += self.bob_speed
        self.bob_dir += 1
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

    def calculate_health(self, bunker_number):
        if bunker_number < 10:
            lower_range = 40 + bunker_number
            upper_range = 50 + bunker_number
        else:
            lower_range = 40 + bunker_number*1.5
            upper_range = 50 + bunker_number*1.5
        
        return lower_range, upper_range

    def __del__(self):
        pass

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return -1

    def respawn(self):
        self.y = self.underground_y
        self.spawning = True
        self.x = random.randint(0, self.swidth)

    def update_enemy(self, player, player_movement):
        if self.spawning:
            if self.y == self.final_y:
                self.spawning = False
            else:
                self.y -= self.burrowing_speed

        self.x += player_movement
        if self.x > self.swidth+200 or self.x < -200:
            self.respawn()

        if self.x < player.x:
            self.direction = "right"
            self.image = tk.PhotoImage(file="Images/mole_idle_right.png")
        else:
            self.direction = "left"
            self.image = tk.PhotoImage(file="Images/mole_idle_left.png")

        self.canvas.create_image(self.x, self.y, image=self.image, anchor="s")
        self.attacking_frame += 1
        if self.attacking_frame %  self.attack_rate == 0:
            self.attacking_frame = 1
            return f"mole_attack_{self.direction}"