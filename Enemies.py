import tkinter as tk
import random

class RatEnemy:
    def __init__(self, x, y, canvas):
        self.x = x
        self.y = y + 20
        self.hitbox_width = 50
        self.hitbox_height = 110
        self.canvas = canvas
        self.image = tk.PhotoImage(file="Images/rat_enemy_right.png")

        self.health = random.randint(20,40)

        self.velx = 0
        self.speed = 3

        self.attack_ready = False
        self.attacking = 0
        self.attack_time = 60
        self.damage = 5

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
        self.canvas.create_image(self.x, self.y, image=self.image)