# importing modules
import pygame
from pygame.locals import *
from random import *
from playsound import *
pygame.init()
from pygame import mixer
from SaveLoadManager import *
import time
#creating the clock
clock = pygame.time.Clock()
TARGET_FPS = 144
RUNNING_FPS = 150
#creating the screen 
screen_width =1600
screen_height = 900
screenSurface = (screen_width, screen_height)
screen = pygame.display.set_mode(screenSurface)
pygame.display.set_caption('Ninja Runner')
shopState = False  

#loading images
backgroundImg = pygame.image.load("background.png")
backgroundImg = pygame.transform.scale(backgroundImg, (3200,900))
groundImg = pygame.image.load("ground.png")
coinImg = pygame.image.load("coin.png")
coinImg = pygame.transform.scale(coinImg, (50,50))
scullImg = pygame.image.load("scull.png")
scullImg = pygame.transform.scale(scullImg, (50,50))
hackerImg = pygame.image.load("hacker.png")
leniosImg = pygame.image.load("lenios.png")
scratchImg = pygame.image.load("student.png")
nerdImg = pygame.image.load("nerd.png")
weebImg = pygame.image.load("weeb.png")

playerRun = []
for i in range(6):
    newImg = pygame.image.load(f"run{i+1}.png")
    newImg = pygame.transform.scale(newImg, (200,148))
    playerRun.append(newImg)

playerAttack = []
for i in range(6):
    newImg = pygame.image.load(f"attack{i+1}.png")
    newImg = pygame.transform.scale(newImg, (200,148))
    playerAttack.append(newImg)
  
skeletonIdle = []  
for i in range(11):
    newImg = pygame.image.load(f"skeletonidle{i+1}.png")
    newImg = pygame.transform.scale(newImg, (100,128))
    newImg = pygame.transform.flip(newImg, True, False)
    skeletonIdle.append(newImg)
buttonImg = []
for i in range(2):
    newImg = pygame.image.load(f"button{i+1}.png")
    newImg = pygame.transform.scale(newImg, (100,100))
    buttonImg.append(newImg)


    
ground_scroll = 3

#loading sounds

slash = pygame.mixer.Sound("slash.wav")
slash.set_volume(0.5)
coinPickup = pygame.mixer.Sound("coin.wav")
coinPickup.set_volume(0.5)
mixer.music.load("music.wav")
mixer.music.set_volume(0.1)
mixer.music.play(-1)

# creating the Ninja() class
class Ninja(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = playerRun[0]
        self.rect = self.image.get_rect(center = (self.x,self.y)) 
        self.state = "run"
        self.index = 0
        self.counter = 0
        self.attack = False
        self.setindex = True
        self.score = 0
        self.scoremult = 1.6
        self.coinworth = 10
        self.passiveincome = 0

    def update(self):
        key_pressed = pygame.key.get_pressed()
        anim_cooldown = 15
        self.counter += 1
        if self.state == "run":
            self.attack = False
            self.setindex = True
            if self.counter > anim_cooldown:
                self.counter = 0
                self.index += 1
                if self.index > len(playerRun)-1 :
                    self.index = 0 
            self.image = playerRun[self.index]
            
        elif self.state == "attack":
            self.attack = True
            if self.setindex == True:
                self.index == 0
                self.setindex = False
                
            if self.counter > anim_cooldown:
                
                self.counter = 0
                if self.index == 3:
                    slash.play()
                self.index += 1
                
                if self.index > len(playerRun)-1 :
                    
                    self.index = 0 
                    
                    self.state = "run"
                    
                self.image = playerAttack[self.index]
            
        if key_pressed[pygame.K_SPACE]:
            self.state = "attack"
        self.rect = self.image.get_rect(center = (self.x,self.y))
    
# create the Effect() class for the particles     
class Effect():
    def __init__(self, x, y, image):
        self.image = image
        self.image = pygame.transform.scale(self.image,(60,60))
        self.x = x
        self.y = y
        self.x_vel = randrange(-6,6)
        self.y_vel = randrange(-20,20)
        if self.x_vel == 0:        
            self.x_vel += 3
        if self.y_vel == 0:
            self.y_vel += 3
        self.lifetime = 0
    def draw(self):
        self.lifetime =+ 1
        if self.lifetime < 5:
            self.x += self.x_vel 
            self.y += self.y_vel
            screen.blit(coinImg, (self.x, self.y))

#creating the Enemy() class     
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = skeletonIdle[1]
        self.rect = self.image.get_rect(center=(x,y))
        self.state = "run"
        self.index = 0
        self.counter = 0 
    def update(self):
        anim_cooldown = 15
        self.counter += 1

        self.attack = False
        
        if self.counter > anim_cooldown:
            self.counter = 0
            self.index += 1
            if self.index > len(skeletonIdle)-1 :
                self.index = 0 
        
        self.rect.x -= ground_scroll 
        if self.rect.right < 0:
            self.kill()
        self.image = skeletonIdle[self.index]

class Area():
    def __init__(self, x=0 , y=0, width=10, height=10, color=None, state=False):
    
        self.rect = pygame.Rect(x,y,width,height)
        self.fill_color = color
        
    
    def color(self, new_color):
        self.fill_color = new_color
    
    def fill(self):
        pygame.draw.rect(screen, self.fill_color, self.rect)

    def outline(self, frame_color, thickness):
        pygame.draw.rect(screen, frame_color, self.rect, thickness)
    
    
class Label(Area):
    def set_text(self, text, fsize=12, text_color=(0,0,0)):
        self.image = pygame.font.SysFont('Bauhaus 93', fsize).render(text, True, text_color)

    def draw(self, shift_x= 60, shift_y=0):
        # self.fill()
        screen.blit(self.image, (self.rect.x + shift_x , self.rect.y + shift_y))
 
class ShopItem():
    def __init__(self, img, x,y, shopstate, extraIncome, cost):
        self.img = img
        self.x = x
        self.y = y
        self.rect = self.img.get_rect(center=(self.x, self.y))
        
        self.clicked = False
        self.counter = 0
        self.extraincome = extraIncome
        self.cost = cost
        self.quantity = 0
    def draw(self):
        self.counter += 1
        clickcooldown = 10
        if shopState:
            screen.blit(self.img, (self.rect.x, self.rect.y))
            pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(pos) and pygame.mouse.get_pressed()[0] and not self.clicked and player.score >= self.cost:
                    player.passiveincome += self.extraincome
                    player.score -= self.cost
                    self.quantity += 1
                    self.clicked = True
            if self.counter == clickcooldown:
                self.clicked = False
                self.counter = 0
        else:
            pass

class Button():
    def __init__(self, action1 ,action2, x,y ):
        self.x = x
        self.y = y
        self.images = buttonImg
        self.image = buttonImg[0]
        self.rect = self.image.get_rect(center=(self.x,self.y))
        self.clicked = False
        self.state = 0
        self.counter = 0
        self.shopstate = False
    def draw(self):
        self.counter += 1
        clickcooldown = 60
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos) and pygame.mouse.get_pressed()[0] and not self.clicked and not self.shopstate:
            self.shopstate = True
            self.image = self.images[1]
            self.clicked = True
        elif self.rect.collidepoint(pos) and pygame.mouse.get_pressed()[0] and not self.clicked and self.shopstate:
            self.shopstate = False
            self.image = self.images[0]
            self.clicked = True
        if self.counter == clickcooldown:
            self.clicked = False
            self.counter = 0
        screen.blit(self.image, (self.rect.x,self.rect.y))
        
class FireFly(pygame.sprite.Sprite):
    def __init__(self, image, x, y, speed, images):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.images = images
        self.speed = speed
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(center=(self.x,self.y))
        self.index = 0
        self.counter = 0
    def update(self):
        cooldown = 16
        self.counter += 1       
        self.rect.x -= self.speed
        if self.counter > cooldown:
            self.index += 1
            self.counter = 0 
        if self.rect.left > 1600:
            self.kill()
        if self.rect.right < 0:
            self.kill()
        if self.index > 2:
            self.index = 0
        self.image = self.images[self.index]

#declaring some variables   
pipe_frequency = 1.4 * 1000 #milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
pay_freq = 1*1000
last_paid = pygame.time.get_ticks() - pay_freq
screen_x = 0
background_scroll = 1
ground_x = 0
playerHasKilled = 0

#creating groups and player refrences
player = Ninja(200, 675)
playerGroup = pygame.sprite.Group()
playerGroup.add(player)
enemyGroup = pygame.sprite.Group()
particles = []

#crating score counters

dogecoins = Label(10, 10, 300, 60)
sculls = Label(10, 80, 200, 60)
fpsCounter = Label(screen_width-160, 10, 150, 60)

saveloadmanager = SaveLoadSystem(".txt", "save_data")

hacker = ShopItem(hackerImg, screen_width-200, 300, True, 5, 50)
scratch = ShopItem(scratchImg, screen_width-200, 400, True,10,100)
weeb = ShopItem(weebImg, screen_width-200,500, True, 15, 150)
nerd = ShopItem(nerdImg, screen_width-200,600, True, 20, 200)
lenios = ShopItem(leniosImg, screen_width-200,700, True, 25, 250)

shopitems = [hacker, scratch, weeb, nerd, lenios]
 
frames = []   
playerHasKilled, player.scoremult, player.score, hacker.quantity, scratch.quantity,weeb.quantity,nerd.quantity,lenios.quantity = saveloadmanager.load_game_data(["playerkills", "playerscoremultiplier", "playerscore","quantity1", "quantity2", "quantity3","quantity4","quantity5"],[0,1.6,0,0,0,0,0,0])
prev_time = time.time()
dt = 0

dtTFPS = dt * TARGET_FPS

dogecoins.color((255,255,255))
fpsCounter.color((255,255,255))
sculls.color((255,255,255))

shopButton = Button("hey", "hehe", screen_width-50,screen_height-50)

#main game loop
running = True
while running:
    clock.tick(RUNNING_FPS)
    shopState = shopButton.shopstate 
    #drawing ground and background aswell as making it scroll
    
    screen.blit(backgroundImg, (screen_x,0))
    screen_x -= background_scroll 
    if screen_x == -1600:
        screen_x = 0
        
    screen.blit(groundImg, (ground_x, 750))
    ground_x -= ground_scroll
    if ground_x < -16000:
        ground_x = 0
        
    #generating enemys
    time_now = pygame.time.get_ticks()
    if time_now - last_pipe > pipe_frequency and len(enemyGroup)<=2:
        e = randint(1,8)
        if e == 1:
            newEnemy = Enemy(screen_width +100, 690)
            enemyGroup.add(newEnemy)
        if e == 2:
            newEnemy = Enemy(screen_width +100, 690)
            enemyGroup.add(newEnemy)
            newEnemy2 = Enemy(screen_width +230, 690)
            enemyGroup.add(newEnemy2)
        if e == 4:
            #newEnemy = FireFly(giannhsSprites[0], screen_width,300, 2.5, giannhsSprites)
            #enemyGroup.add(newEnemy)
            pass
        last_pipe = time_now
        
    if time_now - last_paid > pay_freq:
        for item in shopitems:
            player.score += item.extraincome
        last_paid = time_now

    # collision detection
    playerHitEnemy = pygame.sprite.spritecollide(player, enemyGroup, False, pygame.sprite.collide_mask)
    if playerHitEnemy:
        if player.attack:
            for i in range(3):
                newParticle = Effect(playerHitEnemy[0].rect.x,playerHitEnemy[0].rect.y, coinImg)
                particles.append(newParticle)
            coinPickup.play()
            player.score += player.coinworth * player.scoremult 
            playerHasKilled += 1
            playerHitEnemy[0].kill()
            
    player.score = round(player.score)
    
    #drawing and updating sprites  
    playerGroup.draw(screen)
    playerGroup.update()
    
    enemyGroup.draw(screen)
    enemyGroup.update()
    
    for item in particles:
        item.draw()

    dogecoins.set_text(str(player.score), 50, (0,0,0))
    
    dogecoins.draw()
    screen.blit(coinImg, (15,15))
    
    sculls.set_text(str(playerHasKilled), 50, (0,0,0))
    
    sculls.draw()
    screen.blit(scullImg, (15,85))
    if shopButton.shopstate:
        RUNNING_FPS = 60
        for item in shopitems:
            item.draw()
    else:
        RUNNING_FPS = 144
        
    shopButton.draw()
    #fpsCounter
    if not shopButton.shopstate:
        fpse = clock.get_fps() 
    else:
        fpse = randint(130, 144)
    fpsCounter.set_text(str(round(fpse)), 50, (0,0,0))
    
    fpsCounter.draw()
    
    #checking for events ex if the X button has been hit
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            saveloadmanager.save_game_data([player.score, player.scoremult, playerHasKilled,hacker.quantity, scratch.quantity,weeb.quantity,nerd.quantity,lenios.quantity ], ["playerscore", "playerscoremultiplier", "playerkills", "quantity1", "quantity2", "quantity3", "quantity4", "quantity5"])
            running = False
    #updating the display
    pygame.display.update()
    
#quiting pygame in case 

pygame.quit()