class DamagePopUp:
    def __init__(self, x, y, text, font, canvas):
        self.x = x
        self.y = y
        self.raw_text = text
        self.font = font
        self.canvas = canvas
        self.time_to_live = 5
        self.time_lived = 0

        self.text = self.canvas.create_text(self.x, self.y, text=self.raw_text, font=self.font, fill="red")

    def __del__(self):
        pass

    def update_effect(self, player_movement):
        self.x += player_movement
        self.text = self.canvas.create_text(self.x, self.y, text=self.raw_text, font=self.font, fill="red")
        self.time_lived += 1

        if self.time_lived > self.time_to_live:
            return -1