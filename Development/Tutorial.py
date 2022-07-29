import pygame as pg
from pygame import mixer
import time, os
import random
import csv

#Keep True to Use NLP features
shloka_mode = True
if shloka_mode:
    import shloka

mixer.init()
pg.init()

run = True

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
window = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption('Tutorial')

clock = pg.time.Clock()
fps = 60

a = 255
grav = 0.75
scrollthresh = 200
rows = 16
columns = 150
tilesize = SCREEN_HEIGHT // rows
tiletypes = 21
windowscroll = 0
bgscroll = 0
start_intro = False
light = False
new = True

mlevels = 3
level = 1
sg = False

moving_l = False
moving_r = False
shoot = False
tnade = False
thrown = False

brihu_intro_flag = True

pg.mixer.music.load('../audio/background.mp3')
pg.mixer.music.set_volume(0.3)
pg.mixer.music.play(-1, 0.0, 5000)

brihaspati_intro = pg.mixer.Sound("../audio/Brihaspati_Intro.mp3")
brihaspati_intro.set_volume(0.5)

jfx = pg.mixer.Sound("Tutorial Assets/audio/jump.wav")
jfx.set_volume(0.5)
shotfx = pg.mixer.Sound("Tutorial Assets/audio/shot.wav")
shotfx.set_volume(0.5)
nadefx = pg.mixer.Sound("Tutorial Assets/audio/grenade.wav")
nadefx.set_volume(0.5)

pine1 = pg.image.load("Tutorial Assets/img/Background/pine1.png").convert_alpha()
pine2 = pg.image.load("Tutorial Assets/img/Background/pine2.png").convert_alpha()
mount = pg.image.load("Tutorial Assets/img/Background/mountain.png").convert_alpha()
sky = pg.image.load("Tutorial Assets/img/Background/sky_cloud.png").convert_alpha()
proj1 = pg.image.load("Tutorial Assets/img/icons/bulletr.png").convert_alpha()
proj = pg.image.load("Tutorial Assets/img/icons/bullet.png").convert_alpha()
grenade = pg.image.load("Tutorial Assets/img/icons/grenade.png").convert_alpha()
hbox= pg.image.load("Tutorial Assets/img/icons/health_box.png").convert_alpha()
abox = pg.image.load("Tutorial Assets/img/icons/ammo_box.png").convert_alpha()
gbox = pg.image.load("Tutorial Assets/img/icons/grenade_box.png").convert_alpha()
startimg = pg.image.load("Tutorial Assets/img/start_btn.png").convert_alpha()
endimg = pg.image.load("Tutorial Assets/img/exit_btn.png").convert_alpha()
resimg = pg.image.load("Tutorial Assets/img/restart_btn.png").convert_alpha()
brh = pg.image.load("Tutorial Assets/img/npcs/brihaspati.png").convert_alpha(); brh = pg.transform.scale(brh, (brh.get_width() * 0.2, brh.get_height() * 0.2)); brh.set_alpha(0)
vishnu = pg.image.load("Tutorial Assets/img/npcs/vishnu.png").convert_alpha(); vishnu = pg.transform.scale(vishnu, (vishnu.get_width() * 0.667, vishnu.get_height() * 0.61)); vishnu.set_alpha(100)
imglist = []

for x in range(tiletypes):
    img = pg.image.load(f"Tutorial Assets/img/Tile/{x}.png").convert_alpha()
    img = pg.transform.scale(img, (tilesize, tilesize))
    imglist.append(img)

ib = {'h': hbox, 'a': abox, 'g': gbox}

bgc = (144, 201, 120, 255)
white = (255, 255, 255, 255)
red = (255, 0, 0, 255)
green = (0, 255, 0, 255)
black = (0, 0, 0, 255)
pink = (235, 65, 54, 255)
blue = (0, 0, 255, 255)

font = pg.font.SysFont('Samarkan', 30)

def bg():
    window.fill(bgc)

    w = sky.get_width()

    for i in range(5):
        window.blit(sky, ((i * w) - (bgscroll * 0.5),0))
        window.blit(mount, ((i * w) - (bgscroll * 0.6), SCREEN_HEIGHT - mount.get_height() - 300))
        window.blit(pine1, ((i * w) - (bgscroll * 0.7), SCREEN_HEIGHT - pine1.get_height() - 150))
        window.blit(pine2, ((i * w) - (bgscroll * 0.8), SCREEN_HEIGHT - pine2.get_height()))

def text(text, f, colour, x, y):
    img = f.render(text, True, colour)
    window.blit(img, (x, y))

def reset():
    engp.empty()
    projgp.empty()
    nadegp.empty()
    expgp.empty()
    boxgp.empty()
    decgp.empty()
    watergp.empty()
    exgp.empty()

    data = []

    for row in range(rows):
        r = [-1] * columns
        data.append(r)

    return data

class Button():
    def __init__(self, x, y, image, scale):
        w = image.get_width()
        h = image.get_height()
        self.image = pg.transform.scale(image, (int(w * scale), int(h * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False
        pos = pg.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pg.mouse.get_pressed()[0] == 1 and self.clicked == 0:
                action = True
                self.clicked = True
                self.called = True
                self.tc = pg.time.get_ticks()

        if pg.mouse.get_pressed()[0] == 0:
            self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action

class Character(pg.sprite.Sprite):
    def __init__(self, char, x, y, scale, velx, ammo = 20, gcount = 0):
        pg.sprite.Sprite.__init__(self)
        self.alive = True
        self.char = char
        self.velx = velx
        self.ammo = ammo
        self.start_ammo = ammo
        self.shootcd = 0
        self.gcount = gcount
        self.health = 100
        self.mhealth = self.health
        self.dir = 1
        self.vely = 0
        self.jump = False
        self.air = True
        self.flip = False
        self.al = []
        self.i = 0
        self.action = 0
        self.update_time = pg.time.get_ticks()

        self.mc = 0
        self.idle = False
        self.ic = 0
        self.vision = pg.Rect(0, 0, 150, 20)

        atypes = ['Idle', 'Run', 'Jump', 'Death']

        for a in atypes:
            temp_list = []

            fno = len(os.listdir(f"Tutorial Assets/img/{self.char}/{a}"))

            for i in range(fno):
                img = pg.image.load(f"Tutorial Assets/img/{self.char}/{a}/{i}.png").convert_alpha()
                img = pg.transform.scale(img, (img.get_width()*scale, img.get_height()*scale))
                temp_list.append(img)
            self.al.append(temp_list)

        self.img = self.al[self.action][self.i]
        self.rect = self.img.get_rect()
        self.rect.center = (x,y)
        self.width = self.img.get_width()
        self.height = self.img.get_height()

    def update(self):
        self.update_anim()
        self.calive()
        
        if self.shootcd > 0:
            self.shootcd -= 1

    def move(self, moving_left, moving_right):
        windowscroll = 0
        dx = 0
        dy = 0

        if moving_left:
            self.flip = True
            self.dir = -1
            dx = -self.velx

        if moving_right:
            self.flip = False
            self.dir = 1
            dx = self.velx

        if self.jump == True and self.air == False:
            self.vely = -11
            self.jump = False
            self.air = True

        self.vely += grav
        if self.vely > 10:
            self.vely = 10
        dy += self.vely

        for t in w.oblist:
            if t[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0

                if self.char == 'enemy':
                    self.dir *= -1
                    self.mc = 0

            if t[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vely < 0:
                    self.vely = 0
                    dy = t[1].bottom - self.rect.top

                elif self.vely >= 0:
                    self. vely = 0
                    dy = t[1].top - self.rect.bottom
                    self.air = False

        if pg.sprite.spritecollide(self, watergp, False):
            self.health = 0

        lvlcomp = False
        if pg.sprite.spritecollide(self, exgp, False):
            lvlcomp = True

        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        if self.char == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        self.rect.x += dx
        self.rect.y += dy

        if self.char == 'player':
            if (self.rect.right > SCREEN_WIDTH - scrollthresh and bgscroll < (w.lvllength * tilesize) - SCREEN_WIDTH) or\
                (self.rect.left < scrollthresh and bgscroll > abs(dx)):
                self.rect.x -= dx
                windowscroll = -dx

        return windowscroll, lvlcomp

    def shoot(self):
        if self.shootcd == 0 and self.ammo > 0:
            self.shootcd = 20
            self.ammo -=1

            bullet = Projectile(self.rect.centerx + (self.dir * self.rect.size[0] * 0.75), self.rect.centery, self.dir, self.char)
            projgp.add(bullet)
            shotfx.play()

    def ai(self):
        if self.alive and player.alive:
            if random.randint(1, 200) == 1 and self.idle == False:
                self.update_action(0)
                self.idle = True
                self.ic = 50

            if self.vision.colliderect(player.rect):
                self.update_action(0)
                self.shoot()

            else:
                if not self.idle:
                    if self.dir == 1:
                        aimovingr = True

                    else:
                        aimovingr = False

                    aimovingl = not aimovingr

                    self.move(aimovingl, aimovingr)
                    self.update_action(1)
                    self.mc += 1

                    self.vision.center = (self.rect.centerx + 75 * self.dir, self.rect.centery)

                    if self.mc >= tilesize:
                        self.dir *= -1
                        self.mc *= -1

                else:
                    self.ic -= 1

                    if self.ic <= 0:
                        self.idle = False

        self.rect.x += windowscroll

    def update_anim(self):
        animcd = 100

        if pg.time.get_ticks() - self.update_time > animcd:
            self.update_time = pg.time.get_ticks()
            self.i += 1

            if self.i >= len(self.al[self.action]):
                if self.action == 3:
                    self.i = len(self.al[self.action]) - 1

                else:
                    self.i = 0

            self.img = self.al[self.action][self.i]

    def update_action(self, newact):
        if self.action != newact:
            self.action = newact
            self.i = 0
            self.update_time = pg.time.get_ticks()

    def calive(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.velx = 0
            self.update_action(3)

    def draw(self):
        window.blit(pg.transform.flip(self.img, self.flip, False), self.rect)

class Ability():
    def __init__(self):
        self.active = False
        self.apptime = 600
        self.ticks = 0

    def update(self, active, ticks, type):
        self.ticks = ticks
        self.active = active
        self.type = type

        if self.type == 1:
            if self.active:
                self.img = vishnu.copy()
                player.health = 10000
                self.time = 6000

    def draw(self):
        if self.active:
            if pg.time.get_ticks() - self.ticks < self.time:
                if pg.time.get_ticks() - self.ticks < self.apptime:
                    a = self.img.get_alpha()

                    if a - 3 > 0:
                        self.img.set_alpha(a - 3)
                        window.blit(self.img, (-30, 0))

                pg.draw.circle(window, blue, (player.rect.centerx, player.rect.centery), 40, 2)

            else:
                if self.type == 1:
                    player.health = player.mhealth

                self.active = False

class World():
    def __init__(self):
        self.oblist = []

    def process_data(self, data):
        self.lvllength = len(data[0])

        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = imglist[tile]
                    imgrect = img.get_rect()
                    imgrect.x = x * tilesize
                    imgrect.y = y * tilesize
                    tiledata = (img, imgrect)

                    if 0 <= tile <= 8:
                        self.oblist.append(tiledata)

                    elif 9 <= tile <= 10:
                        water = Water(img, x * tilesize, y * tilesize)
                        watergp.add(water)

                    elif 11 <= tile <= 14:
                        dec = Decoration(img, x * tilesize, y * tilesize)
                        decgp.add(dec)

                    elif tile == 15:
                        player = Character("player", x * tilesize, y * tilesize, 1.65, 5, 20, 5)
                        hb = Healthbar(10, 10, player.health, player.health)

                    elif tile == 16:
                        enemy = Character("enemy", x * tilesize, y * tilesize, 1.65, 2)
                        engp.add(enemy)

                    elif tile == 17:
                        ibox = Itembox('a', x * tilesize, y * tilesize)
                        boxgp.add(ibox)

                    elif tile == 18:
                        ibox = Itembox('g', x * tilesize, y * tilesize)
                        boxgp.add(ibox)

                    elif tile == 19:
                        ibox = Itembox('h', x * tilesize, y * tilesize)
                        boxgp.add(ibox)

                    elif tile == 20:
                        ex = Exit(img, x * tilesize, y * tilesize)
                        exgp.add(ex)

        return player, hb

    def draw(self):
        for t in self.oblist:
            t[1][0] += windowscroll

            window.blit(t[0], t[1])

class Decoration(pg.sprite.Sprite):
    def __init__(self, img, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + (tilesize // 2), y + tilesize - (self.image.get_height()))

    def update(self):
        self.rect.x += windowscroll

class Water(pg.sprite.Sprite):
    def __init__(self, img, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + (tilesize // 2), y + tilesize - (self.image.get_height()))

    def update(self):
        self.rect.x += windowscroll

class Exit(pg.sprite.Sprite):
    def __init__(self, img, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + (tilesize // 2), y + tilesize - (self.image.get_height()))

    def update(self):
        self.rect.x += windowscroll

class Itembox(pg.sprite.Sprite):
    def __init__(self, type, x, y):
        pg.sprite.Sprite.__init__(self)
        self.type = type
        self.image = ib[self.type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + (tilesize // 2), y + (tilesize - self.image.get_height()))

    def update(self):
        self.rect.x += windowscroll
        if pg.sprite.collide_rect(self, player):
            if self.type == 'h':
                if player.health + 25 <= player.mhealth:
                    player.health += 25

                else:
                    player.health = player.mhealth

            elif self.type == 'a':
                player.ammo += 15

            elif self.type == 'g':
                player.gcount += 3

            self.kill()

class Healthbar():
    def __init__(self, x, y, health, mhealth):
        self.x = x
        self.y = y
        self.health = health
        self.mhealth = mhealth

    def draw(self, health):
        self.health = health

        ratio = self.health / self.mhealth

        pg.draw.rect(window, black, (self.x - 2, self.y - 2, 154, 24))
        pg.draw.rect(window, red, (self.x, self.y, 150, 20))
        if armour.active:
            pg.draw.rect(window, green, (self.x, self.y, 150, 20))

        else:
            pg.draw.rect(window, green, (self.x, self.y, 150 * ratio, 20))

class Projectile(pg.sprite.Sprite):
    def __init__(self, x, y, direc, char):
        pg.sprite.Sprite.__init__(self)
        self.vel = 5
        self.dir = direc
        self.flip = False
        self.char = char
        if self.char == 'player':
            if self.dir == 1:
                self.flip = False

            if self.dir == -1:
                self.flip = True

            self.image = pg.transform.flip(proj1, self.flip, False)

        elif self.char == 'enemy':
            self.image = proj

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.x += windowscroll + (self.dir * self.vel)

        if 0 > self.rect.right or self.rect.left > 1000:
            self.kill()

        if pg.sprite.spritecollide(player, projgp, False):
            if player.alive:
                player.health -= 5
                self.kill()

        for t in w.oblist:
            if t[1].colliderect(self.rect):
                self.kill()
                
        for e in engp:
            if pg.sprite.spritecollide(e, projgp, False):
                if e.alive:
                    e.health -= 25
                    self.kill()

    def draw(self):
        window.blit(self.image, self.rect)

class Grenade(pg.sprite.Sprite):
    def __init__(self, x, y, dir):
        pg.sprite.Sprite.__init__(self)
        self.t = 100
        self.vely = -11
        self.velx = 7
        self.image = grenade
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.dir = dir

    def update(self):
        self.vely += grav
        dx = self.dir * self.velx
        dy = self.vely

        for t in w.oblist:
            if t[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.dir *= -1
                dx = self.dir * self.velx
                
            if t[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.velx = 0

                if self.vely < 0:
                    self.vely = 0
                    dy = t[1].bottom - self.rect.top

                elif self.vely >= 0:
                    self. vely = 0
                    dy = t[1].top - self.rect.bottom

        self.rect.x += dx + windowscroll
        self.rect.y += dy

        self.t -= 1

        if self.t <= 0:
            self.kill()
            nadefx.play()

            exp = Explosion(self.rect.x, self.rect.y, 0.5)
            expgp.add(exp)

            if abs(self.rect.centerx - player.rect.centerx) < tilesize * 2 and\
               abs(self.rect.centery - player.rect.centery) < tilesize * 2:

                player.health -= 50

            for e in engp:
                if abs(self.rect.centerx - e.rect.centerx) < tilesize * 2 and\
                   abs(self.rect.centery - e.rect.centery) < tilesize * 2:

                    e.health -= 50

class Explosion(pg.sprite.Sprite):
    def __init__(self, x, y, scale):
        pg.sprite.Sprite.__init__(self)
        self.al = []

        for n in range(1, 6):
            img = pg.image.load(f"Tutorial Assets/img/Explosion/exp{n}.png").convert_alpha()
            img = pg.transform.scale(img, ((int(img.get_width()) * scale),\
                                    (int(img.get_height()) *scale)))
            self.al.append(img)

        self.i = 0
        self.image = self.al[self.i]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.c = 0

    def update(self):
        self.rect.x += windowscroll
        expspeed = 4
        self.c += 1

        if self.c >= expspeed:
            self.c = 0
            self.i += 1

            if self.i >= len(self.al):
                self.kill()

            else:
                self.image = self.al[self.i]

class Fade():
    def __init__(self, direc, colour, vel):
        self.dir = direc
        self.colour = colour
        self.vel = vel
        self.fcounter = 0
        self.a = 255
        self.acounter = 1

    def fade(self):
        fcomp = False
        self.fcounter += self.vel
        
        if self.dir == 2:
            pg.draw.rect(window, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fcounter))

        if self.fcounter >= SCREEN_WIDTH:
            fcomp = True

        return fcomp

ifade = Fade(1, black, 4)
dfade = Fade(2, pink, 4)

engp = pg.sprite.Group()
projgp = pg.sprite.Group()
nadegp = pg.sprite.Group()
expgp = pg.sprite.Group()
boxgp = pg.sprite.Group()
decgp = pg.sprite.Group()
watergp = pg.sprite.Group()
exgp = pg.sprite.Group()
armour = Ability()

startbtn = Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 -150, startimg, 1)
endbtn = Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, endimg, 1)
resbtn = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, resimg, 2)

wdata = []

for row in range(rows):
    r = [-1] * columns
    wdata.append(r)

with open(f'Tutorial Assets/level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter = ',')

    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            wdata[x][y] = int(tile)

w = World()
player, hb = w.process_data(wdata)

while run:
    clock.tick(fps)

    if not sg:
        window.fill(bgc)

        if startbtn.draw(window):
            sg = True
            start_intro = True

        elif endbtn.draw(window):
            run = False
    
    else:
        bg()

        w.draw()

        hb.draw(player.health)

        text('AMMO: ', font, white, 10, 35)

        for c in range(player.ammo):
            window.blit(proj1, (90 + (c * 25), 40))
        
        text('GRENADES: ', font, white, 10, 70)
        
        for c in range(player.gcount):
            window.blit(grenade, (140 + (c * 15), 72.5))

        player.update()

        for e in engp:
            e.ai()
            e.update()

        projgp.update()
        nadegp.update()
        expgp.update()
        boxgp.update()
        decgp.update()
        watergp.update()
        exgp.update()

        player.draw()

        for e in engp:
            e.draw()

        projgp.draw(window)
        nadegp.draw(window)
        expgp.draw(window)
        boxgp.draw(window)
        decgp.draw(window)
        watergp.draw(window)
        exgp.draw(window)

        if armour.active:
            armour.draw()

        if not light and start_intro:
            if brihu_intro_flag == True:
                brihaspati_intro.play()
                brihu_intro_flag = False

            night = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

            window.blit(night, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

            if new:
                if pg.time.get_ticks() - startbtn.tc >= 600:
                    a = brh.get_alpha()

                    if a + 5 <= 255:
                        brh.set_alpha(a + 5)
                        window.blit(brh, (SCREEN_WIDTH - brh.get_width() / 1.2, 0))

                    else:
                        window.blit(brh, (SCREEN_WIDTH - brh.get_width() / 1.2, 0))

                dia = text("The Dark Forces have removed all the light. The Asuras are", font, white, 30, 60)
                dia = text("getting stronger with each day...", font, white, 30, 95)
                dia = text("it is time to conquer them!", font, white, 30, 135)

        elif light and a > 0:
            brihaspati_intro.stop()
            brihu_intro_flag = False
            new = False
            a -= 10

            night.set_alpha(a)
            window.blit(night, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        #if not light:
            #ifade.fade()
            #start_intro = False
            #ifade.fcounter = 0
            #ifade.acounter = 0

        if player.alive:
            if shoot:
                player.shoot()

            elif tnade and not thrown and player.gcount:
                nade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.dir),\
                            player.rect.top, player.dir)
                nadegp.add(nade)

                thrown = True
                player.gcount -= 1

            if player.air:
                player.update_action(2)

            elif moving_l or moving_r:
                player.update_action(1)

            else:
                player.update_action(0)

            windowscroll, lvlcomp = player.move(moving_l, moving_r)
            bgscroll -= windowscroll

            if lvlcomp:
                start_intro = True
                level += 1
                bgscroll = 0
                wdata = reset()

                if level <= mlevels:
                    with open(f'Tutorial Assets/level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter = ',')

                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                wdata[x][y] = int(tile)

                    w = World()
                    player, hb = w.process_data(wdata)

        else:
            windowscroll = 0

            if dfade.fade():
                if resbtn.draw(window):
                    dfade.fcounter = 0
                    start_intro = True
                    a = 255
                    bgscroll = 0
                    wdata = reset()

                    with open(f'Tutorial Assets/level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter = ',')

                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                wdata[x][y] = int(tile)

                    w = World()
                    player, hb = w.process_data(wdata)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
            break

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_a:
                moving_l = True

            if event.key == pg.K_d:
                moving_r = True

            if event.key == pg.K_SPACE:
                shoot = True

            if event.key == pg.K_g:
                tnade = True

            if event.key == pg.K_w and player.alive:
                player.jump = True
                jfx.play()

            if event.key == pg.K_l and not light:
                light = True

            if event.key == pg.K_q:
                if not armour.active:
                    armour.update(True, pg.time.get_ticks(), 1)

            """
            This module is for the NLP side of things, choosing to click 
            the Key M would result in switching the mic on for 5 seconds. 
            This would result starting the recording for 5 seconds, save the audio
            file and eventually performing the speech to text. 
            """
            
            if event.key == pg.K_m:
                #turn background music off
                pg.mixer.music.set_volume(0.0)

                filename = shloka.record_audio(5)
                english_text = shloka.speechToEnglish(filename)[0]
                print(english_text)
                #uncomment if you want to it use Hindi Speech to Text
                #hindi_text = shloka.speechToHindi(filename)[0]

                #SHREYAS here is where you do your if-else game mechanics actions
                if english_text.lower() == "sun":
                    light = True


                pg.mixer.music.set_volume(0.3)

            if event.key == pg.K_ESCAPE:
                run = False
                break

        if event.type == pg.KEYUP:
            if event.key == pg.K_a:
                moving_l = False

            if event.key == pg.K_d:
                moving_r = False

            if event.key == pg.K_SPACE:
                shoot = False

            if event.key == pg.K_g:
                tnade = False
                thrown = False

    pg.display.update()

pg.quit()
