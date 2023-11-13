from tkinter.font import Font
import random
import Enemies
import effects
import weapons

class Spawner:
    def __init__(self, game_manager, player, canvas):
        self.spawn_rate = 60
        self.normal_spawn_rate = self.spawn_rate
        self.spawn_tick = 0

        self.game_manager = game_manager
        self.player = player
        self.canvas = canvas

        self.enemies = []

        self.DAMAGE_FONT = Font(
            family="Courier",
            size=15,
            weight="bold"
        )

    def get_save_info(self):
        return [self.normal_spawn_rate]
    
    def load_save_info(self, saved_info):
        self.spawn_rate = saved_info[0]
        self.normal_spawn_rate = saved_info[0]

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

    def get_current_enemy_count(self):
        return len(self.enemies)

    def spawn_trap(self, swidth, sheight):
        return Enemies.BladeTrap(swidth//2, 4*sheight, self.canvas)

    def spawn_random(self, bunker_number, swidth, sheight):
        self.enemies.append(random.choice([Enemies.RatEnemy(random.choice([swidth+200, -200]), 4*sheight//5, bunker_number, self.canvas), 
                Enemies.BatEnemy(random.choice([swidth+200, -200]), 4*sheight//5, bunker_number, self.canvas),
                Enemies.MoleEnemy(random.randint(0, swidth), 4*sheight//5, bunker_number, self.canvas, swidth)]))

    def check_enemy_collision(self, bullet):
        for enemy in self.enemies:
            if self.game_manager.check_collision(bullet, enemy):
                self.game_manager.add_effect(effects.TextPopUp(enemy.x, enemy.y-enemy.hitbox_height, str(bullet.damage), "red", 5, self.DAMAGE_FONT, self.canvas))
                if enemy.take_damage(bullet.damage) == -1:
                    self.enemies.remove(enemy)
                    del enemy
                return 1
        return 0

    def update_spawner(self, player_movement, remaining_enemies, bunker_number, swidth, sheight):
        for enemy in reversed(self.enemies):
            update_status = enemy.update_enemy(self.player, player_movement)
            if update_status == "hit_player":
                self.game_manager.add_effect(effects.OnHitEffect(swidth, sheight, self.canvas))
            elif update_status != None and "mole_attack" in update_status:
                self.game_manager.add_enemy_projectile(weapons.PickaxeProjectile(enemy.x, enemy.y, sheight, "right" if "right" in update_status else "left", self.canvas))
            elif update_status == "remove":
                self.enemies.remove(enemy)
                del enemy

        if self.spawn_tick >= self.spawn_rate and remaining_enemies > 0:
            self.spawn_random(bunker_number, swidth, sheight)
            self.game_manager.update_bunker_spawns()
            self.spawn_tick = 0

        self.spawn_tick += 1            