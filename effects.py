import tkinter as tk

class TextPopUp:
	def __init__(self, x, y, text, colour, time_to_live, font, canvas):
		self.x = x
		self.y = y
		self.raw_text = text
		self.colour = colour
		self.font = font
		self.canvas = canvas
		self.time_to_live = time_to_live
		self.time_lived = 0
		self.speed = 1

		self.text = self.canvas.create_text(self.x, self.y, text=self.raw_text, font=self.font, fill=self.colour)

	def __del__(self):
		pass

	def update_effect(self, player_movement):
		self.y -= self.speed
		self.x += player_movement
		self.text = self.canvas.create_text(self.x, self.y, text=self.raw_text, font=self.font, fill=self.colour)
		self.time_lived += 1

		if self.time_lived > self.time_to_live:
			return -1
		
class BunkerLevelText:
	def __init__(self, bunker_number, swidth, sheight, canvas):
		self.x = swidth//2
		self.y = sheight//2 - 20
		self.bunker_number = bunker_number
		self.canvas = canvas

		self.time_to_live = 30
		self.time_lived = 0

	def __del__(self):
		pass

	def update_effect(self, player_movement=None):
		self.text = self.canvas.create_text(self.x, self.y, text=f"Level {self.bunker_number}", font=("Courier", 30, "bold"), fill="white")
		self.time_lived += 1

		if self.time_lived > self.time_to_live:
			return -1

class BloodEffect:
	def __init__(self, x, y, canvas):
		self.x = x
		self.y = y
		self.canvas = canvas
		self.current_animation = 1
		self.final_frame = 10
		self.current_frame = 1
		self.image = tk.PhotoImage(file=f"Images/blood_splatter/frame_{self.current_animation}.png")

	def __del__(self):
		pass

	def get_image(self):
		return tk.PhotoImage(file=f"Images/blood_splatter/frame_{self.current_animation}.png")

	def update_effect(self, player_movement=None):
		if self.current_frame % 2 == 0:
			self.current_animation += 1
			self.current_frame = 1

		self.current_frame += 1
		self.x += player_movement
		self.image = self.get_image()
		self.canvas.create_image(self.x, self.y, image=self.image)
		if self.current_animation >= self.final_frame:
			return -1

class OnHitEffect:
	def __init__(self, swidth, sheight, canvas):
		self.x1, self.x2 = 0, swidth
		self.y1, self.y2 = 0, sheight
		self.canvas = canvas
		self.stipple = "gray12"
		self.colour = "red"
		self.time_to_live = 5
		self.time_lived = 0

	def __del__(self):
		pass

	def update_effect(self, player_movement):
		if self.time_lived >= self.time_to_live:
			return -1
		self.time_lived += 1
		self.canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, stipple=self.stipple, fill=self.colour)