import pygame, math, random, struct, sys, io, wave, os

# --- Safe Initialization (Autoback / ANR Fix) ---
pygame.init(); pygame.font.init()
try:
    pygame.mixer.init(11025, -16, 1, 512)
    AUDIO_READY = True
except Exception: AUDIO_READY = False

WIDTH, HEIGHT = 400, 600
try: screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.FULLSCREEN)
except Exception: screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hyper Shift: Ultra Pro Max")
clock = pygame.time.Clock()

SKY_DAY, SKY_NIGHT = (56,189,248), (15,23,42)
SKY_SUN_T, SKY_SUN_B = (249, 115, 22), (253, 224, 71)
GR_T, GR_B = (34,197,94), (120,53,15)
WHITE, RED, GOLD = (255,255,255), (239,68,68), (250,204,21)

# --- Permanent Highscore System ---
high_score = 0
hs_file = "hyper_shift_hs.txt"
if os.path.exists(hs_file):
    try:
        with open(hs_file, "r") as f: high_score = int(f.read())
    except: pass

def save_hs(score):
    try:
        with open(hs_file, "w") as f: f.write(str(score))
    except: pass

# --- CPU Safe Gradient Cache ---
grad_cache = {}
def draw_grad(tc, bc, y, h):
    h = int(h)
    if h <= 0: return
    key = (tc, bc, h)
    if key not in grad_cache:
        surf = pygame.Surface((WIDTH, h))
        for i in range(h):
            r = i / h; c = (int(tc[0]*(1-r)+bc[0]*r), int(tc[1]*(1-r)+bc[1]*r), int(tc[2]*(1-r)+bc[2]*r))
            pygame.draw.line(surf, c, (0, i), (WIDTH, i))
        grad_cache[key] = surf
    screen.blit(grad_cache[key], (0, int(y)))

# --- Lightning Fast Audio Engine ---
def create_sound(freq, dur, vol=1.0, typ='sine'):
    if not AUDIO_READY: return None
    try:
        sr = 11025; ns = int(sr * dur); wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
            buf = bytearray()
            for i in range(ns):
                t = i / sr
                if typ == 'sine': v = math.sin(2 * math.pi * freq * t)
                elif typ == 'square': v = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
                else: v = 2.0 * (t * freq - math.floor(0.5 + t * freq))
                env = (i/200) if i<200 else ((ns-i)/200 if i>ns-200 else 1.0)
                samp = max(-32768, min(32767, int(v * env * vol * 32767.0)))
                buf += struct.pack('<h', samp)
            wf.writeframesraw(buf)
        wav_io.seek(0); return pygame.mixer.Sound(wav_io)
    except Exception: return None

SND_JUMP_B = create_sound(450, 0.15, 0.8, 'sine')
SND_JUMP_D = create_sound(220, 0.18, 1.0, 'square')
SND_COIN = create_sound(1200, 0.1, 0.7, 'sine')
SND_BREAK = create_sound(150, 0.3, 1.0, 'sawtooth')
SND_ROAR = create_sound(100, 0.8, 1.0, 'sawtooth') 
SND_MODE = create_sound(300, 0.5, 0.9, 'sawtooth')
SND_THUNDER = create_sound(80, 0.6, 1.0, 'sawtooth')
SND_BEEP = create_sound(600, 0.15, 0.8, 'sine')
SND_GO = create_sound(1000, 0.3, 1.0, 'square')

def play_sound(snd):
    if snd and AUDIO_READY:
        try: snd.play()
        except Exception: pass

try:
    font_lg = pygame.font.Font(None, 48)
    font_md = pygame.font.Font(None, 32)
    font_sm = pygame.font.Font(None, 24)
except Exception: font_lg = font_md = font_sm = None

def draw_text_outline(t, f, c, x, y):
    if f:
        screen.blit(f.render(t, True, (0,0,0)), (int(x)-1, int(y)-1))
        screen.blit(f.render(t, True, (0,0,0)), (int(x)+1, int(y)+1))
        screen.blit(f.render(t, True, c), (int(x), int(y)))

def draw_logo(x, y, sc):
    x, y = int(x), int(y)
    pygame.draw.circle(screen, (234,88,12), (x,y), int(50*sc))
    pygame.draw.circle(screen, GOLD, (x, y+int(10*sc)), int(35*sc))
    pygame.draw.polygon(screen, GOLD, [(x-int(25*sc), y-int(20*sc)), (x-int(45*sc), y-int(40*sc)), (x-int(10*sc), y-int(30*sc))])
    pygame.draw.polygon(screen, GOLD, [(x+int(25*sc), y-int(20*sc)), (x+int(45*sc), y-int(40*sc)), (x+int(10*sc), y-int(30*sc))])
    pygame.draw.circle(screen, WHITE, (x-int(12*sc), y), int(8*sc)); pygame.draw.circle(screen, WHITE, (x+int(12*sc), y), int(8*sc))
    pygame.draw.circle(screen, (0,0,0), (x-int(12*sc), y), int(3*sc)); pygame.draw.circle(screen, (0,0,0), (x+int(12*sc), y), int(3*sc))
    pygame.draw.polygon(screen, (0,0,0), [(x-int(8*sc), y+int(15*sc)), (x+int(8*sc), y+int(15*sc)), (x, y+int(25*sc))])

def draw_bird(x, y, fo):
    x, y, fo = int(x), int(y), int(fo)
    pygame.draw.polygon(screen, (234,88,12), [(x-20,y), (x-35,y-12), (x-35,y+12)])
    pygame.draw.circle(screen, GOLD, (x,y), 20)
    pygame.draw.ellipse(screen, WHITE, (x-10, y+fo-8, 20, 14))
    pygame.draw.polygon(screen, (249,115,22), [(x+18,y-5), (x+32,y), (x+18,y+5)])
    pygame.draw.circle(screen, WHITE, (x+10,y-8), 6); pygame.draw.circle(screen, (0,0,0), (x+12,y-8), 2)

def draw_dino(x, y, ro):
    x, y, ro = int(x), int(y), int(ro)
    pygame.draw.polygon(screen, (34,197,94), [(x-10,y+5), (x-25,y-10), (x-10,y-5)])
    pygame.draw.rect(screen, (34,197,94), (x-12, y-15, 24, 28))
    for i in range(3): pygame.draw.polygon(screen, (132,204,22), [(x-10+i*9, y-12), (x-6+i*9, y-20), (x-2+i*9, y-12)])
    pygame.draw.rect(screen, (34,197,94), (x+10, y-24, 26, 20)); pygame.draw.rect(screen, (34,197,94), (x+24, y-16, 14, 10))
    pygame.draw.circle(screen, WHITE, (x+26, y-18), 5); pygame.draw.circle(screen, (0, 0, 0), (x+28, y-18), 2)
    pygame.draw.rect(screen, (20,83,45), (x+8, y-5, 8, 4)); pygame.draw.rect(screen, (20,83,45), (x-6, y+13+ro, 6, 12))
    pygame.draw.rect(screen, (20,83,45), (x+6, y+13-ro, 6, 12))

score, coins, frames, state, state_t = 0, 0, 0, "WAIT", 0
hero_y, vel, mode = 200, 0, "FLAPPY"
speed, gap, spawn_rate = 4.0, 160, 110
shield, hp, nxt_sh, pipes_spawned = 0, 0, 5, 0
obs, items, smoke, coin_parts, evt, event_t = [], [], [], [], "NONE", 0
msg, msg_t, lightning_t = "", 0, 0

def reset_game():
    global score, coins, frames, speed, mode, hero_y, vel, shield, hp, nxt_sh, evt, event_t, msg_t, state_t, pipes_spawned, lightning_t
    score, coins, frames, speed, mode, pipes_spawned = 0, 0, 0, 4.0, "FLAPPY", 0
    hero_y, vel, shield, hp, nxt_sh, evt, event_t, lightning_t = 200, 0, 0, 0, 5, "NONE", 0, 0
    obs.clear(); items.clear(); smoke.clear(); coin_parts.clear(); msg_t, state_t = 0, 0

def spawn():
    global nxt_sh, pipes_spawned
    pipes_spawned += 1
    sh = False
    if score >= nxt_sh - 1: sh = True; nxt_sh += 5
    ox = WIDTH + random.randint(20, 50)
    
    is_red = (pipes_spawned % 4 == 0)

    if evt == "COINRUSH":
        wy = random.randint(340, 400) if mode == "DINO" else random.randint(160, 320)
        for c in range(4): items.append({"t": "COIN", "x": ox + c*40, "y": wy + random.randint(-10, 10)})
        return

    ob = {"x": ox, "p": False, "t": mode, "red": is_red}
    if mode == "FLAPPY":
        ob["g"] = gap
        if is_red:
            ob["th"] = random.randint(90, 500 - gap - 90)
            ob["dir"] = 1 if random.random() > 0.5 else -1
            ob["my"] = random.uniform(1.5, 2.5) 
        else:
            ob["th"] = random.randint(50, 500 - gap - 50)
            
        if sh: items.append({"t": "SHIELD", "x": ox+25, "y": ob["th"] + gap//2})
        elif random.random() < 0.4: items.append({"t": "COIN", "x": ox+25, "y": ob["th"] + gap//2})
    else:
        ob["pt"] = True if is_red else random.random() < 0.4
        if is_red:
            ob["y_pos"] = random.randint(330, 410)
            ob["dir"] = 1 if random.random() > 0.5 else -1
            ob["my"] = random.uniform(1.5, 2.5)

        if sh: items.append({"t": "SHIELD", "x": ox+20, "y": 380})
        elif random.random() < 0.5: items.append({"t": "COIN", "x": ox+20, "y": 380})
    obs.append(ob)
running = True
while running:
    tap, act_pos = False, None
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEBUTTONDOWN: tap, act_pos = True, event.pos
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: tap = True

    if state == "WAIT":
        draw_grad((185,28,28), (69,10,10), 0, HEIGHT)
        state_t += 1
        draw_logo(WIDTH//2, HEIGHT//2-50 + math.sin(state_t*0.1)*8, 1.2)
        draw_text_outline("ERROR GAMER", font_lg, WHITE, WIDTH//2-110, HEIGHT//2+40)
        if (state_t//20)%2==0: draw_text_outline("TAP TO BEGIN", font_md, GOLD, WIDTH//2-80, HEIGHT-100)
        if tap: state = "CUTSCENE"; state_t = 0; play_sound(SND_ROAR)

    elif state == "CUTSCENE":
        state_t += 1
        draw_grad(SKY_SUN_T, SKY_SUN_B, 0, HEIGHT*0.7)
        pygame.draw.circle(screen, (253, 224, 71), (WIDTH//2, int(HEIGHT*0.4)), 60)
        pygame.draw.polygon(screen, (22, 163, 74), [(0, int(HEIGHT*0.7)), (120, int(HEIGHT*0.45)), (250, int(HEIGHT*0.7))])
        pygame.draw.polygon(screen, (20, 83, 45), [(150, int(HEIGHT*0.7)), (320, int(HEIGHT*0.35)), (WIDTH, int(HEIGHT*0.7))])
        draw_grad(GR_T, GR_B, HEIGHT*0.7, HEIGHT*0.3)
        
        anim_x = WIDTH//2 - 150 + int((min(state_t, 120)/120)*150)
        draw_dino(anim_x, HEIGHT*0.7 - 25, math.sin(state_t * 0.4) * 6)
        draw_bird(anim_x + 40, HEIGHT*0.7 - 120, math.sin(state_t * 0.5) * 6)
        
        pygame.draw.rect(screen, (0,0,0), (0,0,WIDTH, 80)); pygame.draw.rect(screen, (0,0,0), (0,HEIGHT-80,WIDTH, 80))
        
        if state_t < 120: 
            draw_text_outline("GET READY...", font_lg, WHITE, WIDTH//2-100, HEIGHT*0.2)
        elif state_t < 180: 
            if state_t == 120: play_sound(SND_BEEP)
            draw_text_outline("3", font_lg, RED, WIDTH//2-10, HEIGHT*0.2)
        elif state_t < 240: 
            if state_t == 180: play_sound(SND_BEEP)
            draw_text_outline("2", font_lg, GOLD, WIDTH//2-10, HEIGHT*0.2)
        elif state_t < 300: 
            if state_t == 240: play_sound(SND_BEEP)
            draw_text_outline("1", font_lg, (34, 197, 94), WIDTH//2-10, HEIGHT*0.2)
        elif state_t < 360: 
            if state_t == 300: play_sound(SND_GO)
            draw_text_outline("GO!", font_lg, WHITE, WIDTH//2-30, HEIGHT*0.2)
        else: state = "PLAYING"

    elif state in ["PLAYING", "PAUSE", "GAMEOVER"]:
        if state == "PLAYING":
            frames += 1
            level = (score // 5)
            speed = min(8.5, 4.0 + (level * 0.4))
            
            if score > 0 and score % 8 == 0 and event_t <= 0:
                rc = random.random()
                evt = "WIND" if rc < 0.25 else ("STORM" if rc < 0.5 else ("COINRUSH" if rc < 0.75 else "LOW_GRAV"))
                event_t = 300; play_sound(SND_MODE)
            if event_t > 0:
                event_t -= 1
                if event_t <= 0: evt = "NONE"
            if frames % max(10, int(spawn_rate*(4.0/speed))) == 0: spawn()

            if tap:
                if act_pos and act_pos[0] > WIDTH-60 and act_pos[1] < 60: state = "PAUSE"
                else:
                    if mode == "FLAPPY":
                        vel = -5.5 if evt=="WIND" else (-9.0 if evt=="LOW_GRAV" else -8.0); play_sound(SND_JUMP_B)
                    else:
                        if hero_y >= 500-25: vel = -16.5 if evt=="LOW_GRAV" else -18.5; play_sound(SND_JUMP_D)

            grav = 0.6 if evt=="WIND" else (0.3 if evt=="LOW_GRAV" else (0.5 if mode=="FLAPPY" else 1.2))
            vel += grav; hero_y += vel

            if mode == "FLAPPY":
                if hero_y >= 500-20:
                    if hp > 0: hp-=1; shield=0; vel=-8; play_sound(SND_BREAK)
                    else: 
                        state = "GAMEOVER"; play_sound(SND_BREAK)
                        if score > high_score: high_score = score; save_hs(high_score)
                if hero_y <= 0: hero_y=0; vel=0
            else:
                if hero_y >= 500-25: hero_y = 500-25; vel=0
            if shield > 0: shield -= 1; hp = 0 if shield <= 0 else hp

        if state == "PLAYING" and frames % 2 == 0:
            smoke.append({"x": 60-15 if mode=="DINO" else 60-25, "y": int(hero_y)+10, "s": random.randint(6,12), "a": 180})
        
        for sp in smoke[:]:
            sp["x"] -= speed*0.8; sp["s"] += 0.4; sp["a"] -= 12
            if sp["a"] <= 0: smoke.remove(sp)
            
        for cp in coin_parts[:]:
            cp["x"] += cp["vx"]; cp["y"] += cp["vy"]; cp["life"] -= 1
            if cp["life"] <= 0: coin_parts.remove(cp)

        bg = (10,10,30) if evt=="STORM" else (SKY_DAY if score%30<15 else SKY_NIGHT)
        draw_grad(bg, (224,242,254) if bg==SKY_DAY else (30,27,75), 0, 500)
        draw_grad(GR_T, GR_B, 500, 100)
        
        if lightning_t > 0:
            lightning_t -= 1
            if lightning_t % 4 > 1: draw_grad(WHITE, WHITE, 0, 600)

        for sp in smoke:
            c_val = max(100, min(255, int(sp["a"])))
            pygame.draw.circle(screen, (c_val, c_val, c_val), (int(sp["x"]), int(sp["y"])), int(sp["s"]))

        if evt == "WIND":
            for i in range(8): pygame.draw.line(screen, WHITE, (int((frames*18+i*70)%WIDTH), int(80+i*55)), (int((frames*18+i*70)%WIDTH)+50, int(80+i*55)), 2)
        elif evt == "STORM":
            for i in range(12): pygame.draw.line(screen, (170,210,255), (int((frames*25+i*50)%WIDTH), int((frames*35+i*40)%450)), (int((frames*25+i*50)%WIDTH)-8, int((frames*35+i*40)%450)+20), 2)

        hx, hw, hy, hh = 60, 40, hero_y, 40 if mode=="FLAPPY" else 50
        h_rect = pygame.Rect(hx-20, int(hy-20), hw, hh)

        for it in reversed(items):
            it["x"] -= speed
            i_rect = pygame.Rect(int(it["x"])-12, int(it["y"])-12, 24, 24)
            if h_rect.colliderect(i_rect):
                if it["t"] == "SHIELD": shield = 300; hp = 1; play_sound(SND_COIN)
                elif it["t"] == "COIN": 
                    coins += 1; play_sound(SND_COIN)
                    for _ in range(8): coin_parts.append({"x": it["x"], "y": it["y"], "vx": random.uniform(-3,3), "vy": random.uniform(-3,3), "life": 20})
                items.remove(it); continue
            if it["x"] < -30: items.remove(it); continue
            pygame.draw.circle(screen, (56,189,248) if it["t"]=="SHIELD" else GOLD, (int(it["x"]), int(it["y"])), 12)
            pygame.draw.circle(screen, WHITE, (int(it["x"]), int(it["y"])), 12, 2)

        for cp in coin_parts:
            pygame.draw.circle(screen, GOLD, (int(cp["x"]), int(cp["y"])), 3)

        for o in reversed(obs):
            o["x"] -= speed; hit = False
            
            if o["t"] == "FLAPPY":
                if o.get("red"):
                    o["th"] += o["dir"] * o["my"]
                    if o["th"] < 80 or o["th"] > 500 - o["g"] - 80: o["dir"] *= -1
                
                t_rect = pygame.Rect(int(o["x"]), 0, 50, int(o["th"]))
                b_rect = pygame.Rect(int(o["x"]), int(o["th"]+o["g"]), 50, int(500-(o["th"]+o["g"])))
                pipe_c = (220, 38, 38) if o.get("red") else (6, 95, 70)
                pygame.draw.rect(screen, pipe_c, t_rect); pygame.draw.rect(screen, pipe_c, b_rect)
                if h_rect.colliderect(t_rect) or h_rect.colliderect(b_rect): hit = True
            else:
                if o.get("pt"):
                    if o.get("red"):
                        o["y_pos"] += o["dir"] * o["my"]
                        if o["y_pos"] < 320 or o["y_pos"] > 420: o["dir"] *= -1
                        py = int(o["y_pos"])
                    else: py = 500-110
                    
                    px = int(o["x"])
                    body_c = (220,38,38) if o.get("red") else (126,34,206)
                    wing_c = (248,113,113) if o.get("red") else (168,85,247)
                    pygame.draw.ellipse(screen, body_c, (px, py, 44, 22))
                    pygame.draw.polygon(screen, wing_c, [(px+12,py+11), (px+22,py-6), (px+32,py+11)])
                    if h_rect.colliderect(pygame.Rect(px, py, 44, 22)): hit = True
                else:
                    cx, cy = int(o["x"]), 500-45
                    pygame.draw.rect(screen, (34,139,34), (cx+4, cy, 16, 45), border_radius=4) 
                    pygame.draw.rect(screen, (34,139,34), (cx, cy+12, 8, 14), border_radius=3)
                    pygame.draw.rect(screen, (34,139,34), (cx+16, cy+18, 8, 14), border_radius=3)
                    if h_rect.colliderect(pygame.Rect(cx, cy, 24, 45)): hit = True

            if hit:
                if hp > 0: hp-=1; shield=0; obs.remove(o); play_sound(SND_BREAK); continue
                else: 
                    play_sound(SND_BREAK); state = "GAMEOVER"
                    if score > high_score: high_score = score; save_hs(high_score)
            
            if not o["p"] and o["x"] < 50:
                score += 1; o["p"] = True
                
                if score > 0 and score % 3 == 0:
                    lightning_t = 15; play_sound(SND_THUNDER)
                    
                if score > 0 and score % 5 == 0 and score % 15 != 0:
                    msg = f"LEVEL {score//5 + 1} - SPEED UP!"
                    msg_t = 90; play_sound(SND_COIN)

                if score > 0 and score % 15 == 0:
                    mode = "DINO" if mode == "FLAPPY" else "FLAPPY"
                    obs.clear(); items.clear(); hero_y = 500-25 if mode=="DINO" else 200
                    vel = 0; msg = f"LEVEL {score//5 + 1}: {mode} MODE!"; msg_t = 120; play_sound(SND_COIN)
            
            if o["x"] < -60: obs.remove(o)

        if shield > 0: 
            pulse = abs(math.sin(frames*0.1)) * 5
            pygame.draw.circle(screen, (56,189,248), (60, int(hero_y)), int(30 + pulse), 3)
            
        if mode == "FLAPPY": draw_bird(60, hero_y, math.sin(frames*0.5)*6)
        else: draw_dino(60, hero_y, math.sin(frames*0.8)*5 if vel==0 else 0)

        draw_text_outline(f"SCORE: {score}", font_md, WHITE, 10, 10)
        draw_text_outline(f"COINS: {coins}", font_md, GOLD, 10, 40)
        draw_text_outline(f"HIGH: {high_score}", font_sm, (200,200,200), 10, 70)
        
        pygame.draw.rect(screen, (50,50,50), (WIDTH-50, 10, 40, 30))
        pygame.draw.rect(screen, WHITE, (WIDTH-50, 10, 40, 30), 2)
        pygame.draw.rect(screen, WHITE, (WIDTH-38, 17, 4, 16)); pygame.draw.rect(screen, WHITE, (WIDTH-28, 17, 4, 16))

        if shield > 0: draw_text_outline(f"SHIELD: {shield//60}s", font_sm, (56,189,248), 10, 95)
        if evt != "NONE" and (frames//15)%2==0: draw_text_outline(f"WARNING: {evt}!", font_md, RED, WIDTH//2-90, 120)
        if msg_t > 0: msg_t -= 1; draw_text_outline(msg, font_md, GOLD, WIDTH//2-140, 160)

        if state == "PAUSE":
            s = pygame.Surface((WIDTH, HEIGHT)); s.set_alpha(200); screen.blit(s, (0,0))
            draw_text_outline("PAUSED", font_lg, WHITE, WIDTH//2-70, HEIGHT//2-100)
            rb = pygame.Rect(WIDTH//2-100, HEIGHT//2-20, 200, 50); qb = pygame.Rect(WIDTH//2-100, HEIGHT//2+50, 200, 50)
            pygame.draw.rect(screen, (34,197,94), rb); pygame.draw.rect(screen, (239,68,68), qb)
            draw_text_outline("RESUME", font_md, WHITE, WIDTH//2-50, HEIGHT//2-5)
            draw_text_outline("RESTART", font_md, WHITE, WIDTH//2-55, HEIGHT//2+65)
            if tap and act_pos:
                if rb.collidepoint(act_pos): state = "PLAYING"
                elif qb.collidepoint(act_pos): reset_game(); state = "CUTSCENE"; state_t = 119

        if state == "GAMEOVER":
            s = pygame.Surface((WIDTH, HEIGHT)); s.set_alpha(200); screen.blit(s, (0,0))
            draw_text_outline("GAME OVER", font_lg, RED, WIDTH//2-100, 170)
            draw_text_outline(f"Score: {score}", font_md, WHITE, WIDTH//2-50, 230)
            draw_text_outline(f"Coins: {coins}", font_md, GOLD, WIDTH//2-50, 270)
            rb = pygame.Rect(WIDTH//2-100, 350, 200, 50); pygame.draw.rect(screen, (34,197,94), rb)
            draw_text_outline("RESTART", font_md, WHITE, WIDTH//2-55, 365)
            if tap and act_pos and rb.collidepoint(act_pos): reset_game(); state = "CUTSCENE"; state_t = 119

    pygame.display.flip(); clock.tick(60)

pygame.quit(); sys.exit()
        
