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
        self.image = tk.PhotoImage(file="Images/rat_enemy_right.png")
        lower, upper = self.calculate_health(bunker_number)
        self.health = random.randint(lower, upper)

        self.velx = 0
        self.speed = 3

        self.attack_ready = False
        self.attacking = 0
        self.attack_time = 60
        self.damage = 5

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
        if self.attack_ready:
            self.attacking += 1
            if self.attacking >= self.attack_time:
                if self.x < player.x and self.x > player.x - 50 or self.x > player.x and self.x < player.x + 50:
                    player.take_damage(self.damage)

                self.attack_ready = False
                self.attacking = 0

    def update_enemy(self, player, player_movement):
        if not self.attack_ready:
            if self.x > player.x + 50:
                self.image = tk.PhotoImage(file="Images/rat_enemy_left.png")
                self.velx = -self.speed
            elif self.x < player.x - 50:
                self.image = tk.PhotoImage(file="Images/rat_enemy_right.png")
                self.velx = self.speed
            else:
                self.attack_ready = True
                self.velx = 0
        else:
            self.velx = 0

        self.x += self.velx + player_movement
        self.attack(player)
        self.canvas.create_image(self.x, self.y, image=self.image, anchor="s")

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

        self.attack_ready = False
        self.attacking = 0
        self.attack_time = 60
        self.damage = 5

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
        if self.attack_ready:
            self.attacking += 1
            if self.attacking >= self.attack_time:
                if self.x < player.x and self.x > player.x - 50 or self.x > player.x and self.x < player.x + 50:
                    player.take_damage(self.damage)

                self.attack_ready = False
                self.attacking = 0

    def update_enemy(self, player, player_movement):
        if not self.attack_ready:
            if self.x > player.x + 50:
                self.image = tk.PhotoImage(file="Images/bat_left.png")
                self.velx = -self.speed
            elif self.x < player.x - 50:
                self.image = tk.PhotoImage(file="Images/bat_right.png")
                self.velx = self.speed
            else:
                self.attack_ready = True
                self.velx = 0
        else:
            self.velx = 0

        self.x += self.velx + player_movement
        self.attack(player)
        self.canvas.create_image(self.x, self.y, image=self.image, anchor="s")