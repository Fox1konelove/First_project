import pygame
import random
import time

pygame.init()
pygame.mixer.init()

WIDTH = 700
HEIGHT = 500
FPS = 60

WHITE = (255, 255, 255)
RED = (255, 0, 0)

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Game")

background = pygame.image.load("galaxy.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, player_image, x, y, speed, size_x=65, size_y=65):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(player_image)
        self.image = pygame.transform.scale(self.image, (size_x, size_y))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Bullet(GameSprite):
    def __init__(self, x, y):
        super().__init__("bullet.png", x, y, 7, 15, 20)

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class Player(GameSprite):
    def __init__(self, player_image, x, y, speed, size_x=65, size_y=65):
        super().__init__(player_image, x, y, speed, size_x, size_y)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

class Asteroid(GameSprite):
    def __init__(self):
        x = random.randint(0, WIDTH - 50)
        speed = random.randint(1, 2)
        super().__init__("asteroid.png", x, -50, speed, 50, 50)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - 50)
            self.rect.y = -50
            self.speed = random.randint(1, 2)

class Enemy(GameSprite):
    def __init__(self):
        x = random.randint(0, WIDTH - 65)
        speed = random.randint(1, 2)
        super().__init__("ufo.png", x, -65, speed)

    def update(self):
        global missed_ufos
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - 65)
            self.rect.y = -65
            self.speed = random.randint(1, 3)
            missed_ufos += 1  

def spawn_enemy():
    enemy = Enemy()
    enemies.add(enemy)

player = Player("rocket.png", WIDTH // 2, HEIGHT - 100, 5)
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
for _ in range(5):
    enemy = Enemy()
    enemies.add(enemy)

asteroids = pygame.sprite.Group()
for _ in range(3):
    asteroid = Asteroid()
    asteroids.add(asteroid)

fire_sound = pygame.mixer.Sound("fire.ogg")

pygame.mixer.music.load("space.ogg")
pygame.mixer.music.play(-1)

destroyed_ufos = 0  # Сбитые тарелки
missed_ufos = 0     # Пропущенные тарелки
victory = False     # Флаг победы
num_fire = 0       # Количество выстрелов
rel_time = False   # Флаг перезарядки
last_shot = 0      # Время последнего выстрела
MAX_BULLETS = 5    # Максимальное количество пуль
RELOAD_TIME = 1.5  # Время перезарядки в секундах
lost = 0           # Счетчик поражений
game_over = False  # Флаг окончания игры

pygame.font.init()
game_font = pygame.font.SysFont('Areal', 36)
lose_font = pygame.font.SysFont('Areal', 20)  

clock = pygame.time.Clock()
running = True

collide = False  

while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not rel_time and num_fire < MAX_BULLETS and not victory:  
                bullet = Bullet(player.rect.centerx - 7, player.rect.top)
                bullets.add(bullet)
                fire_sound.play()
                num_fire += 1
                if num_fire >= MAX_BULLETS:
                    rel_time = True
                    last_shot = time.time()

    if not victory and not collide:  
        player.update()
        enemies.update()
        bullets.update()
        asteroids.update()

        if rel_time:
            now = time.time()
            if now - last_shot >= RELOAD_TIME:
                rel_time = False
                num_fire = 0

        collided_bullets = pygame.sprite.groupcollide(bullets, enemies, True, False)
        for bullet, enemy_list in collided_bullets.items():
            destroyed_ufos += len(enemy_list)
            for enemy in enemy_list:
                enemy.kill()  
                spawn_enemy()  

        if not game_over:
            if pygame.sprite.spritecollide(player, enemies, False):
                game_over = True
                victory = False
                collision_type = "enemy"
            elif pygame.sprite.spritecollide(player, asteroids, False):
                game_over = True
                victory = False
                collision_type = "asteroid"
            elif missed_ufos >= 3:
                game_over = True
                victory = False
                collision_type = "missed"
            elif destroyed_ufos >= 10:
                game_over = True
                victory = True

        if rel_time:
            now = time.time()
            if now - last_shot >= RELOAD_TIME:
                rel_time = False
                num_fire = 0

    window.blit(background, (0, 0))
    
    if not victory:
        player.reset()

        for bullet in bullets:
            bullet.reset()

        for enemy in enemies:
            enemy.reset()
        for asteroid in asteroids:
            asteroid.reset()


        destroyed_text = game_font.render(f"Уничтожено: {destroyed_ufos}", True, WHITE)
        missed_text = game_font.render(f"Пропущено: {missed_ufos}", True, WHITE)
        bullets_text = game_font.render(f"Пули: {MAX_BULLETS - num_fire}", True, WHITE)
        window.blit(destroyed_text, (10, 10))
        window.blit(missed_text, (10, 50))
        window.blit(bullets_text, (10, 90))

        if rel_time:
            reload_text = game_font.render("Перезарядка...", True, RED)
            window.blit(reload_text, (WIDTH // 2 - 70, 10))

    if game_over:
        if victory:
            victory_text = game_font.render("Победа! Вы уничтожили 10+ НЛО!", True, WHITE)
            text_rect = victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            window.blit(victory_text, text_rect)
        else:
            lose_text = lose_font.render("Поражение!", True, RED)
            text_rect = lose_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            window.blit(lose_text, text_rect)

            if collision_type == "enemy":
                reason_text = lose_font.render("Столкновение с врагом!", True, RED)
            elif collision_type == "asteroid":
                reason_text = lose_font.render("Проигрыш! Вы столкнулись с метеоритом", True, RED)
            else:
                reason_text = lose_font.render("Пропущено 3+ монстров!", True, RED)
            reason_rect = reason_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
            window.blit(reason_text, reason_rect)

        pygame.display.flip()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

    pygame.display.flip()

pygame.quit()