import tkinter as tk
from tkinter.font import Font
from tkinter import ttk
from PIL import ImageTk, Image
from datetime import datetime
from spawner import Spawner
import effects, bunker, weapons, Enemies, player
import math
import random
import ast

class GameManager:
    def __init__(self, handler):
        #self.handler.get_window().bind("<KeyPress>", self.activate_boss_button)
        self.frame_time = 30
        self.handler = handler

        self.fading_animation_active = False
        self.current_fade = 0
        self.fades = ["gray12", "gray25", "gray50", "gray75", "gray100", "gray100peak", "gray75", "gray50", "gray25", "gray12"]
        self.fading_frames = 5

        self.game_over = False

        self.is_crazy_bunker = False

    def get_score(self):
        return self.score

    def activate_boss_button(self, event):
        if event.char == bindings["Boss Button"]:
            if self.state == "game":
                self.on_escape_key_pressed(None)
            self.handler.get_window().iconify()
    
    def reset_bunker(self):
        self.fading_animation_active = False
        self.current_fade = 0
        self.score += 100
        self.spawner.bunker_reset(self.is_crazy_bunker)
        
    def on_key_pressed(self, event):
        bindings = self.handler.get_bindings()
        self.player.key_pressed(event, bindings)
        if event.char == bindings["Interact"] and self.current_bunker.check_bunker_completed(self.enemies) and not self.fading_animation_active:
            self.fading_animation_active = True
        elif event.char == bindings["Cheats"]:
            self.player.speed = 20
            self.player.damage_lower = 100
            self.player.damage_upper = 100

    def on_key_released(self, event):
        self.player.key_released(event, self.handler.get_bindings())

    def on_mouse_pressed(self, event):
        self.shooting = True

    def on_mouse_released(self, event):
        self.shooting = False
        self.prev_hint_frame = 0

    def on_escape_key_pressed(self, event):
        self.canvas.pack_forget()
        self.handler.set_state("pause")

    def display_bunker_completed(self):
        self.canvas.create_text(self.handler.get_swidth()//2, self.handler.get_sheight()//2, text="Bunker Completed\nE descend", justify="center", fill="white", font=("Courier", 25, "bold"))

    def add_effect(self, effect):
        self.effects.append(effect)

    def add_enemy_projectile(self, projectile):
        self.enemy_projectiles.append(projectile)

    def update_bunker_spawns(self):
        self.current_bunker.enemy_spawned()

    def check_collision(self, object1, object2):
        if object1.x > object2.x-object2.hitbox_width//2 and object1.x < object2.x+object2.hitbox_width//2 and object1.y > object2.y-object2.hitbox_height and object1.y < object2.y:
            return True
        return False

    def call_each_frame(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, self.handler.get_sheight()//5, self.handler.get_swidth(), 4*self.handler.get_sheight()//5, fill="#497325")
        player_movement = -self.player. get_player_movement()
        edge_status = self.current_bunker.check_at_edge(self.handler.get_swidth())
        if edge_status == "right" and player_movement < 0 or edge_status == "left" and player_movement > 0:
            player_movement = 0
            self.player.move(edge_status)
        elif edge_status == "right" and player_movement > 0 and self.player.x > self.handler.get_swidth()//2:
            player_movement = 0
            self.player.move("left")
        elif edge_status == "left" and player_movement < 0 and self.player.x < self.handler.get_swidth()//2:
            player_movement = 0
            self.player.move("right")
            
        self.current_bunker.camera_move_foreground(player_movement)
        pointerx = self.handler.get_window().winfo_pointerx() - self.handler.get_window().winfo_rootx()
        pointery = self.handler.get_window().winfo_pointery() - self.handler.get_window().winfo_rooty()

        self.spawner.update_spawner(player_movement, self.current_bunker.get_remaining_enemies(), self.bunker_count, self.handler.get_swidth(), self.handler.get_sheight())
        
        for bullet in reversed(self.bullets):
            if bullet.update_bullet(player_movement) == -1:
                self.bullets.remove(bullet)
                del bullet
            else:
                if self.spawner.check_enemy_collision(bullet) == 1:
                    self.score += 10
                    self.effects.append(effects.BloodEffect(bullet.x, bullet.y, self.canvas))
                    self.bullets.remove(bullet)
                    del bullet
                    break

        for projectile in reversed(self.enemy_projectiles):
            if projectile.update_projectile(player_movement) == -1:
                self.enemy_projectiles.remove(projectile)
                del projectile
            elif self.check_collision(projectile, self.player):
                self.player.take_damage(projectile.damage)
                self.enemy_projectiles.remove(projectile)
                del projectile

                self.effects.append(effects.OnHitEffect(self.handler.get_swidth(), self.handler.get_sheight(), self.canvas))

        self.player.update_player(pointerx, pointery)
        if self.shooting:
            if self.player.gun.check_ammo():
                bullet_x, bullet_y, bullet_vel_x, bullet_vel_y, is_shoot = self.player.get_bullet_args()
                if is_shoot:
                    self.bullets.append(weapons.Bullet(bullet_x, bullet_y, bullet_vel_x, bullet_vel_y, self.player.get_damage(), self.canvas, self.handler.get_swidth(), self.handler.get_sheight()))
                    self.player.taken_shot()
            else:
                if self.prev_hint_frame % 15 == 0:
                    self.effects.append(effects.TextPopUp(self.handler.get_swidth()//2, self.handler.get_sheight()//2-25, "out of ammo!", "white", 10, ("Courier", 15, "bold"), self.canvas))
                    self.prev_hint_frame = 1
                else:
                    self.prev_hint_frame += 1

        self.current_bunker.draw_foreground()

        for effect in reversed(self.effects):
            if effect.update_effect(player_movement) == -1:
                self.effects.remove(effect)
                del effect            

        if self.current_bunker.check_bunker_completed(self.spawner.get_current_enemy_count()):
            self.display_bunker_completed()

        if self.fading_animation_active:
            if self.current_fade < len(self.fades)*self.fading_frames - self.fading_frames:
                self.current_fade += 1
            else:
                self.reset_bunker()

            if self.fades[self.current_fade//self.fading_frames] == "gray100peak":
                if self.current_fade%self.fading_frames == 1:
                    self.is_crazy_bunker = random.random() < 0.05
                    self.bunker_count += 1
                    self.current_bunker = bunker.Bunker(self.bunker_count, self.canvas, self.handler.get_sheight(), self.is_crazy_bunker)
                    self.effects.append(effects.BunkerLevelText(self.bunker_count, self.handler.get_swidth(), self.handler.get_sheight(), self.canvas))
                self.canvas.create_rectangle(0, 0, self.handler.get_swidth(), self.handler.get_sheight(), fill="black")
            elif self.fades[self.current_fade//self.fading_frames] == "gray100":
                self.canvas.create_rectangle(0, 0, self.handler.get_swidth(), self.handler.get_sheight(), fill="black")
            else:
                self.canvas.create_rectangle(0, 0, self.handler.get_swidth(), self.handler.get_sheight(), fill="black", stipple=self.fades[self.current_fade//self.fading_frames])

        self.player.update_healthbar()
        self.player.gun.display_ammo(self.handler.get_swidth(), self.handler.get_sheight())
        self.canvas.create_text(100, self.handler.get_sheight()-30, text=f"Level {self.bunker_count}", justify="center", fill="white", font=("Courier", 20, "bold"))
        self.canvas.create_text(self.handler.get_swidth()//2, 25, text=f"Score: {self.score}", justify="center", font=("Courier", 15, "bold"), fill="white")
        if self.player.check_dead():
            self.canvas.destroy()
            self.handler.set_state("game_over")

        if self.handler.get_state() == "game":
            self.handler.get_window().after(self.frame_time, self.call_each_frame)

    def setup_game_loop(self, saved_game=None):
        self.canvas = tk.Canvas(width=self.handler.get_swidth(), height=self.handler.get_sheight(), background="black")

        self.player = player.Player(self.handler.get_swidth(), self.handler.get_sheight(), self.canvas)
        self.shooting = False
        self.prev_hint_frame = 1
        self.spawner = Spawner(self, self.player, self.canvas)

        self.score = 0
        self.bunker_count = 1
        if saved_game != None:
            self.load_saved_info(ast.literal_eval(saved_game[1]))
            self.spawner.load_save_info(ast.literal_eval(saved_game[2]))
            self.player.load_save_info(ast.literal_eval(saved_game[3]))

        self.current_bunker = bunker.Bunker(self.bunker_count, self.canvas, self.handler.get_sheight())
        self.bullets = []
        self.enemy_projectiles = []
        self.effects = [effects.BunkerLevelText(self.bunker_count, self.handler.get_swidth(), self.handler.get_sheight(), self.canvas)]

        self.canvas.bind("<KeyPress>", self.on_key_pressed)
        self.canvas.bind("<KeyRelease>", self.on_key_released)
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_pressed)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_released)
        self.canvas.bind("<Escape>", self.on_escape_key_pressed)
        self.canvas.focus_set()
        self.canvas.pack()

        self.call_each_frame()

    def resume(self):
        self.canvas.pack()
        self.call_each_frame()

    def get_save_info(self):
        return f"{self.bunker_count, datetime.now().strftime("%d/%m/%Y")};{[self.bunker_count, self.score]};{self.spawner.get_save_info()};{self.player.get_save_info()}"
    
    def load_saved_info(self, saved_info):
        self.bunker_count = saved_info[0]
        self.score = saved_info[1]