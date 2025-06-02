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

barva_trava = (0, 154, 23)
vyska_travy = 50
barva_hlina = (120, 72, 0)
barva_kamen = (80, 60, 40)

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

def vykresli_text(surf, text, barva, pozice, zarovnat="left", velikost=50, font="Arial"):
    font = get_font(velikost,font)
    text_surface = font.render(text, True, barva)
    text_rect = text_surface.get_rect()
    if zarovnat == "left":
        text_rect.topleft = pozice
    elif zarovnat == "center":
        text_rect.center = pozice
    elif zarovnat == "right":
        text_rect.topright = pozice
    surf.blit(text_surface, text_rect)

def vykresli_tlacitko(surface, text, rect, barva_textu=(255,255,255), barva_pozadi=(0, 70, 140), barva_okraje=(0,0,0), tloustka_okraje=2, velikost_pisma=50, font="Arial"):
    pygame.draw.rect(surface, barva_pozadi, rect)

    pygame.draw.rect(surface, barva_okraje, rect, tloustka_okraje)

    vykresli_text(surface, text, barva_textu, rect.center, "center", velikost_pisma, font)

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

def vykresli_ui(screen, km, energie, kolo_x, rychlost, cas):
    vykresli_text(screen, f"Distance: {round(km/1000,1)} km", (0, 0, 0), (22, 20))

    pygame.draw.rect(screen, (50, 50, 50), (20, 90, 250, 40))
    if energie > 0:
        pygame.draw.rect(screen, (255, 215, 0), (20, 90, 2.5 * energie, 40))
    pygame.draw.rect(screen, (0, 0, 0), (20, 90, 250, 40), 2)

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
    uhel = -220 + (abs(rychlost) / 70) * 262
    uhel_rad = math.radians(uhel)
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
            vykresli_text(screen, f"{round(vzdalenost/1000,1)} km →", (0, 0, 0), (config.obrazovka_sirka - 20, 200), zarovnat="right")

def vykresli_teren(screen, kamera_x, kamera_y, kaminky):
    
    body_trava = [[0, config.obrazovka_vyska]]
    body_hlina = [[0, config.obrazovka_vyska + vyska_travy]]
    body_hrana = []

    x_svet = kamera_x - (kamera_x % config.krok)
    x = int(x_svet)

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

        if not(config.potato_pc) and kaminky is not None and x not in kaminky:
            y_real = fyzika.generace_bod(x)
            y_hlina = y_real + vyska_travy
            segment_kaminky = [
                (random.randint(x, x + config.krok),
                 random.randint(int(y_hlina + 30), int(y_hlina + config.obrazovka_vyska + 30)),
                 random.randint(1, 4))
                for _ in range(10)
            ]
            kaminky[x] = segment_kaminky

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

def vykresli_mraky(screen, kamera_x, kamera_y, mraky):
    for m in mraky:
        x = int(m["x"] - kamera_x * m["parallax"])
        y = int(m["y"] - kamera_y * m["parallax"])
        img = pygame.transform.smoothscale(mrak_img, (int(mrak_img.get_width() * m["velikost"]), int(mrak_img.get_height() * m["velikost"])))
        if x < -img.get_width():
            m["x"] += config.obrazovka_sirka * 2 + img.get_width()
            x = int(m["x"] - kamera_x * m["parallax"])
        elif x > config.obrazovka_sirka + img.get_width():
            m["x"] -= config.obrazovka_sirka * 2 + img.get_width()
            x = int(m["x"] - kamera_x * m["parallax"])
        screen.blit(img, (x, y))

def pause_menu(screen):
    paused = True
    posledni_snimek = screen.copy()
    pokracovat_rect = pygame.Rect(screen.get_width()//2 - 200, 400, 400, 100)
    restart_rect = pygame.Rect(screen.get_width()//2 - 200, 550, 400, 100)
    menu_rect = pygame.Rect(screen.get_width()//2 - 200, 700, 400, 100)
    while paused:
        screen.blit(posledni_snimek, (0, 0))
        pruhledna_cerna = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        pruhledna_cerna.fill((0, 0, 0, 140))
        screen.blit(pruhledna_cerna, (0, 0))
        vykresli_text(screen, "Paused", (255, 255, 255), (screen.get_width()//2, 250), "center", 200)

        vykresli_tlacitko(screen, "Continue", pokracovat_rect)
        vykresli_tlacitko(screen, "Restart", restart_rect)
        vykresli_tlacitko(screen, "Back to menu", menu_rect)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "pokracovat"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pokracovat_rect.collidepoint(event.pos):
                    return "pokracovat"
                elif restart_rect.collidepoint(event.pos):
                    return "restart"
                elif menu_rect.collidepoint(event.pos):
                    return "menu"

def konec_menu(screen, km_ujet):
    konec = True
    posledni_snimek = screen.copy()
    restart_rect = pygame.Rect(screen.get_width()//4 - 200, 550, 400, 100)
    menu_rect = pygame.Rect(screen.get_width()//4 - 200, 700, 400, 100)
    while konec:
        screen.blit(posledni_snimek, (0,0))
        pruhledna_cerna = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        pruhledna_cerna.fill((0, 0, 0, 140))
        screen.blit(pruhledna_cerna, (0, 0))

        vykresli_text(screen, "Game Over", (255, 80, 80), (screen.get_width()//4, 250), "center", 150)
        vykresli_text(screen, f"Money: {config.prachy}", (255, 215, 0), (screen.get_width()//4, 400), "center", 70)
        vykresli_text(screen, f"Distance: {round(km_ujet/1000, 2)} km", (255, 255, 255), (screen.get_width()//4, 480), "center", 60)

        vykresli_tlacitko(screen, "Restart", restart_rect)
        vykresli_tlacitko(screen, "Back to menu", menu_rect)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_rect.collidepoint(event.pos):
                    return "restart"
                elif menu_rect.collidepoint(event.pos):
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

mrak_img = pygame.image.load("img/mrak.png").convert_alpha()
mrak_img = pygame.transform.smoothscale(mrak_img, (mrak_img.get_width() // 2, mrak_img.get_height() // 2))

ztrata_energie = 0.05
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


    start_cas = pygame.time.get_ticks()
    bezi = True

    clock = pygame.time.Clock()
    fps_tick = int(30 + config.fps_limit * 240)
    
    kolo = Bike(Vector(0, fyzika.generace_bod(0)-200))

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

    mince_predmety.empty()
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

    while bezi:
        screen.blit(obloha_img, (0, 0))
        if not config.potato_pc:
            vykresli_mraky(screen, camera.x, camera.y, mraky)

        kolo.tick()
        vykresli_kolo(kolo, camera, rafek_img, ram_obrazky[int(kolo.animace_index)])
        
        vykresli_teren(screen, camera.x, camera.y, kaminky)

        while kolo.rear_axel.position.x + config.obrazovka_sirka >= posledni_mince + vzadelnost_minci:

            posledni_mince += vzadelnost_minci

            je_blizko = False
            for energie_predmet in energie_predmety.copy():
                if abs(posledni_mince - energie_predmet.svet_x) < 50:
                    je_blizko = True
                    break

            if not je_blizko:
                mince_predmety.add(Mince(posledni_mince, fyzika.generace_bod(posledni_mince)-random.randint(100,250)))

        for mince in mince_predmety.copy():
            mince.vykresli(screen, camera.x, camera.y)
            if abs(mince.svet_x - kolo.rear_axel.position.x) < 400:
                mince_mask = mince.get_mask()
                mince_pos = (int(mince.svet_x - camera.x), int(mince.svet_y - camera.y))
                kolo_masky = [(maska_kola, kolo_pos), (rafek_mask_rear, rafek_pos_rear),(rafek_mask_front, rafek_pos_front)]
                for mask, pos in kolo_masky:
                    offset = (mince_pos[0] - pos[0], mince_pos[1] - pos[1])
                    if mask.overlap(mince_mask, offset):
                        config.prachy += 1
                        mince_predmety.remove(mince)

        for predmet in energie_predmety.copy():
            predmet.vykresli(screen, camera.x, camera.y)
            if abs(predmet.svet_x - kolo.rear_axel.position.x) < 400:
                predmet_mask = predmet.get_mask()
                predmet_pos = (int(predmet.svet_x - camera.x), int(predmet.svet_y - camera.y))
                kolo_masky = [(maska_kola, kolo_pos), (rafek_mask_rear, rafek_pos_rear),(rafek_mask_front, rafek_pos_front)]
                for mask, pos in kolo_masky:
                    offset = (predmet_pos[0] - pos[0], predmet_pos[1] - pos[1])
                    if mask.overlap(predmet_mask, offset):
                        kolo.energie = min(kolo.energie + predmet.pridavek_energie, 100)
                        energie_predmety.remove(predmet)
                        break

        if kolo.rear_axel.get_position().x > vzdalenost_predmetu:
            kolikaty_banan += 1
            vzdalenost_predmetu += rust_vzdalenosti * kolikaty_banan
            nova_predmet_x = kolo.rear_axel.get_position().x + vzdalenost_predmetu
            energie_predmety.add(EnergetickyPredmet(nova_predmet_x, fyzika.generace_bod(nova_predmet_x) - 150, jidlo_img, jidlo_energie))

        km_ujet = kolo.rear_axel.get_position().x

        kolo.energie -= ztrata_energie
        if kolo.energie < -10:
            while True:
                akce = konec_menu(screen, km_ujet)
                if akce == "restart":
                    main()
                    return
                elif akce == "menu":
                    return

        vrchni_levy_roh_x = kolo.rear_axel.position.x + offset_x
        vrchni_levy_roh_y = kolo.rear_axel.position.y + offset_y
        
        rohy = [
            rotace_bodu((vrchni_levy_roh_x, vrchni_levy_roh_y), (kolo.rear_axel.position.x, kolo.rear_axel.position.y), -uhel),
            rotace_bodu((vrchni_levy_roh_x + hlava_sirka, vrchni_levy_roh_y), (kolo.rear_axel.position.x, kolo.rear_axel.position.y), -uhel),
            rotace_bodu((vrchni_levy_roh_x + hlava_sirka, vrchni_levy_roh_y + hlava_vyska), (kolo.rear_axel.position.x, kolo.rear_axel.position.y), -uhel),
            rotace_bodu((vrchni_levy_roh_x, vrchni_levy_roh_y + hlava_vyska), (kolo.rear_axel.position.x, kolo.rear_axel.position.y), -uhel)
        ]

        kolize = False
        krok = 10
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
                akce = konec_menu(screen, km_ujet)
                if akce == "restart": 
                    main()
                    return
                elif akce == "menu":
                    return

        rychlost = kolo.rear_wheel.get_speed().x
        vykresli_ui(screen, km_ujet, kolo.energie, kolo.rear_axel.get_position().x, rychlost, pygame.time.get_ticks() - start_cas)

        vykresli_text(screen, f"Money: {config.prachy}", (255, 215, 0), (22, 360), velikost=50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    akce = pause_menu(screen)
                    if akce == "pokracovat":
                        continue
                    elif akce == "restart":
                        main()
                        return
                    elif akce == "menu":
                        bezi = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pause_tlacitko_rect.collidepoint(event.pos):
                    akce = pause_menu(screen)
                    if akce == "pokracovat":
                        continue
                    elif akce == "restart":
                        main()
                        return
                    elif akce == "menu":
                        bezi = False
        if config.fps:
            fps = clock.get_fps()
            vykresli_text(screen, f"FPS: {int(fps)}", (0, 0, 0), (20, 150), velikost=100)

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

        camera = fyzika.lerp(camera, kolo.rear_axel.position - Vector(-config.BIKE_LENGTH / 2 + config.obrazovka_sirka/2, config.obrazovka_vyska/1.5), 0.1)
        pygame.display.flip()
        clock.tick(fps_tick)

