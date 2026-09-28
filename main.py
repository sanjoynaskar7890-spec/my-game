import pygame
import math
import random
import struct

# --- Pygame Initialization ---
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
WIDTH, HEIGHT = 400, 600
# Fullscreen & Scaled for Android devices
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Hyper Shift: Ultra Pro Max")
clock = pygame.time.Clock()

# --- Colors ---
SKY_DAY_TOP = (56, 189, 248)
SKY_DAY_BOT = (224, 242, 254)
SKY_SUNSET_TOP = (249, 115, 22)
SKY_SUNSET_BOT = (253, 224, 71)
SKY_NIGHT_TOP = (15, 23, 42)
SKY_NIGHT_BOT = (30, 27, 75)
GROUND_TOP = (34, 197, 94)
GROUND_BOT = (120, 53, 15)
WHITE = (255, 255, 255)
RED = (239, 68, 68)
GOLD = (250, 204, 21)

# --- Standalone Sound Generator ---
def create_sound(freq, duration, vol=1.0, type='sine'):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = bytearray()
    for i in range(n_samples):
        t = i / sample_rate
        if type == 'sine': val = math.sin(2 * math.pi * freq * t)
        elif type == 'square': val = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
        elif type == 'sawtooth': val = 2.0 * (t * freq - math.floor(0.5 + t * freq))
        else: val = random.uniform(-1, 1)
        
        env = 1.0
        if i < 500: env = i / 500.0
        elif i > n_samples - 500: env = (n_samples - i) / 500.0
        
        sample = int(val * env * vol * 32767.0)
        sample = max(-32768, min(32767, sample))
        buf += struct.pack('<h', sample)
    return pygame.mixer.Sound(buffer=buf)

SND_JUMP_BIRD = create_sound(450, 0.15, 0.8, 'sine')
SND_JUMP_DINO = create_sound(200, 0.2, 1.0, 'square')
SND_SHIELD = create_sound(600, 0.4, 0.8, 'sine')
SND_BREAK = create_sound(150, 0.3, 1.0, 'sawtooth')
SND_ROAR = create_sound(100, 1.5, 1.0, 'sawtooth')
SND_COIN = create_sound(800, 0.1, 0.7, 'sine')
SND_MODE = create_sound(300, 0.5, 0.9, 'sawtooth')

# --- Game Variables ---
state = "WAIT" # WAIT -> CUTSCENE -> PLAYING -> GAMEOVER
state_timer = 0
score = 0
coins = 0
frames = 0

hero_y = 200
velocity = 0
mode = "FLAPPY"
shield_timer = 0
shield_hp = 0
next_shield_at = 5

base_speed = 4.0
current_speed = 4.0
pipe_gap = 160
spawn_rate = 100
is_nightmare = False
is_ultra = False
bg_scroll = 0

current_event = "NONE"
event_timer = 0
obstacles = []
items = []

# --- Drawing Helpers ---
def draw_gradient(surface, top_color, bot_color, y_start, height):
    for i in range(height):
        ratio = i / height
        r = int(top_color[0] * (1 - ratio) + bot_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bot_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bot_color[2] * ratio)
        pygame.draw.line(surface, (r,g,b), (0, y_start + i), (WIDTH, y_start + i))

def draw_lion_logo(x, y, scale=1.0):
    pygame.draw.circle(screen, (234, 88, 12), (x, y), int(50*scale))
    pygame.draw.polygon(screen, (250, 204, 21), [(x-30*scale, y-20*scale), (x+30*scale, y-20*scale), (x, y+35*scale)])
    pygame.draw.circle(screen, WHITE, (x-12*scale, y-5*scale), int(6*scale))
    pygame.draw.circle(screen, WHITE, (x+12*scale, y-5*scale), int(6*scale))
    pygame.draw.polygon(screen, (0,0,0), [(x-10*scale, y+10*scale), (x+10*scale, y+10*scale), (x, y+20*scale)])

def draw_bird(x, y, flap_offset):
    pygame.draw.polygon(screen, (234, 88, 12), [(x-15, y), (x-25, y-10), (x-25, y+10)])
    pygame.draw.circle(screen, GOLD, (x, y), 16)
    pygame.draw.circle(screen, (202, 138, 4), (x, y), 16, 2)
    wing_y = y + flap_offset
    pygame.draw.ellipse(screen, WHITE, (x-5, wing_y-6, 16, 10))
    pygame.draw.polygon(screen, (249, 115, 22), [(x+14, y-4), (x+26, y), (x+14, y+4)])
    pygame.draw.circle(screen, WHITE, (x+8, y-6), 5)
    pygame.draw.circle(screen, (0,0,0), (x+9, y-6), 2)

def draw_dino(x, y, run_offset):
    pygame.draw.rect(screen, (21, 128, 61), (x-15, y-10, 30, 24), border_radius=6)
    pygame.draw.polygon(screen, (22, 163, 74), [(x-15, y-5), (x-30, y-10), (x-15, y+10)])
    for i in range(3): pygame.draw.polygon(screen, (132, 204, 22), [(x-10+i*8, y-10), (x-6+i*8, y-16), (x-2+i*8, y-10)])
    pygame.draw.rect(screen, (22, 163, 74), (x+10, y-20, 24, 18), border_radius=4)
    pygame.draw.circle(screen, RED, (x+24, y-14), 3)
    pygame.draw.rect(screen, (20, 83, 45), (x+10, y-2, 20, 8))
    pygame.draw.rect(screen, (20, 83, 45), (x-10, y+14 + run_offset, 6, 12))
    pygame.draw.rect(screen, (20, 83, 45), (x+5, y+14 - run_offset, 6, 12))

# --- Setup Game ---
font_large = pygame.font.SysFont(None, 48)
font_med = pygame.font.SysFont(None, 32)
font_small = pygame.font.SysFont(None, 24)

def reset_game():
    global score, coins, frames, current_speed, pipe_gap, spawn_rate, is_ultra, is_nightmare, mode
    global hero_y, velocity, shield_timer, shield_hp, next_shield_at, current_event, event_timer, obstacles, items
    score, coins, frames = 0, 0, 0
    current_speed, pipe_gap, spawn_rate = 4.0, 160, 100
    is_ultra, is_nightmare = False, False
    mode = "FLAPPY"
    hero_y, velocity = 200, 0
    shield_timer, shield_hp, next_shield_at = 0, 0, 5
    current_event, event_timer = "NONE", 0
    obstacles.clear()
    items.clear()

def spawn_obstacle():
    global next_shield_at
    spawn_shield = False
    if score >= next_shield_at - 1:
        spawn_shield = True
        next_shield_at += 5
    
    obs_x = WIDTH + 20
    if current_event == "COINRUSH":
        wave_y = random.randint(150, 350)
        for c in range(3):
            items.append({"type": "COIN", "x": obs_x + c*40, "y": wave_y})
        return

    obs = {"x": obs_x, "passed": False, "move_dir": 1, "type": mode}
    if mode == "FLAPPY":
        obs["topH"] = random.randint(40, 500 - pipe_gap - 40)
        obs["gap"] = pipe_gap
        if spawn_shield: items.append({"type": "SHIELD", "x": obs_x + 15, "y": obs["topH"] + pipe_gap//2})
        elif random.random() < 0.4: items.append({"type": "COIN", "x": obs_x + 15, "y": obs["topH"] + pipe_gap//2})
    else:
        obs["isPtero"] = random.random() < 0.45
        if spawn_shield: items.append({"type": "SHIELD", "x": obs_x + 15, "y": 300 if obs["isPtero"] else 400})
        elif random.random() < 0.4: items.append({"type": "COIN", "x": obs_x + 15, "y": 300 if obs["isPtero"] else 400})
    obstacles.append(obs)

# --- Main Game Loop ---
running = True
while running:
    tap_detected = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
            tap_detected = True

    if state == "WAIT":
        draw_gradient(screen, (185, 28, 28), (69, 10, 10), 0, HEIGHT)
        state_timer += 1
        y_float = math.sin(state_timer * 0.1) * 8
        draw_lion_logo(WIDTH//2, HEIGHT//2 - 50 + y_float, 1.2)
        txt = font_large.render("ERRORGAMER", True, WHITE)
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 + 50))
        
        if (state_timer // 20) % 2 == 0:
            blink = font_med.render("TAP TO BEGIN", True, GOLD)
            screen.blit(blink, (WIDTH//2 - blink.get_width()//2, HEIGHT - 100))
        
        if tap_detected:
            state = "CUTSCENE"
            state_timer = 0
            SND_ROAR.play()
            
    elif state == "CUTSCENE":
        screen.fill((0,0,0))
        state_timer += 1
        pygame.draw.circle(screen, RED, (WIDTH//2, int(HEIGHT*0.3)), 80)
        draw_dino(WIDTH//2, int(HEIGHT*0.7), math.sin(state_timer * 0.3) * 5)
        pygame.draw.rect(screen, (0,0,0), (0,0,WIDTH, 80))
        pygame.draw.rect(screen, (0,0,0), (0,HEIGHT-80,WIDTH, 80))
        
        if state_timer > 120:
            reset_game()
            state = "PLAYING"
            
    elif state == "PLAYING" or state == "GAMEOVER":
        frames += 1
        
        if state == "PLAYING":
            if score >= 50:
                if not is_ultra: is_ultra = True; SND_MODE.play()
                current_speed = 7.5 + (score - 50) * 0.06; pipe_gap = 120; spawn_rate = 60
            elif score >= 25:
                if not is_nightmare: is_nightmare = True; SND_MODE.play()
                current_speed = 5.5 + (score - 25) * 0.04; pipe_gap = 135; spawn_rate = 80
            else:
                current_speed = 4.0 + (score * 0.04)

            if score > 4 and score % 10 == 0 and event_timer <= 0:
                r = random.random()
                current_event = "WIND" if r < 0.33 else ("STORM" if r < 0.66 else "COINRUSH")
                event_timer = 350
            if event_timer > 0:
                event_timer -= 1
                if event_timer <= 0: current_event = "NONE"

            if frames % spawn_rate == 0: spawn_obstacle()

            if tap_detected:
                if mode == "FLAPPY":
                    velocity = -6.0 if current_event == "WIND" else -7.5
                    SND_JUMP_BIRD.play()
                else:
                    if hero_y >= 500 - 24:
                        velocity = -15.5
                        SND_JUMP_DINO.play()

            grav = 0.48 if current_event == "WIND" else 0.42
            if mode == "DINO": grav = 0.88
            
            velocity += grav
            hero_y += velocity

            if mode == "FLAPPY":
                if hero_y >= 500 - 16:
                    if shield_hp > 0:
                        shield_hp -= 1; shield_timer = 0; velocity = -8; SND_BREAK.play()
                    else: state = "GAMEOVER"
                if hero_y <= 0: hero_y = 0; velocity = 0
            else:
                if hero_y >= 500 - 24: hero_y = 500 - 24; velocity = 0
                
            if shield_timer > 0:
                shield_timer -= 1
                if shield_timer <= 0: shield_hp = 0

            bg_scroll -= current_speed * 0.3

        # Environment Drawing
        day_cycle = score % 30
        if current_event == "STORM": draw_gradient(screen, SKY_NIGHT_TOP, SKY_NIGHT_BOT, 0, 500)
        else:
            if day_cycle < 10: draw_gradient(screen, SKY_DAY_TOP, SKY_DAY_BOT, 0, 500)
            elif day_cycle < 20: draw_gradient(screen, SKY_SUNSET_TOP, SKY_SUNSET_BOT, 0, 500)
            else: draw_gradient(screen, SKY_NIGHT_TOP, SKY_NIGHT_BOT, 0, 500)
        
        draw_gradient(screen, GROUND_TOP, GROUND_BOT, 500, HEIGHT - 500)

        # Draw Items
        if state == "PLAYING":
            hx, hw, hy, hh = 60, 30, hero_y, 30
            for it in reversed(items):
                it["x"] -= current_speed
                if hx+hw > it["x"] and hx < it["x"]+20 and hy+hh > it["y"] and hy < it["y"]+20:
                    if it["type"] == "SHIELD": shield_timer = 5 * 60; shield_hp = 1; SND_SHIELD.play()
                    elif it["type"] == "COIN": coins += 1; SND_COIN.play()
                    items.remove(it); continue
                if it["x"] < -30: items.remove(it); continue
                
                if it["type"] == "SHIELD":
                    pygame.draw.circle(screen, (56, 189, 248), (int(it["x"]), int(it["y"])), 12)
                    pygame.draw.circle(screen, WHITE, (int(it["x"]), int(it["y"])), 12, 2)
                else:
                    pygame.draw.circle(screen, GOLD, (int(it["x"]), int(it["y"])), 10)
                    pygame.draw.circle(screen, (254, 240, 138), (int(it["x"]), int(it["y"])), 10, 2)

        # Draw Obstacles (Fixed Cactus & Pterodactyl Graphics)
        if state == "PLAYING":
            for o in reversed(obstacles):
                o["x"] -= current_speed
                if is_ultra and o["type"] == "FLAPPY":
                    o["topH"] += o["move_dir"] * 2.5
                    if o["topH"] > 300 or o["topH"] < 50: o["move_dir"] *= -1
                
                hit = False
                if o["type"] == "FLAPPY":
                    top_rect = pygame.Rect(o["x"], 0, 50, o["topH"])
                    bot_rect = pygame.Rect(o["x"], o["topH"]+o["gap"], 50, 500 - (o["topH"]+o["gap"]))
                    pygame.draw.rect(screen, (6, 95, 70), top_rect)
                    pygame.draw.rect(screen, (6, 95, 70), bot_rect)
                    hero_rect = pygame.Rect(hx-10, hy-10, hw, hh)
                    if hero_rect.colliderect(top_rect) or hero_rect.colliderect(bot_rect): hit = True
                else:
                    if o.get("isPtero"):
                        # Clean Pterodactyl graphic instead of a raw box
                        px, py = int(o["x"]), 500 - 150
                        pygame.draw.ellipse(screen, (126, 34, 206), (px, py, 44, 22))
                        pygame.draw.polygon(screen, (168, 85, 247), [(px+12, py+11), (px+22, py-6), (px+32, py+11)])
                        p_rect = pygame.Rect(px, py, 44, 22)
                        hero_rect = pygame.Rect(hx-15, hy-15, hw, hh)
                        if hero_rect.colliderect(p_rect): hit = True
                    else:
                        # Clean Cactus graphic instead of a raw box
                        cx, cy = int(o["x"]), 500 - 52
                        pygame.draw.rect(screen, (153, 27, 27), (cx+8, cy, 16, 52), border_radius=4)
                        pygame.draw.rect(screen, (153, 27, 27), (cx, cy+14, 10, 8), border_radius=3)
                        pygame.draw.rect(screen, (153, 27, 27), (cx+22, cy+22, 10, 8), border_radius=3)
                        c_rect = pygame.Rect(cx, cy, 32, 52)
                        hero_rect = pygame.Rect(hx-15, hy-15, hw, hh)
                        if hero_rect.colliderect(c_rect): hit = True

                if hit:
                    if shield_hp > 0:
                        shield_hp -= 1; shield_timer = 0; obstacles.remove(o); SND_BREAK.play(); continue
                    else:
                        SND_BREAK.play(); state = "GAMEOVER"
                
                if not o["passed"] and o["x"] < 50:
                    score += 1; o["passed"] = True
                    if score % 15 == 0:
                        mode = "DINO" if mode == "FLAPPY" else "FLAPPY"
                        obstacles.clear(); items.clear()
                        hero_y = 500 - 24 if mode == "DINO" else 200
                        velocity = 0; SND_MODE.play()
                
                if o["x"] < -60: obstacles.remove(o)

        # Draw Hero
        if shield_timer > 0: pygame.draw.circle(screen, (56, 189, 248), (60, int(hero_y)), 25, 3)
        if mode == "FLAPPY": draw_bird(60, int(hero_y), math.sin(frames*0.5)*5)
        else: draw_dino(60, int(hero_y), math.sin(frames*0.8)*4 if velocity==0 else 0)

        # Draw HUD
        score_txt = font_med.render(f"SCORE: {score}", True, WHITE)
        coin_txt = font_med.render(f"COINS: {coins}", True, GOLD)
        screen.blit(score_txt, (10, 10))
        screen.blit(coin_txt, (10, 40))
        if shield_timer > 0:
            sh_txt = font_small.render(f"SHIELD: {shield_timer//60}s", True, (56, 189, 248))
            screen.blit(sh_txt, (10, 70))

        if state == "GAMEOVER":
            s = pygame.Surface((WIDTH, HEIGHT))
            s.set_alpha(200); s.fill((0,0,0))
            screen.blit(s, (0,0))
            go = font_large.render("GAME OVER", True, RED)
            sc = font_med.render(f"Final Score: {score}", True, WHITE)
            cn = font_med.render(f"Coins: {coins}", True, GOLD)
            res = font_small.render("TAP ANYWHERE TO REPLAY", True, (34, 197, 94))
            
            screen.blit(go, (WIDTH//2 - go.get_width()//2, 200))
            screen.blit(sc, (WIDTH//2 - sc.get_width()//2, 260))
            screen.blit(cn, (WIDTH//2 - cn.get_width()//2, 300))
            
            if (frames // 30) % 2 == 0:
                screen.blit(res, (WIDTH//2 - res.get_width()//2, 400))
                
            if tap_detected:
                reset_game()
                state = "PLAYING"

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
