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
bg = constants.random_colour()

# Initialize variables (e.g. player)
player = Player()
player.lvl = Lvl1(player)

all_sprites = pygame.sprite.Group(player)

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
                player.attack()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                player.change_speed(0, 5)
            if event.key == pygame.K_s:
                player.change_speed(0, -5)
            if event.key == pygame.K_a:
                player.change_speed(5, 0)
            if event.key == pygame.K_d:
                player.change_speed(-5, 0)

    for bullet in player.lvl.bullets:
        if bullet.rect.x > 800 or bullet.rect.x < 0 or bullet.rect.y > 600 or bullet.rect.y < 0:
            player.lvl.bullets.remove(bullet)

        hit = pygame.sprite.spritecollide(bullet, player.lvl.entities, False)
        for entity in hit:
            entity.on_hit(bullet)
            player.lvl.bullets.remove(bullet)

    all_sprites.update()
    player.lvl.draw(display)
    player.lvl.blocks.update()
    player.lvl.blocks.draw(display)
    player.lvl.bullets.update()
    player.lvl.bullets.draw(display)
    all_sprites.draw(display)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
