import tkinter as tk
from tkinter.font import Font
from tkinter import ttk
from PIL import ImageTk, Image
from datetime import datetime
from spawner import Spawner
import effects, bunker, weapons
import math
import random
import ast

WIDTH, HEIGHT = 960, 540
FRAME_TIME = 30
BULLET_SPEED = 25

def check_collision(object1, object2):
    if object1.x > object2.x-object2.hitbox_width//2 and object1.x < object2.x+object2.hitbox_width//2 and object1.y > object2.y-object2.hitbox_height and object1.y < object2.y:
        return True
    return False

class Player:
    def __init__(self, canvas):
        self.x = WIDTH//2
        self.y = 4*HEIGHT//5 - 20
        self.dimensions = 15
        self.current_image = tk.PhotoImage(file="Images/player_right.png")
        self.canvas = canvas
        self.image = self.canvas.create_image(self.x, self.y, image=self.current_image, anchor="s")
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

    def get_save_info(self):
        return [self.health]
    
    def load_save_info(self, saved_info):
        self.health = saved_info[0]

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

        self.canvas.create_image(self.x, self.y, image=self.current_image, anchor="s")

        self.gun.update_gun(self, pointerx, pointery)

class GameManager:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Nuclear Whiskers")
        self.window.geometry(f"{WIDTH}x{HEIGHT}")

        self.state = "main"

        self.DAMAGE_FONT = Font(
            family="Courier",
            size=15,
            weight="bold"
        )

        self.fading_animation_active = False
        self.current_fade = 0
        self.fades = ["gray12", "gray25", "gray50", "gray75", "gray100", "gray100peak", "gray75", "gray50", "gray25", "gray12"]
        self.fading_frames = 5

        self.game_over = False

        self.is_crazy_bunker = False
    
    def reset_bunker(self):
        self.fading_animation_active = False
        self.current_fade = 0
        self.score += 100
        self.spawner.bunker_reset(self.is_crazy_bunker)
        
    def on_key_pressed(self, event):
        self.player.key_pressed(event)
        if event.char == "e" and self.current_bunker.check_bunker_completed(self.enemies) and not self.fading_animation_active:
            self.fading_animation_active = True

    def on_key_released(self, event):
        self.player.key_released(event)

    def on_mouse_pressed(self, event):
        if self.player.gun.check_ammo():
            bullet_x, bullet_y, bullet_vel_x, bullet_vel_y = self.player.get_bullet_args()
            self.bullets.append(weapons.Bullet(bullet_x, bullet_y, bullet_vel_x, bullet_vel_y, self.canvas, WIDTH, HEIGHT))

    def on_escape_key_pressed(self, event):
        self.state = "pause"
        self.canvas.pack_forget()
        self.current_frame = self.get_pause_frame()
        self.current_frame.pack()

    def display_bunker_completed(self):
        self.canvas.create_text(WIDTH//2, HEIGHT//2, text="Bunker Completed\nE descend", justify="center", fill="white", font=("Courier", 25, "bold"))

    def call_each_frame(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, HEIGHT//5, WIDTH, 4*HEIGHT//5, fill="#497325")
        player_movement = -self.player. get_player_movement()
        edge_status = self.current_bunker.check_at_edge(WIDTH)
        if edge_status == "right" and player_movement < 0:
            player_movement = 0
        elif edge_status == "left" and player_movement > 0:
            player_movement = 0
            
        self.current_bunker.camera_move_foreground(player_movement)
        pointerx = self.window.winfo_pointerx() - self.window.winfo_rootx()
        pointery = self.window.winfo_pointery() - self.window.winfo_rooty()

        enemy = self.spawner.spawn(self.current_bunker.get_remaining_enemies(), self.bunker_count, WIDTH, HEIGHT, self.canvas)
        if enemy is not None:
            self.enemies.append(enemy)
            self.current_bunker.enemy_spawned()
        
        for bullet in reversed(self.bullets):
            if bullet.update_bullet(player_movement) == -1:
                self.bullets.remove(bullet)
                del bullet
            else:
                for enemy in reversed(self.enemies):                    
                    if check_collision(bullet, enemy):
                        self.effects.append(effects.DamagePopUp(enemy.x, enemy.y-enemy.hitbox_height, str(bullet.damage), self.DAMAGE_FONT, self.canvas))

                        if enemy.take_damage(bullet.damage) == -1:
                            self.enemies.remove(enemy)
                            del enemy
                            self.score += 10

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

        if self.current_bunker.check_bunker_completed(self.enemies):
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
                    self.current_bunker = bunker.Bunker(self.bunker_count, self.canvas, HEIGHT, self.is_crazy_bunker)
                    self.effects.append(effects.BunkerLevelText(self.bunker_count, WIDTH, HEIGHT, self.canvas))
                self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="black")
            elif self.fades[self.current_fade//self.fading_frames] == "gray100":
                self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="black")
            else:
                self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="black", stipple=self.fades[self.current_fade//self.fading_frames])

        self.player.update_healthbar()
        self.player.gun.display_ammo(WIDTH, HEIGHT)
        self.canvas.create_text(100, HEIGHT-30, text=f"Level {self.bunker_count}", justify="center", fill="white", font=("Courier", 20, "bold"))
        self.canvas.create_text(WIDTH//2, 25, text=f"Score: {self.score}", justify="center", font=("Courier", 15, "bold"), fill="white")
        if self.player.check_dead():
            self.canvas.destroy()
            self.state = "game_over"
            self.current_frame = self.get_game_over_frame()
            self.current_frame.pack()

        if self.state == "game":
            self.window.after(FRAME_TIME, self.call_each_frame)

    def setup_game_loop(self, saved_game=None):
        self.current_frame.destroy()
        self.canvas = tk.Canvas(width=WIDTH, height=HEIGHT, background="black")

        self.player = Player(self.canvas)
        self.spawner = Spawner()

        self.bunker_count = 1
        if saved_game != None:
            self.load_saved_info(ast.literal_eval(saved_game[1]))
            self.spawner.load_save_info(ast.literal_eval(saved_game[2]))
            self.player.load_save_info(ast.literal_eval(saved_game[3]))

        self.current_bunker = bunker.Bunker(self.bunker_count, self.canvas, HEIGHT)
        self.bullets = []
        self.enemies = []
        self.effects = [effects.BunkerLevelText(self.bunker_count, WIDTH, HEIGHT, self.canvas)]

        self.score = 0
        self.canvas.bind("<KeyPress>", self.on_key_pressed)
        self.canvas.bind("<KeyRelease>", self.on_key_released)
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_pressed)
        self.canvas.bind("<Escape>", self.on_escape_key_pressed)
        self.canvas.focus_set()
        self.canvas.pack()

        self.call_each_frame()

    def save_score(self, player_name):
        with open("leaderboard.txt","a") as leaderboard:
            leaderboard.write(f"{player_name},{self.score},{datetime.now().strftime("%d/%m/%Y")}\n")
            leaderboard.close()

    def resize_image(self, image_dir, width, height):
        image = Image.open(image_dir)
        return ImageTk.PhotoImage(image.resize((width, height), Image.NEAREST))

    def handle_menu_options(self, event):
        # menu options = "Play","Load","Leaderboard","Options","Exit"
        # game over options = "Play Again", "Main Menu"
        option = event.widget["text"]
        if option == "Play" or option == "Play Again":
            self.state = "game"
            self.setup_game_loop()
        elif option == "Load":
            self.state = "Menu"
            self.current_frame.destroy()
            self.current_frame = self.get_load_frame()
            self.current_frame.pack()
        elif option == "Leaderboard":
            self.current_frame.destroy()
            self.current_frame = self.get_leaderboard_frame()
            self.current_frame.pack()
        elif option == "Options":
            # load options menu
            pass
        elif option == "Exit":
            self.window.destroy()
        elif option == "Main Menu":
            self.current_frame.destroy()
            self.current_frame = self.get_main_menu_frame()
            self.current_frame.pack()
        elif option == "Resume":
            self.current_frame.destroy()
            self.canvas.pack()
            self.state = "game"
            self.call_each_frame()
        elif option == "Save and Exit":
            with open("saved_games.txt","a") as saved_games:
                saved_games.write(f"{self.bunker_count, datetime.now().strftime("%d/%m/%Y")};{self.get_save_info()};{self.spawner.get_save_info()};{self.player.get_save_info()}")
                saved_games.close()

            self.state = "menu"
            self.current_frame.destroy()
            self.current_frame = self.get_main_menu_frame()
            self.current_frame.pack()

    def get_save_info(self):
        return [self.bunker_count, self.score]
    
    def load_saved_info(self, saved_info):
        self.bunker_count = saved_info[0]
        self.score = saved_info[1]

    def on_enter(self, event, size=25):
        event.widget.config(fg="yellow", font=("Courier", size, "bold"))

    def on_leave(self, event, size=20):
        event.widget.config(fg="white", font=("Courier", size, "bold"))

    def get_main_menu_frame(self):
        main_menu_frame = tk.Frame(width=WIDTH, height=HEIGHT, background="black")

        self.main_menu_image = self.resize_image("Images/main_menu_image.png", WIDTH//2, HEIGHT)
        for index, text in enumerate(["Play","Load","Leaderboard","Options","Exit"]):
            original_y = 3*HEIGHT//7
            menu_btn = tk.Label(master=main_menu_frame, text=text, fg="white", font=("Courier", 20, "bold"), background="black") 
            menu_btn.bind("<Button-1>", self.handle_menu_options)
            menu_btn.bind("<Enter>", self.on_enter)
            menu_btn.bind("<Leave>", self.on_leave)
            menu_btn.place(x=3*WIDTH//4, y=original_y + 50*index, anchor="center")

        title_label = tk.Label(master=main_menu_frame, text="Nuclear\nWhiskers", fg="white", background="black", font=("Courier", 40, "bold"))
        title_label.place(x=3*WIDTH//4, y=HEIGHT//5, anchor="center")

        main_menu_image_label = tk.Label(master=main_menu_frame, image=self.main_menu_image, background="black")
        main_menu_image_label.place(x=0, y=0)

        return main_menu_frame

    def get_game_over_frame(self):

        def entered_name(event):
            widget = event.widget
            name = widget.get()
            self.save_score(name)
            widget.destroy()
            saved_score_label.place(x=3*WIDTH//4, y=4*HEIGHT//7, anchor="center")

        game_over_frame = tk.Frame(width=WIDTH, height=HEIGHT, background="black")

        game_over_image = self.resize_image("Images/main_menu_image.png", WIDTH//2, HEIGHT)
        for index, text in enumerate(["Play Again", "Main Menu"]):
            original_y = 5*HEIGHT//7
            menu_btn = tk.Label(master=game_over_frame, text=text, fg="white", font=("Courier", 20, "bold"), background="black") 
            menu_btn.bind("<Button-1>", self.handle_menu_options)
            menu_btn.bind("<Enter>", self.on_enter)
            menu_btn.bind("<Leave>", self.on_leave)
            menu_btn.place(x=3*WIDTH//4, y=original_y + 50*index, anchor="center")

        title_label = tk.Label(master=game_over_frame, text="Game Over", fg="white", background="black", font=("Courier", 40, "bold"))
        title_label.place(x=3*WIDTH//4, y=HEIGHT//5, anchor="center")

        score_label = tk.Label(master=game_over_frame, text=f"Final Score: {self.score}", fg="white", background="black", font=("Courier", 20, "bold"))
        score_label.place(x=3*WIDTH//4, y=3*HEIGHT//7, anchor="center")

        game_over_image_label = tk.Label(master=game_over_frame, image=self.main_menu_image, background="black")
        game_over_image_label.place(x=0, y=0)

        save_score_entry = tk.Entry(master=game_over_frame, font=("Courier", 18, "bold"))
        save_score_entry.bind("<Return>", entered_name)
        save_score_entry.place(x=3*WIDTH//4, y=4*HEIGHT//7, anchor="center")

        saved_score_label = tk.Label(master=game_over_frame, text="Score Saved!", font=("Courier", 18, "bold"), fg="yellow", background="black")

        return game_over_frame
    
    def get_pause_frame(self):
        pause_frame = tk.Frame(width=WIDTH, height=HEIGHT, background="black")
        for index, text in enumerate(["Resume", "Options", "Save and Exit", "Main Menu"]):
            original_y = 2*HEIGHT//5
            menu_btn = tk.Label(master=pause_frame, text=text, fg="white", font=("Courier", 20, "bold"), background="black") 
            menu_btn.bind("<Button-1>", self.handle_menu_options)
            menu_btn.bind("<Enter>", self.on_enter)
            menu_btn.bind("<Leave>", self.on_leave)
            menu_btn.place(x=WIDTH//2, y=original_y + 50*index, anchor="center")
        
        pause_title_label = tk.Label(master=pause_frame, text="Paused", fg="white", background="black", font=("Courier", 40, "bold"))
        pause_title_label.place(x=WIDTH//2, y=HEIGHT//5, anchor="center")

        return pause_frame
    
    def get_leaderboard_frame(self):
        leaderboard_frame = tk.Frame(width=WIDTH, height=HEIGHT, background="black")
        leaderboard_title = tk.Label(master=leaderboard_frame, text="Leaderboard", fg="white", background="black", font=("Courier", 40, "bold"))
        leaderboard_title.place(x=3*WIDTH//4, y=HEIGHT//10, anchor="center")
        menu_btn = tk.Label(master=leaderboard_frame, text="Main Menu", fg="white", font=("Courier", 20, "bold"), background="black") 
        menu_btn.bind("<Button-1>", self.handle_menu_options)
        menu_btn.bind("<Enter>", self.on_enter)
        menu_btn.bind("<Leave>", self.on_leave)
        menu_btn.place(x=3*WIDTH//4, y=HEIGHT-100, anchor="center")

        with open("leaderboard.txt","r") as leaderboard:
            scores = leaderboard.readlines()
            scores = list(map(lambda x: x.rstrip().split(","), scores))
            scores.sort(reverse=True, key=lambda x: int(x[1]))
            if len(scores) == 0:
                empty_leaderboard_label = tk.Label(master=leaderboard_frame, text="There are no scores available!",  fg="white", background="black", font=("Courier", 15, "bold"))
                empty_leaderboard_label.place(x=3*WIDTH//4, y=HEIGHT//5, anchor="center")
            else:
                original_y = 1.5*HEIGHT//5
                for index, score in enumerate(scores[:5]):
                    position_label = tk.Label(master=leaderboard_frame, text=f"{index+1}.", fg="yellow", font=("Courier", 15, "bold"), background="black")
                    name_label = tk.Label(master=leaderboard_frame, text=score[0], fg="white", font=("Courier", 15, "bold"), background="black")
                    score_label = tk.Label(master=leaderboard_frame, text=score[1], fg="white", font=("Courier", 15, "bold"), background="black")
                    time_label = tk.Label(master=leaderboard_frame, text=score[2], fg="white", font=("Courier", 15, "bold"), background="black")
                    position_label.place(x=2*WIDTH//4 + 50, y=original_y+index*50, anchor="center")
                    name_label.place(x=3*WIDTH//4 - 100, y=original_y+index*50, anchor="center")
                    score_label.place(x=3*WIDTH//4, y=original_y+index*50, anchor="center")
                    time_label.place(x=3*WIDTH//4 + 100, y=original_y+index*50, anchor="center")

            leaderboard.close()

        leaderboard_label = tk.Label(master=leaderboard_frame, image=self.main_menu_image, background="black")
        leaderboard_label.place(x=0, y=0)

        return leaderboard_frame
    
    def get_load_frame(self):
        def game_loaded(saved_game):
            self.current_frame.destroy()
            self.state = "game"
            self.setup_game_loop(saved_game)

        def on_enter(event):
            event.widget.configure(fg="yellow", font=("Courier", 18, "bold"))
        
        def on_release(event):
            event.widget.configure(fg="white", font=("Courier",15,"bold"))
            
        load_frame = tk.Frame(width=WIDTH, height=HEIGHT, background="black")

        load_title = tk.Label(master=load_frame, text="Load Game", fg="white", background="black", font=("Courier", 40, "bold"))
        load_title.place(x=3*WIDTH//4, y=HEIGHT//10, anchor="center")
        menu_btn = tk.Label(master=load_frame, text="Main Menu", fg="white", font=("Courier", 20, "bold"), background="black") 
        menu_btn.bind("<Button-1>", self.handle_menu_options)
        menu_btn.bind("<Enter>", self.on_enter)
        menu_btn.bind("<Leave>", self.on_leave)
        menu_btn.place(x=3*WIDTH//4, y=HEIGHT-100, anchor="center")

        with open("saved_games.txt","r") as saved_games:
            games = saved_games.readlines()
            original_y = 2*HEIGHT//7
            for index,game in enumerate(games[-5::]):
                game = game.split(";")
                game_text = ast.literal_eval(game[0])
                game_btn = tk.Label(master=load_frame, text=f"Level: {game_text[0]}, Date: {game_text[1]}", fg="white", font=("Courier", 15, "bold"), background="black")
                game_btn.bind("<Button-1>", lambda event: game_loaded(game))
                game_btn.bind("<Enter>", on_enter)
                game_btn.bind("<Leave>", on_release )
                game_btn.place(x=3*WIDTH//4, y=original_y+index*50, anchor="center")

        load_label = tk.Label(master=load_frame, image=self.main_menu_image, background="black")
        load_label.place(x=0, y=0)

        return load_frame

    def start_game(self):
        self.current_frame = self.get_main_menu_frame()
        self.current_frame.pack()

        self.window.mainloop()

game = GameManager()
game.start_game()