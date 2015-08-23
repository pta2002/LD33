import pygame
import constants
import math
import random


class SpriteSheet(object):
    sprite_sheet = None

    def __init__(self, file):
        self.sprite_sheet = pygame.image.load(file)
        self.width = self.sprite_sheet.get_rect().width
        self.height = self.sprite_sheet.get_rect().height

    def get_image(self, x, y, width, height):
        image = pygame.Surface((width, height))
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(constants.BLACK)
        return image


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

    counter = 0

    walking_r = []
    walking_l = []
    walking_u = []
    walking_d = []

    attack_r = []
    attack_l = []
    attack_u = []
    attack_d = []

    shoot_r = []
    shoot_l = []
    shoot_d = []
    shoot_u = []

    direction = "d"

    lvl = None

    spritesheet = SpriteSheet("player.png")

    attacking = False
    health = 20
    lives = 3

    def __init__(self):
        super().__init__()

        # TODO: Make walking sprites
        image = self.spritesheet.get_image(0, 64, 32, 32)
        self.walking_r.append(image)

        image = self.spritesheet.get_image(64, 32, 32, 32)
        self.walking_l.append(image)

        image = self.spritesheet.get_image(32, 32, 32, 32)
        self.walking_d.append(image)

        image = self.spritesheet.get_image(32, 64, 32, 32)
        self.walking_u.append(image)

        image = self.spritesheet.get_image(64, 0, 32, 32)
        self.attack_r.append(image)

        image = self.spritesheet.get_image(32, 0, 32, 32)
        self.attack_l.append(image)

        image = self.spritesheet.get_image(0, 0, 32, 32)
        self.attack_d.append(image)

        image = self.spritesheet.get_image(0, 32, 32, 32)
        self.attack_u.append(image)

        self.spritesheet = SpriteSheet("spritesheet.png")

        image = self.spritesheet.get_image(0, 224, 32, 32)
        self.shoot_u.append(image)
        self.shoot_d.append(pygame.transform.rotate(image, 180))
        self.shoot_l.append(pygame.transform.rotate(image, 270))
        self.shoot_r.append(pygame.transform.rotate(image, 90))

        self.image = self.walking_d[0]
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = 50
        self.dead = False

    def update(self):

        # TODO: Implement animation
        if not self.attacking:
            if self.direction == "d":
                self.image = self.walking_d[0]
            elif self.direction == "u":
                self.image = self.walking_u[0]
            elif self.direction == "r":
                self.image = self.walking_r[0]
            elif self.direction == "l":
                self.image = self.walking_l[0]
        else:
            if self.direction == "d":
                self.image = self.attack_d[0]
            elif self.direction == "u":
                self.image = self.attack_u[0]
            elif self.direction == "r":
                self.image = self.attack_r[0]
            else:
                self.image = self.attack_l[0]

        # Movement
        self.rect.x += self.change_x

        blocks_hit = pygame.sprite.spritecollide(self, self.lvl.blocks, False)
        for block in blocks_hit:
            if not block.noclip:
                if self.change_x > 0:
                    self.rect.right = block.rect.left
                elif self.change_x < 0:
                    self.rect.left = block.rect.right
            block.on_player_touch(self)
            if self.attacking:
                block.on_destroy(self)

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

        powerups_hit = pygame.sprite.spritecollide(self, self.lvl.powerups, False)
        for powerup in powerups_hit:
            powerup.on_pickup(self)
            powerup.kill()

        if self.attacking:
            if self.counter == 30:
                self.attacking = False

        self.counter += 1

        if self.health <= 0:
            if self.lives != 0:
                self.lives -= 1
                self.health = 20
                self.rect.x, self.rect.y = self.lvl.start_pos
            else:
                self.on_death()

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

    def attack(self):
        self.attacking = True
        self.counter = 0

    def on_hit(self, projectile):
        if not self.health <= 0:
            self.health -= projectile.hit_force

    def on_death(self):
        self.dead = True


class Human(pygame.sprite.Sprite):
    # Pick a random spritesheet. TODO: Add more spritesheets
    spritesheets_idle = ["h1_idle.png"]
    spritesheets_move = ["h1_move.png"]

    spritesheet_chosen = random.randint(0, len(spritesheets_idle)-1)

    idle_u = []
    idle_d = []
    idle_l = []
    idle_r = []
    walking_u = []
    walking_d = []
    walking_l = []
    walking_r = []

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
        # Load sprites
        print("Loading sprites...")
        spritesheet = SpriteSheet(self.spritesheets_idle[self.spritesheet_chosen])
        for i in range(spritesheet.width // 32):
            image = spritesheet.get_image(i*32, 0, 32, 32)
            self.idle_u.append(image)
            self.idle_d.append(pygame.transform.flip(image, False, True))
            image = pygame.transform.rotate(image, 90)
            self.idle_l.append(image)
            self.idle_r.append(pygame.transform.flip(image, True, False))
            self.max_anim_frame += 1
        spritesheet = SpriteSheet(self.spritesheets_move[self.spritesheet_chosen])
        for i in range(spritesheet.width // 32):
            image = spritesheet.get_image(i*32, 0, 32, 32)
            self.walking_u.append(image)
            self.walking_d.append(pygame.transform.flip(image, False, True))
            image = pygame.transform.rotate(image, 90)
            self.walking_l.append(image)
            self.walking_r.append(pygame.transform.flip(image, True, False))

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

        self.rect.y += self.change_y
        hit = pygame.sprite.spritecollide(self, self.lvl.blocks, False)
        for block in hit:
            if self.change_y < 0:
                self.rect.top = block.rect.bottom
                self.dir = "d"
            elif self.change_y > 0:
                self.rect.bottom = block.rect.top
                self.dir = "u"

        if self.counter == 30:
            self.counter = 0
            if self.anim_frame != self.max_anim_frame-1:
                self.anim_frame += 1
            else:
                self.anim_frame = 0
        self.image = self.playing_anim[self.anim_frame]
        self.counter += 1


class Wall(Block):
    def __init__(self, x, y):
        super().__init__(x, y)
        spritesheet = SpriteSheet("spritesheet.png")
        self.image = spritesheet.get_image(96, 0, 32, 32)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Exit(Block):
    def __init__(self, x, y):
        super().__init__(x, y)
        spritesheet = SpriteSheet("spritesheet.png")
        self.image = spritesheet.get_image(32, 0, 64, 32)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.noclip = True

    def on_player_touch(self, player):
        if player.lvl.num == 1:
            player.lvl = Lvl2(player)


class Bullet(pygame.sprite.Sprite):
    spritesheet = SpriteSheet("spritesheet.png")
    hit_force = 5

    def __init__(self, x, y, angle, lvl):
        super().__init__()

        self.frames_lived = 0

        self.ori_angle = angle
        self.original_image = self.spritesheet.get_image(240, 0, 16, 16)
        self.original_rect = self.original_image.get_rect()
        self.angle = -math.radians(angle-270)
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_mag = 8
        self.speed = (self.speed_mag * math.cos(self.angle),
                      self.speed_mag * math.sin(self.angle))
        self.lvl = lvl

    def update(self):
        self.frames_lived += 1
        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]
        self.rect.topleft = self.rect.x, self.rect.y
        if self.frames_lived == 5:
            self.image = pygame.transform.rotate(self.spritesheet.get_image(192, 0, 16, 16), self.ori_angle)
        for block in pygame.sprite.spritecollide(self, self.lvl.blocks, False):
            if block.name != "turret":
                self.lvl.bullets.remove(self)


class Turret(Block):
    spritesheet = SpriteSheet("spritesheet.png")
    rot = 0
    counter = 0
    barrel = spritesheet.get_image(160, 0, 32, 32)
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
    spritesheet = SpriteSheet("spritesheet.png")

    def __init__(self, x, y):
        super().__init__(x, y)

        self.image = self.spritesheet.get_image(256, 0, 16, 16)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def on_pickup(self, player):
        player.health = 20


class Heart(pygame.sprite.Sprite):
    spritesheet = SpriteSheet("spritesheet.png")

    def __init__(self, x, y):
        super().__init__()

        self.image = self.spritesheet.get_image(272, 0, 16, 16)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class ExtraLive(PowerUp):
    spritesheet = SpriteSheet("spritesheet.png")

    def __init__(self, x, y):
        super().__init__(x, y)

        self.image = self.spritesheet.get_image(272, 0, 16, 16)
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
        return blocks


# TODO: Move levels to separate file
class Lvl1(Level):
    def __init__(self, player):
        super().__init__(player)

        self.num = 1
        # Level. 25x19

        level = [
            "#########################",
            "#                       #",
            "#                       #",
            "#   ####                #",
            "#                       #",
            "#                       #",
            "#                L      #",
            "#                       #",
            "#                       #",
            "#           T           #",
            "#                       #",
            "#                       #",
            "#                       #",
            "#         ##### H       #",
            "#         #   #         #",
            "#         # P #         #",
            "#         #   #         #",
            "#         #####       E #",
            "#########################",
        ]
        self.blocks = self.convert(level)
        self.player = player


class Lvl2(Level):
    def __init__(self, player):
        super().__init__(player)

        self.num = 2
        level = [
            "#########################",
            "#                       #",
            "#                       #",
            "#                       #",
            "#                       #",
            "#                       #",
            "#                       #",
            "#                   #   #",
            "#                   #   #",
            "#                   #   #",
            "#                   #   #",
            "#                   #   #",
            "#                   #   #",
            "#                   #   #",
            "#                   #   #",
            "#                   #   #",
            "#                   #   #",
            "#                   #   #",
            "#########################",
        ]

        self.blocks = self.convert(level)
        self.player = player
