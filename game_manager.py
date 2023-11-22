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

# handles all logic for when playing the game
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

    # minimises the application if the boss button is activated
    def activate_boss_button(self, event):
        if event.char == bindings["Boss Button"]:
            if self.state == "game":
                self.on_escape_key_pressed(None)
            self.handler.get_window().iconify()
    
    # sets the bunker back to its original state, for when player moves to next level
    def reset_bunker(self):
        self.fading_animation_active = False
        self.current_fade = 0
        self.score += 100
        self.spawner.bunker_reset(self.is_crazy_bunker)
        
    # handles all of the inputs from the keyboard
    def on_key_pressed(self, event):
        # gets the bindings for the game
        bindings = self.handler.get_bindings()
        self.player.key_pressed(event, bindings)
        # if the player interacts (typically "e") and the bunker is complete (text indication is up)
        # begin the fading animation into the next level of the bunker
        if event.char == bindings["Interact"] and self.current_bunker.check_bunker_completed(self.spawner.get_current_enemy_count()) and not self.fading_animation_active:
            self.fading_animation_active = True
        # if not at the end of the bunker and interact is pressed, check structures interactions
        elif event.char == bindings["Interact"]:
            self.current_bunker.check_interact(self.player)
        # if the cheat button is pressed, increase player speed and damage
        elif event.char == bindings["Cheats"]:
            self.player.speed = 20
            self.player.damage_lower = 100
            self.player.damage_upper = 100

    def on_key_released(self, event):
        self.player.key_released(event, self.handler.get_bindings())

    # if you press the mouse, player can shoot
    def on_mouse_pressed(self, event):
        self.shooting = True

    # if button is unpressed, then player stops shooting
    def on_mouse_released(self, event):
        self.shooting = False
        self.prev_hint_frame = 0

    # if escape key is pressed, pause menu is displayed
    def on_escape_key_pressed(self, event):
        self.canvas.pack_forget()
        self.handler.set_state("pause")

    # if bunker is complete, create text to indeicate so saying "Bunker completed" "press E to descend"
    def display_bunker_completed(self):
        self.canvas.create_text(self.handler.get_swidth()//2, self.handler.get_sheight()//2, text="Bunker Completed\nE descend", justify="center", fill="white", font=("Courier", 25, "bold"))

    # used to allow spawner to add effects for enemies
    def add_effect(self, effect):
        self.effects.append(effect)

    # used to allow spawner to add projectiles for the enemies
    def add_enemy_projectile(self, projectile):
        self.enemy_projectiles.append(projectile)

    # each time enemy is spawned, it updates the bunker (to allow for checking if bunker is completed)
    def update_bunker_spawns(self):
        self.current_bunker.enemy_spawned()

    # function to check if two objects overlap
    def check_collision(self, object1, object2):
        if object1.x > object2.x-object2.hitbox_width//2 and object1.x < object2.x+object2.hitbox_width//2 and object1.y > object2.y-object2.hitbox_height and object1.y < object2.y:
            return True
        return False

    # function for all the processes that happen each frame of the game
    def call_each_frame(self):
        # remove all images to blank
        self.canvas.delete("all")
        # create bunker background (solid colour)
        self.canvas.create_rectangle(0, self.handler.get_sheight()//5, self.handler.get_swidth(), 4*self.handler.get_sheight()//5, fill="#497325")
        # entire map/world moves rather than the player moving
        # this allows the player to stay in the center of the screen
        player_movement = -self.player. get_player_movement()
        # check if player is at the edge of the bunker
        edge_status = self.current_bunker.check_at_edge(self.handler.get_swidth())
        # if player is at the edge, but is still moving, allow player to move individually of camera
        # once player reaches the very edge of screen (camera and bunker), then freeze player movement in that direction
        # if player returns to center and moves away from edge, it returns to moving rest of world
        if edge_status == "right" and player_movement < 0 or edge_status == "left" and player_movement > 0:
            player_movement = 0
            self.player.move(edge_status)
        elif edge_status == "right" and player_movement > 0 and self.player.x > self.handler.get_swidth()//2:
            player_movement = 0
            self.player.move("left")
        elif edge_status == "left" and player_movement < 0 and self.player.x < self.handler.get_swidth()//2:
            player_movement = 0
            self.player.move("right")
            
        # move bunker foreground according to player movement
        self.current_bunker.camera_move_foreground(player_movement)
        # get the position (x and y) of the mouse on the screen
        pointerx = self.handler.get_window().winfo_pointerx() - self.handler.get_window().winfo_rootx()
        pointery = self.handler.get_window().winfo_pointery() - self.handler.get_window().winfo_rooty()

        # move bunker structures according to player movement
        self.current_bunker.update_structures(self.player, player_movement)

        # update the spawner each frame to update enemies and spawn in new ones
        self.spawner.update_spawner(player_movement, self.current_bunker.get_remaining_enemies(), self.bunker_count, self.handler.get_swidth(), self.handler.get_sheight())
        
        # logic to update all bullets shot
        for bullet in reversed(self.bullets):
            # if bullet returns -1 (reached edge of screen) remove the bullet from memory
            if bullet.update_bullet(player_movement) == -1:
                self.bullets.remove(bullet)
                del bullet
            else:
                # if bullet collides with enemy and the enemy dies it returns 1
                # remove bullet, apply blood effect and inceases score
                if self.spawner.check_enemy_collision(bullet) == 1:
                    self.score += 10
                    self.effects.append(effects.BloodEffect(bullet.x, bullet.y, self.canvas))
                    self.bullets.remove(bullet)
                    del bullet
                    break

        # updates all projectiles shot by the enemies
        for projectile in reversed(self.enemy_projectiles):
            # if projectile goes off screen, remove it from memory
            if projectile.update_projectile(player_movement) == -1:
                self.enemy_projectiles.remove(projectile)
                del projectile
            # if the projectile collides with the player
            # remove projectile and take health from the player
            elif self.check_collision(projectile, self.player):
                self.player.take_damage(projectile.damage)
                self.enemy_projectiles.remove(projectile)
                del projectile
                # create effect (red screen effect with some alpha to indicate to player)
                self.effects.append(effects.OnHitEffect(self.handler.get_swidth(), self.handler.get_sheight(), self.canvas))

        # update the player
        self.player.update_player(pointerx, pointery, self.spawner)
        # if player is shooting
        if self.shooting:
            # and ammo is available
            if self.player.check_ammo():
                # get the information from the player based on the direction of the gun from the player
                bullet_x, bullet_y, bullet_vel_x, bullet_vel_y, is_shoot = self.player.get_bullet_args()
                # if player is able to shoot (fire is ready)
                if is_shoot:
                    # add bullet to bullets list
                    self.bullets.append(weapons.Bullet(bullet_x, bullet_y, bullet_vel_x, bullet_vel_y, self.player.get_damage(), self.canvas, self.handler.get_swidth(), self.handler.get_sheight()))
                    # indicate to the player to reduce ammo
                    self.player.taken_shot()
            # if player has no ammo
            # draw a text effect to say "out of ammo"
            else:
                if self.prev_hint_frame % 15 == 0:
                    self.effects.append(effects.TextPopUp(self.handler.get_swidth()//2, self.handler.get_sheight()//2-25, "out of ammo!", "white", 10, ("Courier", 15, "bold"), self.canvas))
                    self.prev_hint_frame = 1
                else:
                    self.prev_hint_frame += 1

        # draw foreground of bunker
        # foreground images
        self.current_bunker.draw_foreground()
        # black background
        self.canvas.create_rectangle(0, 0, self.handler.get_swidth(), self.handler.get_sheight()//7, fill="black")
        self.canvas.create_rectangle(0, 4*self.handler.get_sheight()//5, self.handler.get_swidth(), self.handler.get_sheight(), fill="black")

        # for all ui effects update them
        for effect in reversed(self.effects):
            if effect.update_effect(player_movement) == -1:
                self.effects.remove(effect)
                del effect            

        # if the bunker is completed, draw the completed bunker text
        if self.current_bunker.check_bunker_completed(self.spawner.get_current_enemy_count()):
            self.display_bunker_completed()

        # processes to handles the fading animation between bunker levels
        if self.fading_animation_active:
            # if the fading animation is not complete, increment the animation, else reset the bunker
            if self.current_fade < len(self.fades)*self.fading_frames - self.fading_frames:
                self.current_fade += 1
            else:
                self.reset_bunker()
            # if at the peak of the animation
            if self.fades[self.current_fade//self.fading_frames] == "gray100peak":
                # make sure it only happens once 
                if self.current_fade%self.fading_frames == 1:
                    # change the bunker to the next one so that as it fades in
                    # it fades into the new bunker
                    self.is_crazy_bunker = random.random() < 0.05
                    self.bunker_count += 1
                    self.current_bunker = bunker.Bunker(self.bunker_count, self.canvas, self.handler.get_sheight(), self.is_crazy_bunker)
                    self.effects.append(effects.BunkerLevelText(self.bunker_count, self.handler.get_swidth(), self.handler.get_sheight(), self.canvas))
                # draw fading animation rectangle (with current alpha fading effect)
                self.canvas.create_rectangle(0, 0, self.handler.get_swidth(), self.handler.get_sheight(), fill="black")
            # if gray 100 (as this isnt a bitmap) draw a black rectangle
            elif self.fades[self.current_fade//self.fading_frames] == "gray100":
                self.canvas.create_rectangle(0, 0, self.handler.get_swidth(), self.handler.get_sheight(), fill="black")
            else:
                # else draw rectangle with the corresponding stipple (alpha) effect
                self.canvas.create_rectangle(0, 0, self.handler.get_swidth(), self.handler.get_sheight(), fill="black", stipple=self.fades[self.current_fade//self.fading_frames])

        # draw all the ui
        # healthbar
        self.player.update_healthbar()
        # inventory
        self.player.display_inventory(self.handler.get_swidth(), self.handler.get_sheight())
        # score
        self.canvas.create_text(self.handler.get_swidth()//2, 25, text=f"Score: {self.score}", justify="center", font=("Courier", 15, "bold"), fill="white")
        # if player dies, game over screen is displayed
        if self.player.check_dead():
            self.canvas.destroy()
            self.handler.set_state("game_over")
        # if the game is still continuing (not paused or in main menu or game over)
        # call this function again
        if self.handler.get_state() == "game":
            self.handler.get_window().after(self.frame_time, self.call_each_frame)

    # function to set up all the objects and variables for the game 
    def setup_game_loop(self, saved_game=None):
        self.canvas = tk.Canvas(width=self.handler.get_swidth(), height=self.handler.get_sheight(), background="black")

        self.player = player.Player(self.handler.get_swidth(), self.handler.get_sheight(), self.canvas)
        self.shooting = False
        self.prev_hint_frame = 1
        self.spawner = Spawner(self, self.player, self.canvas)

        self.score = 0
        self.bunker_count = 1
        # if loading a saved game, grab all of the information
        if saved_game != None:
            # load information into this class
            self.load_saved_info(ast.literal_eval(saved_game[1]))
            # load information into the spawner
            self.spawner.load_save_info(ast.literal_eval(saved_game[2]))
            # load information into the player
            self.player.load_save_info(ast.literal_eval(saved_game[3]))

        self.current_bunker = bunker.Bunker(self.bunker_count, self.canvas, self.handler.get_sheight())
        self.bullets = []
        self.enemy_projectiles = []
        self.effects = [effects.BunkerLevelText(self.bunker_count, self.handler.get_swidth(), self.handler.get_sheight(), self.canvas)]

        # bind all the key presses and button presses to th ecorrect functions
        self.canvas.bind("<KeyPress>", self.on_key_pressed)
        self.canvas.bind("<KeyRelease>", self.on_key_released)
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_pressed)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_released)
        self.canvas.bind("<Escape>", self.on_escape_key_pressed)
        self.canvas.focus_set()
        self.canvas.pack()

        # start the game
        self.call_each_frame()

    # called when returning to the game after being paused
    def resume(self):
        self.canvas.pack()
        self.call_each_frame()

    # get all the save informatino as a string when saving and exiting the game
    def get_save_info(self):
        return f"{self.bunker_count, datetime.now().strftime("%d/%m/%Y")};{[self.bunker_count, self.score]};{self.spawner.get_save_info()};{self.player.get_save_info()}"
    
    # load saved inforamtion for this class
    def load_saved_info(self, saved_info):
        self.bunker_count = saved_info[0]
        self.score = saved_info[1]