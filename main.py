import pygame
from pygame.locals import *
import constants
from gameobjects import *

pygame.init()
display = pygame.display.set_mode(constants.SCREEN_SIZE)
pygame.display.set_caption(constants.TITLE)
clock = pygame.time.Clock()

done = False
start_screen = True
start_image = pygame.image.load("start.png")
dead_image = pygame.image.load("death.png")
bg = constants.random_colour()

# Initialize variables (e.g. player)
player = Player()
player.lvl = Lvl1(player)

all_sprites = pygame.sprite.Group(player)

hearts = pygame.sprite.Group()

font = pygame.font.Font("PressStart2P.ttf", 20)

while not done:
    # Start screen
    while start_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                start_screen = False
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    start_screen = False
        display.blit(start_image, (0, 0))
        pygame.display.update()

    while player.dead:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                player.dead = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                for human in player.lvl.humans:
                    human.kill()
                for powerup in player.lvl.powerups:
                    powerup.kill()
                for bullet in player.lvl.bullets:
                    bullet.kill()
                start_screen = True
                player.dead = False
                player.lvl = Lvl1(player)
                player.health = 20
                player.lives = 3
                player.rect.x = player.lvl.start_pos[0]
                player.rect.y = player.lvl.start_pos[1]
                player.change_x = 0
                player.change_y = 0
                player.score = 0
        display.blit(dead_image, (0, 0))
        pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                player.change_speed(0, -5)
            if event.key == pygame.K_s:
                player.change_speed(0, 5)
            if event.key == pygame.K_a:
                player.change_speed(-5, 0)
            if event.key == pygame.K_d:
                player.change_speed(5, 0)
            if event.key == pygame.K_SPACE:
                if not player.has_gun:
                    player.attack()
                else:
                    player.start_shooting()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                player.change_speed(0, 5)
            if event.key == pygame.K_s:
                player.change_speed(0, -5)
            if event.key == pygame.K_a:
                player.change_speed(5, 0)
            if event.key == pygame.K_d:
                player.change_speed(-5, 0)
            if event.key == pygame.K_SPACE and player.has_gun:
                player.stop_shooting()

    for bullet in player.lvl.bullets:
        if bullet.rect.x > 800 or bullet.rect.x < 0 or bullet.rect.y > 600 or bullet.rect.y < 0:
            player.lvl.bullets.remove(bullet)

        hit = pygame.sprite.spritecollide(bullet, player.lvl.entities, False)
        for entity in hit:
            if entity.UEID != bullet.dont_affect:
                entity.on_hit(bullet)
                player.lvl.bullets.remove(bullet)

    all_sprites.update()
    player.lvl.draw(display)
    player.lvl.blocks.update()
    player.lvl.blocks.draw(display)
    player.lvl.bullets.update()
    player.lvl.bullets.draw(display)
    player.lvl.powerups.update()
    player.lvl.powerups.draw(display)
    player.lvl.humans.update()
    player.lvl.humans.draw(display)
    all_sprites.draw(display)

    text = font.render("SCORE: " + str(player.score), 1, constants.GREEN if player.score >= player.lvl.required_score \
        else constants.RED)
    textpos = text.get_rect()
    textpos.x = 550
    textpos.y = 10
    display.blit(text, textpos)

    for x in range(player.lives):
        heart = Heart(x*16+10, 10)
        hearts.add(heart)

    hearts.draw(display)

    for x in hearts:
        hearts.remove(x)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
