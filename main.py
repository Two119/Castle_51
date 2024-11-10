import pygame, math, time

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
        self.alive = True
        self.dir = 0
        self.speed = 5
        self.air = 100
        self.effects = {"speed":0, "air":0}
        self.angle = 0
        self.anim_time = time.time()
        self.vel = [0, 0]
    
    def update_animation(self):
        if time.time() - self.anim_time >= 0.125:
            self.frame[0] += 1
            
            if self.frame[0] >= len(knight_animations[self.frame[1]].sheet[0]):
                self.frame[0] = 0
            
            self.anim_time = time.time()
    
    def update(self):
        
        self.rect = pygame.Rect(self.pos[0]+20, self.pos[1] + 12, 76, 116)
        pygame.draw.rect(win, [255, 0, 0], self.rect)
        
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
        
        #self.vel = [self.speed*math.cos(math.radians(self.move_angle)), self.speed*math.sin(math.radians(self.move_angle))]
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        
        win.blit(pygame.transform.flip(knight_animations[self.frame[1]].get([self.frame[0], 0]), self.dir, False), self.pos)
        self.update_animation()
        
crate = scale_image(pygame.image.load("assets/sprites/crate.png").convert())

knight_animations = [SpriteSheet(scale_image(pygame.image.load("assets/sprites/Knight/Idle/Idle-Sheet.png").convert()), [4, 1], [255, 255, 255]), SpriteSheet(scale_image(pygame.image.load("assets/sprites/Knight/Run/Run-Sheet.png").convert()), [6, 1], [255, 255, 255]), SpriteSheet(scale_image(pygame.image.load("assets/sprites/Knight/Death/Death-Sheet.png").convert()), [6, 1], [255, 255, 255])]
wizard_animations = [SpriteSheet(scale_image(pygame.image.load("assets/sprites/Wizard/Idle/Idle-Sheet.png").convert()), [4, 1], [255, 255, 255]), SpriteSheet(scale_image(pygame.image.load("assets/sprites/Wizard/Run/Run-Sheet.png").convert()), [6, 1], [255, 255, 255]), SpriteSheet(scale_image(pygame.image.load("assets/sprites/Wizard/Death/Death-Sheet.png").convert()), [6, 1], [255, 255, 255])]

animation_index = {"idle":0, "run":1, "death":2}

player = Player()

queue = [player]

while True:
    win.fill([0, 0, 0])
    
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    
    for item in queue:
        item.update()
        
    pygame.display.update()