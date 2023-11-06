import tkinter as tk
from tkinter.font import Font
from tkinter import ttk
from PIL import ImageTk, Image
import Enemies, effects, bunker, weapons
import math
import random

WIDTH, HEIGHT = 750, 500
FRAME_TIME = 30
BULLET_SPEED = 25

def check_collision(object1, object2):
    if object1.x > object2.x-object2.hitbox_width//2 and object1.x < object2.x+object2.hitbox_width//2 and object1.y > object2.y-object2.hitbox_height//2 and object1.y < object2.y+object2.hitbox_height//2:
        return True
    return False

class Player:
    def __init__(self, canvas):
        self.x = WIDTH//2
        self.y = 300
        self.dimensions = 15
        self.current_image = tk.PhotoImage(file="Images/player_right.png")
        self.canvas = canvas
        self.image = self.canvas.create_image(self.x, self.y, image=self.current_image)
        self.direction = None
        self.velx = 0

        self.speed = 8

        self.health = 1
        self.healthbar_value = tk.IntVar()
        style = ttk.Style()
        style.theme_use('clam') 
        style.configure("2.Horizontal.TProgressbar", background='red')
        self.healthbar = ttk.Progressbar(variable=self.healthbar_value, mode="determinate", style="2.Horizontal.TProgressbar")
        self.healthbar.place(x=WIDTH//2 - WIDTH//8, y=HEIGHT-30, width=WIDTH//4)

        self.gun = weapons.Gun(self.x, self.y, self.canvas)

    def key_pressed(self, event):
        char = event.char
        if char == "d":
            self.direction = "right"
            self.velx = self.speed
        elif char == "a":
            self.direction = "left"
            self.velx = -self.speed

        elif char == "r":
            self.gun.reload()

    def key_released(self, event):
        char = event.char
        if char == "d" and self.direction == "right":
            self.direction = None
            self.velx = 0

        elif char == "a" and self.direction == "left":
            self.direction = None
            self.velx = 0

    def get_bullet_args(self):
        angle = math.radians(self.gun.angle)
        bullet_velx = BULLET_SPEED * math.sin(angle)
        bullet_vely = BULLET_SPEED * math.cos(angle)
        if self.gun.aiming_up:
            return self.x, self.gun.y, bullet_velx, bullet_vely
        else:
            return self.x, self.gun.y, -bullet_velx, -bullet_vely
        
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

    def update_player(self, pointerx, pointery):
        if pointerx > self.x:
            self.current_image = tk.PhotoImage(file="Images/player_right.png")
        else:
            self.current_image = tk.PhotoImage(file="Images/player_left.png")

        self.canvas.create_image(self.x, self.y, image=self.current_image)

        self.gun.update_gun(self, pointerx, pointery)

class GameManager:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Bunker Game")
        self.window.geometry(f"{WIDTH}x{HEIGHT}")
        self.canvas = tk.Canvas(width=WIDTH, height=HEIGHT, background="black")

        self.player = Player(self.canvas)

        self.DAMAGE_FONT = Font(
            family="Courier",
            size=15,
            weight="bold"
        )

        self.bunker_count = 0
        self.current_bunker = bunker.Bunker(self.canvas, HEIGHT)

        self.fading_animation_active = False
        self.current_fade = 0
        self.fades = ["gray12", "gray25", "gray50", "gray75", "gray100", "gray100", "gray75", "gray50", "gray25", "gray12"]
        self.fading_frames = 5

        self.bullets = []
        self.enemies = [Enemies.RatEnemy(WIDTH+300, 300, self.canvas)]
        self.effects = []

        self.score = 0

        self.game_over = False
        self.game_over_frame = tk.Frame(background="black")
    
    def reset_bunker(self):
        self.fading_animation_active = False
        self.current_fade = 0
        self.bunker_count += 1
        self.score += 100
        self.enemies.append(Enemies.RatEnemy(random.choice([WIDTH+200, -200]), 300, self.canvas))

    def on_key_pressed(self, event):
        self.player.key_pressed(event)
        if event.char == "e" and self.current_bunker.check_bunker_completed() and not self.fading_animation_active:
            self.fading_animation_active = True

    def on_key_released(self, event):
        self.player.key_released(event)

    def on_mouse_pressed(self, event):
        if self.player.gun.check_ammo():
            bullet_x, bullet_y, bullet_vel_x, bullet_vel_y = self.player.get_bullet_args()
            self.bullets.append(weapons.Bullet(bullet_x, bullet_y, bullet_vel_x, bullet_vel_y, self.canvas, WIDTH, HEIGHT))

    def display_bunker_completed(self):
        self.canvas.create_text(WIDTH//2, HEIGHT//2, text="Bunker Completed\nE descend", justify="center", fill="white", font=("Courier", 25, "bold"))

    def call_each_frame(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 100, WIDTH, HEIGHT-100, fill="#497325")
        player_movement = -self.player. get_player_movement()
        edge_status = self.current_bunker.check_at_edge(WIDTH)
        if edge_status == "right" and player_movement < 0:
            player_movement = 0
        elif edge_status == "left" and player_movement > 0:
            player_movement = 0
            
        self.current_bunker.camera_move_foreground(player_movement)
        pointerx = self.window.winfo_pointerx() - self.window.winfo_rootx()
        pointery = self.window.winfo_pointery() - self.window.winfo_rooty()
        
        for bullet in reversed(self.bullets):
            if bullet.update_bullet(player_movement) == -1:
                self.bullets.remove(bullet)
                del bullet
            else:
                for enemy in reversed(self.enemies):                    
                    if check_collision(bullet, enemy):
                        self.effects.append(effects.DamagePopUp(enemy.x, enemy.y-enemy.hitbox_height//2, str(bullet.damage), self.DAMAGE_FONT, self.canvas))

                        if enemy.take_damage(bullet.damage) == -1:
                            self.enemies.remove(enemy)
                            del enemy
                            self.current_bunker.enemy_killed()
                            self.score += 10
                            if not self.current_bunker.check_bunker_completed():
                                self.enemies.append(Enemies.RatEnemy(random.choice([WIDTH+200, -200]), 300, self.canvas))

                        self.bullets.remove(bullet)
                        del bullet
                        break

        for enemy in reversed(self.enemies):
            enemy.update_enemy(self.player, player_movement)

        self.player.update_player(pointerx, pointery)

        self.current_bunker.draw_foreground()

        for effect in reversed(self.effects):
            if effect.update_effect(player_movement) == -1:
                self.effects.remove(effect)
                del effect            

        if self.current_bunker.check_bunker_completed():
            self.display_bunker_completed()

        if self.fading_animation_active:
            if self.current_fade < len(self.fades)*self.fading_frames - self.fading_frames:
                self.current_fade += 1
            else:
                self.reset_bunker()

            if self.fades[self.current_fade//self.fading_frames] == "gray100":
                self.current_bunker = bunker.Bunker(self.canvas, HEIGHT)
                self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="black")
            else:
                self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="black", stipple=self.fades[self.current_fade//self.fading_frames])

        self.player.update_healthbar()
        self.player.gun.display_ammo(WIDTH, HEIGHT)
        self.canvas.create_text(WIDTH//2, 25, text=f"Score: {self.score}", justify="center", font=("Courier", 15, "bold"), fill="white")
        if self.player.check_dead():
            self.game_over_screen()

        if not self.game_over:
            self.window.after(FRAME_TIME, self.call_each_frame)

    def start_game(self):
        self.game_over = False
        self.game_over_frame.destroy()
        self.canvas = tk.Canvas(width=WIDTH, height=HEIGHT, background="black")

        self.player = Player(self.canvas)

        self.bunker_count = 0
        self.current_bunker = bunker.Bunker(self.canvas, HEIGHT)
        self.bullets = []
        self.enemies = [Enemies.RatEnemy(WIDTH+300, 300, self.canvas)]
        self.effects = []

        self.score = 0
        self.canvas.bind("<KeyPress>", self.on_key_pressed)
        self.canvas.bind("<KeyRelease>", self.on_key_released)
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_pressed)
        self.canvas.focus_set()
        self.canvas.pack()

        self.call_each_frame()

        self.window.mainloop()

    def handle_menu_options(self, option):
        if option == "Play":
            self.start_game()
        elif option == "Load":
            # load a previous game
            pass
        elif option == "Options":
            # load options menu
            pass
        else:
            # exit the game
            pass

    def main_menu_screen(self):
        self.canvas.config(background="black")
        self.canvas.create_image(0, 0, image="Images/main_menu_drawing.png")
        self.canvas.create_image(WIDTH//2, 0, image="Images/game_title.png")
        for index, text in enumerate(["Play","Load","Options","Exit"]):
            original_y = HEIGHT//3
            menu_btn = tk.Button(text=text, command=lambda x=text: self.handle_menu_options(text))
            menu_btn.place(x=2*WIDTH//3, y=original_y + 50*index)

    def game_over_screen(self):
        self.game_over = True
        self.canvas.delete("all")
        self.canvas.destroy()
        self.game_over_frame = tk.Frame(width=WIDTH, height=HEIGHT)
        
        game_over_label = tk.Label(master=self.game_over_frame, text="Game Over")
        game_over_label.pack()
        score_label = tk.Label(master=self.game_over_frame, text=f"Final Score: {self.score}")
        score_label.pack()
        restart_button = tk.Button(master=self.game_over_frame, text="Restart", command=self.start_game)
        restart_button.pack()
        return_to_menu_button = tk.Button(master=self.game_over_frame, text="Main Menu")
        return_to_menu_button.pack()
        self.game_over_frame.pack()

game = GameManager()
game.start_game()