import tkinter as tk
from PIL import Image, ImageTk
from datetime import datetime
import ast

# handles all the menus displaying
# main menu, leaderboard, load game, game over, pause and options menu
class MenuManager:
	def __init__(self, handler):
		self.handler = handler

		self.current_frame = self.get_main_menu_frame()
		self.loaded_game = None

	def get_current_frame(self):
		return self.current_frame

	def get_loaded_game(self):
		return self.loaded_game

	def destroy_current_frame(self):
		self.current_frame.destroy()

	def resize_image(self, image_dir, width, height):
		image = Image.open(image_dir)
		return ImageTk.PhotoImage(image.resize((width, height), Image.NEAREST))

	def save_score(self, player_name):
		# opens the leaderboard file
		# gets the current score of the game, the name of the player and the time player
		# writes it to the leaderboard file
		with open("leaderboard.txt","a") as leaderboard:
			leaderboard.write(f"{player_name},{self.handler.get_current_game_score()},{datetime.now().strftime('%d/%m/%Y')}\n")
			leaderboard.close()

	# funciton called whenever the mouse hovers over a menu select label
	def on_enter(self, event, size=25):
		# turns colour to yellow and increases size of the text
		event.widget.config(fg="yellow", font=("Courier", size, "bold"))

	# function called whenever the mouse stops hovering over a menu select label
	def on_leave(self, event, size=20):
		# returns text to white and its original size
		event.widget.config(fg="white", font=("Courier", size, "bold"))

	# change the current frame to the pause menu
	def pause(self):
		self.current_frame = self.get_pause_frame()

	# changes the current frame to the game over menu
	def game_over(self):
		self.current_frame = self.get_game_over_frame()

	# called whenever a menu label is selected
	def handle_menu_options(self, event):
		# gets the option that they pressed (based on the text)
		option = event.widget["text"]
		# retursn to the game
		if option == "Play" or option == "Play Again":
			self.handler.set_state("game")
		# loads the load menu 
		elif option == "Load":
			self.state = "Menu"
			self.current_frame.destroy()
			self.current_frame = self.get_load_frame()
			self.current_frame.pack()
		# loads leaderboard menu
		elif option == "Leaderboard":
			self.current_frame.destroy()
			self.current_frame = self.get_leaderboard_frame()
			self.current_frame.pack()
		# loads options menu
		elif option == "Options":
			self.current_frame.destroy()
			self.current_frame = self.get_options_frame()
			self.current_frame.pack()
		# exits the application
		elif option == "Exit":
			self.handler.get_window().destroy()
		# loads main menu
		elif option == "Main Menu":
			self.current_frame.destroy()
			self.current_frame = self.get_main_menu_frame()
			self.handler.set_state("menu")
		# retuns to the current game
		elif option == "Resume":
			self.current_frame.destroy()
			self.handler.set_state("resume")
		# saves the game and goes to main menu
		elif option == "Save and Exit":
			# gets the information about the current game being player
			# stores that inforamtion into a file
			with open("saved_games.txt","a") as saved_games:
				saved_games.write(self.handler.get_current_game_save_info() + "\n")
				saved_games.close()

			# returns to main menu
			self.state = "menu"
			self.current_frame.destroy()
			self.current_frame = self.get_main_menu_frame()
			self.current_frame.pack()

	# creates the frame and all the tkinter objects that are required for the main menu
	def get_main_menu_frame(self):
		# creates container frame
		main_menu_frame = tk.Frame(width=self.handler.get_swidth(), height=self.handler.get_sheight(), background="black")
		# creates display image
		self.main_menu_image = self.resize_image("Images/main_menu_image.png", self.handler.get_swidth()//2, self.handler.get_sheight())
		# creates all the selectable options of the menu
		# play, load, leaderboard, options and exit
		for index, text in enumerate(["Play","Load","Leaderboard","Options","Exit"]):
			original_y = 3*self.handler.get_sheight()//7
			if text == "Options":
				menu_btn = tk.Label(master=main_menu_frame, text=text, fg="white", font=("Courier", 20, "bold"), background="black", name="main_menu_options") 
			else:
				menu_btn = tk.Label(master=main_menu_frame, text=text, fg="white", font=("Courier", 20, "bold"), background="black") 
			# binds the functions to handle hover animations and the processes when selected
			menu_btn.bind("<Button-1>", self.handle_menu_options)
			menu_btn.bind("<Enter>", self.on_enter)
			menu_btn.bind("<Leave>", self.on_leave)
			# places the label in the frame
			menu_btn.place(x=3*self.handler.get_swidth()//4, y=original_y + 50*index, anchor="center")

		# creates the main menu title (title of the game)
		title_label = tk.Label(master=main_menu_frame, text="Nuclear\nWhiskers", fg="white", background="black", font=("Courier", 40, "bold"))
		title_label.place(x=3*self.handler.get_swidth()//4, y=self.handler.get_sheight()//5, anchor="center")

		# places the display image
		main_menu_image_label = tk.Label(master=main_menu_frame, image=self.main_menu_image, background="black")
		main_menu_image_label.place(x=0, y=0)

		return main_menu_frame

	# creates all the tkinter objects for the game over menu
	def get_game_over_frame(self):
		# function called for when the player writes and saves their name (to save their score)
		def entered_name():
			# gets widgetk and the name entered into the widget
			name = save_score_entry.get()
			save_score_entry.config(state="disabled")
			# saves the score in the leaderboard file
			self.save_score(name)
			# indicates to the player that the score has been saved
			saved_score_label.place(x=3*self.handler.get_swidth()//4, y=4*self.handler.get_sheight()//7, anchor="center")

		# creates the container for all the game over objects
		game_over_frame = tk.Frame(width=self.handler.get_swidth(), height=self.handler.get_sheight(), background="black")

		# get the game over image to go on side of the screen
		game_over_image = self.resize_image("Images/main_menu_image.png", self.handler.get_swidth()//2, self.handler.get_sheight())
		# create a label for each of the options the player can select (play again and main menu)
		for index, text in enumerate(["Play Again", "Main Menu"]):
			original_y = 5*self.handler.get_sheight()//7
			menu_btn = tk.Label(master=game_over_frame, text=text, fg="white", font=("Courier", 20, "bold"), background="black")
			# attach functions for when mouse hovers over and clicks on the label
			menu_btn.bind("<Button-1>", self.handle_menu_options)
			menu_btn.bind("<Enter>", self.on_enter)
			menu_btn.bind("<Leave>", self.on_leave)
			# place the label onto the screen
			menu_btn.place(x=3*self.handler.get_swidth()//4, y=original_y + 50*index, anchor="center")

		# create a label saying game over at the top of the screen
		title_label = tk.Label(master=game_over_frame, text="Game Over", fg="white", background="black", font=("Courier", 40, "bold"))
		title_label.place(x=3*self.handler.get_swidth()//4, y=self.handler.get_sheight()//5, anchor="center")

		# create a label below with the final score of the player
		score_label = tk.Label(master=game_over_frame, text=f"Final Score: {self.handler.get_current_game_score()}", fg="white", background="black", font=("Courier", 20, "bold"))
		score_label.place(x=3*self.handler.get_swidth()//4, y=2*self.handler.get_sheight()//7, anchor="center")

		# draw the game over image to the screen
		# same as main menu one for now
		game_over_image_label = tk.Label(master=game_over_frame, image=self.main_menu_image, background="black")
		game_over_image_label.place(x=0, y=0)

		# create an entry box for the player to enter their name at the end of the game
		# bind when player presses enter in order to save score
		save_score_entry = tk.Entry(master=game_over_frame, font=("Courier", 18, "bold"))
		#save_score_entry.bind("<Return>", entered_name)
		save_score_entry.place(x=3*self.handler.get_swidth()//4, y=3*self.handler.get_sheight()//7, anchor="center")

		save_score_button = tk.Button(master=game_over_frame, text="Save", command=entered_name, font=("Courier", 18, "bold"))
		save_score_button.place(x=6*self.handler.get_swidth()//7, y=3*self.handler.get_sheight()//7 + 30)

		# label that indicates score was saved
		saved_score_label = tk.Label(master=game_over_frame, text="Score Saved!", font=("Courier", 18, "bold"), fg="yellow", background="black")

		return game_over_frame
	
	# function to get the tkinter objects for the pause menu
	def get_pause_frame(self):
		# create pause menu container object
		pause_frame = tk.Frame(width=self.handler.get_swidth(), height=self.handler.get_sheight(), background="black")
		# create a label for each of the options the player can press (resume, options, save and exit, main menu)
		for index, text in enumerate(["Resume", "Options", "Save and Exit", "Main Menu"]):
			# get the y position where the options will start from
			original_y = 2*self.handler.get_sheight()//5
			if text == "Options":
				menu_btn = tk.Label(master=pause_frame, text=text, fg="white", font=("Courier", 20, "bold"), background="black", name="pause_menu_options") 
			else:
				menu_btn = tk.Label(master=pause_frame, text=text, fg="white", font=("Courier", 20, "bold"), background="black")
			# attach the functions for when mouse hovers or selects one of the options
			menu_btn.bind("<Button-1>", self.handle_menu_options)
			menu_btn.bind("<Enter>", self.on_enter)
			menu_btn.bind("<Leave>", self.on_leave)
			# place label onto the screen
			menu_btn.place(x=self.handler.get_swidth()//2, y=original_y + 50*index, anchor="center")
		
		# add a title label that says pause
		pause_title_label = tk.Label(master=pause_frame, text="Paused", fg="white", background="black", font=("Courier", 40, "bold"))
		pause_title_label.place(x=self.handler.get_swidth()//2, y=self.handler.get_sheight()//5, anchor="center")

		# return the container object
		return pause_frame
	
	# function called to get the tkinter objects for the leaderboard
	def get_leaderboard_frame(self):
		# crate the container object
		leaderboard_frame = tk.Frame(width=self.handler.get_swidth(), height=self.handler.get_sheight(), background="black")
		# create the title of the menu (leaderboard)
		leaderboard_title = tk.Label(master=leaderboard_frame, text="Leaderboard", fg="white", background="black", font=("Courier", 40, "bold"))
		leaderboard_title.place(x=3*self.handler.get_swidth()//4, y=self.handler.get_sheight()//10, anchor="center")

		# create a single option label for returning to the main menu
		menu_btn = tk.Label(master=leaderboard_frame, text="Main Menu", fg="white", font=("Courier", 20, "bold"), background="black")
		# attach the functions for when the player hovers or selects one of the options
		menu_btn.bind("<Button-1>", self.handle_menu_options)
		menu_btn.bind("<Enter>", self.on_enter)
		menu_btn.bind("<Leave>", self.on_leave)
		# place label onto screen
		menu_btn.place(x=3*self.handler.get_swidth()//4, y=self.handler.get_sheight()-100, anchor="center")

		# open leaderboard.txt to get the top five scores 
		with open("leaderboard.txt","r") as leaderboard:
			# read all lines
			scores = leaderboard.readlines()
			# separate each entry into their individual components as a list (name, score and date)
			scores = list(map(lambda x: x.rstrip().split(","), scores))
			# sort the list by the score portion of the entry
			scores.sort(reverse=True, key=lambda x: int(x[1]))
			# if there are no scores at all
			if len(scores) == 0:
				# create a label that indicates no score has been saved yet
				empty_leaderboard_label = tk.Label(master=leaderboard_frame, text="There are no scores available!",  fg="white", background="black", font=("Courier", 15, "bold"))
				empty_leaderboard_label.place(x=3*self.handler.get_swidth()//4, y=self.handler.get_sheight()//5, anchor="center")
			else:
				# get the y in which all scores will be placed below
				original_y = 1.5*self.handler.get_sheight()//5

				# for the top 5 scores on the leaderboard
				for index, score in enumerate(scores[:5]):
					# create a label for what position they are in
					position_label = tk.Label(master=leaderboard_frame, text=f"{index+1}.", fg="yellow", font=("Courier", 15, "bold"), background="black")
					# create a label for their name
					name_label = tk.Label(master=leaderboard_frame, text=score[0], fg="white", font=("Courier", 15, "bold"), background="black")
					# create a label for their score
					score_label = tk.Label(master=leaderboard_frame, text=score[1], fg="white", font=("Courier", 15, "bold"), background="black")
					# creat ea label for their time
					time_label = tk.Label(master=leaderboard_frame, text=score[2], fg="white", font=("Courier", 15, "bold"), background="black")
					# place all labels onto the screen
					position_label.place(x=2*self.handler.get_swidth()//4 + 50, y=original_y+index*50, anchor="center")
					name_label.place(x=3*self.handler.get_swidth()//4 - 100, y=original_y+index*50, anchor="center")
					score_label.place(x=3*self.handler.get_swidth()//4, y=original_y+index*50, anchor="center")
					time_label.place(x=3*self.handler.get_swidth()//4 + 100, y=original_y+index*50, anchor="center")

			leaderboard.close()

		# draw the main menu image on the side of the screen
		leaderboard_label = tk.Label(master=leaderboard_frame, image=self.main_menu_image, background="black")
		leaderboard_label.place(x=0, y=0)

		return leaderboard_frame
	
	# function to get the tkinter objects for the load menu
	def get_load_frame(self):
		# function for when player presses one of the saved games labels
		def game_loaded(saved_game):
			# destroys current frame and loads the information from that saved game
			self.current_frame.destroy()
			self.loaded_game = saved_game
			self.handler.set_state("load_game")
		# called whenever mouse hovers over one of the saved game labels
		def on_enter(event):
			# increases size of label and changes colour to yellow
			event.widget.configure(fg="yellow", font=("Courier", 18, "bold"))
		# called whenever mosue unhovers over one of the saved game labels
		def on_release(event):
			# returns label colour to white and its original size
			event.widget.configure(fg="white", font=("Courier",15,"bold"))
			
		# create the container for all leaderboardr items
		load_frame = tk.Frame(width=self.handler.get_swidth(), height=self.handler.get_sheight(), background="black")

		# create the title (load game)
		load_title = tk.Label(master=load_frame, text="Load Game", fg="white", background="black", font=("Courier", 40, "bold"))
		load_title.place(x=3*self.handler.get_swidth()//4, y=self.handler.get_sheight()//10, anchor="center")

		# create single label to return back to main menu
		menu_btn = tk.Label(master=load_frame, text="Main Menu", fg="white", font=("Courier", 20, "bold"), background="black") 
		# bind functions to it for when player hovers or clicks on the option
		menu_btn.bind("<Button-1>", self.handle_menu_options)
		menu_btn.bind("<Enter>", self.on_enter)
		menu_btn.bind("<Leave>", self.on_leave)
		# place label onto the scren
		menu_btn.place(x=3*self.handler.get_swidth()//4, y=self.handler.get_sheight()-100, anchor="center")

		# open saved games to get the most recent entries and display them
		with open("saved_games.txt","r") as saved_games:
			games = saved_games.readlines()
			original_y = 2*self.handler.get_sheight()//7
			for index,game in enumerate(games[-5::]):
				# information split by ; as , was used elsewhere in the saved game format
				game = game.split(";")
				# turn first item into a tuple
				game_text = ast.literal_eval(game[0])
				#create label for each saved game 
				game_btn = tk.Label(master=load_frame, text=f"Level: {game_text[0]}, Date: {game_text[1]}", fg="white", font=("Courier", 15, "bold"), background="black")
				# attach functions for when mouse hovers over the label or selects one
				game_btn.bind("<Button-1>", lambda event: game_loaded(game))
				game_btn.bind("<Enter>", on_enter)
				game_btn.bind("<Leave>", on_release)
				# place label onto the screen
				game_btn.place(x=3*self.handler.get_swidth()//4, y=original_y+index*50, anchor="center")

		# draws main menu image onto the screen 
		load_label = tk.Label(master=load_frame, image=self.main_menu_image, background="black")
		load_label.place(x=0, y=0)

		return load_frame
	
	# function for getting the tkinter objects related to displaying the options menu

	##### control changing needs re doing to allow for all controls to be affected #####
	def get_options_frame(self):
		# function called whenever player types something into the controls
		def check_entry(event):
			text = event.widget.get()
			if len(text) >= 1:
				event.widget.delete(0, tk.END)
				event.widget.insert(0, text[0].upper())

		def exit_options(event):
			bindings = self.handler.get_bindings()
			for index, entry in enumerate(control_entries):
				bindings[control_names[index]] = entry.get().lower()

			self.handler.set_bindings(bindings)

			self.handle_menu_options(event)

		options_frame = tk.Frame(width=self.handler.get_swidth(), height=self.handler.get_sheight(), background="black")
		options_title = tk.Label(master=options_frame, text="Options", fg="white", background="black", font=("Courier", 30, "bold"))
		options_title.place(x=3*self.handler.get_swidth()//4, y=self.handler.get_sheight()//7, anchor="center")

		control_names = list(self.handler.get_bindings().keys())
		control_bindings = list(self.handler.get_bindings().values())
		control_entries = []
		original_y = 2*self.handler.get_sheight()//7
		for i in range(len(self.handler.get_bindings())):
			control_name_label = tk.Label(master=options_frame, text=f"{control_names[i]}:", fg="white", background="black", font=("Courier", 15, "bold"))
			control_label = tk.Entry(master=options_frame, font=("Courier", 15, "bold"), width=3)
			control_label.insert(tk.END, control_bindings[i].upper())
			control_label.bind("<KeyRelease>", check_entry)
			control_name_label.place(x=3*self.handler.get_swidth()//4-50, y=original_y+i*40, anchor="center")
			control_label.place(x=3*self.handler.get_swidth()//4+80, y=original_y+i*40, anchor="center")
			control_entries.append(control_label)

		return_btn = tk.Label(master=options_frame, text="Main Menu", fg="white", background="black",font=("Courier",20,"bold"))
		return_btn.bind("<Button-1>", exit_options)
		return_btn.bind("<Enter>", self.on_enter)
		return_btn.bind("<Leave>", self.on_leave)
		return_btn.place(x=3*self.handler.get_swidth()//4, y=6*self.handler.get_sheight()//7, anchor="center")

		options_image_label = tk.Label(master=options_frame, image=self.main_menu_image, background="black")
		options_image_label.place(x=0, y=0)

		return options_frame