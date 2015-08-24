import pygame
import constants
import math
import random
import string

UEIDs = []


def gen_ueid():
    chars = string.ascii_letters + string.digits
    result = ""
    for x in range(10):
        result += random.choice(chars)
    if result not in UEIDs:
        UEIDs.append(result)
        print("GENERATED UEID:", result)
        return result
    else:
        return gen_ueid()


class SpriteSheet(object):
    _cache = {}

    @classmethod
    def get(cls, filename, alpha=False):
        """Load a sprite sheet, or return the cached sheet if possible."""
        sheet = cls._cache.get(filename)
        if sheet:
            return sheet
        sheet = cls._cache[filename] = SpriteSheet(filename, alpha)
        return sheet

    def __init__(self, filename, alpha=False):
        self.sprite_sheet = pygame.image.load(filename)
        self.alpha = alpha
        if alpha:
            self.sprite_sheet.convert_alpha()
        self.width = self.sprite_sheet.get_rect().width
        self.height = self.sprite_sheet.get_rect().height

    def get_image(self, x, y, width, height):
        if self.alpha:
            image = pygame.Surface((width, height), pygame.SRCALPHA)
        else:
            image = pygame.Surface((width, height))
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        if not self.alpha:
            image.set_colorkey(constants.BLACK)
        return image


def get_sprites(filename, alpha=False):
    """Load a sprite sheet."""
    return SpriteSheet.get(filename, alpha)


class Block(pygame.sprite.Sprite):

    noclip = False
    name = "block"

    def __init__(self, x, y):
        super().__init__()

        self.surface = pygame.Surface((32, 32))
        self.surface.fill(constants.BLUE)
        self.rect = self.surface.get_rect()

        self.rect.x = x
        self.rect.y = y

    def on_player_touch(self, player):
        pass

    def on_destroy(self, player):
        pass


class Player(pygame.sprite.Sprite):

    change_x = 0
    change_y = 0

    has_gun = False

    counter = 0

    name = "player"

    walking_r = []
    walking_l = []
    walking_u = []
    walking_d = []

    attack_r = []
    attack_l = []
    attack_u = []
    attack_d = []

    gun_r = []
    gun_d = []
    gun_l = []
    gun_u = []

    idle_u = []
    idle_d = []
    idle_r = []
    idle_l = []

    idle_g_u = []
    idle_g_d = []
    idle_g_l = []
    idle_g_r = []

    direction = "d"

    lvl = None

    get_sprites
    spritesheet = get_sprites("player.png")

    attacking = False
    shooting = False
    health = 20
    lives = 3

    max_anim_frame = 0
    playing_anim = None
    anim_frame = 0

    score = 0

    def __init__(self):
        super().__init__()
        self.UEID = gen_ueid()

        spritesheet = get_sprites("sprites/monster_back.png", alpha=True)
        image = spritesheet.get_image(288, 0, 32, 32)
        self.idle_u.append(image)
        spritesheet = get_sprites("sprites/monster_front.png", alpha=True)
        image = spritesheet.get_image(288, 0, 32, 32)
        self.idle_d.append(image)
        spritesheet = get_sprites("sprites/monster_left.png", alpha=True)
        image = spritesheet.get_image(288, 0, 32, 32)
        self.idle_l.append(image)
        spritesheet = get_sprites("sprites/monster_right.png", alpha=True)
        image = spritesheet.get_image(288, 0, 32, 32)
        self.idle_r.append(image)
        for i in range(spritesheet.width // 32):
            spritesheet = get_sprites("sprites/monster_back.png", alpha=True)
            image = spritesheet.get_image(i*32, 0, 32, 32)
            self.walking_u.append(image)
            spritesheet = get_sprites("sprites/monster_front.png",
                                      alpha=True)
            image = spritesheet.get_image(i*32, 0, 32, 32)
            self.walking_d.append(image)
            spritesheet = get_sprites("sprites/monster_left.png", alpha=True)
            image = spritesheet.get_image(i*32, 0, 32, 32)
            self.walking_l.append(image)
            spritesheet = get_sprites("sprites/monster_right.png",
                                      alpha=True)
            image = spritesheet.get_image(i*32, 0, 32, 32)
            self.walking_r.append(image)
            self.max_anim_frame += 1

        spritesheet = get_sprites("sprites/monster_back_gun.png", alpha=True)
        image = spritesheet.get_image(288, 0, 32, 32)
        self.idle_g_u.append(image)
        spritesheet = get_sprites("sprites/monster_front_gun.png",
                                  alpha=True)
        image = spritesheet.get_image(288, 0, 32, 32)
        self.idle_g_d.append(image)
        spritesheet = get_sprites("sprites/monster_left_gun.png", alpha=True)
        image = spritesheet.get_image(288, 0, 32, 32)
        self.idle_g_l.append(image)
        spritesheet = get_sprites("sprites/monster_right_gun.png",
                                  alpha=True)
        image = spritesheet.get_image(288, 0, 32, 32)
        self.idle_g_r.append(image)

        for i in range(spritesheet.width // 32):
            spritesheet = get_sprites("sprites/monster_back_gun.png",
                                      alpha=True)
            image = spritesheet.get_image(i*32, 0, 32, 32)
            self.gun_u.append(image)
            spritesheet = get_sprites("sprites/monster_front_gun.png",
                                      alpha=True)
            image = spritesheet.get_image(i*32, 0, 32, 32)
            self.gun_d.append(image)
            spritesheet = get_sprites("sprites/monster_left_gun.png",
                                      alpha=True)
            image = spritesheet.get_image(i*32, 0, 32, 32)
            self.gun_l.append(image)
            spritesheet = get_sprites("sprites/monster_right_gun.png",
                                      alpha=True)
            image = spritesheet.get_image(i*32, 0, 32, 32)
            self.gun_r.append(image)

        spritesheet = get_sprites("sprites/player_thump_back.png",
                                  alpha=True)
        for i in range(spritesheet.width // 32):
            spritesheet = get_sprites("sprites/player_thump_back.png",
                                      alpha=True)
            image = spritesheet.get_image(i*32, 0, 32, 32)
            self.attack_u.append(image)
            spritesheet = get_sprites("sprites/player_thump_front.png",
                                      alpha=True)
            image = spritesheet.get_image(i*32, 0, 32, 32)
            self.attack_d.append(image)
            spritesheet = get_sprites("sprites/player_thump_left.png",
                                      alpha=True)
            image = spritesheet.get_image(i*32, 0, 32, 32)
            self.attack_l.append(image)
            spritesheet = get_sprites("sprites/player_thump_right.png",
                                      alpha=True)
            image = spritesheet.get_image(i*32, 0, 32, 32)
            self.attack_r.append(image)

        self.playing_anim = self.idle_d
        self.image = self.playing_anim[0]
        self.rect = self.image.get_rect()
        self.rect.x = 32
        self.rect.y = 32
        self.dead = False
        self.counter = 0
        self.attack_counter = 0
        self.shoot_counter = 0
        self.shooting_frequency = 4

    def update(self):
        # Movement
        if not self.attacking:
            self.rect.x += self.change_x

        blocks_hit = pygame.sprite.spritecollide(self, self.lvl.blocks, False)
        for block in blocks_hit:
            if not block.noclip:
                if self.change_x > 0:
                    self.rect.right = block.rect.left
                elif self.change_x < 0:
                    self.rect.left = block.rect.right
            block.on_player_touch(self)

        entities_hit = pygame.sprite.spritecollide(self, self.lvl.entities, False)
        for entity in entities_hit:
            if entity.UEID != self.UEID:
                if self.change_x > 0:
                    self.rect.right = entity.rect.left
                elif self.change_x < 0:
                    self.rect.left = entity.rect.right
                entity.on_player_touch(self)

        if not self.attacking:
            self.rect.y += self.change_y

        blocks_hit = pygame.sprite.spritecollide(self, self.lvl.blocks, False)
        for block in blocks_hit:
            if not block.noclip:
                if self.change_y > 0:
                    self.rect.bottom = block.rect.top
                elif self.change_y < 0:
                    self.rect.top = block.rect.bottom
            block.on_player_touch(self)
            if self.attacking:
                block.on_destroy(self)

        entities_hit = pygame.sprite.spritecollide(self, self.lvl.entities, False)
        for entity in entities_hit:
            if entity.UEID != self.UEID:
                if self.change_y > 0:
                    self.rect.bottom = entity.rect.top
                elif self.change_y < 0:
                    self.rect.top = entity.rect.bottom
                entity.on_player_touch(self)

        if self.attacking:
            for block in self.lvl.blocks:
                if block.rect.centerx - 60 < self.rect.centerx < block.rect.centerx + 60 and \
                   block.rect.centery - 60 < self.rect.centery < block.rect.centery + 60:
                    block.on_destroy(self)
            for entity in self.lvl.entities:
                if entity.rect.centerx - 60 < self.rect.centerx < entity.rect.centerx + 60 and \
                   entity.rect.centery - 60 < self.rect.centery < entity.rect.centery + 60:
                    if entity.UEID != self.UEID:
                        entity.on_attacked(self)

        powerups_hit = pygame.sprite.spritecollide(self, self.lvl.powerups, False)
        for powerup in powerups_hit:
            powerup.on_pickup(self)
            powerup.kill()

        if self.attacking:
            if self.attack_counter == 32:
                self.attacking = False
                self.attack_counter = 0

        if self.health <= 0:
            if self.lives != 0:
                self.lives -= 1
                self.health = 20
                self.rect.x, self.rect.y = self.lvl.start_pos
            else:
                self.on_death()

        if not self.has_gun:
            if self.attacking:
                if self.direction == "d":
                    self.playing_anim = self.attack_d
                elif self.direction == "u":
                    self.playing_anim = self.attack_u
                elif self.direction == "l":
                    self.playing_anim = self.attack_l
                elif self.direction == "r":
                    self.playing_anim = self.attack_r
            elif self.change_x != 0 or self.change_y != 0:
                if self.direction == "d":
                    self.playing_anim = self.walking_d
                elif self.direction == "u":
                    self.playing_anim = self.walking_u
                elif self.direction == "l":
                    self.playing_anim = self.walking_l
                elif self.direction == "r":
                    self.playing_anim = self.walking_r
            else:
                if self.direction == "d":
                    self.playing_anim = self.idle_d
                elif self.direction == "u":
                    self.playing_anim = self.idle_u
                elif self.direction == "l":
                    self.playing_anim = self.idle_l
                elif self.direction == "r":
                    self.playing_anim = self.idle_r
        else:
            if self.change_x != 0 or self.change_y != 0:
                if self.direction == "d":
                    self.playing_anim = self.gun_d
                elif self.direction == "u":
                    self.playing_anim = self.gun_u
                elif self.direction == "l":
                    self.playing_anim = self.gun_l
                elif self.direction == "r":
                    self.playing_anim = self.gun_r
            else:
                if self.direction == "d":
                    self.playing_anim = self.idle_g_d
                elif self.direction == "u":
                    self.playing_anim = self.idle_g_u
                elif self.direction == "l":
                    self.playing_anim = self.idle_g_l
                elif self.direction == "r":
                    self.playing_anim = self.idle_g_r

        if self.shooting:
            if self.shoot_counter == self.shooting_frequency:
                if self.direction == "u":
                    self.shoot(0)
                if self.direction == "d":
                    self.shoot(180)
                if self.direction == "l":
                    self.shoot(90)
                if self.direction == "r":
                    self.shoot(270)
                self.shoot_counter = 0

        if self.rect.x > 800:
            self.rect.x = 0
        elif self.rect.x < 0:
            self.rect.x = 800
        elif self.rect.y > 600:
            self.rect.y = 0
        elif self.rect.y < 0:
            self.rect.y = 600

        if self.counter == 1:
            self.counter = 0
            if self.anim_frame != self.max_anim_frame-1:
                self.anim_frame += 1
            else:
                self.anim_frame = 0
        if self.change_x != 0 or self.change_y != 0 or self.attacking:
            self.image = self.playing_anim[self.anim_frame]
        else:
            self.image = self.playing_anim[0]
        self.counter += 1
        if self.attacking:
            self.attack_counter += 1
        if self.shooting:
            self.shoot_counter += 1

    def change_speed(self, x, y):
        self.change_x += x
        self.change_y += y

        if not self.change_x == 0 or not self.change_y == 0:
            if self.change_y > 0:
                self.direction = "d"
            elif self.change_y < 0:
                self.direction = "u"
            elif self.change_x > 0:
                self.direction = "r"
            else:
                self.direction = "l"

    def start_shooting(self):
        self.shooting = True

    def stop_shooting(self):
        self.shooting = False

    def attack(self):
        self.attacking = True
        self.attack_counter = 0
        self.anim_frame = 0

    def on_hit(self, projectile):
        if not self.health <= 0:
            self.health -= projectile.hit_force

    def on_death(self):
        self.dead = True

    def shoot(self, rot):
        self.lvl.bullets.add(Bullet(self.rect.centerx, self.rect.centery, random.randint(rot-5, rot+5), self.lvl, \
                                    self.UEID))


class Human(pygame.sprite.Sprite):
    # Pick a random spritesheet. TODO: Add more spritesheets
    spritesheets_front = ["sprites/scientist_front.png", "sprites/person_front.png"]
    spritesheets_back = ["sprites/scientist_back.png", "sprites/person_back.png"]
    spritesheets_side = ["sprites/scientist_side.png", "sprites/person_side.png"]

    name = "human"

    # Pick a random direction
    dir = random.choice(["r", "l", "u", "d"])
    stopped = True

    change_x = 0
    change_y = 0

    playing_anim = None

    counter = 0
    anim_frame = 0
    max_anim_frame = 0

    def __init__(self, x, y, lvl):
        super().__init__()
        self.UEID = gen_ueid()

        self.idle_u = []
        self.idle_d = []
        self.idle_l = []
        self.idle_r = []
        self.walking_u = []
        self.walking_d = []
        self.walking_l = []
        self.walking_r = []

        spritesheet_chosen = random.randint(0, len(self.spritesheets_front)-1)
        # Load sprites
        print("Loading sprites...")
        spritesheet = get_sprites(self.spritesheets_back[spritesheet_chosen],
                                  alpha=True)
        image = spritesheet.get_image(0, 0, 32, 32)
        self.idle_u.append(image)
        spritesheet = get_sprites(
            self.spritesheets_front[spritesheet_chosen], alpha=True)
        image = spritesheet.get_image(0, 0, 32, 32)
        self.idle_d.append(image)
        spritesheet = get_sprites(
            self.spritesheets_side[spritesheet_chosen], alpha=True)
        image = spritesheet.get_image(0, 0, 32, 32)
        self.idle_l.append(image)
        self.idle_r.append(pygame.transform.flip(image, True, False))
        for i in range(spritesheet.width // 32):
            spritesheet = get_sprites(
                self.spritesheets_back[spritesheet_chosen], alpha=True)
            image = spritesheet.get_image(i*32, 0, 32, 32)
            self.walking_u.append(image)
            spritesheet = get_sprites(
                self.spritesheets_front[spritesheet_chosen], alpha=True)
            image = spritesheet.get_image(i*32, 0, 32, 32)
            self.walking_d.append(image)
            spritesheet = get_sprites(
                self.spritesheets_side[spritesheet_chosen], alpha=True)
            image = spritesheet.get_image(i*32, 0, 32, 32)
            self.walking_l.append(image)
            self.walking_r.append(pygame.transform.flip(image, True, False))
            self.max_anim_frame += 1

        # Grab the stuff and things and stuff (and things)
        if self.dir == "u":
            self.image = self.idle_u[0]
            self.playing_anim = self.idle_u
        elif self.dir == "d":
            self.image = self.idle_d[0]
            self.playing_anim = self.idle_d
        elif self.dir == "l":
            self.image = self.idle_l[0]
            self.playing_anim = self.idle_l
        else:
            self.image = self.idle_r[0]
            self.playing_anim = self.idle_r

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.lvl = lvl

    def update(self):
        # AI
        # 1/20 chance it will start moving/stop
        if random.randint(0, 200) == 1:
            self.stopped = not self.stopped

        # 1/10 chance it will change direction
        if random.randint(0, 100) == 1:
            self.dir = random.choice(["r", "l", "d", "u"])

        if self.stopped:
            self.change_x = 0
            self.change_y = 0
            if self.dir == "r":
                self.playing_anim = self.idle_r
            elif self.dir == "l":
                self.playing_anim = self.idle_l
            elif self.dir == "u":
                self.playing_anim = self.idle_u
            else:
                self.playing_anim = self.idle_d
        else:
            if self.dir == "r":
                self.change_x = 2
                self.change_y = 0
                self.playing_anim = self.walking_r
            elif self.dir == "l":
                self.change_x = -2
                self.change_y = 0
                self.playing_anim = self.walking_l
            elif self.dir == "u":
                self.change_x = 0
                self.change_y = -2
                self.playing_anim = self.walking_u
            else:
                self.change_x = 0
                self.change_y = 2
                self.playing_anim = self.walking_d

        self.rect.x += self.change_x
        hit = pygame.sprite.spritecollide(self, self.lvl.blocks, False)
        for block in hit:
            if self.change_x > 0:
                self.rect.right = block.rect.left
                self.dir = "l"
            elif self.change_x < 0:
                self.rect.left = block.rect.right
                self.dir = "r"

        entities_hit = pygame.sprite.spritecollide(self, self.lvl.entities, False)
        for entity in entities_hit:
            if entity.UEID != self.UEID:
                if self.change_x > 0:
                    self.rect.right = entity.rect.left
                    self.dir = "l"
                elif self.change_x < 0:
                    self.rect.top = entity.rect.bottom
                    self.dir = "r"

        self.rect.y += self.change_y
        hit = pygame.sprite.spritecollide(self, self.lvl.blocks, False)
        for block in hit:
            if self.change_y < 0:
                self.rect.top = block.rect.bottom
                self.dir = "d"
            elif self.change_y > 0:
                self.rect.bottom = block.rect.top
                self.dir = "u"

        entities_hit = pygame.sprite.spritecollide(self, self.lvl.entities, False)
        for entity in entities_hit:
            if entity.UEID != self.UEID:
                if self.change_y > 0:
                    self.rect.bottom = entity.rect.top
                    self.dir = "u"
                elif self.change_y < 0:
                    self.rect.top = entity.rect.bottom
                    self.dir = "d"

        if self.counter == 1:
            self.counter = 0
            if not self.stopped:
                if self.anim_frame != self.max_anim_frame-1:
                    self.anim_frame += 1
                else:
                    self.anim_frame = 0
            else:
                self.anim_frame = 0
        self.image = self.playing_anim[self.anim_frame]
        self.counter += 1

    def on_hit(self, projectile):
        self.kill()
        if projectile.dont_affect == projectile.lvl.player.UEID:
            projectile.lvl.player.score += 10

    def on_attacked(self, player):
        self.kill()
        player.score += 10

    def on_player_touch(self, player):
        pass


class Soldier(pygame.sprite.Sprite):
    # Pick a random spritesheet. TODO: Add more spritesheets
    spritesheets_idle = ["h1_idle.png"]
    spritesheets_move = ["h1_move.png"]

    spritesheet_chosen = 0

    idle_u = []
    idle_d = []
    idle_l = []
    idle_r = []
    walking_u = []
    walking_d = []
    walking_l = []
    walking_r = []
    name = "soldier"

    # Pick a random direction
    dir = random.choice(["r", "l", "u", "d"])
    stopped = True

    change_x = 0
    change_y = 0

    playing_anim = None

    counter = 0
    shoot_counter = 0
    shoot_rot = 0
    # Less = Faster
    shoot_rate = 5
    anim_frame = 0
    max_anim_frame = 0
    mas_idle_anim_frame = 0

    def __init__(self, x, y, lvl):
        super().__init__()
        self.UEID = gen_ueid()
        # Load sprites
        spritesheet_u = get_sprites("sprites/military_back.png", alpha=True)
        spritesheet_d = get_sprites("sprites/military_front.png", alpha=True)
        spritesheet_r = get_sprites("sprites/military_side.png", alpha=True)
        self.idle_u.append(spritesheet_u.get_image(0, 0, 32, 32))
        self.idle_d.append(spritesheet_d.get_image(0, 0, 32, 32))
        self.idle_r.append(spritesheet_r.get_image(0, 0, 32, 32))
        self.idle_l.append(pygame.transform.flip(spritesheet_r.get_image(0, 0, 32, 32), True, False))
        for i in range(spritesheet_u.width // 32):
            image = spritesheet_u.get_image(i*32, 0, 32, 32)
            self.walking_u.append(image)
            image = spritesheet_d.get_image(i*32, 0, 32, 32)
            self.walking_d.append(image)
            image = spritesheet_r.get_image(i*32, 0, 32, 32)
            self.walking_r.append(image)
            self.walking_l.append(pygame.transform.flip(image, True, False))
            self.max_anim_frame += 1

        # Grab the stuff and things and stuff (and things)
        if self.dir == "u":
            self.image = self.idle_u[0]
            self.playing_anim = self.idle_u
        elif self.dir == "d":
            self.image = self.idle_d[0]
            self.playing_anim = self.idle_d
        elif self.dir == "l":
            self.image = self.idle_l[0]
            self.playing_anim = self.idle_l
        else:
            self.image = self.idle_r[0]
            self.playing_anim = self.idle_r

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.lvl = lvl
        self.shooting = True

    def update(self):
        # AI
        # 1/20 chance it will start moving/stop
        if random.randint(0, 200) == 1:
            self.stopped = not self.stopped

        # 1/10 chance it will change direction
        if random.randint(0, 100) == 1:
            self.dir = random.choice(["r", "l", "d", "u"])

        if self.stopped:
            self.change_x = 0
            self.change_y = 0
            if self.dir == "r":
                self.playing_anim = self.idle_r
            elif self.dir == "l":
                self.playing_anim = self.idle_l
            elif self.dir == "u":
                self.playing_anim = self.idle_u
            else:
                self.playing_anim = self.idle_d
        else:
            if self.dir == "r":
                self.change_x = 5
                self.change_y = 0
                self.playing_anim = self.walking_r
            elif self.dir == "l":
                self.change_x = -5
                self.change_y = 0
                self.playing_anim = self.walking_l
            elif self.dir == "u":
                self.change_x = 0
                self.change_y = -5
                self.playing_anim = self.walking_u
            else:
                self.change_x = 0
                self.change_y = 5
                self.playing_anim = self.walking_d

        self.rect.x += self.change_x
        hit = pygame.sprite.spritecollide(self, self.lvl.blocks, False)
        for block in hit:
            if self.change_x > 0:
                self.rect.right = block.rect.left
                self.dir = "l"
            elif self.change_x < 0:
                self.rect.left = block.rect.right
                self.dir = "r"

        entities_hit = pygame.sprite.spritecollide(self, self.lvl.entities, False)
        for entity in entities_hit:
            if entity.UEID != self.UEID:
                if self.change_x > 0:
                    self.rect.right = entity.rect.left
                    self.dir = "l"
                elif self.change_x < 0:
                    self.rect.top = entity.rect.bottom
                    self.dir = "r"

        self.rect.y += self.change_y
        hit = pygame.sprite.spritecollide(self, self.lvl.blocks, False)
        for block in hit:
            if self.change_y < 0:
                self.rect.top = block.rect.bottom
                self.dir = "d"
            elif self.change_y > 0:
                self.rect.bottom = block.rect.top
                self.dir = "u"

        entities_hit = pygame.sprite.spritecollide(self, self.lvl.entities, False)
        for entity in entities_hit:
            if entity.UEID != self.UEID:
                if self.change_y > 0:
                    self.rect.bottom = entity.rect.top
                    self.dir = "u"
                elif self.change_y < 0:
                    self.rect.top = entity.rect.bottom
                    self.dir = "d"

        if self.counter == 5:
            self.counter = 0
            if self.anim_frame != self.max_anim_frame-1:
                self.anim_frame += 1
            else:
                self.anim_frame = 0

        if self.shooting:
            if self.shoot_counter == 20:
                self.shoot(self.shoot_rot)
                self.shoot_counter = 0
            self.shoot_counter += 1

        if self.rect.centerx - 100 < self.lvl.player.rect.centerx < self.rect.centerx + 100:
            self.shooting = True
            if self.lvl.player.rect.y < self.rect.y:
                # Shoot UP
                self.shoot_rot = 0
                self.dir = "u"
            else:
                # Shoot DOWN
                self.shoot_rot = 180
                self.dir = "d"
            self.stopped = True
        elif self.rect.centery - 100 < self.lvl.player.rect.centery < self.rect.centery + 100:
            self.shooting = True
            if self.lvl.player.rect.x > self.rect.x:
                # Shoot RIGHT
                self.shoot_rot = 270
                self.dir = "r"
            else:
                # Shoot LEFT
                self.shoot_rot = 90
                self.dir = "l"
            self.stopped = True
        else:
            self.shooting = False

        if self.stopped:
            self.image = self.playing_anim[self.mas_idle_anim_frame]
        else:
            self.image = self.playing_anim[self.anim_frame]
        self.counter += 1

    def shoot(self, rot):
        self.lvl.bullets.add(Bullet(self.rect.centerx, self.rect.centery, random.randint(rot-5, rot+5), self.lvl, self.UEID))

    def on_hit(self, projectile):
        if projectile.dont_affect != self.UEID:
            self.kill()
        if projectile.dont_affect == self.lvl.player.UEID:
            projectile.lvl.player.score += 20
        gun = Gun(self.rect.centerx, self.rect.centery)
        self.lvl.powerups.add(gun)
        print(self.rect.center)
        print([x.rect.center for x in self.lvl.powerups])

    def on_attacked(self, player):
        self.kill()
        player.score += 20
        gun = Gun(self.rect.centerx, self.rect.centery)
        self.lvl.powerups.add(gun)

    def on_player_touch(self, player):
        pass


class Wall(Block):
    def __init__(self, x, y):
        super().__init__(x, y)
        spritesheet = get_sprites("spritesheet.png")
        self.image = spritesheet.get_image(64, 0, 32, 32)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Spawner(Block):
    def __init__(self, x, y, lvl):
        super().__init__(x, y)

        spritesheet = get_sprites("spritesheet.png")
        self.image = spritesheet.get_image(128, 0, 32, 32)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.timer = 0
        self.lvl = lvl

    def update(self):
        if self.timer == 200:
            if random.randint(0, 10) == 3:
                human = Soldier(self.rect.x, self.rect.y - 40, self.lvl)
            else:
                human = Human(self.rect.x, self.rect.y - 40, self.lvl)
            self.lvl.entities.add(human)
            self.lvl.humans.add(human)
            self.timer = 0
        self.timer += 1
        print(self.timer)


class Exit(Block):
    def __init__(self, x, y):
        super().__init__(x, y)
        spritesheet = get_sprites("spritesheet.png")
        self.image = spritesheet.get_image(0, 0, 64, 32)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.noclip = True

    def on_player_touch(self, player):
        if player.score >= player.lvl.required_score:
            for human in player.lvl.humans:
                human.kill()
            for powerup in player.lvl.powerups:
                powerup.kill()
            for bullet in player.lvl.bullets:
                bullet.kill()

            if player.lvl.num == 1:
                player.lvl = Lvl2(player)
            elif player.lvl.num == 2:
                player.lvl = Lvl3(player)
            player.rect.x = player.lvl.start_pos[0]
            player.rect.y = player.lvl.start_pos[1]


class Bullet(pygame.sprite.Sprite):
    spritesheet = get_sprites("spritesheet.png")
    hit_force = 5

    def __init__(self, x, y, angle, lvl, dont_affect="--------"):
        super().__init__()

        self.frames_lived = 0

        self.ori_angle = angle
        self.original_image = self.spritesheet.get_image(160, 16, 16, 16)
        self.original_rect = self.original_image.get_rect()
        self.angle = -math.radians(angle-270)
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_mag = 8
        self.speed = (self.speed_mag * math.cos(self.angle),
                      self.speed_mag * math.sin(self.angle))
        self.lvl = lvl
        self.dont_affect = dont_affect

    def update(self):
        self.frames_lived += 1
        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]
        self.rect.topleft = self.rect.x, self.rect.y
        if self.frames_lived == 5:
            self.image = pygame.transform.rotate(self.spritesheet.get_image(160, 0, 16, 16), self.ori_angle)
        for block in pygame.sprite.spritecollide(self, self.lvl.blocks, False):
            if block.name != "turret":
                self.lvl.bullets.remove(self)


class Turret(Block):
    spritesheet = get_sprites("spritesheet.png")
    rot = 0
    counter = 0
    barrel = spritesheet.get_image(96, 0, 32, 32)
    disabled = False
    name = "turret"

    def __init__(self, x, y, player):
        super().__init__(x, y)

        # TODO: Display base
        self.image = self.spritesheet.get_image(160, 0, 32, 32)
        self.rect = self.image.get_rect()
        self.original_image = self.barrel
        self.original_rect = self.rect
        self.rect.x = x
        self.rect.y = y
        self.player = player

    def update(self):
        if not self.disabled:
            offset = (self.player.rect.y-self.rect.centery, self.player.rect.x-self.rect.centerx)
            self.rot = 270-math.degrees(math.atan2(*offset))
            self.image = pygame.transform.rotate(self.original_image, self.rot)
            self.rect = self.image.get_rect(center=self.rect.center)
            if self.counter != 100:
                self.counter += 1
            else:
                self.counter = 0
                self.shoot()

    def shoot(self):
        self.player.lvl.bullets.add(Bullet(self.rect.centerx, self.rect.centery, self.rot, self.player.lvl))

    def on_destroy(self, player):
        self.disabled = True


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

    def on_pickup(self, player):
        pass


class HealingPot(PowerUp):
    spritesheet = get_sprites("spritesheet.png")

    def __init__(self, x, y):
        super().__init__(x, y)

        self.image = self.spritesheet.get_image(172, 0, 16, 16)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def on_pickup(self, player):
        player.health = 20


class Heart(pygame.sprite.Sprite):
    spritesheet = get_sprites("spritesheet.png")

    def __init__(self, x, y):
        super().__init__()

        self.image = self.spritesheet.get_image(176, 16, 16, 16)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Gun(PowerUp):
    spritesheet = get_sprites("spritesheet.png")

    def __init__(self, x, y):
        super().__init__(x, y)

        self.image = self.spritesheet.get_image(192, 0, 16, 16)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def on_pickup(self, player):
        player.has_gun = True


class ExtraLive(PowerUp):
    spritesheet = get_sprites("spritesheet.png")

    def __init__(self, x, y):
        super().__init__(x, y)

        self.image = self.spritesheet.get_image(176, 16, 16, 16)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def on_pickup(self, player):
        player.lives += 1
        player.health = 20


class Level(object):
    blocks = pygame.sprite.Group()
    bg = constants.random_colour()
    num = 0
    bullets = pygame.sprite.Group()
    entities = pygame.sprite.Group()
    turrets = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    start_pos = (50, 50)
    required_score = 0
    humans = pygame.sprite.Group()

    def __init__(self, player):
        self.player = player
        self.entities.add(player)

    def draw(self, display):
        display.fill(self.bg)

    def convert(self, level):
        blocks = pygame.sprite.Group()
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == "#":
                    block = Wall(x*32, y*32)
                    blocks.add(block)
                elif level[y][x] == "E":
                    block = Exit(x*32, y*32)
                    blocks.add(block)
                elif level[y][x] == "T":
                    block = Turret(x*32, y*32, self.player)
                    blocks.add(block)
                    self.turrets.add(block)
                elif level[y][x] == "H":
                    pot = HealingPot(x*32, y*32)
                    self.powerups.add(pot)
                elif level[y][x] == "L":
                    pot = ExtraLive(x*32, y*32)
                    self.powerups.add(pot)
                elif level[y][x] == "P":
                    per = Human(x*32, y*32, self)
                    self.humans.add(per)
                    self.entities.add(per)
                elif level[y][x] == "S":
                    per = Soldier(x*32, y*32, self)
                    self.humans.add(per)
                    self.entities.add(per)
                elif level[y][x] == "D":
                    block = Spawner(x*32, y*32, self)
                    blocks.add(block)
                elif level[y][x] == "G":
                    p = Gun(x*32, y*32)
                    self.powerups.add(p)
        return blocks


class Lvl1(Level):
    def __init__(self, player):
        super().__init__(player)

        self.num = 1
        self.required_score = 100
        # Level. 25x19

        level = [
            "#########################",
            "#  #                    #",
            "#  #                    #",
            "#  ######D####          #",
            "#            #          #",
            "#            #          #",
            "#            #          #",
            "#      T     #          #",
            "#            #          #",
            "#            #          #",
            "#            #          #",
            "#  ###########          #",
            "#                       #",
            "#                       #",
            "#  ################D#####",
            "#                       #",
            "#                       #",
            "#                     E #",
            "#########################",
        ]
        self.blocks = self.convert(level)
        self.player = player


class Lvl2(Level):
    def __init__(self, player):
        super().__init__(player)

        self.start_pos = (800-64, 600-64)
        self.required_score = 250

        self.num = 2
        level = [
            "#########################",
            "#                       #",
            "#    S       S          #",
            "#                       #",
            "#         ######D####   #",
            "#                   #   #",
            "#    S        T     #   #",
            "#             T     #   #",
            "#             T     #   #",
            "#             T     #   #",
            "#    S        T     #   #",
            "#                   #   #",
            "#                   #   #",
            "#                   #   #",
            "#    S              #   #",
            "#                   #   #",
            "########### H       #   #",
            "# P #E   L          #   #",
            "#########################",
        ]

        self.blocks = self.convert(level)
        self.player = player


class Lvl3(Level):
    def __init__(self, player):
        super().__init__(player)

        self.start_pos = (400, 300)
        self.num = 3
        self.required_score = 400

        level = [
            "#########################",
            "#S          #          S#",
            "# ###  #### # ####  ### #",
            "# ###  #### # ####  ### #",
            "#                       #",
            "# ###  #  ##D##  #  ### #",
            "#S     #    #    #     S#",
            "###### ###     ###  #####",
            "###### #   # #   #  #####",
            "                         ",
            "###### # # # # # #  #####",
            "###### # #     # #  #####",
            "#      # # ### # #      #",
            "#           #           #",
            "# #DD# #### # #### #DD# #",
            "#    #  E       E  #    #",
            "##   # ##### ##### #    #",
            "#H                     L#",
            "#########################",
        ]

        self.blocks = self.convert(level)
        self.player = player

class Lvl4(Level):
    def __init__(self, player):
        super().__init__(player)

        level = [
            "#########################",
            "#                       #",
            "#                       #",
            "#                       #",
            "#                       #",
            "#                       #",
            "#                       #",
            "#                       #",
            "#                       #",
            "#                       #",
            "#                       #",
            "#                       #",
            "#                       #",
            "#                       #",
            "#                       #",
            "#                       #",
            "#                       #",
            "#                       #",
            "#########################",
        ]