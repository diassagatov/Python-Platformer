import pgzrun
import random
import os
from pgzero.builtins import Actor, Rect, sounds
from math import sin
from hero import Hero
from game_platform import Platform

WIDTH = 600
HEIGHT = 400
BEST_SCORE_FILE = 'best_score.txt'

bg1 = Actor('backgrounds/back.jpg')

# Sound control
game_muted = False

ENEMY_DATA = {
    'bee':   {'images': ['enemy/bee_a', 'enemy/bee_b'], 'rest': 'enemy/bee_rest', 'speed': 1},
    'snail': {'images': ['enemy/snail_walk_a', 'enemy/snail_walk_b'], 'rest': 'enemy/snail_rest', 'speed': 1},
    'saw':   {'images': ['enemy/saw_a', 'enemy/saw_b'], 'rest': 'enemy/saw_rest', 'speed': 2}
}

def play_sound(name):
    if not game_muted:
        getattr(sounds, name).play()

def load_best_score():
    try:
        with open(BEST_SCORE_FILE) as f: return int(f.read().strip())
    except: return 0

def save_best_score(score):
    with open(BEST_SCORE_FILE, 'w') as f: f.write(str(score))

class Enemy:
    def __init__(self, x, y, etype):
        d = ENEMY_DATA[etype]
        self.etype, self.images, self.rest_image, self.speed = etype, d['images'], d['rest'], d['speed']
        self.actor = Actor(self.images[0], (x, y))
        self.anim_timer = self.anim_frame = 0
        self.is_moving = False
        self.attack_cooldown = 0
        if etype == 'snail': self.direction = random.choice([-1, 1])
        if etype == 'saw': self.base_y, self.angle = y, random.uniform(0, 3.14)
    def update(self, hero):
        if self.attack_cooldown > 0: self.attack_cooldown -= 1
        if self.etype == 'bee':
            self.is_moving = False
            for axis in ['x', 'y']:
                if getattr(self.actor, axis) < getattr(hero.actor, axis):
                    setattr(self.actor, axis, getattr(self.actor, axis) + self.speed)
                    self.is_moving = True
                elif getattr(self.actor, axis) > getattr(hero.actor, axis):
                    setattr(self.actor, axis, getattr(self.actor, axis) - self.speed)
                    self.is_moving = True
        elif self.etype == 'snail':
            self.is_moving = True
            self.actor.x += self.speed * self.direction
            if self.actor.x < 0 or self.actor.x > WIDTH: self.direction *= -1
            self.actor.y = 300
        elif self.etype == 'saw':
            self.is_moving = True
            self.actor.x -= self.speed
            self.angle += 0.07
            self.actor.y = self.base_y + 40 * sin(self.angle)
            if self.actor.x < -30:
                self.actor.x = WIDTH + 30
                self.base_y = random.randint(100, 250)
        if self.is_moving:
            self.anim_timer += 1
            if self.anim_timer % 12 == 0:
                self.anim_frame = (self.anim_frame + 1) % len(self.images)
            self.actor.image = self.images[self.anim_frame]
        else:
            self.actor.image = self.rest_image
    def draw(self): self.actor.draw()
    def collides_with_hero(self, hero):
        e = self.actor; h = hero.actor
        return Rect(e.x-e.width//2,e.y-e.height//2,e.width,e.height).colliderect(
               Rect(h.x-h.width//2,h.y-h.height//2,h.width,h.height))

def spawn_enemy(etype):
    if etype == 'bee':
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        x, y = (random.randint(0, WIDTH), 0) if edge=='top' else \
               (random.randint(0, WIDTH), HEIGHT) if edge=='bottom' else \
               (0, random.randint(0, HEIGHT)) if edge=='left' else \
               (WIDTH, random.randint(0, HEIGHT))
    elif etype == 'snail': x, y = random.randint(50, WIDTH-50), 300
    else: x, y = random.randint(WIDTH//2, WIDTH), random.randint(100, 250)
    return Enemy(x, y, etype)

def random_platforms():
    return [Platform(random.randint(60, WIDTH-160), y, random.randint(80, 140), 20)
            for y in sorted(random.sample(range(150, 320, 30), random.randint(2, 4)))]

def reset_game():
    global hero, hero_health, platforms, enemies, score, platform_speed
    hero = Hero(WIDTH//2, HEIGHT-100); hero.jump_speed = 12
    hero_health = 100
    platforms = random_platforms()
    platform_speed = random.randint(1, 3)
    enemies = [spawn_enemy(t) for t in ['bee', 'snail', 'saw']]
    score = 0

reset_game()
state = 'menu'
best_score = load_best_score()
button_rect = Rect(30, 30, 120, 40)
mute_rect = Rect(WIDTH//2-80, HEIGHT//2+60, 160, 40)
exit_rect = Rect(WIDTH//2-80, HEIGHT//2+120, 160, 40)

def update():
    global state, hero_health, score, best_score
    if state != 'game': return
    was_on_ground = hero.on_ground
    hero.update(platforms, moving_left=keyboard.a, moving_right=keyboard.d)
    hero.set_state('idle')
    if keyboard.a: hero.move_left()
    if keyboard.d: hero.move_right()
    if keyboard.w:
        if was_on_ground and hero.on_ground == False:
            play_sound('sfx_jump')
        hero.jump_up()
    hero.keep_in_bounds(WIDTH)
    for p in platforms: p.move_left(platform_speed); p.reset_if_offscreen(WIDTH)
    for e in enemies:
        e.update(hero)
        if e.collides_with_hero(hero) and e.attack_cooldown == 0:
            hero_health -= 1; hero_health = round(hero_health, 2)
            play_sound('sfx_hurt'); e.attack_cooldown = 30
            if hero_health < 0:
                hero_health = 0; state = 'gameover'; play_sound('sfx_disappear')
                if score > best_score: best_score = score; save_best_score(best_score)
    score += 1

def draw():
    screen.clear(); bg1.draw()
    if state == 'menu': draw_menu()
    elif state == 'gameover': draw_gameover()
    else:
        for p in platforms: p.draw(screen)
        hero.draw()
        for e in enemies: e.draw()
        draw_health_bar(); draw_menu_button(); draw_score(); draw_best_score()

def draw_health_bar():
    x, y, w, h = 20, 20, 180, 20
    screen.draw.rect(Rect(x-2, y-2, w+4, h+4), (255,255,255))
    screen.draw.filled_rect(Rect(x, y, w, h), (60, 60, 60))
    health_width = int(w * hero_health / 100)
    color = (0,200,0) if hero_health>40 else (200,100,0) if hero_health>15 else (200,0,0)
    screen.draw.filled_rect(Rect(x, y, health_width, h), color)
    screen.draw.text(f"HP: {hero_health:.2f}", (x+8, y+2), color="white", fontsize=22)

def draw_score():
    screen.draw.text(f"Score: {score}", (WIDTH-160, 20), color="#000000", fontsize=32)

def draw_best_score():
    screen.draw.text(f"Best: {best_score}", (WIDTH-160, 60), color="#000000", fontsize=28)

def draw_menu():
    y, spacing = HEIGHT//2-60, 60
    screen.draw.text("RUN FOR YOUR LIFE", center=(WIDTH//2, y-80), fontsize=54, color="#fffbe0", owidth=2, ocolor="black")
    screen.draw.text(f"Best Score: {best_score}", center=(WIDTH//2, y-30), fontsize=36, color="#000000")
    start_rect = Rect(WIDTH//2-80, y+20, 160, 50)
    screen.draw.filled_rect(start_rect, (50,100,200)); screen.draw.text("START", center=start_rect.center, fontsize=40, color="white")
    mute_rect.y = y+90; screen.draw.filled_rect(mute_rect, (100,100,100)); screen.draw.text("MUTE" if not game_muted else "UNMUTE", center=mute_rect.center, fontsize=32, color="white")
    exit_rect.y = y+150; screen.draw.filled_rect(exit_rect, (200,50,50)); screen.draw.text("EXIT", center=exit_rect.center, fontsize=32, color="white")
    icon_y, icon_x = exit_rect.centery+spacing+20, WIDTH//2-80
    screen.blit('enemy/bee_a', (icon_x, icon_y)); screen.blit('enemy/snail_walk_a', (icon_x+60, icon_y)); screen.blit('enemy/saw_a', (icon_x+120, icon_y))
    screen.draw.text("Enemies:", (icon_x-100, icon_y+10), fontsize=28, color="#fffbe0")
    screen.draw.text("Jump on platforms, avoid enemies!", center=(WIDTH//2, icon_y+70), fontsize=32, color="#fffbe0")

def draw_gameover():
    screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2-60), fontsize=60, color="red", owidth=2, ocolor="black")
    screen.draw.text(f"Final Score: {score}", center=(WIDTH//2, HEIGHT//2), fontsize=40, color="yellow")
    screen.draw.text(f"Best: {best_score}", center=(WIDTH//2, HEIGHT//2+50), fontsize=32, color="#00e0ff")
    menu_btn = Rect(WIDTH//2-80, HEIGHT//2+100, 160, 50)
    screen.draw.filled_rect(menu_btn, (50,100,200)); screen.draw.text("MENU", center=menu_btn.center, fontsize=36, color="white")

def draw_menu_button():
    btn = Rect(WIDTH-150, HEIGHT-60, 120, 40)
    screen.draw.filled_rect(btn, (200,50,50))
    screen.draw.text("MENU", center=btn.center, fontsize=28, color="white")

def on_mouse_down(pos):
    global state, game_muted
    y = HEIGHT//2-60; start_rect = Rect(WIDTH//2-80, y+20, 160, 50)
    game_menu_btn = Rect(WIDTH-150, HEIGHT-60, 120, 40)
    gameover_menu_btn = Rect(WIDTH//2-80, HEIGHT//2+100, 160, 50)
    if state == 'menu':
        if start_rect.collidepoint(pos): state = 'game'; reset_game()
        elif mute_rect.collidepoint(pos): game_muted = not game_muted
        elif exit_rect.collidepoint(pos): quit()
    elif state == 'game':
        if game_menu_btn.collidepoint(pos): state = 'menu'; reset_game()
    elif state == 'gameover':
        if gameover_menu_btn.collidepoint(pos): state = 'menu'; reset_game()

pgzrun.go()

