import pygame, math

pygame.init() 
pygame.mixer.init()

win = pygame.display.set_mode([1280, 720])

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
        self.clicksound = pygame.mixer.Sound("click.ogg")
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
        
