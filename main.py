import pygame, math, time, random, asyncio

pygame.init()
pygame.mixer.init()

win = pygame.display.set_mode([1920, 1080])

clock = pygame.time.Clock()

# pygame.display.set_caption("")


def angle_between(points):
    return math.atan2(points[1][1] - points[0][1], points[1][0] - points[0][0]) * 180 / math.pi


def scale_image(img, factor=4.0):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size).convert()


def swap_color(img, col1, col2):
    pygame.transform.threshold(img, img, col1, (10, 10, 10), col2, 1, None, True)


def load_level(filename: str):
    f = open(filename, "r")
    level = []
    for line in f.readlines():
        level.append(list(map(int, line.split(","))))
    f.close()
    return level


class SpriteSheet:
    def __init__(self, sheet, size, colorkey=[0, 0, 0]):
        self.spritesheet = sheet
        self.colorkey = colorkey
        self.size = [self.spritesheet.get_width() / size[0], self.spritesheet.get_height() / size[1]]
        self.sheet = []
        for i in range(size[1]):
            self.sheet.append([])
            for j in range(size[0]):
                image = pygame.Surface((self.size))
                image.set_colorkey(self.colorkey)
                image.blit(self.spritesheet, (0, 0), [j * self.size[0], i * self.size[1], self.size[0], self.size[1]])
                self.sheet[i].append(image)

    def get(self, loc):
        return self.sheet[loc[1]][loc[0]]


class Button:
    def __init__(self, position, textures, function):
        self.textures = textures
        self.onclick = function
        self.pos = position
        self.current = 0
        self.rect = self.textures[self.current].get_rect(topleft=self.pos)
        self.click_delay = 0
        self.max_delay = 500
        self.delaying = False
        self.pressed = False
        self.clicksound = pygame.mixer.Sound("assets/sounds/click.ogg")

    def update(self):
        self.current = 0
        if self.delaying:
            self.click_delay += 1
        if self.click_delay >= self.max_delay:
            self.delaying = False
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                if not self.delaying and not self.pressed:
                    self.onclick()
                    self.clicksound.play()
                self.pressed = True
            else:
                self.pressed = False
            self.current = 1
        win.blit(self.textures[self.current], self.pos)
        self.rect = self.textures[self.current].get_rect(topleft=self.pos)


class Notification:
    def __init__(self, surf: pygame.Surface):
        self.surf = surf
        self.alpha = 255
        self.pos = [(win.get_width() - self.surf.get_width()) / 2, (win.get_height() - self.surf.get_height()) / 2]
        self.speed = 1
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.surf.get_width(), self.surf.get_height())

    def update(self):
        self.pos[1] -= self.speed
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.surf.get_width(), self.surf.get_height())
        self.alpha -= (self.speed * 1.5) * (60 / current_fps)
        if self.alpha <= 0:
            self.alpha = 0
        self.surf.set_alpha(int(self.alpha))
        win.blit(self.surf, self.pos)

class Slider:
    def __init__(self, pos):
        self.overall_rect = pygame.Rect(pos[0] - 16, pos[1] - 16, 300, 60)
        self.rect = pygame.Rect(pos[0] + 20, pos[1] + 8, 200, 12)
        self.choice_rect = pygame.Rect(pos[0] + 60, pos[1] + 2, 16, 24)
        self.pos = pos
        self.value = 1
    def update(self):
        
        self.overall_rect = pygame.Rect(self.pos[0] - 16, self.pos[1] - 16, 300, 60)
        self.rect = pygame.Rect(self.pos[0] + 20, self.pos[1] + 8, 200, 12)
        m_pos = pygame.mouse.get_pos()
        m_rect = pygame.Rect(m_pos[0], m_pos[1], 12, 18)
        
        if (self.choice_rect.colliderect(m_rect) or self.rect.colliderect(m_rect)) and pygame.mouse.get_pressed()[0]:
            self.choice_rect.x = m_pos[0]
            
            if self.choice_rect.x > self.pos[0] + 204:
                self.choice_rect.x = self.pos[0] + 204
                
            if self.choice_rect.x < self.pos[0] + 20:
                self.choice_rect.x = self.pos[0] + 20
            
        if self.choice_rect.x <= self.pos[0] + 20:
            self.value = 0.1
        else:
            if self.choice_rect.x <= self.pos[0] + 40:
                self.value = 0.2
            else:
                if self.choice_rect.x <= self.pos[0] + 60:
                    self.value = 0.3
                else:
                    if self.choice_rect.x <= self.pos[0] + 80:
                        self.value = 0.4
                    else:
                        if self.choice_rect.x <= self.pos[0] + 100:
                            self.value = 0.5
                        else:
                            if self.choice_rect.x <= self.pos[0] + 120:
                                self.value = 0.6
                            else:
                                if self.choice_rect.x <= self.pos[0] + 140:
                                    self.value = 0.7
                                else:
                                    if self.choice_rect.x <= self.pos[0] + 160:
                                        self.value = 0.8
                                    else:
                                        if self.choice_rect.x <= self.pos[0] + 180:
                                            self.value = 0.9
                                        else:
                                            if self.choice_rect.x <= self.pos[0] + 200:
                                                self.value = 1
        
        pygame.draw.rect(win, (48,208,216), self.rect)
        pygame.draw.rect(win, [200, 200, 200], self.choice_rect)

def isequal(color1: pygame.Color, color2: tuple) -> bool:
    if color1.r == color2[0] and color1.g == color2[1] and color1.b == color2[2]:
        return True
    else:
        return False


def dye(img: pygame.Surface, color: tuple, colorkey: tuple, alpha: int = 128):
    surf = img.copy()
    rect_surf = pygame.Surface([1, 1])
    rect_surf.fill(color)
    rect_surf.set_alpha(alpha)
    for j in range(surf.get_height()):
        for i in range(surf.get_width()):
            if not isequal(surf.get_at([i, j]), colorkey):
                surf.blit(rect_surf, [i, j])
    return surf


class State:
    last = -1
    current = -1
    on_change = None

    @classmethod
    def change(cls, new_state):
        changed = new_state != cls.current
        if changed:
            cls.last = cls.current
            cls.current = new_state
            if cls.on_change:
                cls.on_change()
        return changed


def play():
    global State
    global player
    State.change(1)
    player.alive = False
    pygame.mixer.music.stop()
    global music_slider
    music_slider.pos = (441, 8)
    music_slider.choice_rect = pygame.Rect(music_slider.pos[0], music_slider.pos[1] + 2, 16, 24)
    music_slider.choice_rect.x += (music_slider.value * music_slider.rect.w)


def resume():
    global State
    global screenshot
    State.change(1)
    screenshot = None
    global music_slider
    music_slider.pos = (441, 8)
    music_slider.choice_rect = pygame.Rect(music_slider.pos[0], music_slider.pos[1] + 2, 16, 24)
    music_slider.choice_rect.x += (music_slider.value * music_slider.rect.w)


global transitioning
transitioning = False


def menu():
    global transitioning, State
    transitioning = True
    State.change(1)

    player.alive = False
    pygame.mixer.music.stop()


def menu2():
    global State
    State.current = 0


def pause():
    global screenshot, State
    screenshot = win.copy()
    screenshot.blit(small_button_spritesheet.sheet[0][0], small_button_pos)
    State.change(2)
    pygame.mixer.music.stop()
    global music_slider
    music_slider.pos = [escape_screen_buttons[0].pos[0] - 32, escape_screen_buttons[0].pos[1] - 64]
    music_slider.choice_rect = pygame.Rect(music_slider.pos[0], music_slider.pos[1] + 2, 16, 24)
    music_slider.choice_rect.x += (music_slider.value * music_slider.rect.w)


def tutorial_start():
    global State
    State.current = 3


def show_credits():
    global State
    State.current = 4


button_spritesheet = SpriteSheet(scale_image(pygame.image.load("assets/sprites/buttons.png").convert()), [2, 1], [0, 0, 0])
button_center_pos = [(win.get_width() - button_spritesheet.size[0]) / 2, (win.get_height() - button_spritesheet.size[1]) / 2]

small_button_spritesheet = SpriteSheet(
    scale_image(pygame.image.load("assets/sprites/small_buttons.png").convert()), [2, 1], [255, 255, 255]
)
small_button_pos = [(win.get_width() - 64 * 4) / 2 + 276, win.get_height() - 88]

title_screen_font = pygame.font.Font("assets/font/yoster.ttf", 30)
title_screen_buttons = [
    Button(button_center_pos, button_spritesheet.sheet[0], play),
    Button([button_center_pos[0], button_center_pos[1] + 78], button_spritesheet.sheet[0], tutorial_start),
    Button([button_center_pos[0], button_center_pos[1] + 156], button_spritesheet.sheet[0], show_credits),
]
title_screen_text = [
    [
        title_screen_font.render("Play", False, [255, 255, 255], [0, 0, 0]),
        [title_screen_buttons[0].pos[0] + 36, title_screen_buttons[0].pos[1] + 18],
    ],
    [
        title_screen_font.render("Learn", False, [255, 255, 255], [0, 0, 0]),
        [title_screen_buttons[0].pos[0] + 28, title_screen_buttons[0].pos[1] + 96],
    ],
    [
        title_screen_font.render("Credit", False, [255, 255, 255], [0, 0, 0]),
        [title_screen_buttons[1].pos[0] + 22, title_screen_buttons[1].pos[1] + 96],
    ],
]
title_screen_text[0][0].set_colorkey((0, 0, 0))
title_screen_text[1][0].set_colorkey((0, 0, 0))
title_screen_text[2][0].set_colorkey((0, 0, 0))

escape_screen_buttons = [
    Button(button_center_pos, button_spritesheet.sheet[0], menu),
    Button([button_center_pos[0], button_center_pos[1] + 88], button_spritesheet.sheet[0], resume),
]
escape_screen_text = [
    [
        title_screen_font.render("Menu", False, [255, 255, 255], [0, 0, 0]),
        [title_screen_buttons[0].pos[0] + 36, title_screen_buttons[0].pos[1] + 18],
    ],
    [
        title_screen_font.render("Back", False, [255, 255, 255], [0, 0, 0]),
        [title_screen_buttons[1].pos[0] + 32, title_screen_buttons[1].pos[1] + 28],
    ],
]
escape_screen_text[0][0].set_colorkey((0, 0, 0))
escape_screen_text[1][0].set_colorkey((0, 0, 0))

pause_button = Button(small_button_pos, small_button_spritesheet.sheet[0], pause)


async def main():
    class Player:
        def __init__(self):
            self.pos = [100, 100]
            self.frame = [0, 0]
            self.rect = pygame.Rect(self.pos[0] + 16, self.pos[1], 112, 128)
            self.wide_rect = pygame.Rect(self.pos[0] - 8, self.pos[1] - 8, 128, 128)
            self.alive = True
            self.win = False
            self.has_artifact = False
            self.dir = 0
            self.speed = 5
            self.air = 100
            self.health = 100
            self.inventory = {"speed_potions": 0, "air_potions": 0, "health_potions": 0, "weapon": 0}
            self.inv_no = 0
            self.angle = 0
            self.anim_time = time.time()
            self.vel = [0, 0]
            self.crate = None
            self.pressed = [0, 0, 0, 0]
            self.mask = pygame.mask.from_surface(
                pygame.transform.flip(knight_animations[self.frame[1]].get([self.frame[0], 0]), self.dir, False)
            )
            self.inventory_box = pygame.Rect((win.get_width() - 64 * 4) / 2, win.get_height() - 88, 64 * 4, 64)
            self.speed_effect = 0
            self.speed_time = time.time()
            self.damange_jitter_timer = time.time() - 3
            self.damange_jitter_duration = 1
            self.true_rect = pygame.Rect(self.pos[0]+20, self.pos[1] + 12, 76, 116)

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
            self.true_rect = pygame.Rect(self.pos[0]+20, self.pos[1] + 12, 76, 116)
            self.rect = pygame.Rect(self.pos[0] + 32, self.pos[1] + 12, 64, 116)
            self.wide_rect = pygame.Rect(self.pos[0], self.pos[1] - 8, 128, 144)
            # pygame.draw.rect(win, [255, 0, 0], self.rect)
            # pygame.draw.rect(win, [255, 0, 0], self.wide_rect)
            if self.crate == None:
                if pygame.key.get_pressed()[pygame.K_d] or pygame.key.get_pressed()[pygame.K_RIGHT]:
                    self.dir = 0
                    self.vel[0] = (self.speed + self.speed_effect) * 1
                    self.frame[1] = 1

                elif pygame.key.get_pressed()[pygame.K_a] or pygame.key.get_pressed()[pygame.K_LEFT]:
                    self.dir = 1
                    self.vel[0] = (self.speed + self.speed_effect) * -1
                    self.frame[1] = 1

                else:
                    self.vel[0] = 0
                    if self.vel[1] == 0:
                        self.frame[1] = 0

                if pygame.key.get_pressed()[pygame.K_w] or pygame.key.get_pressed()[pygame.K_UP]:
                    self.vel[1] = (self.speed + self.speed_effect) * -1
                    self.frame[1] = 1

                elif pygame.key.get_pressed()[pygame.K_s] or pygame.key.get_pressed()[pygame.K_DOWN]:
                    self.vel[1] = (self.speed + self.speed_effect) * 1
                    self.frame[1] = 1

                else:
                    self.vel[1] = 0
            else:
                self.vel = [0, 0]
                # print(ctrl_pressed)
                current_crate_coord = [
                    int(crates[self.crate][1].x / crate.get_width()),
                    int(crates[self.crate][1].y / crate.get_height()),
                ]

                if not ctrl_pressed:
                    if pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]:
                        ctrl_pressed = True
                        self.crate = None

                if pygame.key.get_pressed()[pygame.K_d] or pygame.key.get_pressed()[pygame.K_RIGHT]:
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

                if pygame.key.get_pressed()[pygame.K_a] or pygame.key.get_pressed()[pygame.K_LEFT]:
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

                if pygame.key.get_pressed()[pygame.K_w] or pygame.key.get_pressed()[pygame.K_UP]:
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

                if pygame.key.get_pressed()[pygame.K_s] or pygame.key.get_pressed()[pygame.K_DOWN]:
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
                self.health -= (0.5) * (60 / current_fps)

            if self.health <= 0:
                self.alive = False
                if not music_player.level_end_sfx.get_busy():
                    pygame.mixer.music.stop()
                    music_player.level_end_sfx.play(music_player.death_sound)
                self.health = 0

            if self.crate == None:
                if self.air < 100:
                    self.air += (0.25) * (60 / current_fps)

                try:
                    if (time.time() - self.damange_jitter_timer) < self.damange_jitter_duration:
                        win.blit(
                            pygame.transform.flip(dyed_knight_animations[self.frame[1]][self.frame[0]], self.dir, False),
                            [self.pos[0] + random.randint(1, 12), self.pos[1] + random.randint(1, 12)],
                        )
                    else:
                        win.blit(
                            pygame.transform.flip(knight_animations[self.frame[1]].get([self.frame[0], 0]), self.dir, False),
                            self.pos,
                        )

                    self.mask = pygame.mask.from_surface(
                        pygame.transform.flip(knight_animations[self.frame[1]].get([self.frame[0], 0]), self.dir, False)
                    )
                except:
                    self.frame[0] = 0
            else:
                self.air -= (0.75) * (60 / current_fps)

                current_crate_coord = [
                    int((crates[self.crate][1].x + level_adjustments[current_level][0]) / crate.get_width()),
                    int((crates[self.crate][1].y + level_adjustments[current_level][1]) / crate.get_height()),
                ]

                if potions[current_level][current_crate_coord[1]][current_crate_coord[0]] == 1:
                    potion_type = random.randint(0, 2)
                    if potion_type == 0:
                        self.inventory["speed_potions"] += 1

                    elif potion_type == 1:
                        self.inventory["air_potions"] += 1

                    else:
                        self.inventory["health_potions"] += 1
                    potions[current_level][current_crate_coord[1]][current_crate_coord[0]] = 0

                if potions[current_level][current_crate_coord[1]][current_crate_coord[0]] == 7 and not self.has_artifact:
                    self.has_artifact = True
                    notifications.append(Notification(key_notification))
                    if not music_player.found_key_channel.get_busy():
                            music_player.found_key_channel.play(music_player.found_key_sound)
                    # print(potion_type)

            self.pos[0] += self.vel[0] * (60 / current_fps)
            self.pos[1] += self.vel[1] * (60 / current_fps)

    staff = scale_image(pygame.image.load("assets/sprites/Wizard/staff.png").convert())
    staff.set_colorkey((255, 255, 255))

    class Wizard:
        def __init__(self, x, y):
            self.pos = [x, y]
            self.frame = [0, 0]
            self.rect = pygame.Rect(self.pos[0] + 16, self.pos[1], 112, 128)
            self.wide_rect = pygame.Rect(self.pos[0] - 8, self.pos[1] - 8, 128, 128)
            self.dir = 0
            self.speed = 5
            self.anim_time = time.time()
            self.vel = [0, 0]
            self.mask = pygame.mask.from_surface(
                pygame.transform.flip(wizard_animations[self.frame[1]].get([self.frame[0], 0]), self.dir, False)
            )
            self.speed_effect = 0
            self.blit_surf = pygame.Surface((32 * 4, 36 * 4))
            self.angle = 0
            self.staff_pos = [0, 0]
            self.bullet_delay = time.time()
            self.bullet_repeat_time = 0.8
            self.b_pos = [0, 0]
            self.adjusted = False

        def update_animation(self):
            if time.time() - self.anim_time >= 0.1:
                self.frame[0] += 1

                try:
                    wizard_animations[self.frame[1]].get([self.frame[0], 0])

                except:
                    self.frame[0] = 0

                self.anim_time = time.time()

        def update(self):

            if not self.wide_rect.colliderect(player.wide_rect):
                self.angle = angle_between((self.pos, player.pos))
                self.vel = [self.speed * math.cos(math.radians(self.angle)), self.speed * math.sin(math.radians(self.angle))]

                for wizard in wizards[current_level]:
                    if wizard != self:
                        if self.rect.colliderect(wizard.rect):
                            if self.vel[0] > 0:
                                if wizard.rect.x > self.rect.x:
                                    self.vel[0] = 0

                            if self.vel[0] < 0:
                                if wizard.rect.x < self.rect.x:
                                    self.vel[0] = 0

                            if self.vel[1] > 0:
                                if wizard.rect.y > self.rect.y:
                                    self.vel[1] = 0

                            if self.vel[1] < 0:
                                if wizard.rect.y < self.rect.y:
                                    self.vel[1] = 0

                            break

                self.frame[1] = 1

            else:
                self.vel = [0, 0]
                self.frame[1] = 0
                self.angle = angle_between((self.pos, player.pos))
            try:
                wizard_animations[self.frame[1]].get([self.frame[0], 0])

            except:
                self.frame[0] = 0

            self.rect = pygame.Rect(
                self.pos[0],
                self.pos[1],
                wizard_animations[self.frame[1]].get([self.frame[0], 0]).get_width(),
                wizard_animations[self.frame[1]].get([self.frame[0], 0]).get_height(),
            )
            self.wide_rect = pygame.Rect(
                self.pos[0] - 32,
                self.pos[1] - 32,
                wizard_animations[self.frame[1]].get([self.frame[0], 0]).get_width() + 64,
                wizard_animations[self.frame[1]].get([self.frame[0], 0]).get_height() + 64,
            )

            img = pygame.transform.flip(wizard_animations[self.frame[1]].get([self.frame[0], 0]), self.dir, False)
            self.mask = pygame.mask.from_surface(img)

            staff_img = pygame.transform.rotate(staff, 290 - self.angle)
            staff_mask = pygame.mask.from_surface(staff_img)
            self.staff_pos = (
                self.pos[0] + (img.get_width() - staff_img.get_width()) / 2,
                self.pos[1] + (img.get_height() - staff_img.get_height()) / 2,
            )
            # staff_pos

            for j in range(0, staff_img.get_height(), 4):
                for i in range(0, staff_img.get_width(), 4):
                    if staff_img.get_at((i, j)).r == 240:
                        self.b_pos = [self.staff_pos[0] + i, self.staff_pos[1] + j]

            for crate_, rect in crates:
                if self.wide_rect.colliderect(rect):
                    if (rect.y - self.pos[1]) < 172 and (rect.y - self.pos[1]) > 48:
                        overlap_img = self.mask.overlap_mask(crate_mask, (rect.x - self.pos[0], rect.y - self.pos[1])).to_surface(
                            unsetcolor=(0, 0, 0, 0), setcolor=(255, 255, 255)
                        )
                        img.blit(overlap_img, (-4, 0))
                        img.blit(overlap_img, (0, -4))
                        img.blit(overlap_img, (0, 0))

                        overlap_img2 = staff_mask.overlap_mask(
                            crate_mask, (rect.x - self.staff_pos[0], rect.y - self.staff_pos[1])
                        ).to_surface(unsetcolor=(0, 0, 0, 0), setcolor=(255, 255, 255))
                        staff_img.blit(overlap_img2, (0, 0))

                if crate_mask.overlap(self.mask, (self.pos[0] - rect.x, self.pos[1] - rect.y)):
                    if (rect.y - self.rect.y) < 96 and (rect.y - self.rect.y) > 0:
                        if self.vel[1] > 0:
                            self.vel[1] = 0
                        if (rect.y - self.rect.y) < 72 and (rect.y - self.rect.y) > 0:
                            if self.vel[0] != 0:
                                if self.pos[0] - rect.x > 0:
                                    if self.vel[0] < 0:
                                        self.vel[0] = 0
                                if self.pos[0] - rect.x < 0:
                                    if self.vel[0] > 0:
                                        self.vel[0] = 0

                    if (self.rect.y - rect.y) < 16 and (self.rect.y - rect.y) > 0:
                        if self.vel[1] < 0:
                            self.vel[1] = 0

            if self.rect.colliderect(player.wide_rect):
                if (player.pos[1] - self.pos[1]) < 172 and (player.pos[1] - self.pos[1]) > 16:
                    overlap_img = self.mask.overlap_mask(
                        player.mask, (player.pos[0] - self.pos[0], player.pos[1] - self.pos[1])
                    ).to_surface(unsetcolor=(0, 0, 0, 0), setcolor=(255, 255, 255))
                    img.blit(overlap_img, (0, 0))

            swap_color(img, [255, 255, 255], [0, 0, 0])
            swap_color(staff_img, [255, 255, 255], [0, 0, 0])

            img.set_colorkey([0, 0, 0])
            staff_img.set_colorkey([0, 0, 0])

            win.blit(img, self.pos)
            win.blit(staff_img, self.staff_pos)

            global current_fps
            self.pos[0] += self.vel[0] * (60 / current_fps)
            self.pos[1] += self.vel[1] * (60 / current_fps)

            if time.time() - self.bullet_delay >= self.bullet_repeat_time and player.crate is None:
                self.bullet_delay = time.time()
                bullet_manager.add_bullet(
                    (pygame.Rect(self.b_pos[0], self.b_pos[1], 16, 12), angle_between((self.staff_pos, player.pos)))
                )

            self.update_animation()

    class Skeleton:
        def __init__(self, x, y):
            self.pos = [x, y]
            self.frame = [0, 0]
            self.rect = pygame.Rect(self.pos[0] + 16, self.pos[1], 112, 128)
            self.wide_rect = pygame.Rect(self.pos[0] - 8, self.pos[1] - 8, 128, 128)
            self.dir = 0
            self.speed = 5
            self.anim_time = time.time()
            self.vel = [0, 0]
            self.mask = pygame.mask.from_surface(
                pygame.transform.flip(skele_animations[self.frame[1]].get([self.frame[0], 0]), self.dir, False)
            )
            self.speed_effect = 0
            self.blit_surf = pygame.Surface((32 * 4, 36 * 4))
            self.angle = 0
            self.staff_pos = [0, 0]
            self.bullet_delay = time.time()
            self.bullet_repeat_time = 0.8
            self.b_pos = [0, 0]
            self.adjusted = False

        def update_animation(self):
            if time.time() - self.anim_time >= 0.1:
                self.frame[0] += 1

                try:
                    skele_animations[self.frame[1]].get([self.frame[0], 0])

                except:
                    self.frame[0] = 0

                self.anim_time = time.time()

        def update(self):

            if not self.wide_rect.colliderect(player.wide_rect):
                self.angle = angle_between((self.pos, player.pos))

                for wizard in wizards[current_level]:
                    if wizard != self:
                        if self.rect.colliderect(wizard.rect):
                            if self.vel[0] > 0:
                                if wizard.rect.x > self.rect.x:
                                    self.vel[0] = 0

                            if self.vel[0] < 0:
                                if wizard.rect.x < self.rect.x:
                                    self.vel[0] = 0

                            if self.vel[1] > 0:
                                if wizard.rect.y > self.rect.y:
                                    self.vel[1] = 0

                            if self.vel[1] < 0:
                                if wizard.rect.y < self.rect.y:
                                    self.vel[1] = 0

                            break

            else:
                self.vel = [0, 0]
                self.frame[1] = 0
                self.angle = angle_between((self.pos, player.pos))
            try:
                skele_animations[self.frame[1]].get([self.frame[0], 0])

            except:
                self.frame[0] = 0

            self.rect = pygame.Rect(
                self.pos[0],
                self.pos[1],
                skele_animations[self.frame[1]].get([self.frame[0], 0]).get_width(),
                skele_animations[self.frame[1]].get([self.frame[0], 0]).get_height(),
            )
            self.wide_rect = pygame.Rect(
                self.pos[0] - 32,
                self.pos[1] - 32,
                skele_animations[self.frame[1]].get([self.frame[0], 0]).get_width() + 64,
                skele_animations[self.frame[1]].get([self.frame[0], 0]).get_height() + 64,
            )

            img = pygame.transform.flip(skele_animations[self.frame[1]].get([self.frame[0], 0]), self.dir, False)
            self.mask = pygame.mask.from_surface(img)

            staff_img = pygame.transform.rotate(staff, 290 - self.angle)
            staff_mask = pygame.mask.from_surface(staff_img)
            self.staff_pos = (
                self.pos[0] + (img.get_width() - staff_img.get_width()) / 2,
                self.pos[1] + (img.get_height() - staff_img.get_height()) / 2,
            )
            # staff_pos

            for j in range(0, staff_img.get_height(), 4):
                for i in range(0, staff_img.get_width(), 4):
                    if staff_img.get_at((i, j)).r == 240:
                        self.b_pos = [self.staff_pos[0] + i, self.staff_pos[1] + j]

            for crate_, rect in crates:
                if self.wide_rect.colliderect(rect):
                    if (rect.y - self.pos[1]) < 172 and (rect.y - self.pos[1]) > 48:
                        overlap_img = self.mask.overlap_mask(crate_mask, (rect.x - self.pos[0], rect.y - self.pos[1])).to_surface(
                            unsetcolor=(0, 0, 0, 0), setcolor=(255, 255, 255)
                        )
                        img.blit(overlap_img, (-4, 0))
                        img.blit(overlap_img, (0, -4))
                        img.blit(overlap_img, (0, 0))

                        overlap_img2 = staff_mask.overlap_mask(
                            crate_mask, (rect.x - self.staff_pos[0], rect.y - self.staff_pos[1])
                        ).to_surface(unsetcolor=(0, 0, 0, 0), setcolor=(255, 255, 255))
                        staff_img.blit(overlap_img2, (0, 0))

                if crate_mask.overlap(self.mask, (self.pos[0] - rect.x, self.pos[1] - rect.y)):
                    if (rect.y - self.rect.y) < 96 and (rect.y - self.rect.y) > 0:
                        if self.vel[1] > 0:
                            self.vel[1] = 0
                        if (rect.y - self.rect.y) < 72 and (rect.y - self.rect.y) > 0:
                            if self.vel[0] != 0:
                                if self.pos[0] - rect.x > 0:
                                    if self.vel[0] < 0:
                                        self.vel[0] = 0
                                if self.pos[0] - rect.x < 0:
                                    if self.vel[0] > 0:
                                        self.vel[0] = 0

                    if (self.rect.y - rect.y) < 16 and (self.rect.y - rect.y) > 0:
                        if self.vel[1] < 0:
                            self.vel[1] = 0

            if self.rect.colliderect(player.wide_rect):
                if (player.pos[1] - self.pos[1]) < 172 and (player.pos[1] - self.pos[1]) > 16:
                    overlap_img = self.mask.overlap_mask(
                        player.mask, (player.pos[0] - self.pos[0], player.pos[1] - self.pos[1])
                    ).to_surface(unsetcolor=(0, 0, 0, 0), setcolor=(255, 255, 255))
                    img.blit(overlap_img, (0, 0))

            swap_color(img, [255, 255, 255], [0, 0, 0])
            swap_color(staff_img, [255, 255, 255], [0, 0, 0])

            img.set_colorkey([0, 0, 0])
            staff_img.set_colorkey([0, 0, 0])

            win.blit(img, self.pos)
            win.blit(staff_img, self.staff_pos)

            if time.time() - self.bullet_delay >= self.bullet_repeat_time and player.crate is None:
                self.bullet_delay = time.time()
                bullet_manager.add_bullet(
                    (pygame.Rect(self.b_pos[0], self.b_pos[1], 16, 12), angle_between((self.staff_pos, player.pos)))
                )

            self.update_animation()

    class BulletManager:
        def __init__(self):
            self.bullets = []
            self.bullet_sprite = scale_image(pygame.image.load("assets/sprites/bullet.png").convert())
            self.bullet_sprite.set_colorkey((0, 0, 0))
            self.bullet_mask = pygame.mask.from_surface(self.bullet_sprite)
            self.bullet_speed = 7

        def add_bullet(self, bullet):
            self.bullets.append(bullet)

        def update(self):
            global artifact
            global artifact_crate
            for bullet in self.bullets:
                if (
                    bullet[0].x < 0 - self.bullet_sprite.get_width()
                    or bullet[0].x > win.get_width()
                    or bullet[0].y < 0 - self.bullet_sprite.get_height()
                    or bullet[0].y > win.get_height()
                ):
                    self.bullets.remove(bullet)
                    continue

                if (
                    self.bullet_mask.overlap(player.mask, (player.pos[0] - bullet[0].x, player.pos[1] - bullet[0].y))
                    and player.crate == None
                ):
                    self.bullets.remove(bullet)
                    player.health -= 25
                    player.damange_jitter_timer = time.time()
                    if not music_player.player_hurt_channel.get_busy():
                        music_player.player_hurt_channel.play(music_player.hurt_sound)
                    continue

                c = 0
                for crate_, rect in crates:
                    if bullet[0].colliderect(rect):
                        self.bullets.remove(bullet)
                        if player.crate != None:
                            if c == player.crate:
                                player.crate = None
                            else:
                                if c < player.crate:
                                    player.crate -= 1
                        if artifact is None:
                            current_crate_coord = [
                                int((crates[c][1].x + level_adjustments[current_level][0]) / crate.get_width()),
                                int((crates[c][1].y + level_adjustments[current_level][1]) / crate.get_height()),
                            ]

                            if player.alive and not player.has_artifact:
                                if potions[current_level][current_crate_coord[1]][current_crate_coord[0]] == 7:
                                    artifact = pygame.Rect(
                                        rect.x + key.get_width() / 2,
                                        rect.y + key.get_height() / 3,
                                        key.get_width(),
                                        key.get_height(),
                                    )

                        crates.pop(c)
                        explosions.append([(rect.x + crate.get_width() / 2, rect.y + crate.get_height() / 2), 0, time.time()])
                    
                        break
                    c += 1
                win.blit(pygame.transform.rotate(self.bullet_sprite, 360 - bullet[1]), (bullet[0].x, bullet[0].y))

                global current_fps
                bullet[0].x += self.bullet_speed * math.cos(math.radians(bullet[1])) * (60 / current_fps)
                bullet[0].y += self.bullet_speed * math.sin(math.radians(bullet[1])) * (60 / current_fps)

    class MusicPlayer:
        def __init__(self):
            self.songs = ["assets/songs/lvl1.ogg", "assets/songs/lvl2.ogg", "assets/songs/lvl3.ogg", "assets/songs/lvl4.ogg", "assets/songs/lvl5.ogg", "assets/songs/title1.ogg"]

            self.title_songs = ["assets/songs/title1.ogg"]

            self.player_hurt_channel = pygame.mixer.Channel(1)
            self.hurt_sound = pygame.mixer.Sound("assets/sounds/hurt.ogg")

            self.crate_explode_channel = pygame.mixer.Channel(2)
            self.explode_sound = pygame.mixer.Sound("assets/sounds/crate-destruction.ogg")

            self.found_key_channel = pygame.mixer.Channel(2)
            self.found_key_sound = pygame.mixer.Sound("assets/sounds/found_item.ogg")

            self.potion_drink_channel = pygame.mixer.Channel(3)
            self.potion_sound = pygame.mixer.Sound("assets/sounds/drink.ogg")
            
            self.level_end_sfx = pygame.mixer.Channel(4)
            self.win_sound = pygame.mixer.Sound("assets/sounds/win.ogg")
            self.death_sound = pygame.mixer.Sound("assets/sounds/death.ogg")

        def update(self):
            global State

            if not pygame.mixer.music.get_busy():
                if State.current == 1:
                    fn = self.songs[current_level]
                else:
                    fn = self.title_songs[random.randint(0, len(self.title_songs) - 1)]
                    
                pygame.mixer.music.load(fn)
                pygame.mixer.music.play()

    class Video:
        def __init__(self, sheet, pos):
            self.sheet = sheet
            self.pos = pos
            self.frame = [0, 0]
            self.delay = time.time()
            self.delay_duration = 0.04

        def update(self):
            if time.time() - self.delay >= self.delay_duration:
                self.delay = time.time()
                self.frame[0] += 1
                if self.frame[0] > len(self.sheet.sheet[0]) - 1:
                    self.frame[0] = 0
            win.blit(self.sheet.get(self.frame), self.pos)

    crate_video = Video(
        SpriteSheet(pygame.image.load("assets/sprites/tutorial_gifs/enter_crate_tutorial_clip.png"), [48, 1]), [512, 600]
    )

    esc_video = Video(
        SpriteSheet(scale_image(pygame.image.load("assets/sprites/tutorial_gifs/escape_tutorial_clip.png"), 1.75), [47, 1]),
        [512, 600],
    )
    esc_video.sheet.sheet[0] = esc_video.sheet.sheet[0][:38]
    esc_video.delay_duration = 0.065

    music_player = MusicPlayer()

    bullet_manager = BulletManager()

    crate = scale_image(pygame.image.load("assets/sprites/crate.png").convert())
    crate.set_colorkey([255, 255, 255])
    crate_mask = pygame.mask.from_surface(crate)

    crate_explosion = SpriteSheet(
        scale_image(pygame.image.load("assets/sprites/crate_explosion.png").convert()), (6, 1), (255, 255, 255)
    )

    explosions = []

    knight_animations = [
        SpriteSheet(scale_image(pygame.image.load("assets/sprites/Knight/Idle/Idle-Sheet.png").convert()), [4, 1], [255, 255, 255]),
        SpriteSheet(scale_image(pygame.image.load("assets/sprites/Knight/Run/Run-Sheet.png").convert()), [6, 1], [255, 255, 255]),
        SpriteSheet(
            scale_image(pygame.image.load("assets/sprites/Knight/Death/Death-Sheet.png").convert()), [6, 1], [255, 255, 255]
        ),
    ]
    dyed_knight_animations = [
        [dye(img, [255, 0, 0], [255, 255, 255], 72) for img in spritesheet.sheet[0]] for spritesheet in knight_animations
    ]
    wizard_animations = [
        SpriteSheet(scale_image(pygame.image.load("assets/sprites/Wizard/Idle/Idle-Sheet.png").convert()), [4, 1], [255, 255, 255]),
        SpriteSheet(scale_image(pygame.image.load("assets/sprites/Wizard/Run/Run-Sheet.png").convert()), [6, 1], [255, 255, 255]),
        SpriteSheet(
            scale_image(pygame.image.load("assets/sprites/Wizard/Death/Death-Sheet.png").convert()), [6, 1], [255, 255, 255]
        ),
    ]
    skele_animations = [
        SpriteSheet(
            scale_image(pygame.image.load("assets/sprites/Skeleton/Idle/Idle-Sheet.png").convert()), [4, 1], [255, 255, 255]
        ),
        SpriteSheet(scale_image(pygame.image.load("assets/sprites/Skeleton/Run/Run-Sheet.png").convert()), [6, 1], [255, 255, 255]),
        SpriteSheet(
            scale_image(pygame.image.load("assets/sprites/Skeleton/Death/Death-Sheet.png").convert()), [6, 1], [255, 255, 255]
        ),
    ]

    # animation_index = {"idle":0, "run":1, "death":2}
    global notifications
    notifications = []

    global level_adjustments
    level_adjustments = [
        [3 * crate.get_width(), 5 * crate.get_height() - 64],
        [3 * crate.get_width(), 5 * crate.get_height() - 64],
        [3 * crate.get_width(), 5 * crate.get_height() - 64],
        [3 * crate.get_width(), 5 * crate.get_height() - 64],
        [3 * crate.get_width(), 5 * crate.get_height() - 64],
        [3 * crate.get_width(), 5 * crate.get_height() - 64],
    ]

    global player
    player = Player()

    wizards = [
        [Wizard(14 * 64, 8 * 64)],
        [Wizard(15 * 64, 7 * 64), Wizard(15 * 64, 11 * 64)],
        [Wizard(12 * 64, 4 * 64), Skeleton(20 * 64, 11 * 64), Skeleton(9 * 64, 8 * 64), Skeleton(20 * 64, 4 * 64)],
        [Skeleton(21 * 64, 4.5 * 64), Skeleton(7 * 64, 4.5 * 64), Skeleton(21 * 64, 11 * 64), Skeleton(7 * 64, 11 * 64)],
        [Skeleton(21 * 64, 4.5 * 64), Skeleton(7 * 64, 4.5 * 64), Skeleton(21 * 64, 11 * 64), Skeleton(7 * 64, 11 * 64)],
        []
    ]

    above_player = []
    below_player = []

    levels = [
        load_level("assets/maps/csv/crates_lvl_1.csv"),
        load_level("assets/maps/csv/crates_lvl_2.csv"),
        load_level("assets/maps/csv/crates_lvl_3.csv"),
        load_level("assets/maps/csv/crates_lvl_4.csv"),
        load_level("assets/maps/csv/crates_lvl_5.csv"),
        load_level("assets/maps/csv/crates_lvl_6.csv"),
    ]
    potions = [[], [], [], [], [], []]

    crates = []

    global current_level
    current_level = 0

    key_coords = [random.randint(0, len(levels[current_level][0]) - 1), random.randint(0, len(levels[current_level]) - 1)]
    while levels[current_level][key_coords[1]][key_coords[0]] != 1 and current_level != 5:
        key_coords = [random.randint(0, len(levels[current_level][0]) - 1), random.randint(0, len(levels[current_level]) - 1)]

    for i, row in enumerate(levels[current_level]):

        potions[current_level].append([])

        for j, tile in enumerate(row):

            if tile == 1:
                potions[current_level][i].append(random.randint(1, 6))

                if key_coords[0] == j and key_coords[1] == i:
                    potions[current_level][i][j] = 7

                crates.append(
                    [
                        (
                            j * crate.get_width() - level_adjustments[current_level][0],
                            i * crate.get_height() - level_adjustments[current_level][1],
                        ),
                        pygame.Rect(
                            j * crate.get_width() + 4 - level_adjustments[current_level][0],
                            i * crate.get_height() + 4 - level_adjustments[current_level][1],
                            crate.get_width() - 8,
                            crate.get_height() - 8,
                        ),
                    ]
                )
            else:
                potions[current_level][i].append(0)

    global artifact_crate
    artifact_crate = random.randint(0, len(crates))

    key = scale_image(pygame.image.load("assets/sprites/key.png").convert())
    key.set_colorkey((255, 255, 255))

    global artifact
    artifact = None

    global ctrl_pressed
    ctrl_pressed = False

    potion_sprites = [
        scale_image(pygame.image.load("assets/sprites/Potions/speed.png").convert()),
        scale_image(pygame.image.load("assets/sprites/Potions/air.png").convert()),
        scale_image(pygame.image.load("assets/sprites/Potions/health.png").convert()),
    ]

    potion_sprites[0].set_colorkey([255, 255, 255])
    potion_sprites[1].set_colorkey([255, 255, 255])
    potion_sprites[2].set_colorkey([255, 255, 255])

    bg = scale_image(pygame.image.load("assets/maps/png/level_1.png").convert())

    inv_font = pygame.font.Font("assets/font/yoster.ttf", 20)
    above_inv_font = pygame.font.Font("assets/font/yoster.ttf", 24)
    ui_font = pygame.font.Font("assets/font/yoster.ttf", 28)
    tutorial_font = pygame.font.Font("assets/font/yoster.ttf", 40)
    big_font = pygame.font.Font("assets/font/yoster.ttf", 64)

    health_text = ui_font.render("HEALTH", False, [255, 255, 255], [0, 0, 0])
    health_text.set_colorkey([0, 0, 0])

    air_text = ui_font.render("AIR", False, [255, 255, 255], [0, 0, 0])
    air_text.set_colorkey([0, 0, 0])

    suffocation_warning = ui_font.render("YOU ARE SUFFOCATING!", False, [255, 255, 255], [0, 0, 0])
    suffocation_warning.set_colorkey([0, 0, 0])

    key_notification = ui_font.render("FOUND KEY!", False, [255, 255, 255], [0, 0, 0])
    key_notification.set_colorkey([0, 0, 0])

    death_text = big_font.render("YOU DIED!", False, [255, 255, 255], [0, 0, 0])
    death_text.set_colorkey([0, 0, 0])

    win_text = big_font.render("YOU WIN!", False, [255, 255, 255], [0, 0, 0])
    win_text.set_colorkey([0, 0, 0])

    speed_potion_text = above_inv_font.render("5 Sec Speed Boost Potion", False, [255, 255, 255], [0, 0, 0])
    speed_potion_text.set_colorkey([0, 0, 0])

    air_potion_text = above_inv_font.render("Air Refill Potion", False, [255, 255, 255], [0, 0, 0])
    air_potion_text.set_colorkey([0, 0, 0])

    health_potion_text = above_inv_font.render("Health Potion", False, [255, 255, 255], [0, 0, 0])
    health_potion_text.set_colorkey([0, 0, 0])

    key_slot_text = above_inv_font.render("Key", False, [255, 255, 255], [0, 0, 0])
    key_slot_text.set_colorkey([0, 0, 0])

    win_rects = [
        pygame.Rect(1784, 0, 152, 196),
        pygame.Rect(1784, 0, 152, 196),
        pygame.Rect(1784, 0, 152, 196),
        pygame.Rect(1784, 0, 152, 196),
        pygame.Rect(1784, 0, 152, 196),
        pygame.Rect(1784, 0, 152, 196),
    ]

    tutorial_tiles = [
        pygame.image.load("assets/sprites/tutorial/slide1.png").convert(),
        pygame.image.load("assets/sprites/tutorial/slide2.png").convert(),
        pygame.image.load("assets/sprites/tutorial/slide3.png").convert(),
        pygame.image.load("assets/sprites/tutorial/slide4.png").convert(),
    ]

    tutorial_tile_indicators = [
        tutorial_font.render("Slide 1 out of 4", False, [255, 255, 255], [0, 0, 0]),
        tutorial_font.render("Slide 2 out of 4", False, [255, 255, 255], [0, 0, 0]),
        tutorial_font.render("Slide 3 out of 4", False, [255, 255, 255], [0, 0, 0]),
        tutorial_font.render("Slide 4 out of 4", False, [255, 255, 255], [0, 0, 0]),
    ]

    global current_tile
    current_tile = 0

    right_arrow_button_spritesheet = SpriteSheet(
        scale_image(pygame.image.load("assets/sprites/right_arrow_buttons.png").convert()), [2, 1], [255, 255, 255]
    )
    left_arrow_button_spritesheet = SpriteSheet(
        scale_image(pygame.image.load("assets/sprites/left_arrow_buttons.png").convert()), [2, 1], [255, 255, 255]
    )

    def tutorial_forward_function():
        global current_tile
        if current_tile < 3:
            current_tile += 1

    def tutorial_backward_function():
        global current_tile
        if current_tile > 0:
            current_tile -= 1

    tutorial_forward_button = Button([1200, 32], right_arrow_button_spritesheet.sheet[0], tutorial_forward_function)

    tutorial_behind_button = Button([662, 32], left_arrow_button_spritesheet.sheet[0], tutorial_backward_function)

    tutorial_to_menu_button = Button([(win.get_width() - button_spritesheet.size[0]) / 2, 100], button_spritesheet.sheet[0], menu2)
    credits_to_menu_button = Button([(win.get_width() - button_spritesheet.size[0]) / 2, 790], button_spritesheet.sheet[0], menu2)

    menu_text = title_screen_font.render("Menu", False, [255, 255, 255], [0, 0, 0])
    menu_text.set_colorkey([0, 0, 0])
    
    global music_slider
    music_slider = Slider((368 + (256-health_text.get_width())/2, 8))
    music_slider.value = 0.3
    
    music_text = ui_font.render("Music: ", False, [255, 255, 255], [0, 0, 0])
    music_text.set_colorkey([0, 0, 0])

    global screenshot
    screenshot = None

    e_pressed = False
    dark_overlay_surf = pygame.Surface((win.get_width(), win.get_height()))
    dark_overlay_surf.fill([0, 0, 0])
    dark_overlay_surf.set_alpha(75)
    radius = 0
    
    current_key_scale = 1
    global zoom_factor
    zoom_factor = 1

    global current_fps
    current_fps = 60

    global State
    global transitioning

    State.on_change = music_player.update

    State.change(0)
    
    class OutlinedText(object):
        def __init__(
                self,
                text,
                position,
                outline_width,
                font_size,
                screen,
                foreground_color=(255, 255, 255),
                background_color=(0, 0, 0)
        ):

            self.text = text
            self.position = position
            self.foreground = foreground_color
            self.background = background_color
            self.outline_width = outline_width
            self.screen = screen
            self.font = pygame.font.Font("assets/font/yoster.ttf", font_size)
            self.text_surface = self.font.render(self.text, True, self.foreground)
            self.text_outline_surface = self.font.render(self.text, True, self.background)
            # There is no good way to get an outline with pygame, so we draw
            # the text at 8 points around the main text to simulate an outline.
            self.directions = [
                (self.outline_width, self.outline_width),
                (0, self.outline_width),
                (-self.outline_width, self.outline_width),
                (self.outline_width, 0),
                (-self.outline_width, 0),
                (self.outline_width, -self.outline_width),
                (0, -self.outline_width),
                (-self.outline_width, -self.outline_width)
            ]

        def get_width(self):

            return self.text_surface.get_width() + self.outline_width * 2
        
        def get_height(self):

            return self.text_surface.get_height() + self.outline_width * 2

        def change_position(self, position):

            self.position = position

        def change_text(self, text):

            self.text = text
            self._update_text()

        def change_foreground_color(self, color):

            self.foreground = color
            self._update_text()

        def change_outline_color(self, color):

            self.background = color
            self._update_text()

        def _update_text(self):

            self.text_surface = self.font.render(self.text, True, self.foreground)
            self.text_outline_surface = self.font.render(self.text, True, self.background)

        def draw(self):
            # blit outline images to screen
            for direction in self.directions:
                self.screen.blit(
                    self.text_outline_surface,
                    (
                        self.position[0] - direction[0],
                        self.position[1] - direction[1]
                    )
                )
            # blit foreground image to the screen
            self.screen.blit(self.text_surface, self.position)
    
    game_title = OutlinedText("Castle 51", (100, 100), 6, 56, win)
    game_title.position = [(win.get_width() - game_title.get_width())/2, (win.get_height() - game_title.get_height())/2 - 64]
    
    credits_screen = pygame.image.load("assets/sprites/credits.png").convert()
    victory_screen = scale_image(pygame.image.load("assets/maps/png/victory.png").convert())

    while True:
        if not player.alive:
            if screenshot is None:
                screenshot = win.copy()

        win.fill([0, 0, 0])
        win.blit(bg, [0, 0])
        
        clock.tick(240)

        current_fps = clock.get_fps()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        if State.current == 1:
            
            if current_level == 5:
                win.blit(victory_screen, [0, 0])
                credits_to_menu_button.update()
                win.blit(menu_text, [(win.get_width() - menu_text.get_width()) / 2, 806 + credits_to_menu_button.current * 4])
            
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
                # pygame.draw.rect(win, [255, 0, 0], rect)
                if rect.colliderect(player.wide_rect):
                    if rect.y < player.true_rect.y:
                        below_player.append(count)
                    else:
                        above_player.append(count)

                    if (rect.y + rect.h) < (player.true_rect.y + player.true_rect.h):
                        below_player.append(count)
                        if count in above_player:
                            above_player.remove(count)
                            
                    if rect.colliderect(player.rect):
                        if (pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]) and not ctrl_pressed:
                            ctrl_pressed = True
                            if player.crate == None:
                                player.crate = count

                                if (rect.y - player.rect.y) < 64 and (rect.y - player.rect.y) > 0:
                                    player.pos[1] = rect.y - 64

                        if (rect.y - player.rect.y) < 64 and (rect.y - player.rect.y) > 0:
                            if player.vel[1] > 0:
                                player.vel[1] = 0
                            if (rect.y - player.rect.y) < 48 and (rect.y - player.rect.y) > 0:
                                if player.vel[0] != 0:
                                    if player.pos[0] - rect.x > 0:
                                        if player.vel[0] < 0:
                                            player.vel[0] = 0
                                            player.pos[0] += 4
                                    if player.pos[0] - rect.x < 0:
                                        if player.vel[0] > 0:
                                            player.vel[0] = 0
                                            player.pos[0] -= 4

                        if (player.rect.y - rect.y) < 28 and (player.rect.y - rect.y) > 0:
                            if player.vel[1] < 0:
                                player.vel[1] = 0

                else:
                    below_player.append(count)

            for explosion in explosions:
                win.blit(
                    crate_explosion.get((explosion[1], 0)),
                    (explosion[0][0] - crate_explosion.size[1] / 2, explosion[0][1] - crate_explosion.size[0] / 2),
                )
                if time.time() - explosion[2] >= 0.05:
                    explosion[2] = time.time()
                    explosion[1] += 1
                    if explosion[1] > 5:
                        explosion[1] = 5

            if artifact != None:
                if not player.has_artifact:
                        
                    current_key_scale += 0.025*zoom_factor*(60/clock.get_fps())
                    if current_key_scale <= 0.8:
                        zoom_factor = 1
                    if current_key_scale >= 1.2:
                        zoom_factor = -1
                    
                    current_key_sprite = scale_image(key, current_key_scale)
                    win.blit(current_key_sprite, (artifact.x - current_key_sprite.get_width()/2, artifact.y - current_key_sprite.get_height()/2))
                    
                    if player.rect.colliderect(artifact) and (player.crate is None):
                        notifications.append(Notification(key_notification))
                        player.has_artifact = True
                        if not music_player.found_key_channel.get_busy():
                            music_player.found_key_channel.play(music_player.found_key_sound)

            for x in below_player:
                win.blit(crate, crates[x][0])

            if player.alive:
                player.render()

            for x in above_player:
                win.blit(crate, crates[x][0])

            if player.crate != None:
                pygame.draw.rect(win, [255, 255, 255], crates[player.crate][1], 4)

            for wizard in wizards[current_level]:
                wizard.update()

            air_notification = False
            for notification in notifications:

                for notification2 in notifications:
                    if notification2 != notification:
                        if notification2.rect.colliderect(notification.rect):
                            if notification.pos[1] > notification2.pos[1]:
                                notification.pos[1] += 32
                            else:
                                notification2.pos[1] += 32

                notification.update()
                if notification.surf == suffocation_warning:
                    air_notification = True
                if notification.alpha < 5:
                    notifications.remove(notification)

            if player.air < 30 and not air_notification and player.crate != None:
                notifications.append(Notification(suffocation_warning))

            pygame.draw.rect(win, [75, 75, 75], player.inventory_box, 4)
            pygame.draw.line(
                win,
                [75, 75, 75],
                [player.inventory_box.x + (1 * player.inventory_box.w / 4), player.inventory_box.y],
                [player.inventory_box.x + (1 * player.inventory_box.w / 4), player.inventory_box.y + player.inventory_box.h - 4],
                4,
            )
            pygame.draw.line(
                win,
                [75, 75, 75],
                [player.inventory_box.x + (2 * player.inventory_box.w / 4), player.inventory_box.y],
                [player.inventory_box.x + (2 * player.inventory_box.w / 4), player.inventory_box.y + player.inventory_box.h - 4],
                4,
            )
            pygame.draw.line(
                win,
                [75, 75, 75],
                [player.inventory_box.x + (3 * player.inventory_box.w / 4), player.inventory_box.y],
                [player.inventory_box.x + (3 * player.inventory_box.w / 4), player.inventory_box.y + player.inventory_box.h - 4],
                4,
            )

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
                win.blit(potion_sprites[1], [player.inventory_box.x + 16 + player.inventory_box.w / 4, player.inventory_box.y + 12])
                win.blit(air_potions_no, [player.inventory_box.x + 48 + player.inventory_box.w / 4, player.inventory_box.y + 44])

            if player.inventory["health_potions"] > 0:
                win.blit(potion_sprites[2], [player.inventory_box.x + 16 + player.inventory_box.w / 2, player.inventory_box.y + 12])
                win.blit(health_potions_no, [player.inventory_box.x + 48 + player.inventory_box.w / 2, player.inventory_box.y + 44])

            if player.has_artifact:
                win.blit(key, [player.inventory_box.x + 1 + player.inventory_box.w - key.get_width(), player.inventory_box.y + 0.5])

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
                            if not music_player.potion_drink_channel.get_busy():
                                music_player.potion_drink_channel.play(music_player.potion_sound)

                    if player.inv_no == 1:
                        if player.inventory["air_potions"] > 0:
                            player.inventory["air_potions"] -= 1
                            player.air += 33
                            if not music_player.potion_drink_channel.get_busy():
                                music_player.potion_drink_channel.play(music_player.potion_sound)
                                
                    if player.inv_no == 2:
                        if player.inventory["health_potions"] > 0:
                            player.inventory["health_potions"] -= 1
                            player.health += 33
                            if player.health > 100:
                                player.health = 100
                            if not music_player.potion_drink_channel.get_busy():
                                music_player.potion_drink_channel.play(music_player.potion_sound)
                            
                    e_pressed = True

            if not pygame.key.get_pressed()[pygame.K_e]:
                e_pressed = False

            bullet_manager.update()

            if player.inv_no == 0:
                if player.inventory["speed_potions"] > 0:
                    win.blit(
                        speed_potion_text,
                        [
                            player.inventory_box.x + (player.inventory_box.w - speed_potion_text.get_width()) / 2,
                            player.inventory_box.y - speed_potion_text.get_height() - 8,
                        ],
                    )

            elif player.inv_no == 1:
                if player.inventory["air_potions"] > 0:
                    win.blit(
                        air_potion_text,
                        [
                            player.inventory_box.x + (player.inventory_box.w - air_potion_text.get_width()) / 2,
                            player.inventory_box.y - air_potion_text.get_height() - 8,
                        ],
                    )

            elif player.inv_no == 2:
                if player.inventory["health_potions"] > 0:
                    win.blit(
                        health_potion_text,
                        [
                            player.inventory_box.x + (player.inventory_box.w - health_potion_text.get_width()) / 2,
                            player.inventory_box.y - health_potion_text.get_height() - 8,
                        ],
                    )

            elif player.inv_no == 3:
                if player.has_artifact:
                    win.blit(
                        key_slot_text,
                        [
                            player.inventory_box.x + (player.inventory_box.w - key_slot_text.get_width()) / 2,
                            player.inventory_box.y - key_slot_text.get_height() - 8,
                        ],
                    )

            pygame.draw.rect(
                win,
                [125, 125, 125],
                pygame.Rect(
                    player.inventory_box.x + (player.inv_no * player.inventory_box.w / 4),
                    player.inventory_box.y,
                    player.inventory_box.h,
                    player.inventory_box.h,
                ),
                4,
            )

            pygame.draw.rect(win, [75, 200, 75], pygame.Rect(692, 8, (player.health / 100) * 256, 28))
            pygame.draw.rect(win, [25, 100, 25], pygame.Rect(692, 8, 256, 28), 4)

            pygame.draw.rect(win, [75, 75, 200], pygame.Rect(964, 8, (player.air / 100) * 256, 28))
            pygame.draw.rect(win, [25, 25, 100], pygame.Rect(964, 8, 256, 28), 4)

            win.blit(health_text, [692 + (256 - health_text.get_width()) / 2, 8])
            win.blit(air_text, [964 + (256 - air_text.get_width()) / 2, 8])

            if player.rect.colliderect(win_rects[current_level]) and player.has_artifact:
                player.alive = False
                pygame.mixer.music.stop()
                player.win = True
                player.has_artifact = False
                current_level += 1
                music_player.level_end_sfx.play(music_player.win_sound)
                if current_level > len(levels) - 1:
                    current_level -= 1

            pause_button.update()
            
            music_slider.update()
            
            win.blit(music_text, (music_slider.pos[0] - music_text.get_width() + 8, 8))
            
            pygame.mixer.music.set_volume(music_slider.value)

            if not player.alive and screenshot is not None:
                win.blit(screenshot, [0, 0])
                win.blit(dark_overlay_surf, [0, 0])
                pygame.draw.circle(win, [0, 0, 0], [win.get_width() / 2, win.get_height() / 2], radius)
                radius += 15 * (60 / current_fps)

                if player.win:
                    win.blit(
                        win_text, [(win.get_width() - win_text.get_width()) / 2, (win.get_height() - win_text.get_height()) / 2]
                    )
                else:
                    if player.health <= 0 and not transitioning:
                        win.blit(
                            death_text,
                            [(win.get_width() - death_text.get_width()) / 2, (win.get_height() - death_text.get_height()) / 2],
                        )

                if radius > 1000:

                    radius = 0

                    screenshot = None

                    crates = []

                    explosions.clear()

                    notifications.clear()

                    player = Player()

                    wizards = [
                        [Wizard(14 * 64, 8 * 64)],
                        [Wizard(15 * 64, 7 * 64), Wizard(15 * 64, 11 * 64)],
                        [Wizard(12 * 64, 4 * 64), Skeleton(20 * 64, 11 * 64), Skeleton(9 * 64, 8 * 64), Skeleton(20 * 64, 4 * 64)],
                        [
                            Skeleton(21 * 64, 4.5 * 64),
                            Skeleton(7 * 64, 4.5 * 64),
                            Skeleton(21 * 64, 11 * 64),
                            Skeleton(7 * 64, 11 * 64),
                        ],
                        [
                            Wizard(15 * 64, 6.5 * 64),
                            Skeleton(21 * 64, 4.5 * 64),
                            Skeleton(7 * 64, 4.5 * 64),
                            Skeleton(21 * 64, 11 * 64),
                            Skeleton(7 * 64, 11 * 64),
                        ],
                        []
                    ]
                    
                    if current_level == 4:
                        player.inventory["health_potions"] = 1
                        player.inv_no = 2

                    bullet_manager.bullets.clear()

                    above_player = []
                    below_player = []

                    potions = [[], [], [], [], [], []]

                    crates = []

                    key_coords = [
                        random.randint(0, len(levels[current_level][0]) - 1),
                        random.randint(0, len(levels[current_level]) - 1),
                    ]
                    while levels[current_level][key_coords[1]][key_coords[0]] != 1 and current_level != 5:
                        key_coords = [
                            random.randint(0, len(levels[current_level][0]) - 1),
                            random.randint(0, len(levels[current_level]) - 1),
                        ]

                    for i, row in enumerate(levels[current_level]):

                        potions[current_level].append([])

                        for j, tile in enumerate(row):

                            if tile == 1:
                                potions[current_level][i].append(random.randint(1, 6))

                                if key_coords[0] == j and key_coords[1] == i:
                                    potions[current_level][i][j] = 7

                                crates.append(
                                    [
                                        (
                                            j * crate.get_width() - level_adjustments[current_level][0],
                                            i * crate.get_height() - level_adjustments[current_level][1],
                                        ),
                                        pygame.Rect(
                                            j * crate.get_width() + 4 - level_adjustments[current_level][0],
                                            i * crate.get_height() + 4 - level_adjustments[current_level][1],
                                            crate.get_width() - 8,
                                            crate.get_height() - 8,
                                        ),
                                    ]
                                )
                            else:
                                potions[current_level][i].append(0)

                    artifact = None
                    artifact_crate = random.randint(0, len(crates))
                    
                    if transitioning:
                        transitioning = False
                        State.change(0)

                    if State.current != 0:
                        pygame.mixer.music.stop()
                        music_player.update()
                    
                    continue
                        
            if pygame.key.get_pressed()[pygame.K_SPACE] and player.alive:
                State.change(2)
                screenshot = win.copy()
                pygame.mixer.music.stop()
                music_slider.pos = [escape_screen_buttons[0].pos[0] - 32, escape_screen_buttons[0].pos[1] - 64]
                music_slider.choice_rect = pygame.Rect(music_slider.pos[0], music_slider.pos[1] + 2, 16, 24)
                music_slider.choice_rect.x += (music_slider.value * music_slider.rect.w)
                

        elif State.current == 0:
            for count, button in enumerate(title_screen_buttons):
                button.update()
                win.blit(
                    title_screen_text[count][0],
                    [title_screen_text[count][1][0], title_screen_text[count][1][1] + button.current * 4],
                )

            game_title.draw()

        elif State.current == 2:

            win.blit(screenshot, [0, 0])
            win.blit(dark_overlay_surf, [0, 0])
            
            music_slider.update()
            
            win.blit(music_text, (music_slider.pos[0] - music_text.get_width() + 8, music_slider.pos[1]))

            for count, button in enumerate(escape_screen_buttons):
                button.update()
                win.blit(
                    escape_screen_text[count][0],
                    [escape_screen_text[count][1][0], escape_screen_text[count][1][1] + button.current * 4],
                )

        elif State.current == 3:

            win.blit(tutorial_tiles[current_tile], [0, 0])

            win.blit(
                tutorial_tile_indicators[current_tile],
                [(win.get_width() - tutorial_tile_indicators[current_tile].get_width()) / 2, 36],
            )

            tutorial_to_menu_button.update()
            win.blit(menu_text, [(win.get_width() - menu_text.get_width()) / 2, 116 + tutorial_to_menu_button.current * 4])

            if current_tile == 1:
                crate_video.update()

            if current_tile == 3:
                esc_video.update()

            tutorial_forward_button.update()
            tutorial_behind_button.update()
            
        elif State.current == 4:
            win.blit(credits_screen, [0, 0])
            credits_to_menu_button.update()
            win.blit(menu_text, [(win.get_width() - menu_text.get_width()) / 2, 806 + credits_to_menu_button.current * 4])
        # pygame.draw.rect(win, [255, 0, 0], win_rects[current_level])
        pygame.display.update()
        await asyncio.sleep(0)


asyncio.run(main())
