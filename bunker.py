import tkinter as tk
from PIL import Image, ImageTk
import random

# ------ pick-up items ------ #
bandage = {"Image_dir": "Images/bandages.png", "type":"bandage"}
ammo = {"Image_dir": "Images/ammo.png", "type":"ammo"}

# ------ structures ------ #
class Shelf:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = tk.PhotoImage(file="Images/shelf.png")
        self.table_height = 9
        self.item_x_offset = random.choice([random.randint(0, 50), -random.randint(0,50)])

        self.range = 120
        # item does not always spawn on shelf
        self.has_item = random.choice([True, False])
        # choose between the items
        if self.has_item:
            self.item = random.choice([bandage, ammo])
            self.item_image = tk.PhotoImage(file=self.item["Image_dir"])

    # function called when player pressed "e"
    def check_collected(self, player):
        # check if the player is close to the structure
        if self.has_item and player.x < self.x + self.range and player.x > self.x - self.range:
            self.has_item = False
            # player increments the item count
            player.collect_item(self.item["type"])

    # function called when bunker created to move into place according to player spawn
    def move(self, dx):
        self.x += dx

    # function called to handle all processes and drawing of the structure onto the screen
    def draw(self, player, player_movement, canvas):
        # move according to player
        self.x += player_movement
        if self.has_item:
            # if player is in range, draw text on screen indicating that it can be collected
            if player.x < self.x + self.range and player.x > self.x - self.range:
                canvas.create_text(self.x + self.item_x_offset, self.y - (self.table_height+30), text="E to Collect", justify="center", font=("Courier",14,"bold"), fill="white")
            # draw item onto screen
            canvas.create_image(self.x + self.item_x_offset, self.y - self.table_height, image=self.item_image, anchor="s")
        # draw structure onto screen
        canvas.create_image(self.x, self.y, image=self.image, anchor="s")

class Table:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = tk.PhotoImage(file="Images/table.png")
        self.table_height = 70
        self.item_x_offset = random.choice([random.randint(0, 50), -random.randint(0,50)])

        self.range = 120
        self.has_item = True

        # randomly choose item spawning
        self.item = random.choice([bandage, ammo])
        self.item_image = tk.PhotoImage(file=self.item["Image_dir"])

    # function called when "e" is pressed
    def check_collected(self, player):
        # if structure is within range, pickup item
        if self.has_item and player.x < self.x + self.range and player.x > self.x - self.range:
            self.has_item = False
            player.collect_item(self.item["type"])

    # function called when bunker created to move into place according to player spawn
    def move(self, dx):
        self.x += dx

    # function called to handle all processes and drawing of the structure onto the screen
    def draw(self, player, player_movement, canvas):
        # move object according to player movement
        self.x += player_movement
        if self.has_item:
            # check if strucutre is in range, if it is draw text on screen indicating it can be collected
            if player.x < self.x + self.range and player.x > self.x - self.range:
                canvas.create_text(self.x + self.item_x_offset, self.y - (self.table_height+30), text="E to Collect", justify="center", font=("Courier",14,"bold"), fill="white")
            # draw item onto screen
            canvas.create_image(self.x + self.item_x_offset, self.y - self.table_height, image=self.item_image, anchor="s")
        # draw structure onto screen
        canvas.create_image(self.x, self.y, image=self.image, anchor="s")

# ------ bunker ------ #
# foreground class contains and handles the position of the foreground images
class Foreground:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image

    def move(self, dx=0, dy=0):
        self.x += dx
        self.y += dy

    def draw(self, canvas):
        canvas.create_image(self.x, self.y, image=self.image)

# class to handle all the logic about the bunker/map that the player traverses
class Bunker:
    def __init__(self, bunker_number, canvas, sheight, is_crazy_bunker=False):
        self.sheight = sheight
        self.canvas = canvas
        lower, upper = self.calculate_enemy_range(bunker_number, is_crazy_bunker)
        self.total_enemies = random.randint(lower, upper)
        self.enemy_count = 0
        self.bunker_complete = False

        self.bunker_width = random.randint(1, 4)
        self.foreground_dimensions = [500, sheight*3//5]
        self.background_dimensions = [1000, 300]

        self.foreground_image = self.generate_foreground_image("Images/foreground.png")
        self.foreground_edge_right = self.generate_foreground_image("Images/foreground_edge_right.png")
        self.foreground_edge_left = self.generate_foreground_image("Images/foreground_edge_left.png")
        self.foreground = self.create_foreground()

        self.structures = []
        self.create_structures()

        self.begin_bunker()

    # function called at the beginning of each bunker
    # calculates the amount of enemies that should be spawned in this bunker
    # increases in difficulty as the bunker increases
    def calculate_enemy_range(self, bunker_number, is_crazy_bunker):
        # base lower range = 5
        # base upper range = 10
        lower_range = 5 + bunker_number
        # 50% chance of bunker enemy count by 2 instead of 1
        if random.random() > 0.5:
            upper_range = 10 + bunker_number*2
        else:
            upper_range = 10 + bunker_number
        # doubles the enemy count if the bunker is "crazy" <-- random chance of this happening
        if is_crazy_bunker:
            return 2*lower_range, 2*upper_range
        else:
            return lower_range, upper_range

    def get_remaining_enemies(self):
        return self.total_enemies - self.enemy_count

    # function called when an enemy is killed
    def enemy_spawned(self):
        self.enemy_count += 1

    def check_bunker_completed(self, current_enemy_count):
        # if no more enemies can be spawned and all enemies are dead. bunker is complete
        if self.enemy_count >= self.total_enemies and current_enemy_count == 0:
            return True
        return False

    # called to check all structures when "e" is pressed
    def check_interact(self, player):
        for structure in self.structures:
            structure.check_collected(player)

    def generate_foreground_image(self, image_dir):
        # resizes foreground image so that it is the correct size for the game
        image = Image.open(image_dir)
        resized_image = image.resize((self.foreground_dimensions[0], self.foreground_dimensions[1]), Image.NEAREST)
        return ImageTk.PhotoImage(resized_image)

    # function called at beginning of each bunker
    # foreground used to give 3d feel to game and help the player see they are moving
    # created from coordinate 0 (beginning) onwards
    def create_foreground(self):
        # creates number of foreground images depending on random chance
        foreground = [Foreground(self.foreground_dimensions[0]*i, self.sheight//2, self.foreground_image) for i in range(self.bunker_width*2)]
        # adds end pieces to each side of the bunker
        foreground.insert(0, Foreground(-self.foreground_dimensions[0], self.sheight//2, self.foreground_edge_left))
        foreground.append(Foreground(self.foreground_dimensions[0]*self.bunker_width, self.sheight//2, self.foreground_edge_right))
        return foreground

    def create_structures(self):
        # creates 1 table for every 2 middle foreground pieces
        for i in range(self.bunker_width//2):
            self.structures.append(Table(random.randint(0, self.bunker_width * self.foreground_dimensions[0]), 5.2*self.sheight//7))
        # 50% chance of a shelf spawning on each foreground piece
        for foreground in self.foreground:
            if random.random() < 0.5:
                current_shelf = Shelf(foreground.x + random.randint(0, self.foreground_dimensions[0]), 3.5*self.sheight//7 - random.randint(0, 50))
                self.structures.append(current_shelf)

    # finds the mid point of the bunker
    def get_starting_x(self):
        index = self.bunker_width // 2
        return self.foreground[index].x + self.foreground_dimensions[0]//2
        
    def begin_bunker(self):
        # moves each of the foreground pieces and structures according to spawn point of player (center of bunker)
        # otherwise always spawns player at left edge of bunker
        change_in_x = self.get_starting_x()
        for foreground_image in self.foreground:
            foreground_image.move(dx=-change_in_x)

        for structure in self.structures:
            structure.move(-change_in_x)

    # checks whether the player is at either end of the bunker
    # function used to stop the player moving out of the allotted bunker
    def check_at_edge(self, width):
        # checks whether player on left edge
        if self.foreground[0].x - self.background_dimensions[0]//4 >= 0:
            return "left"
        # checks whether player on right edge
        elif self.foreground[-1].x + self.background_dimensions[0]//4 <= width:
            return "right"
        else:
            return None
    # rather than moving player, in order to get smooth camera, the entire map moves (keeps player in the center)
    def camera_move_foreground(self, player_x):
        # moves each foreground piece according to player movement
        for foreground_image in self.foreground:
            foreground_image.move(dx=player_x)
    # function to draw each part of the foreground
    def draw_foreground(self):
        for foreground in self.foreground:
            foreground.draw(self.canvas)
    # draws and moves each structure
    def update_structures(self, player, player_movement):
        for structure in self.structures:
            structure.draw(player, player_movement, self.canvas)