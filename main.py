import pygame, math, time, random, asyncio

pygame.init() 
pygame.mixer.init()

win = pygame.display.set_mode([1280, 960])

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
        
async def main():    
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
            self.health = 100
            self.inventory = {"speed_potions":0,"air_potions":0, "health_potions":0, "weapon":0}
            self.inv_no = 0
            self.angle = 0
            self.anim_time = time.time()
            self.vel = [0, 0]
            self.crate = None
            self.pressed = [0, 0, 0, 0]
            self.mask = pygame.mask.from_surface(pygame.transform.flip(knight_animations[self.frame[1]].get([self.frame[0], 0]), self.dir, False))
            self.inventory_box = pygame.Rect((win.get_width() - 64*4)/2, win.get_height() - 88, 64*4, 64)
            self.speed_effect = 0
            self.speed_time = time.time()
        
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
                    self.vel[0] = (self.speed + self.speed_effect)*1
                    self.frame[1] = 1
                    
                elif pygame.key.get_pressed()[pygame.K_LEFT]:
                    self.dir = 1
                    self.vel[0] = (self.speed + self.speed_effect)*-1
                    self.frame[1] = 1
                    
                else:
                    self.vel[0] = 0
                    if self.vel[1] == 0:
                        self.frame[1] = 0
                        
                if pygame.key.get_pressed()[pygame.K_UP]:
                    self.vel[1] = (self.speed + self.speed_effect)*-1
                    self.frame[1] = 1
                    
                elif pygame.key.get_pressed()[pygame.K_DOWN]:
                    self.vel[1] =(self.speed + self.speed_effect)*1
                    self.frame[1] = 1
                    
                else:
                    self.vel[1] = 0
            else:
                self.vel = [0, 0]
                #print(ctrl_pressed)
                current_crate_coord = [int(crates[self.crate][1].x / crate.get_width()), int(crates[self.crate][1].y / crate.get_height())]
                
                if not ctrl_pressed:
                    if (pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]):
                        ctrl_pressed = True
                        self.crate = None
                        
                if pygame.key.get_pressed()[pygame.K_RIGHT]:
                    if not self.pressed[0]:
                        for count, crate_ in enumerate(crates):
                            coord = [int(crate_[1].x / crate.get_width()), int(crate_[1].y / crate.get_height())]
                            
                            if coord[0] - current_crate_coord[0] == 1 and coord[1] == current_crate_coord[1]:
                                self.crate = count
                                self.pos[0] += crate.get_width()
                                break
                    self.pressed[0] = 1
                else:
                    self.pressed[0] = 0
                    
                if pygame.key.get_pressed()[pygame.K_LEFT]:
                    if not self.pressed[1]:
                        for count, crate_ in enumerate(crates):
                            coord = [int(crate_[1].x / crate.get_width()), int(crate_[1].y / crate.get_height())]
                            
                            if coord[0] - current_crate_coord[0] == -1 and coord[1] == current_crate_coord[1]:
                                self.crate = count
                                self.pos[0] -= crate.get_width()
                                break
                    self.pressed[1] = 1
                else:
                    self.pressed[1] = 0
                    
                if pygame.key.get_pressed()[pygame.K_UP]:
                    if not self.pressed[2]:
                        for count, crate_ in enumerate(crates):
                            coord = [int(crate_[1].x / crate.get_width()), int(crate_[1].y / crate.get_height())]
                            
                            if coord[1] - current_crate_coord[1] == -1 and coord[0] == current_crate_coord[0]:
                                self.crate = count
                                self.pos[1] -= crate.get_height()
                                break
                    self.pressed[2] = 1
                else:
                    self.pressed[2] = 0
                    
                if pygame.key.get_pressed()[pygame.K_DOWN]:
                    if not self.pressed[3]:
                        for count, crate_ in enumerate(crates):
                            coord = [int(crate_[1].x / crate.get_width()), int(crate_[1].y / crate.get_height())]
                            
                            if coord[1] - current_crate_coord[1] == 1 and coord[0] == current_crate_coord[0]:
                                self.crate = count
                                self.pos[1] += crate.get_height()
                                break
                    self.pressed[3] = 1
                else:
                    self.pressed[3] = 0

            if time.time() - self.speed_time >= 5:
                self.speed_time = time.time()
                self.speed_effect = 0

            self.update_animation()
            
        def render(self):
            if self.air > 100:
                    self.air = 100
                    
            if self.air < 0:
                self.air = 0
                
            if self.air <= 0:
                self.health -= 0.5
                
            if self.health <= 0:
                self.alive = False
                self.health = 0
                    
            if self.crate == None:
                if self.air < 100:
                    self.air += 0.25
                
                try:
                    win.blit(pygame.transform.flip(knight_animations[self.frame[1]].get([self.frame[0], 0]), self.dir, False), self.pos)
                    self.mask = pygame.mask.from_surface(pygame.transform.flip(knight_animations[self.frame[1]].get([self.frame[0], 0]), self.dir, False))
                except:    
                    self.frame[0] = 0
            else:
                self.air -= 0.75
                
                current_crate_coord = [int((crates[self.crate][1].x - (4 + (win.get_width() - 10*crate.get_width())/2))/ crate.get_width()), int((crates[self.crate][1].y - (4 + (win.get_height() - 6*crate.get_height())/2))/ crate.get_height())]

                if potions[current_level][current_crate_coord[1]][current_crate_coord[0]] == 1:
                    potion_type = random.randint(0, 2)
                    if potion_type == 0:
                        self.inventory["speed_potions"] += 1
                        
                    elif potion_type == 1:
                        self.inventory["air_potions"] += 1
                    
                    else:
                        self.inventory["health_potions"] += 1
                    potions[current_level][current_crate_coord[1]][current_crate_coord[0]] = 0
                    #print(potion_type)
        
            self.pos[0] += self.vel[0]
            self.pos[1] += self.vel[1]
            
    class Wizard:
        def __init__(self):
            self.pos = [300, 100]
            self.frame = [0, 0]
            self.rect = pygame.Rect(self.pos[0]+16, self.pos[1], 112, 128)
            self.wide_rect = pygame.Rect(self.pos[0] - 8, self.pos[1] - 8, 128, 128)
            self.dir = 0
            self.speed = 5
            self.anim_time = time.time()
            self.vel = [0, 0]
            self.mask = pygame.mask.from_surface(pygame.transform.flip(wizard_animations[self.frame[1]].get([self.frame[0], 0]), self.dir, False))
            self.speed_effect = 0
            self.blit_surf = pygame.Surface((32*4, 36*4))
            
        def update_animation(self):
            if time.time() - self.anim_time >= 0.1:
                self.frame[0] += 1
                
                try:
                    wizard_animations[self.frame[1]].get([self.frame[0], 0])
                    
                except:
                    self.frame[0] = 0
                
                self.anim_time = time.time()
        
        def update(self):

            """if pygame.key.get_pressed()[pygame.K_RIGHT]:
                self.dir = 0
                self.vel[0] = (self.speed + self.speed_effect)*1
                self.frame[1] = 1
                
            elif pygame.key.get_pressed()[pygame.K_LEFT]:
                self.dir = 1
                self.vel[0] = (self.speed + self.speed_effect)*-1
                self.frame[1] = 1
                
            else:
                self.vel[0] = 0
                if self.vel[1] == 0:
                    self.frame[1] = 0
                    
            if pygame.key.get_pressed()[pygame.K_UP]:
                self.vel[1] = (self.speed + self.speed_effect)*-1
                self.frame[1] = 1
                
            elif pygame.key.get_pressed()[pygame.K_DOWN]:
                self.vel[1] =(self.speed + self.speed_effect)*1
                self.frame[1] = 1
                
            else:
                self.vel[1] = 0"""
                
            self.pos[0] += self.vel[0]
            self.pos[1] += self.vel[1]
            
            try:
                wizard_animations[self.frame[1]].get([self.frame[0], 0])
                
            except:
                self.frame[0] = 0
                
            self.rect = pygame.Rect(self.pos[0], self.pos[1], wizard_animations[self.frame[1]].get([self.frame[0], 0]).get_width(), wizard_animations[self.frame[1]].get([self.frame[0], 0]).get_height())
            
            
            img = pygame.transform.flip(wizard_animations[self.frame[1]].get([self.frame[0], 0]), self.dir, False)
            self.mask = pygame.mask.from_surface(img)
            
            for crate_, rect in crates:
                if self.rect.colliderect(rect):
                    if (rect.y - self.pos[1]) < 172 and (rect.y - self.pos[1]) > 48:
                        overlap_img = self.mask.overlap_mask(crate_mask, (rect.x - self.pos[0], rect.y - self.pos[1])).to_surface(unsetcolor=(0, 0, 0, 0), setcolor = (255,255,255))
                        img.blit(overlap_img, (-4, 0))
                        img.blit(overlap_img, (0, -4))
                        img.blit(overlap_img, (0, 0))
                        
            if self.rect.colliderect(player.wide_rect):
                    if (player.pos[1] - self.pos[1]) < 172 and (player.pos[1] - self.pos[1]) > 24:
                        overlap_img = self.mask.overlap_mask(player.mask, (player.pos[0] - self.pos[0], player.pos[1] - self.pos[1])).to_surface(unsetcolor=(0, 0, 0, 0), setcolor = (255,255,255))
                        img.blit(overlap_img, (-4, 0))
                        img.blit(overlap_img, (0, -4))
                        img.blit(overlap_img, (0, 0))
                                  
            swap_color(img, [255, 255, 255], [0, 0, 0])
            
            img.set_colorkey([0, 0, 0])
            
            win.blit(img, self.pos)
            self.update_animation()
            
    crate = scale_image(pygame.image.load("assets/sprites/crate.png").convert())
    crate.set_colorkey([255, 255, 255])
    crate_mask = pygame.mask.from_surface(crate)

    knight_animations = [SpriteSheet(scale_image(pygame.image.load("assets/sprites/Knight/Idle/Idle-Sheet.png").convert()), [4, 1], [255, 255, 255]), SpriteSheet(scale_image(pygame.image.load("assets/sprites/Knight/Run/Run-Sheet.png").convert()), [6, 1], [255, 255, 255]), SpriteSheet(scale_image(pygame.image.load("assets/sprites/Knight/Death/Death-Sheet.png").convert()), [6, 1], [255, 255, 255])]
    wizard_animations = [SpriteSheet(scale_image(pygame.image.load("assets/sprites/Wizard/Idle/Idle-Sheet.png").convert()), [4, 1], [255, 255, 255]), SpriteSheet(scale_image(pygame.image.load("assets/sprites/Wizard/Run/Run-Sheet.png").convert()), [6, 1], [255, 255, 255]), SpriteSheet(scale_image(pygame.image.load("assets/sprites/Wizard/Death/Death-Sheet.png").convert()), [6, 1], [255, 255, 255])]

    animation_index = {"idle":0, "run":1, "death":2}

    player = Player()
    
    wizards = [Wizard()]

    above_player = []
    below_player = []

    levels = [[]]
    potions = [[]]

    crates = []

    for count, level in enumerate(levels):
        
        for i in range(6):
            
            levels[count].append([])
            potions[count].append([])
            
            for j in range(10):
                n = random.randint(0, 10)
                levels[count][i].append(n)
                if n < 4:
                    potions[count][i].append(random.randint(1, 6))
                    levels[count][i].append(1)
                    crates.append([(j*crate.get_width(), i*crate.get_height()), pygame.Rect(j*crate.get_width() + 4 + (win.get_width() - 10*crate.get_width())/2, i*crate.get_height()  + 64 + (win.get_height() - 6*crate.get_height())/2, crate.get_width() - 8, crate.get_height() - 8)])
                else:
                    levels[count][i].append(0)
                    potions[count][i].append(0)
                    
    current_level = 0
    global ctrl_pressed
    ctrl_pressed = False

    potion_sprites = [scale_image(pygame.image.load("assets/sprites/Potions/speed.png").convert()), scale_image(pygame.image.load("assets/sprites/Potions/air.png").convert()), scale_image(pygame.image.load("assets/sprites/Potions/health.png").convert())]

    potion_sprites[0].set_colorkey([255, 255, 255])
    potion_sprites[1].set_colorkey([255, 255, 255])
    potion_sprites[2].set_colorkey([255, 255, 255])

    bg = scale_image(pygame.image.load("assets/maps/png/level_1.png").convert())
    
    inv_font = pygame.font.Font("assets/font/yoster.ttf", 20)
    ui_font = pygame.font.Font("assets/font/yoster.ttf", 28)
    big_font = pygame.font.Font("assets/font/yoster.ttf", 64)
    
    health_text = ui_font.render("HEALTH", False, [255, 255, 255], [0, 0, 0])
    health_text.set_colorkey([0, 0, 0])
    
    air_text = ui_font.render("AIR", False, [255, 255, 255], [0, 0, 0])
    air_text.set_colorkey([0, 0, 0])
    
    death_text = big_font.render("YOU DIED!", False, [255, 255, 255], [0, 0, 0])
    death_text.set_colorkey([0, 0, 0])
    
    e_pressed = False
    screenshot = None
    dark_overlay_surf = pygame.Surface((win.get_width(), win.get_height()))
    dark_overlay_surf.fill([0, 0, 0])
    dark_overlay_surf.set_alpha(75)
    radius = 0
    
    while True:

        if not player.alive:
            if screenshot is None:
                screenshot = win.copy()
            
        win.fill([0, 0, 0])
        win.blit(bg, [0, 0])
        
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        count = -1
        
        below_player.clear()
        above_player.clear()
        
        
        if player.alive:
            player.update()
        
        if (player.rect.y + player.rect.h) > (win.get_height() - 40):
            if player.vel[1] > 0:
                player.vel[1] = 0
                
        if (player.rect.y) < (128):
            if player.vel[1] < 0:
                player.vel[1] = 0
                
        if (player.rect.x) < (40):
            if player.vel[0] < 0:
                player.vel[0] = 0
                
        if (player.rect.x + player.rect.w) > (win.get_width() - 40):
            if player.vel[0] > 0:
                player.vel[0] = 0
        
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
                
                if crate_mask.overlap(player.mask, [player.pos[0] - rect.x, player.pos[1] - rect.y]):
                    if (pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]) and not ctrl_pressed:
                        ctrl_pressed = True
                        if player.crate == None:
                            player.crate = count
                            
                            if (rect.y - player.rect.y) < 64 and (rect.y - player.rect.y) > 0:
                                player.pos[1] -= 48 - (player.rect.y - player.rect.y)
                    
                    if (rect.y - player.rect.y) < 64 and (rect.y - player.rect.y) > 0:
                        if player.vel[1] > 0:
                            player.vel[1] = 0
                        if (rect.y - player.rect.y) < 48 and (rect.y - player.rect.y) > 0:
                            if player.vel[0] != 0:
                                if player.pos[0] - rect.x > 0:
                                    if player.vel[0] < 0:
                                        player.vel[0] = 0
                                if player.pos[0] - rect.x < 0:
                                    if player.vel[0] > 0:
                                        player.vel[0] = 0
                            
                    if (player.rect.y - rect.y) < 28 and (player.rect.y - rect.y) > 0:
                        if player.vel[1] < 0:
                            player.vel[1] = 0
                
            else:
                below_player.append(count)
        
        for x in below_player:
            win.blit(crate, [crates[x][0][0] + (win.get_width() - 10*crate.get_width())/2, crates[x][0][1] + 60 + (win.get_height() - len(levels[current_level])*crate.get_height())/2])
            
        if player.alive:
            player.render()
            
        for x in above_player:
            win.blit(crate, [crates[x][0][0] + (win.get_width() - 10*crate.get_width())/2, crates[x][0][1] + 60 + (win.get_height() - len(levels[current_level])*crate.get_height())/2])
        
        if player.crate != None:
            pygame.draw.rect(win, [255, 255, 255], crates[player.crate][1], 4)
            
        for wizard in wizards:
            wizard.update()
            
        pygame.draw.rect(win, [75, 75, 75], player.inventory_box, 4)
        pygame.draw.line(win, [75, 75, 75], [player.inventory_box.x + (1*player.inventory_box.w/4), player.inventory_box.y], [player.inventory_box.x + (1*player.inventory_box.w/4), player.inventory_box.y + player.inventory_box.h - 4], 4)
        pygame.draw.line(win, [75, 75, 75], [player.inventory_box.x + (2*player.inventory_box.w/4), player.inventory_box.y], [player.inventory_box.x + (2*player.inventory_box.w/4), player.inventory_box.y + player.inventory_box.h - 4], 4)
        pygame.draw.line(win, [75, 75, 75], [player.inventory_box.x + (3*player.inventory_box.w/4), player.inventory_box.y], [player.inventory_box.x + (3*player.inventory_box.w/4), player.inventory_box.y + player.inventory_box.h - 4], 4)
        
        speed_potions_no = inv_font.render(str(player.inventory["speed_potions"]), False, [255, 255, 255], [0, 0, 0])
        speed_potions_no.set_colorkey([0, 0, 0])
        
        air_potions_no = inv_font.render(str(player.inventory["air_potions"]), False, [255, 255, 255], [0, 0, 0])
        air_potions_no.set_colorkey([0, 0, 0])
        
        health_potions_no = inv_font.render(str(player.inventory["health_potions"]), False, [255, 255, 255], [0, 0, 0])
        health_potions_no.set_colorkey([0, 0, 0])
        
        if player.inventory["speed_potions"] > 0:
            win.blit(potion_sprites[0], [player.inventory_box.x + 16, player.inventory_box.y + 12])
            win.blit(speed_potions_no, [player.inventory_box.x + 48, player.inventory_box.y + 44])
            
        if player.inventory["air_potions"] > 0:
            win.blit(potion_sprites[1], [player.inventory_box.x + 16 + player.inventory_box.w/4, player.inventory_box.y + 12])
            win.blit(air_potions_no, [player.inventory_box.x + 48 + player.inventory_box.w/4, player.inventory_box.y + 44])
            
        if player.inventory["health_potions"] > 0:
            win.blit(potion_sprites[2], [player.inventory_box.x + 16 + player.inventory_box.w/2, player.inventory_box.y + 12])
            win.blit(health_potions_no, [player.inventory_box.x + 48 + player.inventory_box.w/2, player.inventory_box.y + 44])
            
        if pygame.key.get_pressed()[pygame.K_1]:
            player.inv_no = 0
        if pygame.key.get_pressed()[pygame.K_2]:
            player.inv_no = 1
        if pygame.key.get_pressed()[pygame.K_3]:
            player.inv_no = 2
        if pygame.key.get_pressed()[pygame.K_4]:
            player.inv_no = 3
            
        if not e_pressed:
            if pygame.key.get_pressed()[pygame.K_e]:
                if player.inv_no == 0:
                    if player.inventory["speed_potions"] > 0:
                        player.inventory["speed_potions"] -= 1
                        player.speed_effect = 2.5
                        player.speed_time = time.time()
                        
                if player.inv_no == 1:
                    if player.inventory["air_potions"] > 0:
                        player.inventory["air_potions"] -= 1
                        player.air += 33
                        
                if player.inv_no == 2:
                    if player.inventory["health_potions"] > 0:
                        player.inventory["health_potions"] -= 1
                        player.health += 33
                        if player.health > 100:
                            player.health = 100
                e_pressed = True
                
        if not pygame.key.get_pressed()[pygame.K_e]:
            e_pressed = False
             
        pygame.draw.rect(win, [125, 125, 125], pygame.Rect(player.inventory_box.x + (player.inv_no*player.inventory_box.w/4), player.inventory_box.y, player.inventory_box.h, player.inventory_box.h), 4)
        
        pygame.draw.rect(win, [75, 200, 75], pygame.Rect(324, 8, (player.health/100)*256, 28))
        pygame.draw.rect(win, [25, 100, 25], pygame.Rect(324, 8, 256, 28), 4)
        
        pygame.draw.rect(win, [75, 75, 200], pygame.Rect(692, 8, (player.air/100)*256, 28))
        pygame.draw.rect(win, [25, 25, 100], pygame.Rect(692, 8, 256, 28), 4)     
    
        win.blit(health_text, [324 + (256-health_text.get_width())/2, 8])
        win.blit(air_text, [692 + (256-air_text.get_width())/2, 8])
        
        if not player.alive and screenshot is not None:
            win.blit(screenshot, [0,0])
            win.blit(dark_overlay_surf, [0,0])
            pygame.draw.circle(win, [0, 0, 0], [win.get_width()/2, win.get_height()/2], radius)
            radius += 15
            win.blit(death_text, [(win.get_width() - death_text.get_width())/2, (win.get_height() - death_text.get_height())/2])
            
            if radius > 1000:
                
                radius = 0
                
                screenshot = None
                
                player = Player()

                above_player = []
                below_player = []

                levels = [[]]
                potions = [[]]

                crates = []

                for count, level in enumerate(levels):
                    
                    for i in range(6):
                        
                        levels[count].append([])
                        potions[count].append([])
                        
                        for j in range(10):
                            n = random.randint(0, 10)
                            levels[count][i].append(n)
                            if n < 4:
                                potions[count][i].append(random.randint(1, 6))
                                levels[count][i].append(1)
                                crates.append([(j*crate.get_width(), i*crate.get_height()), pygame.Rect(j*crate.get_width() + 4 + (win.get_width() - 10*crate.get_width())/2, i*crate.get_height()  + 64 + (win.get_height() - 6*crate.get_height())/2, crate.get_width() - 8, crate.get_height() - 8)])
                            else:
                                levels[count][i].append(0)
                                potions[count][i].append(0)
                
        pygame.display.update()
        await asyncio.sleep(0)
asyncio.run(main())