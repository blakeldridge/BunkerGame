	import tkinter as tk

class Menus:
	@classmethod
	def get_main_menu_frame(self):
	    main_menu_frame = tk.Frame(width=WIDTH, height=HEIGHT, background="black")

	    self.main_menu_image = self.resize_image("Images/main_menu_image.png", WIDTH//2, HEIGHT)
	    for index, text in enumerate(["Play","Load","Leaderboard","Options","Exit"]):
	        original_y = 3*HEIGHT//7
	        if text == "Options":
	            menu_btn = tk.Label(master=main_menu_frame, text=text, fg="white", font=("Courier", 20, "bold"), background="black", name="main_menu_options") 
	        else:
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

	@classmethod
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

	@classmethod
	def get_pause_frame(self):
	    pause_frame = tk.Frame(width=WIDTH, height=HEIGHT, background="black")
	    for index, text in enumerate(["Resume", "Options", "Save and Exit", "Main Menu"]):
	        original_y = 2*HEIGHT//5
	        if text == "Options":
	            menu_btn = tk.Label(master=pause_frame, text=text, fg="white", font=("Courier", 20, "bold"), background="black", name="pause_menu_options") 
	        else:
	            menu_btn = tk.Label(master=pause_frame, text=text, fg="white", font=("Courier", 20, "bold"), background="black") 
	        menu_btn.bind("<Button-1>", self.handle_menu_options)
	        menu_btn.bind("<Enter>", self.on_enter)
	        menu_btn.bind("<Leave>", self.on_leave)
	        menu_btn.place(x=WIDTH//2, y=original_y + 50*index, anchor="center")
	    
	    pause_title_label = tk.Label(master=pause_frame, text="Paused", fg="white", background="black", font=("Courier", 40, "bold"))
	    pause_title_label.place(x=WIDTH//2, y=HEIGHT//5, anchor="center")

	    return pause_frame

	@classmethod
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

	@classmethod
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

	@classmethod
	def get_options_frame(self):
	    def check_entry(event):
	        text = event.widget.get()
	        if len(text) >= 1:
	            event.widget.delete(0, tk.END)
	            event.widget.insert(0, text[0].upper())

	    def exit_options(event):
	        for index, entry in enumerate(control_entries):
	            bindings[control_names[index]] = entry.get().lower()

	        self.handle_menu_options(event)

	    options_frame = tk.Frame(width=WIDTH, height=HEIGHT, background="black")
	    options_title = tk.Label(master=options_frame, text="Options", fg="white", background="black", font=("Courier", 30, "bold"))
	    options_title.place(x=3*WIDTH//4, y=HEIGHT//7, anchor="center")

	    control_names = list(bindings.keys())
	    control_bindings = list(bindings.values())
	    control_entries = []
	    original_y = 2*HEIGHT//7
	    for i in range(len(bindings)):
	        control_name_label = tk.Label(master=options_frame, text=f"{control_names[i]}:", fg="white", background="black", font=("Courier", 15, "bold"))
	        control_label = tk.Entry(master=options_frame, font=("Courier", 15, "bold"), width=3)
	        control_label.insert(tk.END, control_bindings[i].upper())
	        control_label.bind("<KeyRelease>", check_entry)
	        control_name_label.place(x=3*WIDTH//4-50, y=original_y+i*40, anchor="center")
	        control_label.place(x=3*WIDTH//4+80, y=original_y+i*40, anchor="center")
	        control_entries.append(control_label)

	    return_btn = tk.Label(master=options_frame, text="Main Menu", fg="white", background="black",font=("Courier",20,"bold"))
	    return_btn.bind("<Button-1>", exit_options)
	    return_btn.bind("<Enter>", self.on_enter)
	    return_btn.bind("<Leave>", self.on_leave)
	    return_btn.place(x=3*WIDTH//4, y=6*HEIGHT//7, anchor="center")

	    options_image_label = tk.Label(master=options_frame, image=self.main_menu_image, background="black")
	    options_image_label.place(x=0, y=0)

	    return options_frame