from pgzero.builtins import Actor, keyboard, Rect

WIDTH = 600
HEIGHT = 400

class Hero:
    def __init__(self, x, y):
        self.images = {
            'idle': 'hero/character_purple_idle',
            'idleL': 'hero/character_purple_idle_left',
            'walk': ['hero/character_purple_walk_a', 'hero/character_purple_walk_b'],
            'walkL': ['hero/character_purple_walk_a_left', 'hero/character_purple_walk_b_left'],
            'jump': 'hero/character_purple_jump',
            'jumpL': 'hero/character_purple_jump_left'
        }
        self.actor = Actor(self.images['idle'])
        self.actor.x = x
        self.actor.y = y
        self.actor.z = 10
        self.speed = 5
        self.state = 'idle'  # 'idle', 'walk', 'jump'
        self.walk_frame = 0
        self.walk_anim_timer = 0
        self.on_ground = True
        self.jump_speed = 8
        self.vy = 0
        self.facing_right = True

    def draw(self):
        if self.facing_right:
            self.actor.angle = 0
        else:
            self.actor.flip = 180
        self.actor.draw()

    def move_left(self):
        self.actor.x -= self.speed
        if self.on_ground:
            self.state = 'walkL'
        self.facing_right = False

    def move_right(self):
        self.actor.x += self.speed
        if self.on_ground:
            self.state =  'walk'
        self.facing_right = True

    def jump_up(self):
        if self.on_ground:
            self.vy = -self.jump_speed
            self.on_ground = False
            self.state = 'jump' if self.facing_right else 'jumpL'

    def keep_in_bounds(self, width):
        self.actor.x = max(0, min(width, self.actor.x))

    def set_state(self, state):
        self.state = state

    def update(self, platforms=None, moving_left=False, moving_right=False):
        gravity = 0.5
        prev_on_ground = self.on_ground
        self.on_ground = False
        # Handle jumping and falling
        if not prev_on_ground or self.vy != 0:
            self.vy += gravity
            self.actor.y += self.vy
            hero_rect = Rect(
                self.actor.x - self.actor.width // 2,
                self.actor.y - self.actor.height // 2,
                self.actor.width,
                self.actor.height
            )
            if platforms:
                for platform in platforms:
                    platform_top = platform.rect.y
                    platform_left = platform.rect.x
                    platform_right = platform.rect.x + platform.rect.width
                    hero_feet = self.actor.y + self.actor.height // 2
                    hero_prev_feet = self.actor.y + self.actor.height // 2 - self.vy
                    if (self.vy > 0 and
                        hero_prev_feet <= platform_top and
                        hero_feet >= platform_top and
                        platform_left < self.actor.x < platform_right):
                        self.actor.y = platform_top - self.actor.height // 2 + 1
                        self.vy = 0
                        self.on_ground = True
                        self.state = 'idle'
                        break
            if self.actor.y >= 300:
                self.actor.y = 300
                self.vy = 0
                self.on_ground = True
                self.state = 'idle'
        # Animation logic
        if self.on_ground and (moving_left or moving_right):
            self.walk_anim_timer += 1
            if self.walk_anim_timer % 10 == 0:
                self.walk_frame = (self.walk_frame + 1) % 2
            self.actor.image = self.images['walk' if self.facing_right else 'walkL'][self.walk_frame]
        elif self.state == 'jump' or self.state == 'jumpL':
            self.actor.image = self.images['jump' if self.facing_right else 'jumpL']
        else:
            img = self.images[self.state]
            if isinstance(img, list):
                self.actor.image = img[0]
            else:
                self.actor.image = img
        if (self.state == 'walk' or self.state == 'walkL') and not (moving_left or moving_right):
            self.state = 'idle' if self.facing_right else 'idleL'

