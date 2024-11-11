import pygame, math, time, random

pygame.init() 
pygame.mixer.init()

win = pygame.display.set_mode([1280, 720])

clock = pygame.time.Clock()

#pygame.display.set_caption("")

def angle_between(points):
    return math.atan2(points[1][1] - points[0][1], points[1][0] - points[0][0])*180/math.pi

def scale_image(img, factor=4.0):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size).convert()

def swap_color(img, col1, col2):
    pygame.transform.threshold(img, img, col1, (10, 10, 10), col2, 1, None, True)
    
class SpriteSheet:
    def __init__(self, sheet, size, colorkey = [0, 0, 0]):
        self.spritesheet = sheet
        self.colorkey = colorkey
        self.size = [self.spritesheet.get_width()/size[0], self.spritesheet.get_height()/size[1]]
        self.sheet = []
        for i in range(size[1]):
            self.sheet.append([])
            for j in range(size[0]):
                image = pygame.Surface((self.size))
                image.set_colorkey(self.colorkey)
                image.blit(self.spritesheet, (0, 0), [j*self.size[0], i*self.size[1], self.size[0], self.size[1]])
                self.sheet[i].append(image)
    def get(self, loc):
        return self.sheet[loc[1]][loc[0]]

class Button:
    def __init__(self, position, textures, function):
        self.textures = textures
        self.onlick = function[0]
        self.args = function[1]
        self.pos = position
        self.current = 0
        self.rect = self.textures[self.current].get_rect(topleft=self.pos)
        self.click_delay = 0
        self.max_delay = 500
        self.delaying = False
        self.clicksound = pygame.mixer.Sound("assets/sounds/click.ogg")
    def update(self):
        self.current = 0
        if self.delaying:
            self.click_delay += 1
        if self.click_delay >= self.max_delay:
            self.delaying = False
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                if not self.delaying:
                    self.onlick(self.args)
                    self.clicksound.play()
            self.current = 1
        win.blit(self.textures[self.current], self.pos)
        self.rect = self.textures[self.current].get_rect(topleft=self.pos)
        
class Player:
    def __init__(self):
        self.pos = [100, 100]
        self.frame = [0, 0]
        self.rect = pygame.Rect(self.pos[0]+16, self.pos[1], 112, 128)
        self.wide_rect = pygame.Rect(self.pos[0] - 8, self.pos[1] - 8, 128, 128)
        self.alive = True
        self.dir = 0
        self.speed = 5
        self.air = 100
        self.effects = {"speed":0, "air":0}
        self.angle = 0
        self.anim_time = time.time()
        self.vel = [0, 0]
        self.crate = None
    
    def update_animation(self):
        if time.time() - self.anim_time >= 0.1:
            self.frame[0] += 1
            
            try:
                knight_animations[self.frame[1]].get([self.frame[0], 0])
                
            except:
                self.frame[0] = 0
            
            self.anim_time = time.time()
    
    def update(self):
        global ctrl_pressed
        self.rect = pygame.Rect(self.pos[0]+20, self.pos[1] + 12, 76, 116)
        self.wide_rect = pygame.Rect(self.pos[0], self.pos[1] - 8, 128, 144)
        #pygame.draw.rect(win, [255, 0, 0], self.rect)
        #pygame.draw.rect(win, [255, 0, 0], self.wide_rect)
        if self.crate == None:
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                self.dir = 0
                self.vel[0] = self.speed*1
                self.frame[1] = 1
                
            elif pygame.key.get_pressed()[pygame.K_LEFT]:
                self.dir = 1
                self.vel[0] = self.speed*-1
                self.frame[1] = 1
                
            else:
                self.vel[0] = 0
                if self.vel[1] == 0:
                    self.frame[1] = 0
                    
            if pygame.key.get_pressed()[pygame.K_UP]:
                self.vel[1] = self.speed*-1
                self.frame[1] = 1
                
            elif pygame.key.get_pressed()[pygame.K_DOWN]:
                self.vel[1] = self.speed*1
                self.frame[1] = 1
                
            else:
                self.vel[1] = 0
        else:
            self.vel = [0, 0]
            #print(ctrl_pressed)
            if not ctrl_pressed:
                if (pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]):
                    ctrl_pressed = True
                    self.crate = None
                    
            
                    #print("A")
        #self.vel = [self.speed*math.cos(math.radians(self.move_angle)), self.speed*math.sin(math.radians(self.move_angle))]

        self.update_animation()
        
    def render(self):
        if self.crate == None:
            try:
                win.blit(pygame.transform.flip(knight_animations[self.frame[1]].get([self.frame[0], 0]), self.dir, False), self.pos)
            except:    
                self.frame[0] = 0
            
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        
crate = scale_image(pygame.image.load("assets/sprites/crate.png").convert())
crate.set_colorkey([255, 255, 255])

knight_animations = [SpriteSheet(scale_image(pygame.image.load("assets/sprites/Knight/Idle/Idle-Sheet.png").convert()), [4, 1], [255, 255, 255]), SpriteSheet(scale_image(pygame.image.load("assets/sprites/Knight/Run/Run-Sheet.png").convert()), [6, 1], [255, 255, 255]), SpriteSheet(scale_image(pygame.image.load("assets/sprites/Knight/Death/Death-Sheet.png").convert()), [6, 1], [255, 255, 255])]
wizard_animations = [SpriteSheet(scale_image(pygame.image.load("assets/sprites/Wizard/Idle/Idle-Sheet.png").convert()), [4, 1], [255, 255, 255]), SpriteSheet(scale_image(pygame.image.load("assets/sprites/Wizard/Run/Run-Sheet.png").convert()), [6, 1], [255, 255, 255]), SpriteSheet(scale_image(pygame.image.load("assets/sprites/Wizard/Death/Death-Sheet.png").convert()), [6, 1], [255, 255, 255])]

animation_index = {"idle":0, "run":1, "death":2}

player = Player()

above_player = []
below_player = []

levels = [[]]

crates = []

for count, level in enumerate(levels):
    
    for i in range(6):
        
        levels[count].append([])
        
        for j in range(10):
            n = random.randint(0, 10)
            if n < 4:
                levels[count][i].append(n)
                crates.append([(j*crate.get_width(), i*crate.get_height()), pygame.Rect(j*crate.get_width() + 4 + (win.get_width() - 10*crate.get_width())/2, i*crate.get_height()  + 4 + (win.get_height() - 6*crate.get_height())/2, crate.get_width() - 8, crate.get_height() - 8)])

current_level = 0
global ctrl_pressed
ctrl_pressed = False
while True:
    win.fill([0, 0, 0])
    
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    
    count = -1
    below_player.clear()
    above_player.clear()
    
    player.update()
    
    if not (pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]):
        ctrl_pressed = False
    
    for crate_, rect in crates:
        count += 1
        #pygame.draw.rect(win, [255, 0, 0], rect)
        if rect.colliderect(player.wide_rect):
            if rect.y < player.rect.y:
                below_player.append(count)
            else:
                above_player.append(count)
                
            if (rect.y + rect.h) < (player.rect.y + player.rect.h):
                below_player.append(count)
                if count in above_player:
                    above_player.remove(count)
            
            if rect.colliderect(player.rect):
                if (pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]) and not ctrl_pressed:
                    ctrl_pressed = True
                    if player.crate == None:
                        player.crate = count
                
                if (rect.y - player.rect.y) < 36 and (rect.y - player.rect.y) > 0:
                    if player.vel[1] > 0:
                        player.vel[1] = 0
                        
                if (player.rect.y - rect.y) < 28 and (player.rect.y - rect.y) > 0:
                    if player.vel[1] < 0:
                        player.vel[1] = 0
            
        else:
            below_player.append(count)
    
    for x in below_player:
        win.blit(crate, [crates[x][0][0] + (win.get_width() - 10*crate.get_width())/2, crates[x][0][1] + (win.get_height() - len(levels[current_level])*crate.get_height())/2])
        
    player.render()
        
    for x in above_player:
        win.blit(crate, [crates[x][0][0] + (win.get_width() - 10*crate.get_width())/2, crates[x][0][1] + (win.get_height() - len(levels[current_level])*crate.get_height())/2])
    
    if player.crate != None:
        pygame.draw.rect(win, [255, 255, 255], crates[player.crate][1], 4)
        
    pygame.display.update()