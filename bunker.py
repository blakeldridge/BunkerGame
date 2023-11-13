from PIL import Image, ImageTk
import random

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

        self.begin_bunker()

    def calculate_enemy_range(self, bunker_number, is_crazy_bunker):
        lower_range = 5 + bunker_number
        if random.random() > 0.5:
            upper_range = 10 + bunker_number*2
        else:
            upper_range = 10 + bunker_number

        if is_crazy_bunker:
            return 2*lower_range, 2*upper_range
        else:
            return lower_range, upper_range

    def get_remaining_enemies(self):
        return self.total_enemies - self.enemy_count

    def enemy_spawned(self):
        self.enemy_count += 1

    def check_bunker_completed(self, current_enemy_count):
        if self.enemy_count >= self.total_enemies and current_enemy_count == 0:
            return True
        return False

    def generate_foreground_image(self, image_dir):
        image = Image.open(image_dir)
        resized_image = image.resize((self.foreground_dimensions[0], self.foreground_dimensions[1]), Image.NEAREST)
        return ImageTk.PhotoImage(resized_image)

    def create_foreground(self):
        foreground = [Foreground(self.foreground_dimensions[0]*i, self.sheight//2, self.foreground_image) for i in range(self.bunker_width*2)]
        foreground.insert(0, Foreground(-self.foreground_dimensions[0], self.sheight//2, self.foreground_edge_left))
        foreground.append(Foreground(self.foreground_dimensions[0]*self.bunker_width, self.sheight//2, self.foreground_edge_right))
        return foreground

    def get_starting_x(self):
        index = self.bunker_width // 2
        return self.foreground[index].x + self.foreground_dimensions[0]//2
        
    def begin_bunker(self):
        change_in_x = self.get_starting_x()
        for foreground_image in self.foreground:
            foreground_image.move(dx=-change_in_x)

    def check_at_edge(self, width):
        if self.foreground[0].x - self.background_dimensions[0]//4 >= 0:
            return "left"
        elif self.foreground[-1].x + self.background_dimensions[0]//4 <= width:
            return "right"
        else:
            return None
        
    def camera_move_foreground(self, player_x):
        for foreground_image in self.foreground:
            foreground_image.move(dx=player_x)

    def draw_foreground(self):
        for foreground in self.foreground:
            foreground.draw(self.canvas)