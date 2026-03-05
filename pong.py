import pygame
import math
import random
import sys

pygame.init()
pygame.mixer.init()
info = pygame.display.Info()

SCREEN_WIDTH = info.current_w if info.current_w > 0 else 800
SCREEN_HEIGHT = info.current_h if info.current_h > 0 else 600

FPS = 60
MAX_BALL_SPEED = 35
ACCELERATION = 1.03
START_SPEED = 10

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Ball(pygame.sprite.Sprite):
    """Een bal die beweegt met vectoren en versnelling ondersteunt"""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (10, 10), 10)
        self.rect = self.image.get_rect()
        self.hit = False  
        self.reset()

    def reset(self):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        kant = random.choice([0, math.pi])
        hoek = kant + random.uniform(-0.2, 0.2)
        self.speed = START_SPEED
        self.vector = (hoek, self.speed)

    def update(self):
        angle, speed = self.vector
        self.rect.x += speed * math.cos(angle)
        self.rect.y += speed * math.sin(angle)

        if self.rect.top <= 0:
            self.rect.top = 0
            self.vector = (-angle, speed)
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vector = (-angle, speed)

        if self.rect.left <= 0: return "P2_SCORES"
        if self.rect.right >= SCREEN_WIDTH: return "P1_SCORES"
        return None

class Bat(pygame.sprite.Sprite):
    """Bestuurbaar batje"""
    def __init__(self, side):
        super().__init__()
        self.image = pygame.Surface((20, 120))
        self.image.fill(WHITE)
        self.speed = 15
        self.movepos = [0, 0] 
        self.side = side
        
        if side == "left":
            self.rect = self.image.get_rect(midleft=(50, SCREEN_HEIGHT // 2))
        else:
            self.rect = self.image.get_rect(midright=(SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2))

    def moveup(self): self.movepos[1] = -self.speed
    def movedown(self): self.movepos[1] = self.speed
    def stop(self): self.movepos[1] = 0

    def update(self):
        newpos = self.rect.move(self.movepos)
        if newpos.top >= 0 and newpos.bottom <= SCREEN_HEIGHT:
            self.rect = newpos

def main():
    try:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    except:
        screen = pygame.display.set_mode((800, 600))
        
    pygame.display.set_caption("Pong - Progressive Speed")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 60)

    try:
        hit_sound = pygame.mixer.Sound("geluid.mp3")
    except:
        hit_sound = None
        print("Let op: geluid.mp3 niet gevonden in de map.")

    player1 = Bat("left")
    player2 = Bat("right")
    ball = Ball()
    
    score_p1 = 0
    score_p2 = 0

    all_sprites = pygame.sprite.Group(player1, player2, ball)

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                if event.key == pygame.K_w: player1.moveup()
                if event.key == pygame.K_s: player1.movedown()
                if event.key == pygame.K_UP: player2.moveup()
                if event.key == pygame.K_DOWN: player2.movedown()
            
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_w, pygame.K_s): player1.stop()
                if event.key in (pygame.K_UP, pygame.K_DOWN): player2.stop()

        result = ball.update()
        player1.update()
        player2.update()

        if result == "P1_SCORES":
            score_p1 += 1
            ball.reset()
        elif result == "P2_SCORES":
            score_p2 += 1
            ball.reset()

        p1_hitbox = player1.rect.inflate(-2, -2)
        p2_hitbox = player2.rect.inflate(-2, -2)
        max_bounce_angle = math.radians(50)

        if ball.rect.colliderect(p1_hitbox) and not ball.hit:
            if hit_sound: hit_sound.play()

            current_speed = ball.vector[1]
            new_speed = min(current_speed * ACCELERATION, MAX_BALL_SPEED)

            rel_y = (ball.rect.centery - player1.rect.centery) / (player1.rect.height / 2)
            new_angle = rel_y * max_bounce_angle
            ball.vector = (new_angle, new_speed)
            ball.hit = True

        elif ball.rect.colliderect(p2_hitbox) and not ball.hit:
            if hit_sound: hit_sound.play()

            current_speed = ball.vector[1]
            new_speed = min(current_speed * ACCELERATION, MAX_BALL_SPEED)

            rel_y = (ball.rect.centery - player2.rect.centery) / (player2.rect.height / 2)
            new_angle = math.pi - (rel_y * max_bounce_angle)
            ball.vector = (new_angle, new_speed)
            ball.hit = True
            
        elif ball.hit:
            if not ball.rect.colliderect(p1_hitbox) and not ball.rect.colliderect(p2_hitbox):
                ball.hit = False

        screen.fill(BLACK)
        pygame.draw.line(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)
        score_surf = font.render(f"{score_p1}      {score_p2}", True, WHITE)
        screen.blit(score_surf, (SCREEN_WIDTH // 2 - 75, 50))
        all_sprites.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()