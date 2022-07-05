import pygame
import math
import time
import random


def format_number(num):
    if num < 1000:
        return num

    out = ""
    for i, val in enumerate((str(num)[::-1])):
        out += val
        if (i + 1) % 3 == 0 and i != len(str(num)) - 1:
            out += ","
    out = out[::-1]

    return out


def deg2rad(angle):
    pi = 3.14
    return angle * pi / 180


def increase_score_base():
    global score_base, base_cost, score
    score_base += 1
    score -= base_cost
    out = 3 * 1.15 ** score_base
    return int(out)


def increase_score_multiplier():
    global score_multiplier, multiplier_cost, score
    score_multiplier += 1
    score -= multiplier_cost
    out = 5 * 1.75 ** score_multiplier
    return int(out)


def increase_autoclicker():
    global autoclicker, autoclicker_cost, score
    autoclicker += 1
    score -= autoclicker_cost
    out = 50 * 2.15 ** autoclicker
    return int(out)


class Cookie:
    radius = 100
    # colour = (255, 255, 0)
    cookie_image = pygame.image.load("cookie.png")

    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)

        self.transform(self.radius * 2)
        self.grow_factor = 1.1
        self.is_scaled = False
        # min_chocolate_chips = 5
        # max_chocolate_chips = 10
        # self.chocolate_chips = [self.add_chocolate_chips() for i in
        #                         range(random.randint(min_chocolate_chips, max_chocolate_chips))]

    def transform(self, size):
        self.image = pygame.image.load("cookie.png")
        self.image = pygame.transform.scale(self.image, (int(size), int(size)))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.centering = pygame.Vector2(self.width / 2, self.height / 2)

    def add_chocolate_chips(self):
        direction = deg2rad(random.randint(0, 360))
        magnitude = random.randint(0, int(self.radius * 3 / 4))
        return pygame.Vector2(magnitude * math.cos(direction), magnitude * math.sin(direction))

    def is_touching_mouse_pointer(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if math.sqrt((self.position.x - mouse_x) ** 2 + (self.position.y - mouse_y) ** 2) <= self.radius:
            return True
        return False

    # def lighten(self):
    #     darken_percent = .50
    #     dark = pygame.Surface(self.image.get_size()).convert_alpha()
    #     dark.fill((0, 0, 0), darken_percent * 0)
    #     self.image.blit(dark, (0, 0))

    # def darken(self):
    # darken_percent = .50
    # dark = pygame.Surface(self.image.get_size()).convert_alpha()
    # dark.fill((0, 0, 0, darken_percent * 255))
    # self.image.blit(dark, (0, 0))
    # self.image.set_alpha(225)

    def update(self, delta, limit_x):
        if self.is_touching_mouse_pointer():
            self.transform(self.grow_factor * self.radius * 2)
            self.is_scaled = True
        elif self.is_scaled:
            self.transform(self.radius * 2)
            self.is_scaled = False

    def draw(self, surface):
        surface.blit(self.image, self.position - self.centering)

        # pygame.draw.circle(surface, self.colour, self.position, self.radius, width=0)

        # for chip in self.chocolate_chips:
        #     pygame.draw.circle(surface, (0, 0, 0), self.position + chip, self.radius / len(self.chocolate_chips),
        #                        width=0)


class FallingCookie(Cookie):
    radius = 40
    gravity = 5

    def __init__(self):
        temp = self.reset()
        super().__init__(temp[0], temp[1])

    def reset(self):
        return pygame.Vector2(random.randint(self.radius, SCREEN_WIDTH - self.radius),
                              -random.randint(0, SCREEN_HEIGHT * 2) - self.radius)

    def update(self, delta, limit_x):
        self.position.y += self.gravity * delta / 50
        if self.position.y - self.radius > SCREEN_HEIGHT:
            self.position = self.reset()
        if self.position.x <= limit_x + self.radius + Rectangle.horizontal_padding:
            self.position = self.reset()


class CPSCounter:
    click_counter = 0
    clicks = []
    start_time = time.time()
    cps = 0
    highest_cps = 0

    def __init__(self):
        self.cps_label_text = [f"CPS: {self.cps}"]
        self.cps_label = Label(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + Cookie.radius + Label.vertical_padding,
                               self.cps_label_text, 25, text_colour=(20, 20, 20))

    def add_click(self):
        self.clicks.append(time.time() - self.start_time)
        self.clear_clicks()

    def clear_clicks(self):
        del_counter = 0
        latest = self.clicks[-1]
        for pos, val in enumerate(self.clicks):
            if latest - val > 1:
                del self.clicks[pos - del_counter]
                del_counter += 1
            else:
                break

    @staticmethod
    def find_range(lis):  # lis for list input
        if len(lis) > 0:
            return lis[-1] - lis[0]
        else:
            return 0

    def update(self, delta):
        self.cps = len(self.clicks)
        self.highest_cps = max(self.highest_cps, self.cps)
        for i in range(len(self.clicks)):
            if self.find_range(self.clicks) > 1 or (
                    self.cps > 0 and time.time() - self.start_time - self.clicks[-1] > 1):
                del self.clicks[0]
            else:
                break
        self.cps_label_text = [f"CPS: {self.cps}"]
        self.cps_label.update(delta, self.cps_label_text)

    def draw(self, surface):
        self.cps_label.draw(surface)


class Label:
    horizontal_padding = 5
    vertical_padding = 5
    outline_thickness = 2

    def __init__(self, x, y, text, font_size, text_colour=(0, 0, 0), antialias=True, fill_colour=(150, 150, 150),
                 outline_colour=(0, 0, 0)):
        self.position = pygame.Vector2(x, y)
        self.font = pygame.font.Font("MontserratBlack-ZVK6J.otf", font_size)
        self.text_colour = text_colour
        self.antialias = antialias
        self.fill_colour = fill_colour
        self.outline_colour = outline_colour
        self.text, self.width, self.height = self.create_text(text)
        self.centering = pygame.Vector2(0, 0)

    def create_text(self, text):
        out = []
        max_width = 0
        max_height = 0
        for line in text:
            text_surface = self.font.render(line, self.antialias, self.text_colour)
            width = text_surface.get_width()
            height = text_surface.get_height()
            out.append((text_surface, width, height))
            max_width = max(max_width, width)
            max_height += height
        return out, max_width, max_height

    def update(self, delta, new_text=None, x=None, y=None, width=None, height=None, colour=None):
        if new_text is not None:
            self.text, self.width, self.height = self.create_text(new_text)
        if x is not None:
            self.position.x = x
        if y is not None:
            self.position.y = y
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if colour is not None:
            self.fill_colour = colour

    def draw(self, surface, centered_x=True, centered_y=True, outlined=False, filled=False):
        if centered_x:
            self.centering.x = self.width / 2
        if centered_y:
            self.centering.y = self.height / 2
        if filled:
            r = pygame.Rect(
                self.position - pygame.Vector2(self.horizontal_padding, self.vertical_padding) - self.centering,
                pygame.Vector2(self.width + 2 * self.horizontal_padding,
                               self.height + self.vertical_padding * 2))
            pygame.draw.rect(surface, self.fill_colour, r)
        if outlined:
            r = pygame.Rect(
                self.position - pygame.Vector2(self.horizontal_padding, self.vertical_padding) - self.centering,
                pygame.Vector2(self.width + 2 * self.horizontal_padding,
                               self.height + self.vertical_padding * 2))
            pygame.draw.rect(surface, self.outline_colour, r, self.outline_thickness)

        prev_height = 0
        for line in self.text:
            text_surface, width, height = line
            surface.blit(text_surface, self.position - self.centering + pygame.Vector2(0, prev_height))
            prev_height += height


class Button(Label):

    def __init__(self, x, y, text, font_size, text_colour=(0, 0, 0), antialias=True, fill_color=(150, 150, 150),
                 outline_colour=(0, 0, 0)):
        super().__init__(x, y, text, font_size, text_colour=text_colour, antialias=antialias, fill_colour=fill_color,
                         outline_colour=outline_colour)

    def is_touching_mouse_pointer(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if (self.position.x - self.centering.x <= mouse_x <= self.position.x + self.width - self.centering.x
                and self.position.y - self.centering.y <= mouse_y <= self.position.y + self.height - self.centering.y):
            return True
        return False

    def lighten(self):
        self.fill_colour = (100, 100, 100)

    def darken(self):
        self.fill_colour = (150, 150, 150)

    def update(self, delta, new_text=None, x=None, y=None, width=None, height=None, colour=None):
        super().update(delta, new_text=new_text, x=x, y=y, width=width, height=height, colour=colour)
        if self.is_touching_mouse_pointer():
            self.lighten()
        else:
            self.darken()

    def run_function(self, function):
        return function()


class Rectangle:
    horizontal_padding = 12
    vertical_padding = 12
    outline_colour = (40, 40, 40)
    outline_thickness = 5

    def __init__(self, x, y, width, height, colour):
        self.position = pygame.Vector2(x, y)
        self.width = width
        self.height = height
        self.fill_colour = colour
        self.centering = pygame.Vector2(0, 0)

    def update(self, x=None, y=None, width=None, height=None, colour=None):
        if x is not None:
            self.position.x = x
        if y is not None:
            self.position.y = y
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if colour is not None:
            self.fill_colour = colour

    def draw(self, surface, centered_x=True, centered_y=True, outlined=True):
        if centered_x:
            self.centering.x = self.width / 2
        if centered_y:
            self.centering.y = self.height / 2
        if outlined:
            r = pygame.Rect(
                self.position - pygame.Vector2(self.horizontal_padding, self.vertical_padding) - self.centering,
                pygame.Vector2(self.width + 2 * self.horizontal_padding,
                               self.height + self.vertical_padding))
            pygame.draw.rect(surface, self.outline_colour, r, self.outline_thickness)
        r = pygame.Rect(self.position - pygame.Vector2(self.horizontal_padding, self.vertical_padding) - self.centering,
                        pygame.Vector2(self.width + 2 * self.horizontal_padding, self.height + self.vertical_padding))
        pygame.draw.rect(surface, self.fill_colour, r)


pygame.init()

SCREEN_HEIGHT = 820
SCREEN_WIDTH = 1260
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cookie Clicker")
icon = pygame.transform.scale(Cookie.cookie_image, (32, 32))
pygame.display.set_icon(icon)
cookie = Cookie(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
score = 0
score_multiplier = 1
multiplier_cost = 10
score_base = 1
base_cost = 1
autoclicker = 0
autoclicker_cost = 100
autoclicker_delay_MS = 1000
autoclick_event = pygame.USEREVENT
pygame.time.set_timer(autoclick_event, autoclicker_delay_MS)

score_label_text = [f"Cookies:: {score}"]
score_label = Label(Label.horizontal_padding, 0, score_label_text, 24, text_colour=(0, 0, 0))

cookies_per_click = 1
cookies_per_click_label_text = [f"{cookies_per_click} cookies per click"]
cookies_per_click_label = Label(Label.horizontal_padding, score_label.height + Label.vertical_padding,
                                cookies_per_click_label_text, 17, text_colour=(95, 96, 102))
cookies_per_second = 0
cookies_per_second_label_text = [f"{cookies_per_second} cookies per second"]
cookies_per_second_label = Label(Label.horizontal_padding,
                                 score_label.height + cookies_per_click_label.height + Label.vertical_padding * 2,
                                 cookies_per_second_label_text, 17, text_colour=(95, 96, 102))

title_label_text = ["Cookie Clicker"]
title_label = Label(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - Cookie.radius - Label.vertical_padding * 2 - 50,
                    title_label_text, 50)

subtitle_label_text = ["–BETTER EDITION–"]
subtitle_label = Label(SCREEN_WIDTH / 2,
                       SCREEN_HEIGHT / 2 - Cookie.radius - Label.vertical_padding * 2 - 50 + title_label.height / 2,
                       subtitle_label_text, 20, text_colour=(74, 76, 82))

base_cost_button_text = [f"Base Cookies Per Click: {score_base}", f"Cost to upgrade: {base_cost}"]
base_cost_button = Button(Label.horizontal_padding * 2, SCREEN_HEIGHT / 2, base_cost_button_text, 16,
                          fill_color=(94, 131, 214), text_colour=(10, 10, 10), outline_colour=(50, 50, 50))

multiplier_cost_button_text = [f"Cookie Multiplier: {score_multiplier}", f"Cost to upgrade: {multiplier_cost}"]
multiplier_cost_button = Button(Label.horizontal_padding * 2,
                                SCREEN_HEIGHT / 2 + base_cost_button.height + Label.vertical_padding * 2 + Label.outline_thickness * 2,
                                multiplier_cost_button_text, 16, fill_color=(94, 131, 214), text_colour=(10, 10, 10),
                                outline_colour=(50, 50, 50))

autoclicker_cost_button_text = [f"Autoclickers: {autoclicker}", f"Cost to upgrade: {autoclicker_cost}"]
autoclicker_cost_button = Button(Label.horizontal_padding * 2,
                                 SCREEN_HEIGHT / 2 + base_cost_button.height + multiplier_cost_button.height + Label.vertical_padding * 4 + Label.outline_thickness * 4,
                                 autoclicker_cost_button_text, 16, fill_color=(94, 131, 214), text_colour=(10, 10, 10),
                                 outline_colour=(50, 50, 50))

shop_title_label_text = ["Shop"]
shop_title_label = Label(Label.horizontal_padding * 2,
                         SCREEN_HEIGHT / 2 - base_cost_button.height / 2 - Label.vertical_padding * 4 - Label.outline_thickness * 4,
                         shop_title_label_text, 25, text_colour=(44, 46, 52))
shop_items = [base_cost_button.width, multiplier_cost_button.width, autoclicker_cost_button.width, score_label.width,
              cookies_per_click_label.width, cookies_per_second_label.width, 250]
shop_limit = max(shop_items) + 2 * Label.horizontal_padding
shop = Rectangle(0, 0, shop_limit, SCREEN_HEIGHT, (150, 179, 242))

total_shop_height = (
                                SCREEN_HEIGHT / 2 + base_cost_button.height + multiplier_cost_button.height + Label.vertical_padding * 4 + Label.outline_thickness * 4 + (
                                    autoclicker_cost_button.height / 2 + Label.vertical_padding + Label.outline_thickness)) - (
                                SCREEN_HEIGHT / 2 - base_cost_button.height / 2 - Label.vertical_padding * 4 - Label.outline_thickness * 4 - shop_title_label.height / 2 - Label.vertical_padding - Label.outline_thickness)
shop_y_offset = total_shop_height / 2 - 32.5  # too lazy to find the right way to do this
base_cost_button.update(0, y=base_cost_button.position.y - shop_y_offset + base_cost_button.height / 2)
multiplier_cost_button.update(0,
                              y=multiplier_cost_button.position.y - shop_y_offset + multiplier_cost_button.height / 2)
autoclicker_cost_button.update(0,
                               y=autoclicker_cost_button.position.y - shop_y_offset + autoclicker_cost_button.height / 2)
shop_title_label.update(0, y=shop_title_label.position.y - shop_y_offset + shop_title_label.height / 2)

num_falling_cookies = 15
falling_cookies = [FallingCookie() for i in range(num_falling_cookies)]
falling_cookie_multiplier = 2

click_effects = []

C = CPSCounter()

fps_cap = 60
fps_display_iteration = 0
fps_display_refresh_rate = 60  # every this number frames it refreshes
fps = fps_cap

clock = pygame.time.Clock()
delta = 1
background_colour = (134, 161, 219)

fps_label_text = [f"FPS: {fps}"]
fps_label = Label(0, Label.vertical_padding, fps_label_text, 24, text_colour=(0, 0, 0))

is_running = True
while is_running:

    screen.fill(background_colour)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if cookie.is_touching_mouse_pointer():
                score += score_base * score_multiplier
                C.add_click()
                click_effects.append(
                    Label(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], [f"+{score_base * score_multiplier}"],
                          17, text_colour=(10, 10, 10)))
            for c in falling_cookies:
                if c.is_touching_mouse_pointer():
                    c.position = c.reset()
                    score += score_base * score_multiplier * falling_cookie_multiplier
                    C.add_click()
                    click_effects.append(Label(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1],
                                               [f"+{score_base * score_multiplier * falling_cookie_multiplier}"], 20,
                                               text_colour=(10, 10, 10)))

            if base_cost_button.is_touching_mouse_pointer() and score >= base_cost:
                click_effects.append(Label(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1],
                                           [f"-{base_cost}"], 20, text_colour=(70, 70, 70)))
                base_cost = base_cost_button.run_function(increase_score_base)
            elif multiplier_cost_button.is_touching_mouse_pointer() and score >= multiplier_cost:
                click_effects.append(Label(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1],
                                           [f"-{base_cost}"], 20, text_colour=(70, 70, 70)))
                multiplier_cost = multiplier_cost_button.run_function(increase_score_multiplier)
            elif autoclicker_cost_button.is_touching_mouse_pointer() and score >= autoclicker_cost:
                click_effects.append(Label(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1],
                                           [f"-{base_cost}"], 20, text_colour=(70, 70, 70)))
                autoclicker_cost = autoclicker_cost_button.run_function(increase_autoclicker)
        elif event.type == autoclick_event:
            score += score_base * score_multiplier * autoclicker
            if autoclicker > 0:
                click_effects.append(Label(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1],
                                           [f"+{score_base * score_multiplier * autoclicker}"], 25,
                                           text_colour=(25, 25, 25)))
    fps_display_iteration += 1
    if fps_display_iteration % fps_display_refresh_rate == 0:
        fps = min(1000 // delta, fps_cap)

        fps_display_iteration %= fps_display_refresh_rate
    fps_label_text = [f"FPS: {format_number(fps)}"]
    fps_label.update(delta, fps_label_text, x=SCREEN_WIDTH - (Label.horizontal_padding * 2 + fps_label.width))
    fps_label.draw(screen, centered_x=False, centered_y=False)

    shop_items = [base_cost_button.width, multiplier_cost_button.width, autoclicker_cost_button.width,
                  score_label.width, cookies_per_click_label.width, cookies_per_second_label.width, 250]
    shop_limit = max(shop_items) + 2 * Label.horizontal_padding
    shop.update(width=shop_limit)
    shop.draw(screen, centered_x=False, centered_y=False)

    score_label_text = [f"Cookies: {format_number(score)}"]
    score_label.update(delta, score_label_text)
    score_label.draw(screen, centered_x=False, centered_y=False)

    cookies_per_click = score_base * score_multiplier
    if cookies_per_click != 1:
        cookies_per_click_label_text = [f"{format_number(cookies_per_click)} cookies per click"]
    else:
        cookies_per_click_label_text = [f"{format_number(cookies_per_click)} cookie per click"]
    cookies_per_click_label.update(delta, cookies_per_click_label_text)
    cookies_per_click_label.draw(screen, centered_x=False, centered_y=False)

    cookies_per_second = (C.cps + autoclicker) * cookies_per_click
    if cookies_per_second != 1:
        cookies_per_second_label_text = [f"{format_number(cookies_per_second)} cookies per second"]
    else:
        cookies_per_second_label_text = [f"{format_number(cookies_per_second)} cookie per second"]
    cookies_per_second_label.update(delta, cookies_per_second_label_text)
    cookies_per_second_label.draw(screen, centered_x=False, centered_y=False)

    title_label.draw(screen)
    subtitle_label.draw(screen)

    shop_title_label.update(delta, x=shop_limit / 2 - shop_title_label.width / 2 - Label.horizontal_padding)
    shop_title_label.draw(screen, centered_x=False, centered_y=True)

    base_cost_button_text = [f"Base Cookies Per Click: {format_number(score_base)}",
                             f"Cost to upgrade: {format_number(base_cost)}"]
    base_cost_button.update(delta, new_text=base_cost_button_text)
    base_cost_button.draw(screen, centered_x=False, centered_y=True, outlined=True, filled=True)

    multiplier_cost_button_text = [f"Cookie Multiplier: {format_number(score_multiplier)}",
                                   f"Cost to upgrade: {format_number(multiplier_cost)}"]
    multiplier_cost_button.update(delta, new_text=multiplier_cost_button_text)
    multiplier_cost_button.draw(screen, centered_x=False, centered_y=True, outlined=True, filled=True)

    autoclicker_cost_button_text = [f"Autoclickers: {format_number(autoclicker)}",
                                    f"Cost to upgrade: {format_number(autoclicker_cost)}"]
    autoclicker_cost_button.update(delta, new_text=autoclicker_cost_button_text)
    autoclicker_cost_button.draw(screen, centered_x=False, centered_y=True, outlined=True, filled=True)

    C.update(delta)
    C.draw(screen)

    cookie.update(delta, 0)
    cookie.draw(screen)
    for c in falling_cookies:
        c.update(delta, shop_limit)
        c.draw(screen)

    effect_del_offset = 0
    for i, effect in enumerate(click_effects):
        effect.update(delta, y=effect.position.y - FallingCookie.gravity)
        effect.draw(screen)
        if effect.position.y + effect.height < 0:
            del click_effects[i - effect_del_offset]
            effect_del_offset += 1

    pygame.display.update()
    delta = clock.tick(fps_cap)

pygame.quit()
