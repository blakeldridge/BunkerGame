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
    def __init__(self, canvas, sheight):
        self.sheight = sheight
        self.canvas = canvas
        self.total_enemies = 1 #random.randint(5,10)
        self.enemy_count = 0
        self.bunker_complete = False

        self.bunker_width = random.randint(1, 4)
        self.foreground_dimensions = [500, 300]
        self.background_dimensions = [1000, 300]

        self.foreground_image = self.generate_foreground_image("Images/foreground.png")
        self.foreground_edge_right = self.generate_foreground_image("Images/foreground_edge_right.png")
        self.foreground_edge_left = self.generate_foreground_image("Images/foreground_edge_left.png")
        self.foreground = self.create_foreground()

        self.begin_bunker()

    def enemy_killed(self):
        self.enemy_count += 1

    def check_bunker_completed(self):
        if self.enemy_count >= self.total_enemies:
            return True
        return False

    def generate_foreground_image(self, image_dir):
        image = Image.open(image_dir)
        resized_image = image.resize((self.foreground_dimensions[0], self.foreground_dimensions[1]), Image.NEAREST)
        return ImageTk.PhotoImage(resized_image)

    def create_foreground(self):
        """foreground = [Foreground(self.foreground_dimensions[0]*i, (self.sheight-self.foreground_dimensions[1])//2, self.foreground_image) for i in range(self.bunker_width*2)]
        foreground.insert(0, Foreground(-self.foreground_dimensions[0], (self.sheight-self.foreground_dimensions[1])//2, self.foreground_edge_left))
        foreground.append(Foreground(self.foreground_dimensions[0]*self.bunker_width, (self.sheight-self.foreground_dimensions[1])//2, self.foreground_edge_right))
        """
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