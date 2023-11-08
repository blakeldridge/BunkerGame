import random
import Enemies

class Spawner:
    def __init__(self):
        self.spawn_rate = 60
        self.normal_spawn_rate = self.spawn_rate
        self.spawn_tick = 0

    def bunker_reset(self, is_crazy_bunker):
        if is_crazy_bunker:
            self.normal_spawn_rate = self.spawn_rate
            self.spawn_rate = self.spawn_rate // 1.5
        else:
            self.spawn_rate = self.normal_spawn_rate
            if self.spawn_rate >= 20 and random.random() > 0.5:
                self.spawn_rate -= 1
            self.spawn_tick = 0
            self.normal_spawn_rate = self.spawn_rate

    def spawn(self, remaining_enemies, bunker_number, swidth, sheight, canvas):
        enemy = None
        if self.spawn_tick >= self.spawn_rate and remaining_enemies > 0:
            enemy = random.choice([Enemies.RatEnemy(random.choice([swidth+200, -200]), 4*sheight//5, bunker_number, canvas), Enemies.BatEnemy(random.choice([swidth+200, -200]), 4*sheight//5, bunker_number, canvas)])
            self.spawn_tick = 0

        self.spawn_tick += 1
        return enemy