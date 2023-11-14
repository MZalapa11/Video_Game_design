#This file was created by: Miguel Zalapa
# content from kids can code: http://kidscancode.org/blog/

# import libraries and modules
#Goals: two players, health bar, mobs that chase you, coins/mystery boxes
import pygame as pg
from pygame.sprite import Sprite
from random import randint
import os
from settings import *

vec = pg.math.Vector2

# setup asset folders here - images sounds etc.
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'images')
snd_folder = os.path.join(game_folder, 'sounds')


def draw_text(text, size, color, x, y):
    font_name = pg.font.match_font('arial')
    font = pg.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x,y)
    screen.blit(text_surface, text_rect)

def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    pg.draw.rect(surf, GREEN, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)


class Player(Sprite):
    def __init__(self):
        Sprite.__init__(self)
        # self.image = pg.Surface((50, 50))
        # self.image.fill(GREEN)
        # use an image for player sprite...
        self.image = pg.image.load(os.path.join(img_folder, 'theBell.png')).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.pos = vec(WIDTH/2, HEIGHT/2)
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        print(self.rect.center)
        self.hitpoints = 100
    def controls(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            self.acc.x = -5
        if keys[pg.K_d]:
            self.acc.x = 5
        if keys[pg.K_SPACE]:
            self.jump()
    def jump(self):
        hits = pg.sprite.spritecollide(self, all_platforms, False)
        if hits:
            print("i can jump")
            self.vel.y = -PLAYER_JUMP
    def update(self):
        self.acc = vec(0,PLAYER_GRAV)
        self.controls()
        # if friction - apply here
        self.acc.x += self.vel.x * -0.2
        # this would only apply when doing a top down video game
        # self.acc.y += self.vel.y * -0.2
        # equations of motion
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        self.rect.midbottom = self.pos
        
        
# platforms

class Platform(Sprite):
    def __init__(self, x, y, w, h, category):
        Sprite.__init__(self)
        self.image = pg.Surface((w, h))
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        print(self.rect.center)
        self.category = category
        self.speed = 0
        if self.category == "moving":
            self.speed = 5
    def update(self):
        if self.category == "moving":
            self.rect.x += self.speed
            if self.rect.x > WIDTH-self.rect.width or self.rect.x < 0:
                self.speed = -self.speed
        if self.category == "lava":
            self.image.fill(ORANGE)

class Mob(Sprite):
    def __init__(self, x, y, w, h, category):
        Sprite.__init__(self)
        self.image = pg.Surface((w, h))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.category = category
        self.speed = 2

        if self.category == "moving":
            self.speed = 2  # You can adjust the speed based on your preference

    def update(self):
            self.rect.x += self.speed

            # Check if the mob is on one side of the screen or the other
            if self.rect.x > WIDTH - self.rect.width or self.rect.x < 0:
                self.speed = -self.speed
                self.rect.y += self.rect.height  # Move the mob vertically when changing direction

            # Change colors depending on position
            if self.rect.x > WIDTH / 2:
                self.image.fill((randint(0, 100), randint(0, 255), randint(0, 255)))
            else:
                self.image.fill((randint(0, 255), randint(0, 255), randint(0, 100)))



# init pygame and create a window
pg.init()
pg.mixer.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("My Game...")

clock = pg.time.Clock()

# create a group for all sprites
all_sprites = pg.sprite.Group()
all_platforms = pg.sprite.Group()
all_mobs = pg.sprite.Group()

# instantiate classes
player = Player()
all_sprites.add(player)

# add instances to groups

for i in range(15):
    m = Mob(randint(0,WIDTH), randint(0,HEIGHT), 25, 25, "lava")
    all_sprites.add(m)
    all_mobs.add(m)

for plat in PLATFORM_LIST:
    p = Platform(*plat)
    all_sprites.add(p)
    all_platforms.add(p)


# Game loop
running = True
while running:
    # keep the loop running using clock
    currentFPS = clock.tick(FPS)
        
    for event in pg.event.get():
        # check for closed window
        if event.type == pg.QUIT:
            running = False
    
    ############ Update ##############
    # update all sprites
    all_sprites.update()
    mob_collisions = pg.sprite.spritecollide(player, all_mobs, True)
    for mob in mob_collisions:
        # Perform any additional actions when a mob is touched (e.g., increase score)
        player.hitpoints -= 10  # Adjust as needed
    if player.rect.y > HEIGHT:
        player.pos = vec(WIDTH/2, HEIGHT/2)
    # this is what prevents the player from falling through the platform when falling down...
    if player.vel.y > 0:
            hits = pg.sprite.spritecollide(player, all_platforms, False)
            if hits:
                player.pos.y = hits[0].rect.top
                player.vel.y = 0
                player.vel.x = hits[0].speed*1.5
                
    # this prevents the player from jumping up through a platform
    if player.vel.y < 0:
        hits = pg.sprite.spritecollide(player, all_platforms, False)
        if hits:
            print("ouch")
            SCORE -= 1
            if player.rect.bottom >= hits[0].rect.top - 5:
                player.rect.top = hits[0].rect.bottom
                player.acc.y = 5
                player.vel.y = 0

    mhits = pg.sprite.spritecollide(player, all_mobs, False)
    if mhits:
        player.hitpoints -= 100
    ############ Draw ################
    # draw the background screen
    screen.fill(BLACK)
    # draw all sprites
    all_sprites.draw(screen)
    draw_text("FPS: " + str(currentFPS), 22, WHITE, WIDTH/2, HEIGHT/10)
    draw_text("Hitpoints: " + str(player.hitpoints), 22, WHITE, WIDTH/2, HEIGHT/20)
    
    # buffer - after drawing everything, flip display
    pg.display.flip()

pg.quit()

