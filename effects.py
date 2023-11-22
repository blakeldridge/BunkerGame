import tkinter as tk

# simple ui popup that fades away after a few seconds
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

	# function used so it can be removed from memory once finished
	def __del__(self):
		pass

	# function called each gameloop
	def update_effect(self, player_movement):
		# moves slightly upwards each frame
		self.y -= self.speed
		# moves according to player movement
		self.x += player_movement
		# draws text onto screen
		self.text = self.canvas.create_text(self.x, self.y, text=self.raw_text, font=self.font, fill=self.colour)
		self.time_lived += 1
		# if text has been drawn for long enough, return -1 to be removed from the scene
		if self.time_lived > self.time_to_live:
			return -1

# ui text to indicate the level of the bunker, created after each bunker is completed	
class BunkerLevelText:
	def __init__(self, bunker_number, swidth, sheight, canvas):
		self.x = swidth//2
		self.y = sheight//2 - 20
		self.bunker_number = bunker_number
		self.canvas = canvas

		self.time_to_live = 30
		self.time_lived = 0

	# function used so it can be removed from memory once finished
	def __del__(self):
		pass

	# funciton called each gameloop
	def update_effect(self, player_movement=None):
		# draws text onto screen
		self.text = self.canvas.create_text(self.x, self.y, text=f"Level {self.bunker_number}", font=("Courier", 30, "bold"), fill="white")
		self.time_lived += 1
		# if text has been drawn for long enough, return -1 to be removed from the scene
		if self.time_lived > self.time_to_live:
			return -1

# animation blood splatter effect for when enemies are hit
class BloodEffect:
	def __init__(self, x, y, canvas):
		self.x = x
		self.y = y
		self.canvas = canvas
		self.current_animation = 1
		self.final_frame = 10
		self.current_frame = 1
		self.image = tk.PhotoImage(file=f"Images/blood_splatter/frame_{self.current_animation}.png")

	# function used so it can be removed from memory once finished
	def __del__(self):
		pass

	# returns the next frame in the animation
	def get_image(self):
		return tk.PhotoImage(file=f"Images/blood_splatter/frame_{self.current_animation}.png")

	# called each gameloop
	def update_effect(self, player_movement=None):
		# move to next animation frame every 2 frames
		if self.current_frame % 2 == 0:
			self.current_animation += 1
			self.current_frame = 1

		self.current_frame += 1
		# move according to player movement
		self.x += player_movement
		# get frame to be drawn onto the screen
		self.image = self.get_image()
		# draw image onto screen
		self.canvas.create_image(self.x, self.y, image=self.image)
		# once the animation has complete, return -1 to be removed from the scene
		if self.current_animation >= self.final_frame:
			return -1

# effect player when the player is hit
# slightly transparent red rectangle that covers the screen
class OnHitEffect:
	def __init__(self, swidth, sheight, canvas):
		self.x1, self.x2 = 0, swidth
		self.y1, self.y2 = 0, sheight
		self.canvas = canvas
		self.stipple = "gray12"
		self.colour = "red"
		self.time_to_live = 5
		self.time_lived = 0

	# method used to allow for it to be removed from memory once the effect is completed
	def __del__(self):
		pass

	# called each frame and handles all the processes of the effect
	def update_effect(self, player_movement):
		# if effect is completed, return -1 to indicate it needs to be removed
		if self.time_lived >= self.time_to_live:
			return -1
		self.time_lived += 1
		# draw the effect onto the screen
		self.canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, stipple=self.stipple, fill=self.colour)

# effect that displays an exclamation mark before an incoming trap
class TrapWarningEffect:
	def __init__(self, x, y, spawner, canvas):
		self.x = x
		self.y = y
		self.canvas = canvas
		self.spawner = spawner

		self.time_to_live = 20
		self.time_lived = 0

		self.image = tk.PhotoImage(file="Images/exclamation.png")

	# method to allow for object to be removed from memory once it has finished
	def __del__(self):
		pass

	# function called each frame that handles all the processes of the ffect
	def update_effect(self, player_movement):
		# checks if it has been displayed for long enough
		if self.time_lived >= self.time_to_live:
			# spawns a trap before being removed
			self.spawner.spawn_trap(self.x, self.y)
			return -1

		self.time_lived += 1
		# adjust the position based on players movement
		self.x += player_movement
		# draw the exlcamtion image
		self.canvas.create_image(self.x, self.y, image=self.image)