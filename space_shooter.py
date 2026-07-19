import pygame, sys, random, math
from pygame import Rect
import traceback

WIDTH, HEIGHT = 800, 720
FPS = 60
BG_COLOR = (6, 11, 30)
FONT_NAME = None

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(FONT_NAME, 18)
bigfont = pygame.font.SysFont(FONT_NAME, 36)

def draw_text(surf, txt, x, y, color=(255,255,255), f=font):
    surf.blit(f.render(txt, True, color), (x,y))

def clamp(v, a, b): return max(a, min(b, v))

class Player:
    def __init__(self):
        self.w, self.h = 48, 48
        self.x = WIDTH//2 - self.w//2
        self.y = HEIGHT - self.h - 24
        self.speed = 6
        self.health_max = 120
        self.health = self.health_max
        self.fire_cool = 10
        self.fire_timer = 0
        self.damage = 18
        self.fire_rate_level = 0
        self.damage_level = 0
        self.health_level = 0
        self.gold = 60
        self.score = 0
        self.alive = True
        self.color = (42, 200, 220)

    def update(self, keys):
        if keys[pygame.K_LEFT]: self.x -= self.speed
        if keys[pygame.K_RIGHT]: self.x += self.speed
        self.x = clamp(self.x, 0, WIDTH - self.w)
        if self.fire_timer > 0: self.fire_timer -= 1

    def shoot(self):
        if self.fire_timer > 0: return None
        self.fire_timer = max(3, self.fire_cool - self.fire_rate_level*2)
        dmg = self.damage + self.damage_level*6
        bx = self.x + self.w//2
        by = self.y - 8
        return Bullet(bx-4, by, 8, 14, -12, dmg, (255,240,100))

    def take_damage(self, d):
        self.health -= d
        if self.health <= 0:
            self.health = 0
            self.alive = False

    def heal(self, amt):
        self.health = clamp(self.health + amt, 0, self.health_max)

    def draw(self, surf):
        pygame.draw.polygon(surf, (20,60,80), [(self.x+self.w//2, self.y-16),(self.x+6,self.y+10),(self.x+self.w-6,self.y+10)])
        pygame.draw.rect(surf, self.color, Rect(self.x, self.y, self.w, self.h), border_radius=6)
        bar_w = self.w
        hpw = int(bar_w * (self.health / self.health_max))
        pygame.draw.rect(surf, (60,60,60), Rect(self.x, self.y+self.h+6, bar_w, 8))
        pygame.draw.rect(surf, (30,220,110), Rect(self.x, self.y+self.h+6, hpw, 8))

class Bullet:
    def __init__(self, x,y,w,h,dy,damage,color=(255,255,0)):
        self.rect = Rect(x,y,w,h)
        self.dy = dy
        self.damage = damage
        self.color = color
        self.alive = True

    def update(self):
        self.rect.y += self.dy
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.alive = False

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect, border_radius=3)

class Enemy:
    def __init__(self, x,y,w,h,spd,hp,value, kind=0):
        self.rect = Rect(x,y,w,h)
        self.spd = spd
        self.hp = hp
        self.alive = True
        self.value = value
        self.kind = kind
        self.color = (180, 80, 200) if kind==0 else (200,120,60)

    def update(self):
        self.rect.y += self.spd
        self.rect.x += int(math.sin(self.rect.y * 0.04 + self.rect.x*0.01) * 1.6)
        if self.rect.top > HEIGHT + 100:
            self.alive = False

    def take_damage(self, d):
        self.hp -= d
        if self.hp <= 0:
            self.alive = False

    def shoot_towards(self, tx, ty, level):
        dx = tx - (self.rect.centerx)
        dy = ty - (self.rect.centery)
        dist = math.hypot(dx,dy) or 1
        speed = 3.0 + random.random()*0.8 + level*0.1
        vx = dx / dist * speed
        vy = dy / dist * speed
        return EnemyBullet(self.rect.centerx-5, self.rect.centery-5, 10,10, vx, vy, damage=6 + level//2)

    def draw(self, surf):
        pygame.draw.ellipse(surf, self.color, self.rect)
        bar_w = self.rect.w
        ratio = max(0, self.hp) / max(1, 20 + self.value)
        pygame.draw.rect(surf, (40,40,40), Rect(self.rect.x, self.rect.y-8, bar_w, 6))
        pygame.draw.rect(surf, (220,80,80), Rect(self.rect.x, self.rect.y-8, int(bar_w*ratio), 6))

class EnemyBullet:
    def __init__(self,x,y,w,h,vx,vy,damage):
        self.x = float(x); self.y = float(y)
        self.w = w; self.h = h
        self.vx = vx; self.vy = vy
        self.damage = damage
        self.alive = True

    def update(self):
        self.x += self.vx; self.y += self.vy
        if self.y > HEIGHT + 50 or self.x < -50 or self.x > WIDTH+50 or self.y < -50:
            self.alive = False

    def rect(self): return Rect(int(self.x), int(self.y), self.w, self.h)

    def draw(self, surf):
        pygame.draw.ellipse(surf, (255,140,60), self.rect())

class Shop:
    def __init__(self, player):
        self.player = player
        self.w = 520; self.h = 420
        self.x = WIDTH//2 - self.w//2
        self.y = HEIGHT//2 - self.h//2
        self.bg = (12,18,40,220)

    def draw(self, surf):
        s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        s.fill(self.bg)
        surf.blit(s, (self.x, self.y))
        draw_text(surf, "SHOP - Press S to close", self.x+20, self.y+14)
        draw_text(surf, f"Gold: {self.player.gold}", self.x+20, self.y+40)
        draw_text(surf, "1) Upgrade Damage (+6 per level)   Cost: 30 + 20*n", self.x+20, self.y+80)
        draw_text(surf, "2) Upgrade Fire Rate (faster shots) Cost: 30 + 20*n", self.x+20, self.y+120)
        draw_text(surf, "3) Increase Max Health (+20)        Cost: 40 + 25*n", self.x+20, self.y+160)
        draw_text(surf, "Tip: Buy between waves. Press 1/2/3 to buy.", self.x+20, self.y+220)
        draw_text(surf, f"Damage level: {self.player.damage_level}  Rate level: {self.player.fire_rate_level}  Health level: {self.player.health_level}", self.x+20, self.y+260)

    def handle_purchase(self, key):
        if key == pygame.K_1:
            cost = 30 + self.player.damage_level*20
            if self.player.gold >= cost:
                self.player.gold -= cost
                self.player.damage_level += 1
                self.player.damage += 6
        elif key == pygame.K_2:
            cost = 30 + self.player.fire_rate_level*20
            if self.player.gold >= cost:
                self.player.gold -= cost
                self.player.fire_rate_level += 1
                self.player.fire_cool = max(3, self.player.fire_cool - 2)
        elif key == pygame.K_3:
            cost = 40 + self.player.health_level*25
            if self.player.gold >= cost:
                self.player.gold -= cost
                self.player.health_level += 1
                self.player.health_max += 20
                self.player.heal(20)

class Game:
    def __init__(self):
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.ebullets = []
        self.level = 1
        self.spawn_timer = 0
        self.spawn_rate = 90
        self.frames = 0
        self.paused = False
        self.shop_open = False
        self.shop = Shop(self.player)
        self.game_over = False

    def reset(self):
        self.__init__()

    def spawn_wave(self):
        count = 1 + self.level//2 + random.randint(0, self.level//2)
        for _ in range(count):
            w = 36 + (0 if random.random()<0.85 else 24)
            h = w
            x = random.randint(0, WIDTH - w)
            y = -random.randint(20, 200)
            spd = 1 + random.random()*0.8 + self.level*0.12
            hp = 12 + self.level*6 + random.randint(0, self.level*3)
            value = 8 + self.level*3
            kind = 0 if random.random() < 0.8 else 1
            self.enemies.append(Enemy(x,y,w,h, spd, hp, value, kind))
        if random.random() < min(0.35, 0.08 + self.level*0.03):
            w = 80; h = 80; x = random.randint(0, WIDTH-w)
            spd = 0.6 + self.level*0.06
            hp = 60 + self.level*30
            val = 60 + self.level*20
            self.enemies.append(Enemy(x, -100, w,h, spd, hp, val, kind=1))

    def update(self, keys):
        if self.game_over or self.paused or self.shop_open:
            return
        self.frames += 1
        self.player.update(keys)
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_wave()
            self.spawn_timer = 0
        if self.frames % (FPS * 20) == 0:
            self.level += 1
            self.spawn_rate = max(28, self.spawn_rate - 6)
            self.player.gold += 18 + self.level*3
        for b in self.bullets:
            b.update()
        self.bullets = [b for b in self.bullets if b.alive]
        for en in self.enemies:
            en.update()
            if random.random() < 0.009 + self.level*0.002:
                self.ebullets.append(en.shoot_towards(self.player.x + self.player.w//2, self.player.y + self.player.h//2, self.level))
        self.enemies = [e for e in self.enemies if e.alive]
        for eb in self.ebullets:
            eb.update()
        self.ebullets = [eb for eb in self.ebullets if eb.alive]
        for b in list(self.bullets):
            for e in list(self.enemies):
                if b.rect.colliderect(e.rect):
                    e.take_damage(b.damage)
                    b.alive = False
                    if not e.alive:
                        self.player.score += e.value
                        self.player.gold += e.value//2
                    break
        for eb in list(self.ebullets):
            if eb.rect().colliderect(Rect(self.player.x, self.player.y, self.player.w, self.player.h)):
                self.player.take_damage(eb.damage)
                eb.alive = False
        for e in list(self.enemies):
            if e.rect.colliderect(Rect(self.player.x, self.player.y, self.player.w, self.player.h)):
                self.player.take_damage(14)
                e.take_damage(9999)
        self.bullets = [b for b in self.bullets if b.alive]
        self.enemies = [e for e in self.enemies if e.alive]
        self.ebullets = [eb for eb in self.ebullets if eb.alive]
        if not self.player.alive:
            self.game_over = True

    def draw(self, surf):
        surf.fill(BG_COLOR)
        for i in range(80):
            x = (i*37 + self.frames* (1 + i%3)) % WIDTH
            y = (i*53 + (i*7)) % HEIGHT
            surf.set_at((x,y), (18,24,60))
        self.player.draw(surf)
        for b in self.bullets: b.draw(surf)
        for e in self.enemies: e.draw(surf)
        for eb in self.ebullets: eb.draw(surf)
        draw_text(surf, f"Score: {self.player.score}", 12, 10)
        draw_text(surf, f"Level: {self.level}", 12, 32)
        draw_text(surf, f"Health: {self.player.health}/{self.player.health_max}", 12, 54)
        draw_text(surf, f"Gold: {self.player.gold}", 12, 76)
        draw_text(surf, "P:Pause  S:Shop  R:Restart  Esc:Quit", WIDTH-340, 10)
        if self.paused:
            surf.blit(bigfont.render("PAUSED", True, (240,240,240)), (WIDTH//2-70, HEIGHT//2-28))
        if self.shop_open:
            self.shop.draw(surf)
        if self.game_over:
            surf.blit(bigfont.render("GAME OVER", True, (240,80,80)), (WIDTH//2-110, HEIGHT//2-64))
            draw_text(surf, "Press R to restart or Esc to quit", WIDTH//2-140, HEIGHT//2+8)

game = Game()

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if event.key == pygame.K_p and not game.game_over:
                game.paused = not game.paused
            if event.key == pygame.K_s and not game.game_over:
                game.shop_open = not game.shop_open
            if event.key == pygame.K_r:
                game.reset()
            if game.shop_open:
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    game.shop.handle_purchase(event.key)
            if event.key == pygame.K_SPACE and not (game.paused or game.shop_open or game.game_over):
                b = game.player.shoot()
                if b: game.bullets.append(b)

while True:
    dt = clock.tick(FPS)
    handle_events()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and not (game.paused or game.shop_open or game.game_over):
        b = game.player.shoot()
        if b: game.bullets.append(b)
    game.update(keys)
    game.draw(screen)
    pygame.display.flip()