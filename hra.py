import pygame
import pygame.gfxdraw
import math
import random
import config
from fyzika import Vector, Bike

pygame.init()

import fyzika

screen = pygame.display.set_mode((config.obrazovka_sirka, config.obrazovka_vyska))
pygame.display.set_caption("Tour de Bike")

vyska_travy = 50

FONTY = {}

def nahrat_obrazky(kolo):
    global pomer
    obrazky = []
    
    for i in range(14):
        if i < 10:
            img = pygame.image.load(f"img/{kolo}/kolo000{i}.png").convert_alpha()
        else:
            img = pygame.image.load(f"img/{kolo}/kolo00{i}.png").convert_alpha()
        img_sirka = img.get_width()
        img_vyska = img.get_height()
        pomer = config.BIKE_LENGTH / img_sirka
        img = pygame.transform.smoothscale(img, (img_sirka * pomer, img_vyska * pomer))
        obrazky.append(img)
    return obrazky

def blit_rotate_bottom_left(surf, image, bottom_left_pos, angle):
    global maska_kola, kolo_pos
    offset_y = pomer * 80

    image_rect = image.get_rect()
    width, height = image_rect.size
    offset_center_to_bl = pygame.math.Vector2(-width / 2, height / 2 - offset_y)
    rotated_offset = offset_center_to_bl.rotate(-angle)
    rotated_center = (bottom_left_pos[0] - rotated_offset.x, bottom_left_pos[1] - rotated_offset.y)
    rotated_image = pygame.transform.rotozoom(image, angle, 1.0)
    new_rect = rotated_image.get_rect(center=rotated_center)
    maska_kola = pygame.mask.from_surface(rotated_image)
    kolo_pos = (new_rect.left, new_rect.top)

    surf.blit(rotated_image, new_rect.topleft)

def get_font(velikost, font):
    klic = (velikost, font)
    if klic not in FONTY:
        FONTY[klic] = pygame.font.SysFont(font, velikost)
    return FONTY[klic]

def vykresli_text(surf, text, barva, pozice, zarovnat="left", velikost=50, font="Arial", bold=False, podrtzeny=False, shadow=False, shadow_offset=(3, 3)):
    pismo = get_font(velikost,font)
    pismo.set_bold(bold)
    pismo.set_underline(podrtzeny)
    text_surface = pismo.render(text, True, barva)
    text_rect = text_surface.get_rect()
    if zarovnat == "left":
        text_rect.topleft = pozice
    elif zarovnat == "center":
        text_rect.center = pozice
    elif zarovnat == "right":
        text_rect.topright = pozice

    if shadow:
        shadow_surface = pismo.render(text, True, (0,0,0))
        shadow_rect = shadow_surface.get_rect()
        if zarovnat == "left":
            shadow_rect.topleft = (pozice[0] + shadow_offset[0], pozice[1] + shadow_offset[1])
        elif zarovnat == "center":
            shadow_rect.center = (pozice[0] + shadow_offset[0], pozice[1] + shadow_offset[1])
        elif zarovnat == "right":
            shadow_rect.topright = (pozice[0] + shadow_offset[0], pozice[1] + shadow_offset[1])
        surf.blit(shadow_surface, shadow_rect)

    surf.blit(text_surface, text_rect)

def vykresli_tlacitko(surface, text, rect, barva_textu=(255,255,255), barva_pozadi=(0, 70, 140), barva_okraje=(0,0,0), tloustka_okraje=2, velikost_pisma=50, font="Arial", shadow=False):
    pygame.draw.rect(surface, barva_pozadi, rect)

    if tloustka_okraje > 0:
        pygame.draw.rect(surface, barva_okraje, rect, tloustka_okraje)

    vykresli_text(surface, text, barva_textu, rect.center, "center", velikost_pisma, font, shadow=shadow)

class EnergetickyPredmet(pygame.sprite.Sprite):
    def __init__(self, x, y, obrazek, pridavek_energie):
        super().__init__()
        self.svet_x = x
        self.svet_y = y
        self.pridavek_energie = pridavek_energie
        self.image = obrazek
        self.mask = pygame.mask.from_surface(self.image)

    def vykresli(self, screen, kamera_x, kamera_y):
        screen.blit(self.image, (self.svet_x - kamera_x, self.svet_y - kamera_y))

    def get_mask(self):
        return self.mask
    
    def get_position(self):
        return int(self.svet_x), int(self.svet_y)
    
class Mince(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.svet_x = x
        self.svet_y = y
        self.image = mince_img
        self.mask = pygame.mask.from_surface(self.image)

    def vykresli(self, screen, kamera_x, kamera_y):
        screen.blit(self.image, (self.svet_x - kamera_x, self.svet_y - kamera_y))

    def get_mask(self):
        return self.mask

    def get_position(self):
        return int(self.svet_x), int(self.svet_y)

class Particle:
    def __init__(self, pos):
        self.x, self.y = pos
        self.rychlost_x = random.uniform(-1, 1)
        self.rychlost_y = random.uniform(-2, 0)
        self.zivot = random.randint(20, 40)
    
    def update(self):
        self.x += self.rychlost_x
        self.y += self.rychlost_y
        self.rychlost_y += 0.1  
        self.zivot -= 1

    def draw(self, surface, camera, barva):
        if self.zivot > 0:
            pygame.draw.circle(surface, barva, (int(self.x - camera.x), int(self.y - camera.y)),4)

def vykresli_ui(screen, km, energie, kolo_x, rychlost, cas, uhel_rucicky, fps, jidlo_img):
    vykresli_text(screen, f"Distance: {round(km/1000,1)} km", (255,255,255), (20, 20), shadow=True)

    pygame.draw.rect(screen, (50, 50, 50), (20, 90, 250, 40), border_radius=10)
    if energie > 0:
        pygame.draw.rect(screen, (255, 215, 0), (20, 90, 2.5 * energie, 40), border_radius=10)
    pygame.draw.rect(screen, (0, 0, 0), (20, 90, 250, 40), 2, border_radius=10)

    screen.blit(tachometr_img, (50, 650))

    sekundy = cas // 1000
    minuty = sekundy // 60
    hodiny = minuty // 60
    sekundy = sekundy % 60
    minuty = minuty % 60

    vykresli_text(screen, f"{hodiny}:{minuty}:{sekundy}", (255, 255, 255), (252, 970), zarovnat="center", velikost=30)

    stred_x = 250
    stred_y = 845
    delka_rucicky = 170
    cilovy_uhel = -220 + rychlost * 262

    novy_uhel = uhel_rucicky + (cilovy_uhel - uhel_rucicky) * 0.15

    uhel_rad = math.radians(novy_uhel)
    konec_x = stred_x + delka_rucicky * math.cos(uhel_rad)
    konec_y = stred_y + delka_rucicky * math.sin(uhel_rad)
    pygame.draw.line(screen, (255, 0, 0), (stred_x, stred_y), (konec_x, konec_y), 6)

    if energie_predmety:
        predmety_vpravo = []
        for predmet in energie_predmety:
            if predmet.svet_x > kolo_x:
                predmety_vpravo.append(predmet)

        nejblizsi = None
        nejmensi_vzdalenost = None

        for predmet in predmety_vpravo:
            rozdil = predmet.svet_x - kolo_x
            if nejmensi_vzdalenost is None or rozdil < nejmensi_vzdalenost:
                nejblizsi = predmet
                nejmensi_vzdalenost = rozdil

        if nejblizsi:
            vzdalenost = nejblizsi.svet_x - kolo_x
            text = f"{round(vzdalenost/1000,1)} km →"
            font = get_font(50, "Arial")
            text_sirka,text_vyska = font.size(text)

            obrazek_sirka = jidlo_img.get_width()
            obrazek_vyska = jidlo_img.get_height()

            total_width = text_sirka + obrazek_sirka + 10
            x = config.obrazovka_sirka - total_width - 20  

            y_centr = 200 

            obrazek_y = y_centr - obrazek_vyska // 2
            text_y = y_centr - text_vyska // 2
            screen.blit(jidlo_img, (x, obrazek_y))

            vykresli_text(screen, text, (255,255,255), (config.obrazovka_sirka - 20, text_y), zarovnat="right", shadow=True)

    vykresli_text(screen, f"{config.prachy} $", (255, 215, 0), (20, 145), shadow=True)

    if config.fps:
        vykresli_text(screen, f"FPS: {int(fps)}", (255,255,255), (20, 210), shadow=True)

    return novy_uhel

def vykresli_teren(screen, kamera_x, kamera_y, kaminky, barva_trava, barva_hlina, barva_kamen):
    
    body_trava = [[0, config.obrazovka_vyska]]
    body_hlina = [[0, config.obrazovka_vyska]]
    body_hrana = []

    x_svet = kamera_x - (kamera_x % config.krok)
    x = int(x_svet)
    body_trava.append([0, fyzika.generace_bod(x)-kamera_y])
    klice_na_smazani = []

    while x < kamera_x + config.obrazovka_sirka + 2 * config.krok:
        x_obrazovka = x - kamera_x

        if not(config.potato_pc) and (x < kamera_x - 2 * config.obrazovka_sirka or x > kamera_x + 2 * config.obrazovka_sirka):
            klice_na_smazani.append(x)

        y = fyzika.generace_bod(x) - kamera_y
        body_trava.append([x_obrazovka, y])

        if len(body_trava) > 1:
            perp_vec = (Vector(*body_trava[-1]) - Vector(*body_trava[-2])).perpendicular()
            if perp_vec.y < 0:
                perp_vec *= -1
            hlina_vec = Vector(x_obrazovka, y) + perp_vec * vyska_travy
            body_hlina.append([hlina_vec.x, hlina_vec.y])
            body_hrana.append((x_obrazovka, y))

            kx = int(hlina_vec.x + kamera_x)
            if not(config.potato_pc) and kaminky is not None and kx not in kaminky:
                ky = hlina_vec.y + kamera_y
                segment_kaminky = [
                    (
                        random.randint(kx,kx+config.krok),
                        random.randint(int(ky+20),int(ky+config.obrazovka_vyska + 20)),
                        random.randint(1, 5)
                    )
                    for _ in range(5)
                ]
                kaminky[kx] = segment_kaminky

        x += config.krok

    if not(config.potato_pc):
        for klic in klice_na_smazani:
            if klic in kaminky:
                del kaminky[klic]

    body_trava.append([config.obrazovka_sirka, fyzika.generace_bod(kamera_x + config.obrazovka_sirka + config.krok) - kamera_y])
    body_trava.append([config.obrazovka_sirka, config.obrazovka_vyska])

    body_hlina.append([config.obrazovka_sirka, fyzika.generace_bod(kamera_x + config.obrazovka_sirka + config.krok) + vyska_travy - kamera_y])
    body_hlina.append([config.obrazovka_sirka, config.obrazovka_vyska])

    pygame.gfxdraw.filled_polygon(screen, body_trava, barva_trava)
    pygame.gfxdraw.filled_polygon(screen, body_hlina, barva_hlina)

    if not(config.potato_pc) and kaminky is not None:
        for _, segment in kaminky.items():
            for kx, ky, r in segment:
                if kamera_x < kx < kamera_x + config.obrazovka_sirka and int(ky - kamera_y) < config.obrazovka_vyska:
                    pygame.draw.circle(screen, barva_kamen, (int(kx - kamera_x), int(ky - kamera_y)), r)

    pygame.draw.lines(screen, (0, 0, 0), False, body_hrana, 2)

def vykresli_kolo(kolo, camera, rafek_img, kolo_img):
    global rafek_mask_front, rafek_mask_rear, rafek_pos_front, rafek_pos_rear, uhel
    rafek_rear_rot = pygame.transform.rotozoom(rafek_img, (kolo.rear_wheel.get_position().x / (config.WHEEL_RADIUS)) * (-180 / math.pi), 1.0)
    rafek_mask_rear = pygame.mask.from_surface(rafek_rear_rot)
    rafek_front_rot = pygame.transform.rotozoom(rafek_img, (kolo.front_wheel.get_position().x / (config.WHEEL_RADIUS)) * (-180 / math.pi), 1.0)
    rafek_mask_front = pygame.mask.from_surface(rafek_front_rot)

    rafek_rect_rear = rafek_rear_rot.get_rect(center=(int(kolo.rear_wheel.position.x - camera.x), int(kolo.rear_wheel.position.y - camera.y)))
    rafek_pos_rear = (rafek_rect_rear.left, rafek_rect_rear.top)
    rafek_rect_front = rafek_front_rot.get_rect(center=(int(kolo.front_wheel.position.x - camera.x), int(kolo.front_wheel.position.y - camera.y)))
    rafek_pos_front = (rafek_rect_front.left, rafek_rect_front.top)

    screen.blit(rafek_rear_rot, rafek_rect_rear.topleft)
    screen.blit(rafek_front_rot, rafek_rect_front.topleft)

    center = kolo.rear_axel.position
    uhel = (-180 / math.pi) * math.atan2(kolo.front_axel.position.y - kolo.rear_axel.position.y, kolo.front_axel.position.x - kolo.rear_axel.position.x)
    blit_rotate_bottom_left(screen, kolo_img, (int(center.x - camera.x), int(center.y - camera.y)), uhel)

def vykresli_mraky(screen, kamera_x, kamera_y, mraky, mapa):
    for m in mraky:
        x = int(m["x"] - kamera_x * m["parallax"])
        y = int(m["y"] - kamera_y * m["parallax"])
        if mapa == 1:
            img = pygame.transform.smoothscale(hvezda_img, (int(hvezda_img.get_width() * m["velikost"]), int(hvezda_img.get_height() * m["velikost"])))
        else:
            img = pygame.transform.smoothscale(mrak_img, (int(mrak_img.get_width() * m["velikost"]), int(mrak_img.get_height() * m["velikost"])))
        if x < -img.get_width():
            m["x"] += config.obrazovka_sirka * 2 + img.get_width()
            x = int(m["x"] - kamera_x * m["parallax"])
        elif x > config.obrazovka_sirka + img.get_width():
            m["x"] -= config.obrazovka_sirka * 2 + img.get_width()
            x = int(m["x"] - kamera_x * m["parallax"])
        screen.blit(img, (x, y))

def pause_menu(screen, km_ujet):
    config.uloz_config()
    paused = True
    posledni_snimek = screen.copy()
    pokracovat_rect = pygame.Rect(config.obrazovka_sirka//2 - 200, 400, 400, 100)
    restart_rect = pygame.Rect(config.obrazovka_sirka//2 - 200, 550, 400, 100)
    menu_rect = pygame.Rect(config.obrazovka_sirka//2 - 200, 700, 400, 100)
    while paused:
        screen.blit(posledni_snimek, (0, 0))
        pruhledna_cerna = pygame.Surface((config.obrazovka_sirka, config.obrazovka_vyska), pygame.SRCALPHA)
        pruhledna_cerna.fill((0, 0, 0, 140))
        screen.blit(pruhledna_cerna, (0, 0))
        vykresli_text(screen, "Paused", (255, 255, 255), (config.obrazovka_sirka//2, 250), "center", 200, shadow=True)

        vykresli_tlacitko(screen, "Continue", pokracovat_rect, shadow=True)
        vykresli_tlacitko(screen, "Restart", restart_rect, shadow=True)
        vykresli_tlacitko(screen, "Back to menu", menu_rect, shadow=True)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                config.uloz_config()
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "pokracovat"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pokracovat_rect.collidepoint(event.pos):
                    zvuky["ui_click"].play()
                    return "pokracovat"
                elif restart_rect.collidepoint(event.pos):
                    zvuky["ui_click"].play()
                    return "restart"
                elif menu_rect.collidepoint(event.pos):
                    km_ujet = round(km_ujet/1000, 2)
                    if km_ujet > config.rekordy[config.vybrana_mapa]:
                        config.rekordy[config.vybrana_mapa] = km_ujet
                    zvuky["ui_click"].play()
                    return "menu"

def konec_menu(screen, km_ujet, run_prachy, proc):
    config.uloz_config()
    zvuky["smrt"].play()
    konec = True
    posledni_snimek = screen.copy()
    restart_rect = pygame.Rect(config.obrazovka_sirka//4 - 200, 690, 400, 100)
    menu_rect = pygame.Rect(config.obrazovka_sirka//4 - 200, 840, 400, 100)
    
    km_ujet = round(km_ujet/1000, 2)

    if km_ujet > config.rekordy[config.vybrana_mapa]:
        config.rekordy[config.vybrana_mapa] = km_ujet

    while konec:
        screen.blit(posledni_snimek, (0,0))
        pruhledna_cerna = pygame.Surface((config.obrazovka_sirka, config.obrazovka_vyska), pygame.SRCALPHA)
        pruhledna_cerna.fill((0, 0, 0, 140))
        screen.blit(pruhledna_cerna, (0, 0))

        vykresli_text(screen, f"Game Over", (255, 80, 80), (config.obrazovka_sirka//4,  250), "center", 150, shadow=True)
        vykresli_text(screen, f"{proc}", (247, 153, 153), (config.obrazovka_sirka//4,  370), "center", 70, shadow=True)
        vykresli_text(screen, f"This run: {run_prachy} $", (255, 215, 0), (config.obrazovka_sirka//4, 450), "center", 70, shadow=True)
        vykresli_text(screen, f"Total: {config.prachy} $", (255, 215, 0), (config.obrazovka_sirka//4, 530), "center", 70, shadow=True)
        vykresli_text(screen, f"Distance: {km_ujet} km", (255, 255, 255), (config.obrazovka_sirka//4, 610), "center", 70, shadow=True)


        vykresli_tlacitko(screen, "Restart", restart_rect, shadow=True)
        vykresli_tlacitko(screen, "Back to menu", menu_rect, shadow=True)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                config.uloz_config()
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_rect.collidepoint(event.pos):
                    zvuky["ui_click"].play()
                    return "restart"
                elif menu_rect.collidepoint(event.pos):
                    zvuky["ui_click"].play()
                    return "menu"

banan_img = pygame.image.load("img/banan.png").convert_alpha()
k = 70 / banan_img.get_width()
banan_img = pygame.transform.smoothscale(banan_img, (int(banan_img.get_width() * k), int(banan_img.get_height() * k)))
banan_energie = 30

tycinka_img = pygame.image.load("img/tycinka.png").convert_alpha()
k = 120 / tycinka_img.get_width()
tycinka_img = pygame.transform.smoothscale(tycinka_img, (int(tycinka_img.get_width() * k), int(tycinka_img.get_height() * k)))
tycinka_energie = 50

kure_img = pygame.image.load("img/kure.png").convert_alpha()
k = 85 / kure_img.get_width()
kure_img = pygame.transform.smoothscale(kure_img, (int(kure_img.get_width() * k), int(kure_img.get_height() * k)))
kure_energie = 100

energie_predmety = pygame.sprite.Group()

mince_img = pygame.image.load("img/mince.png").convert_alpha()
k = 60 / mince_img.get_width()
mince_img = pygame.transform.smoothscale(mince_img, (int(mince_img.get_width() * k), int(mince_img.get_height() * k)))

mince_predmety = pygame.sprite.Group()
vzadelnost_minci = 500

rafek_img = pygame.image.load("img/rafek.png").convert_alpha()
rafek_img = pygame.transform.smoothscale(rafek_img, (config.WHEEL_RADIUS * 2, config.WHEEL_RADIUS * 2))

tachometr_img = pygame.image.load("img/tachometr.png").convert_alpha()
tachometr_img = pygame.transform.smoothscale(tachometr_img, (400, 400))

obloha_img = pygame.image.load("img/obloha.png").convert()
obloha_img = pygame.transform.smoothscale(obloha_img, (config.obrazovka_sirka, config.obrazovka_vyska))

obloha_mesic_img = pygame.image.load("img/mapy/mesic_pozadi.png").convert()
obloha_img = pygame.transform.smoothscale(obloha_img, (config.obrazovka_sirka, config.obrazovka_vyska))

mrak_img = pygame.image.load("img/mrak.png").convert_alpha()
mrak_img = pygame.transform.smoothscale(mrak_img, (mrak_img.get_width() // 2, mrak_img.get_height() // 2))

hvezda_img = pygame.image.load("img/mapy/hvezda.png").convert_alpha()
hvezda_img = pygame.transform.smoothscale(hvezda_img, (hvezda_img.get_width() // 4, hvezda_img.get_height() // 4))

zvuky = {
    "ui_click": pygame.mixer.Sound("sounds/ui_click.mp3"),
    "coin": pygame.mixer.Sound("sounds/coin.mp3"),
    "jidlo_eat": pygame.mixer.Sound("sounds/jidlo_eat.mp3"),
    "smrt": pygame.mixer.Sound("sounds/smrt.mp3"),
    "flip": pygame.mixer.Sound("sounds/flip.mp3"),
    "start": pygame.mixer.Sound("sounds/start.mp3")
}

for i in zvuky.values():
    i.set_volume(config.volume_sound)

rust_vzdalenosti = 200

def rotace_bodu(bod, pivot, uhel_stupne):
    uhel_rad = math.radians(uhel_stupne)
    x, y = bod
    piv_x, piv_y = pivot

    dx = x - piv_x
    dy = y - piv_y

    x_rot = dx * math.cos(uhel_rad) - dy * math.sin(uhel_rad)
    y_rot = dx * math.sin(uhel_rad) + dy * math.cos(uhel_rad)

    return (x_rot + piv_x, y_rot + piv_y)

def main():
    ram_obrazky = nahrat_obrazky(config.vybrane_kolo)

    vybrana_mapa = config.vybrana_mapa
    
    if not(config.potato_pc):
        mraky = []
        if not config.potato_pc:
            for vrstva in range(3):
                parallax = 0.15 + 0.2 * vrstva
                for i in range(2):
                    x = random.randint(0, config.obrazovka_sirka * 2)
                    y = vrstva * 10 - random.randint(70, 80)
                    velikost = 0.7 + 0.3 * random.random()
                    mraky.append({
                        "x": x,
                        "y": y,
                        "parallax": parallax,
                        "velikost": velikost,
                        "vrstva": vrstva
                    })


        kaminky = {}
        
        particly = []
        na_zemi_predni = False
        na_zemi_zadni = False


    if vybrana_mapa == 1:  # mesic
        config.GRAVITY = (0, 0.1)
    else:
        config.GRAVITY = (0, 0.2)

    if vybrana_mapa == 1:  # mesic
        barva_trava = (166, 166, 166)
        barva_hlina = (232, 232, 232)
        barva_kamen = (200, 200, 200)
    elif vybrana_mapa == 2: # dalnice
        barva_trava = (60, 60, 60)      
        barva_hlina = (100, 100, 100)   
        barva_kamen = (180, 180, 180)
    elif vybrana_mapa == 3: # duny
        barva_trava = (242, 222, 163) 
        barva_hlina = (210, 180, 100)   
        barva_kamen = (153, 140, 101)
    else:
        barva_trava = (0, 154, 23)
        barva_hlina = (120, 72, 0)
        barva_kamen = (80, 60, 40)

    start_cas = pygame.time.get_ticks()
    bezi = True

    # https://gafferongames.com/post/fix_your_timestep/
    clock = pygame.time.Clock()
    dt = 1.0 / 60
    accumulator = 0.0
    t = 0.0
    posledni_cas = pygame.time.get_ticks() / 1000.0
    
    kolo = Bike(Vector(0, fyzika.generace_bod(0)-200))
    kolo_predchozi = Bike(Vector(0, fyzika.generace_bod(0)-200))
    kolo_predchozi.copy_state_from(kolo)

    km_ujet = 0
    vzdalenost_predmetu = 1000
    kolikaty_banan = 0

    if config.vybrane_jidlo == 0:
        jidlo_img = banan_img
        jidlo_energie = banan_energie
    elif config.vybrane_jidlo == 1:
        jidlo_img = tycinka_img
        jidlo_energie = tycinka_energie
    elif config.vybrane_jidlo == 2:
        jidlo_img = kure_img
        jidlo_energie = kure_energie
    else:
        jidlo_img = banan_img
        jidlo_energie = banan_energie

    posledni_mince = 0

    camera = Vector(0, 0)

    pause_tlacitko_polomer = 50
    pause_tlacitko_center = (config.obrazovka_sirka - pause_tlacitko_polomer - 30, pause_tlacitko_polomer + 30)
    pause_tlacitko_rect = pygame.Rect(
        pause_tlacitko_center[0] - pause_tlacitko_polomer,
        pause_tlacitko_center[1] - pause_tlacitko_polomer,
        pause_tlacitko_polomer * 2,
        pause_tlacitko_polomer * 2
    )

    hlava_sirka = 140 * pomer
    hlava_vyska = 140 * pomer
    offset_x = 390 * pomer
    offset_y = -570 * pomer
    
    energie_predmety.empty()
    mince_predmety.empty()

    uhel_rucicky = -220 

    zvuky["start"].play()

    run_prachy = 0

    energie_predmety.add(EnergetickyPredmet(vzdalenost_predmetu, fyzika.generace_bod(vzdalenost_predmetu) - 150, jidlo_img, jidlo_energie))
    while bezi:
        ted = pygame.time.get_ticks() / 1000.0
        snimky_cas = ted - posledni_cas
        if snimky_cas > 0.25:
            snimky_cas = 0.25
        posledni_cas = ted

        accumulator += snimky_cas

        # PYGAME EVENTY
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                config.uloz_config()
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    akce = pause_menu(screen, km_ujet)
                    if akce == "pokracovat":
                        continue
                    elif akce == "restart":
                        main()
                        return
                    elif akce == "menu":
                        bezi = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pause_tlacitko_rect.collidepoint(event.pos):
                    zvuky["ui_click"].play()
                    akce = pause_menu(screen, km_ujet)
                    if akce == "pokracovat":
                        continue
                    elif akce == "restart":
                        main()
                        return
                    elif akce == "menu":
                        bezi = False

        # FYZYKA
        while accumulator >= dt:
            kolo_predchozi.copy_state_from(kolo)

            na_zemi_zadni, na_zemi_predni = kolo.tick(pressed_keys)
            kolo.energie -= config.ztrata_energie

            # backflipy a frontflipy 
            if kolo.udelal_backflip:
                kolo.udelal_backflip = False
                if kolo.backflip_cas > 0:
                    kolo.pocet_backflipu += 1
                else:
                    kolo.pocet_backflipu = 1
                kolo.backflip_cas = 2.0 
                
                zvuky["flip"].play()
                config.prachy += 5

                if kolo.pocet_backflipu == 1:
                    kolo.zobrazeni_textu = "Backflip! +5$"
                elif kolo.pocet_backflipu == 2:
                    kolo.zobrazeni_textu = "Double Backflip! +10$"
                elif kolo.pocet_backflipu == 3:
                    kolo.zobrazeni_textu = "Triple Backflip! +15$"
                else:
                    kolo.zobrazeni_textu = f"{kolo.pocet_backflipu}x Backflip! +{kolo.pocet_backflipu*5}$"

                kolo.text_cas = 2.0

            if kolo.udelal_frontflip:
                kolo.udelal_frontflip = False
                if kolo.frontflip_cas > 0:
                    kolo.pocet_frontflipu += 1
                else:
                    kolo.pocet_frontflipu = 1
                kolo.frontflip_cas = 2.0  

                zvuky["flip"].play()
                config.prachy += 5

                if kolo.pocet_frontflipu == 1:
                    kolo.zobrazeni_textu = "Frontflip! +5$"
                elif kolo.pocet_frontflipu == 2:
                    kolo.zobrazeni_textu = "Double Frontflip! +10$"
                elif kolo.pocet_frontflipu == 3:
                    kolo.zobrazeni_textu = "Triple Frontflip! +15$"
                else:
                    kolo.zobrazeni_textu = f"{kolo.pocet_frontflipu}x Frontflip! +{kolo.pocet_frontflipu*5}$"

                kolo.text_cas = 2.0 

            if kolo.backflip_cas > 0:
                kolo.backflip_cas -= dt
            else:
                kolo.pocet_backflipu = 0

            if kolo.frontflip_cas > 0:
                kolo.frontflip_cas -= dt
            else:
                kolo.pocet_frontflipu = 0

            if kolo.text_cas > 0:
                kolo.text_cas -= dt

            # mince spawn
            while kolo.rear_axel.position.x + config.obrazovka_sirka >= posledni_mince + vzadelnost_minci:
                posledni_mince += vzadelnost_minci
                je_blizko = False
                for energie_predmet in energie_predmety.copy():
                    if abs(posledni_mince - energie_predmet.svet_x) < 50:
                        je_blizko = True
                        break
                if not je_blizko:
                    mince_predmety.add(Mince(posledni_mince, fyzika.generace_bod(posledni_mince)-random.randint(100,250)))

            # kolize mince
            for mince in mince_predmety.copy():
                if abs(mince.svet_x - kolo.rear_axel.position.x) < 400:
                    mince_mask = mince.get_mask()
                    mince_pos = (int(mince.svet_x - camera.x), int(mince.svet_y - camera.y))
                    kolo_masky = [(maska_kola, kolo_pos), (rafek_mask_rear, rafek_pos_rear), (rafek_mask_front, rafek_pos_front)]
                    for mask, pos in kolo_masky:
                        offset = (mince_pos[0] - pos[0], mince_pos[1] - pos[1])
                        if mask.overlap(mince_mask, offset):
                            zvuky["coin"].play()
                            config.prachy += 1
                            run_prachy += 1
                            mince_predmety.remove(mince)
                            break

            # kolize energie
            for predmet in energie_predmety.copy():
                if abs(predmet.svet_x - kolo.rear_axel.position.x) < 400:
                    predmet_mask = predmet.get_mask()
                    predmet_pos = (int(predmet.svet_x - camera.x), int(predmet.svet_y - camera.y))
                    kolo_masky = [(maska_kola, kolo_pos), (rafek_mask_rear, rafek_pos_rear), (rafek_mask_front, rafek_pos_front)]
                    for mask, pos in kolo_masky:
                        offset = (predmet_pos[0] - pos[0], predmet_pos[1] - pos[1])
                        if mask.overlap(predmet_mask, offset):
                            zvuky["jidlo_eat"].play()
                            kolo.energie = min(kolo.energie + predmet.pridavek_energie, 100)
                            energie_predmety.remove(predmet)
                            break

            # spawn energie
            if kolo.rear_axel.get_position().x > vzdalenost_predmetu:
                kolikaty_banan += 1
                vzdalenost_predmetu += rust_vzdalenosti * kolikaty_banan
                nova_predmet_x = kolo.rear_axel.get_position().x + vzdalenost_predmetu
                energie_predmety.add(EnergetickyPredmet(nova_predmet_x, fyzika.generace_bod(nova_predmet_x) - 150, jidlo_img, jidlo_energie))

            # smrt - energie
            km_ujet = kolo.rear_axel.get_position().x
            if kolo.energie < -10:
                while True:
                    akce = konec_menu(screen, km_ujet, run_prachy, "Out of energy!")
                    if akce == "restart":
                        main()
                        return
                    elif akce == "menu":
                        return

            # smrt - kolize hlavy
            vrchni_levy_roh_x = kolo.rear_axel.position.x + offset_x
            vrchni_levy_roh_y = kolo.rear_axel.position.y + offset_y
            rohy = [
                rotace_bodu((vrchni_levy_roh_x, vrchni_levy_roh_y), (kolo.rear_axel.position.x, kolo.rear_axel.position.y), -uhel),
                rotace_bodu((vrchni_levy_roh_x + hlava_sirka, vrchni_levy_roh_y), (kolo.rear_axel.position.x, kolo.rear_axel.position.y), -uhel),
                rotace_bodu((vrchni_levy_roh_x + hlava_sirka, vrchni_levy_roh_y + hlava_vyska), (kolo.rear_axel.position.x, kolo.rear_axel.position.y), -uhel),
                rotace_bodu((vrchni_levy_roh_x, vrchni_levy_roh_y + hlava_vyska), (kolo.rear_axel.position.x, kolo.rear_axel.position.y), -uhel)
            ]
            kolize = False
            krok = config.krok
            for i in range(4):
                x1, y1 = rohy[i]
                x2, y2 = rohy[(i+1)%4]
                for s in range(krok + 1):
                    t = s / krok
                    x = x1 + (x2 - x1) * t
                    y = y1 + (y2 - y1) * t
                    vyska_terenu = fyzika.generace_bod(x)
                    if y > vyska_terenu:
                        kolize = True
                        break
                if kolize:
                    break
            if kolize:
                while True:
                    akce = konec_menu(screen, km_ujet, run_prachy, "Skull cracked!")
                    if akce == "restart":
                        main()
                        return
                    elif akce == "menu":
                        return

            accumulator -= dt

        # # INTERPOLACE
        alpha = accumulator / dt
        kolo_interpolace = kolo_predchozi.interpolate(kolo, alpha)

        # KRESLENI
        if vybrana_mapa == 1:
            screen.blit(obloha_mesic_img, (0,0))
        else:
            screen.blit(obloha_img, (0, 0))
        if not config.potato_pc:
            vykresli_mraky(screen, camera.x, camera.y, mraky, vybrana_mapa)

        vykresli_kolo(kolo_interpolace, camera, rafek_img, ram_obrazky[int(kolo_interpolace.animace_index)])
        vykresli_teren(screen, camera.x, camera.y, kaminky, barva_trava, barva_hlina, barva_kamen)
        
        rychlost = (abs(kolo.rear_wheel.get_speed().x / dt))/2000
        if not(config.potato_pc):
            if random.random() < rychlost:
                if na_zemi_zadni:
                    particly.append(Particle((kolo_interpolace.rear_wheel.get_position().x, kolo_interpolace.rear_wheel.get_position().y + config.WHEEL_RADIUS)))
                if na_zemi_predni:
                    particly.append(Particle((kolo_interpolace.front_wheel.get_position().x, kolo_interpolace.front_wheel.get_position().y + config.WHEEL_RADIUS)))

            for particle in particly:
                particle.update()
                particle.draw(screen, camera, barva_hlina)
                if particle.zivot <= 0:
                    particly.remove(particle)

        for mince in mince_predmety.copy():
            mince.vykresli(screen, camera.x, camera.y)
        for predmet in energie_predmety.copy():
            predmet.vykresli(screen, camera.x, camera.y)

        uhel_rucicky = vykresli_ui(screen, kolo_interpolace.rear_axel.get_position().x, kolo_interpolace.energie, kolo_interpolace.rear_axel.get_position().x, rychlost, pygame.time.get_ticks() - start_cas, uhel_rucicky, clock.get_fps(), jidlo_img)

        if kolo.text_cas > 0:
            vykresli_text(screen, kolo.zobrazeni_textu, (255, 200, 0), (config.obrazovka_sirka//2, config.obrazovka_vyska//4), zarovnat="center", shadow=True, velikost=100)

        pygame.draw.circle(screen, (240, 240, 255), pause_tlacitko_center, pause_tlacitko_polomer)
        pygame.draw.circle(screen, (0, 0, 0), pause_tlacitko_center, pause_tlacitko_polomer, 4)
        cara_sirka = 12
        cara_vyska = 50
        cara_mezera = 16
        cara_barva = (0,0,0)
        x1 = pause_tlacitko_center[0] - cara_mezera // 2 - cara_sirka
        x2 = pause_tlacitko_center[0] + cara_mezera // 2
        y = pause_tlacitko_center[1] - cara_vyska // 2
        pygame.draw.rect(screen, cara_barva, (x1, y, cara_sirka, cara_vyska), border_radius=6)
        pygame.draw.rect(screen, cara_barva, (x2, y, cara_sirka, cara_vyska), border_radius=6)

        camera = fyzika.lerp(camera, kolo_interpolace.rear_axel.position - Vector(-config.BIKE_LENGTH / 2 + config.obrazovka_sirka/2, config.obrazovka_vyska/1.6), 0.1)
        clock.tick(int(30 + config.fps_limit * 240))
        pygame.display.flip()
        