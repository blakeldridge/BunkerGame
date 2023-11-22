import tkinter as tk
import game_manager
import menu_manager

# class to handle the interactions between menus (game over, pause and main menu) and the game
# also handles when the game is started
class Handler:
	def __init__(self):
		self.swidth, self.sheight = 960, 540

		self.window = tk.Tk()
		self.window.title("Nuclear Whiskers")
		self.window.geometry(f"{self.swidth}x{self.sheight}")

		self.bindings = {"Move Right":"d", "Move Left":"a", "Interact":"e", "Reload":"r", "Heal":"2", "Melee":"3", "Boss Button":"o", "Cheats": "p"}

		self.game = game_manager.GameManager(self)
		self.menu = menu_manager.MenuManager(self)

		self.state = "menu"

	def get_swidth(self):
		return self.swidth

	def get_sheight(self):
		return self.sheight

	def get_window(self):
		return self.window

	def get_bindings(self):
		return self.bindings

	def get_state(self):
		return self.state

	def get_current_game_save_info(self):
		return self.game.get_save_info()

	def get_current_game_score(self):
		return self.game.get_score()

	def set_bindings(self, bindings):
		self.bindings = bindings

	# called each time a state of the game is changed
	# displays the correct menu or the game depending on which state it it
	def set_state(self, state):
		self.state = state
		if state == "menu":
			self.menu.get_current_frame().pack()
		elif state == "game":
			self.menu.destroy_current_frame()
			self.game.setup_game_loop()
		elif state == "pause":
			self.menu.pause()
			self.menu.get_current_frame().pack()
		elif state == "resume":
			self.state = "game"
			self.menu.destroy_current_frame()
			self.game.resume()
		elif state == "game_over":
			self.menu.game_over()
			self.menu.get_current_frame().pack()
		elif state == "load_game":
			self.state = "game"
			self.game.setup_game_loop(self.menu.get_loaded_game())

	# function called to load the application
	def loop(self):
		self.menu.get_current_frame().pack()

		self.window.mainloop()

if __name__ == "__main__":
	handler = Handler()
	handler.loop()