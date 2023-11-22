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

    # called when the player mvoes to the next bunker level
    def bunker_reset(self, is_crazy_bunker):
        # increase the spawn rate if the bunker is "crazy"
        if is_crazy_bunker:
            self.normal_spawn_rate = self.spawn_rate
            self.spawn_rate = self.spawn_rate // 1.5
        # if not, simply increase spawn rate
        else:
            self.spawn_rate = self.normal_spawn_rate
            if self.spawn_rate >= 20 and random.random() > 0.5:
                self.spawn_rate -= 1
            self.spawn_tick = 0
            self.normal_spawn_rate = self.spawn_rate

    def get_current_enemy_count(self):
        return len(self.enemies)

    def spawn_trap(self, x, y):
        self.enemies.append(Enemies.BladeTrap(x, y, self.canvas))

    # called when player attacks during the melee
    def melee_attack(self, pointer_dir):
        # loops through each of the enemies
        for enemy in reversed(self.enemies):
            # get the hitbox from whether player is facing left or right
            if pointer_dir == "right":
                hit_condition = enemy.x > self.player.x and enemy.x < self.player.x + 150
            else:
                hit_condition = enemy.x < self.player.x and enemy.x > self.player.x - 150
            # if the enemy is within the hit range and is not a trap
            if type(enemy) != Enemies.BladeTrap and hit_condition:
                # add blood effect and take damage, remove enemy if they have no more health
                self.game_manager.add_effect(effects.TextPopUp(enemy.x, enemy.y-enemy.hitbox_height, str(self.player.melee_damage), "red", 5, self.DAMAGE_FONT, self.canvas))
                if enemy.take_damage(self.player.melee_damage) == -1:
                    self.enemies.remove(enemy)
                    del enemy

    # function to spawn an enemy
    def spawn_random(self, bunker_number, swidth, sheight):
        # 25% chance for any enemy to spawn
        # this is implemented as trap has different spawning version than regular enemies
        if random.random() > 0.25:
            # randomly spawn in enemy outside of the screen
            self.enemies.append(random.choice([Enemies.RatEnemy(random.choice([swidth+200, -200]), 4*sheight//5, bunker_number, self.canvas), 
                    Enemies.BatEnemy(random.choice([swidth+200, -200]), 4*sheight//5, bunker_number, self.canvas),
                    Enemies.MoleEnemy(random.randint(0, swidth), 4*sheight//5, bunker_number, self.canvas, swidth)]))
        else:
            self.game_manager.add_effect(effects.TrapWarningEffect(swidth//2, 4*sheight//5, self, self.canvas))

    # function to check whether a collision occurs with any enemy
    def check_enemy_collision(self, bullet):
        # check all enemies
        for enemy in reversed(self.enemies):
            # if enemy is not a trap and the enemy collides wit hthe bullet
            if type(enemy) != Enemies.BladeTrap and self.game_manager.check_collision(bullet, enemy):
                # add blood effect and take damage, if the enemy is dead, remove from spawner
                self.game_manager.add_effect(effects.TextPopUp(enemy.x, enemy.y-enemy.hitbox_height, str(bullet.damage), "red", 5, self.DAMAGE_FONT, self.canvas))
                if enemy.take_damage(bullet.damage) == -1:
                    self.enemies.remove(enemy)
                    del enemy
                return 1
        return 0

    # function that is called each frame and handles all enemy logic
    def update_spawner(self, player_movement, remaining_enemies, bunker_number, swidth, sheight):
        # loops through enemies all enemies to update them
        for enemy in reversed(self.enemies):
            update_status = enemy.update_enemy(self.player, player_movement)
            # if returns hit player, player takes damage
            if update_status == "hit_player":
                self.game_manager.add_effect(effects.OnHitEffect(swidth, sheight, self.canvas))
            # if reutnrs mole attack (when mole enemy attacks), add the pickaxe projectile to the enemy projectiles list
            elif update_status != None and "mole_attack" in update_status:
                self.game_manager.add_enemy_projectile(weapons.PickaxeProjectile(enemy.x, enemy.y, sheight, "right" if "right" in update_status else "left", self.canvas))
            # if retursn remove, remove the enemy from the enemies list (usually comes from traps once finished)
            elif update_status == "remove":
                self.enemies.remove(enemy)
                del enemy

        # check whether ready to spawn
        if self.spawn_tick >= self.spawn_rate and remaining_enemies > 0:
            # spawn an enemy and restart the counter
            self.spawn_random(bunker_number, swidth, sheight)
            self.game_manager.update_bunker_spawns()
            self.spawn_tick = 0

        self.spawn_tick += 1            