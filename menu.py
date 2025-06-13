import pygame
import config
from hra import main as spust_hru
from hra import vykresli_text
from hra import vykresli_tlacitko
from hra import get_font
from fyzika import nastav_kolo

pygame.init()


screen = pygame.display.set_mode((config.obrazovka_sirka, config.obrazovka_vyska))
pygame.display.set_caption("Tour de Bike - Menu")

main_menu_imgs = []
for i in range(3):
    for j in range(3):
        main_menu_imgs.append(pygame.image.load(f"img/main_menu/{i}{j}.png").convert())

silnicka_img = pygame.image.load("img/silnicka.png").convert_alpha()
celopero_img = pygame.image.load("img/celopero.png").convert_alpha()
hardtail_img = pygame.image.load("img/hardtail.png").convert_alpha()
bike_imgs = [("Road bike", silnicka_img), ("Hardtail", hardtail_img), ("Full suspension", celopero_img)]
kolo_delka = 500
for i in range(len(bike_imgs)):
    delka = bike_imgs[i][1].get_width()
    k = kolo_delka / delka
    kolo_vyska = k * bike_imgs[i][1].get_height()
    bike_imgs[i] = (bike_imgs[i][0], pygame.transform.smoothscale(bike_imgs[i][1], (k * delka, kolo_vyska)))

obloha_img = pygame.image.load("img/obloha.png").convert()
obloha_img = pygame.transform.smoothscale(obloha_img, (config.obrazovka_sirka, config.obrazovka_vyska))

jidla = [
    ("Banana", pygame.image.load("img/banan.png").convert_alpha(), 30),
    ("Protein bar", pygame.image.load("img/tycinka.png").convert_alpha(), 50),
    ("Chicken", pygame.image.load("img/kure.png").convert_alpha(), 100)
]
jidlo_delka = 100
for i in range(len(jidla)):
    delka = jidla[i][1].get_width()
    k = jidlo_delka / delka

    jidla[i] = (jidla[i][0], pygame.transform.smoothscale(jidla[i][1], (k * delka, k * jidla[i][1].get_height())), jidla[i][2])

zamek = pygame.image.load("img/zamek.png").convert_alpha()
zamek_sirka = zamek.get_width()
zamek_vyska = zamek.get_height()


mapy = [
    ("Earth hills", pygame.image.load("img/mapy/default.png").convert()),
    ("Moon", pygame.image.load("img/mapy/mesic.png").convert()),
    ("Highway D1", pygame.image.load("img/mapy/dalnice.png").convert()),
    ("Sand dunes", pygame.image.load("img/mapy/pisecne_duny.png").convert()),
    # ("Night", pygame.image.load("img/mapy/mountains.png").convert())
]

#vybrane_kolo = 0 # 0=silnicka, 1=hardtail, 2=celopero
#vybrane_jidlo = 0 # 0=banan, 1=tycinka, 2=kure


margin_x = 50

# TODO
# procentualne na obrazovce vykreslovat
# hudba, zvuk!
# optimalizace
# cedulky s rekordama
# tutorial
# easter eggy

def menu():
    while True:
        screen.blit(main_menu_imgs[config.vybrane_kolo * 3 + config.vybrane_jidlo], (0,0))

        tlacitko_start = pygame.Rect(50,335,250,150)
        tlacitko_vylepseni = pygame.Rect(50,525,500,150)
        tlacitko_nastaveni = pygame.Rect(50,700,450,150)
        tlacitko_konec = pygame.Rect(50,880,250,150)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                config.uloz_config()
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if tlacitko_start.collidepoint(event.pos):
                    vyber = menu_mapy()
                    if vyber is not None:
                        nastav_kolo(config.vybrane_kolo)
                        config.nastav_upgrady()
                        config.uloz_config()
                        spust_hru()
                elif tlacitko_vylepseni.collidepoint(event.pos):
                    menu_vylepseni()
                elif tlacitko_nastaveni.collidepoint(event.pos):
                    menu_nastaveni()
                elif tlacitko_konec.collidepoint(event.pos):
                    config.uloz_config()
                    pygame.quit()
                    quit()

def menu_mapy():
    bezi = True
    while bezi:
        screen.blit(obloha_img, (0,0))
        vykresli_text(screen, "Select Map", (0,0,0), (config.obrazovka_sirka//2, 100), "center", velikost=125, podrtzeny=True)

        leva_sipka = pygame.Rect(400, 400, 120, 150)
        prava_sipka = pygame.Rect(1400, 400, 120, 150)
        pygame.draw.polygon(screen, (100, 100, 100), [(leva_sipka.right, leva_sipka.top), (leva_sipka.left, leva_sipka.centery), (leva_sipka.right, leva_sipka.bottom)])
        pygame.draw.polygon(screen, (100, 100, 100), [(prava_sipka.left, prava_sipka.top), (prava_sipka.right, prava_sipka.centery), (prava_sipka.left, prava_sipka.bottom)])

        nazev, img = mapy[config.vybrana_mapa]
        img = pygame.transform.smoothscale(img, (608, 342))
        screen.blit(img, (config.obrazovka_sirka//2 - 300, 250))
        if config.vybrana_mapa == 0:
            barva = (0, 154, 23)
        elif config.vybrana_mapa == 1:
            barva = (232, 232, 232)
        elif config.vybrana_mapa == 2:
            barva = (100, 100, 100)
        else:
            barva = (210, 180, 100) 
        vykresli_text(screen, nazev, barva, (config.obrazovka_sirka//2, 650), "center", 80, shadow=True)
        vykresli_text(screen, f"Personal best: {config.rekordy[config.vybrana_mapa]} km", (255, 200, 0),(config.obrazovka_sirka//2, 750), "center", 80, shadow=True)

        tlacitko_start = pygame.Rect(config.obrazovka_sirka//2 - 200, 850, 400, 100)
        vykresli_tlacitko(screen, "Start", tlacitko_start, barva_pozadi=(180,255,180), barva_textu=(0,0,0))

        tlacitko_zpet = pygame.Rect(50, 900, 250, 80)
        vykresli_tlacitko(screen, "Back", tlacitko_zpet, barva_pozadi=(255, 100, 100), barva_textu=(0,0,0))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                config.uloz_config()
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if leva_sipka.collidepoint(event.pos):
                    config.vybrana_mapa = (config.vybrana_mapa - 1) % len(mapy)
                elif prava_sipka.collidepoint(event.pos):
                    config.vybrana_mapa = (config.vybrana_mapa + 1) % len(mapy)
                elif tlacitko_start.collidepoint(event.pos):
                    return config.vybrana_mapa
                elif tlacitko_zpet.collidepoint(event.pos):
                    return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    config.uloz_config()
                    return None

def menu_vylepseni():
    bezi = True
    while bezi:
        screen.blit(obloha_img, (0, 0))
        vykresli_text(screen, "Upgrades", (0, 0, 0), (300, 100), "center", velikost=125, podrtzeny=True)

        leva_sipka = pygame.Rect(200, 400, 120, 150)
        prava_sipka = pygame.Rect(320 + 2 * margin_x + kolo_delka, 400, 120, 150)
        pygame.draw.polygon(screen, (100, 100, 100), [(leva_sipka.right, leva_sipka.top), (leva_sipka.left, leva_sipka.centery), (leva_sipka.right, leva_sipka.bottom)])
        pygame.draw.polygon(screen, (100, 100, 100), [(prava_sipka.left, prava_sipka.top), (prava_sipka.right, prava_sipka.centery), (prava_sipka.left, prava_sipka.bottom)])

        id_kola = config.vybrane_kolo
        kolo_nazev, kolo_img = bike_imgs[id_kola]

        kolo_rect = pygame.Rect(leva_sipka.right + margin_x, leva_sipka.top - 80, kolo_delka, kolo_vyska)
        screen.blit(kolo_img, (kolo_rect.x, kolo_rect.y))
        vykresli_text(screen, kolo_nazev, (0, 0, 0), (kolo_rect.centerx, kolo_rect.bottom + 50), "center", 80)

        tlacitko_kolo = pygame.Rect(kolo_rect.x + margin_x, kolo_rect.y-100, kolo_rect.width - 2 * margin_x, 70)
        if config.kola_odemcena[id_kola]:
            if config.vybrane_kolo == id_kola:
                barva = (180,255,180)
            else:
                barva = (200,200,200)
            vykresli_tlacitko(screen, "Selected", tlacitko_kolo, barva_pozadi=barva, barva_textu=(0,0,0))
        else:
            barva = (255,220,220)
            vykresli_tlacitko(screen, f"{config.ceny_kol[id_kola]} $", tlacitko_kolo, barva_pozadi=barva, barva_textu=(0,0,0))

        vykresli_text(screen, "Upgrades are separate for each bike", (0,0,0), (600,970))

        if not config.kola_odemcena[id_kola]:
            zamek_x = kolo_rect.x + (kolo_rect.width - zamek_sirka) // 2
            zamek_y = kolo_rect.y + (kolo_rect.height - zamek_vyska) // 2
            screen.blit(zamek, (zamek_x, zamek_y))

        upgrade_jmena = ["Speed", "Endurance"]
        upgrade_rects = []
        for upgrade_idx in range(2):
            upgrade_jmeno = upgrade_jmena[upgrade_idx]
            upgrade_level = config.kola_upgrady[id_kola][upgrade_idx]
            upgrade_rect = pygame.Rect(kolo_rect.x, kolo_rect.bottom + 100 + upgrade_idx*60, kolo_rect.width, 50)
            upgrade_rects.append(upgrade_rect)
            if upgrade_idx == 0:
                barva = (180,180,255)
            else:
                barva = (180,255,180)
            if upgrade_level == config.max_upgrade:
                vykresli_tlacitko(
                    screen,
                    f"{upgrade_jmeno}: MAXED",
                    upgrade_rect,
                    barva_pozadi=barva,
                    barva_textu=(0,0,0)
                )
            else:
                vykresli_tlacitko(
                screen,
                f"{upgrade_jmeno}: {upgrade_level}/{config.max_upgrade} {config.cena_upgrade[upgrade_idx]}$",
                upgrade_rect,
                barva_pozadi=barva,
                barva_textu=(0,0,0)
                )

        jidlo_rects = []
        for i in range(len(jidla)):
            nazev, img, energie = jidla[i]
            y = 150 + i * 250
            rect = pygame.Rect(1200, y, 500, 200)
            jidlo_rects.append(rect)
            if i == 0:
                barva = (255,255,180)
            elif i == 1:
                barva = (220,255,220)
            else:
                barva = (255,220,220)
            pygame.draw.rect(screen, barva, rect)
            pygame.draw.rect(screen, (0,0,0), rect, 2)
            img_rect = img.get_rect()
            img_x = rect.x + margin_x / 2.2
            img_y = rect.y + (rect.height - img_rect.height) // 2
            screen.blit(img, (img_x, img_y))
            vykresli_text(screen, nazev, (0,0,0), (rect.x + 35 + img_rect.width, rect.y + 60), velikost=38)
            vykresli_text(screen, f"Energy: {energie}", (0,0,0), (rect.x + 35 + img_rect.width, rect.y + 100), velikost=30)
            tlacitko = pygame.Rect(rect.right - 200, rect.y, 200, rect.height)
            if config.jidla_odemcena[i]:
                if config.vybrane_jidlo == i:
                    barva_pozadi = (180,255,180)
                else:
                    barva_pozadi = (200,200,200)
                if config.vybrane_jidlo == i:
                    vykresli_tlacitko(screen, "Selected", tlacitko, barva_pozadi=barva_pozadi, barva_textu=(0,0,0))
                else:
                    vykresli_tlacitko(screen, "Select", tlacitko, barva_pozadi=barva_pozadi, barva_textu=(0,0,0))
            else:
                vykresli_tlacitko(screen, f"{config.ceny_jidel[i]} $", tlacitko, barva_pozadi=(255, 133, 113), barva_textu=(0,0,0))
                scale = (jidlo_delka - 20) / zamek_sirka
                zamek_small = pygame.transform.smoothscale(zamek, (zamek_sirka * scale, zamek_vyska * scale))
                zamek_x = img_x + ((img_rect.width - zamek_sirka * scale)/2)
                zamek_y = img_y + ((img_rect.height - zamek_vyska * scale)/2)
                screen.blit(zamek_small, (zamek_x, zamek_y))

        vykresli_text(screen, f"{config.prachy} $", (255, 215, 0), (700, 75), velikost=70)
        tlacitko_zpet = pygame.Rect(30, 950,400, 100)
        if not config.kola_odemcena[config.vybrane_kolo]:
            vykresli_tlacitko(screen, "Select unlocked bike", tlacitko_zpet, barva_pozadi=(180, 180, 180), barva_textu=(120,120,120))
            zpet_povoleno = False
        else:
            vykresli_tlacitko(screen, "Back", tlacitko_zpet, barva_pozadi=(255, 100, 100), barva_textu=(0,0,0))
            zpet_povoleno = True


        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                config.uloz_config()
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if leva_sipka.collidepoint(event.pos):
                    config.vybrane_kolo = (config.vybrane_kolo - 1) % len(bike_imgs)
                elif prava_sipka.collidepoint(event.pos):
                    config.vybrane_kolo = (config.vybrane_kolo + 1) % len(bike_imgs)
                elif tlacitko_kolo.collidepoint(event.pos):
                    id_kola = config.vybrane_kolo
                    if config.kola_odemcena[id_kola]:
                        config.vybrane_kolo = id_kola
                    elif config.prachy >= config.ceny_kol[id_kola]:
                        config.prachy -= config.ceny_kol[id_kola]
                        config.kola_odemcena[id_kola] = True
                        config.vybrane_kolo = id_kola
                for upgrade_idx in range(2):
                    upgrade_rect = upgrade_rects[upgrade_idx]
                    if upgrade_rect.collidepoint(event.pos) and config.kola_odemcena[id_kola]:
                        if config.kola_upgrady[id_kola][upgrade_idx] < config.max_upgrade and config.prachy >= config.cena_upgrade[upgrade_idx]:
                            config.prachy -= config.cena_upgrade[upgrade_idx]
                            config.kola_upgrady[id_kola][upgrade_idx] += 1

                for i in range(len(jidlo_rects)):
                    rect = jidlo_rects[i]
                    if rect.collidepoint(event.pos):
                        if config.jidla_odemcena[i]:
                            config.vybrane_jidlo = i
                        elif config.prachy >= config.ceny_jidel[i]:
                            config.prachy -= config.ceny_jidel[i]
                            config.jidla_odemcena[i] = True
                            config.vybrane_jidlo = i

                if tlacitko_zpet.collidepoint(event.pos) and zpet_povoleno:
                    config.uloz_config()
                    bezi = False

            elif event.type == pygame.KEYDOWN:
                if zpet_povoleno and event.key == pygame.K_ESCAPE:
                    config.uloz_config()
                    bezi = False

def vykresli_slider(screen, y, posuvnik_delka, value, popisek, max_text="100", jednotka = "%", min_text="0"):
    slider_vyska = 8
    posuvnik_polomer = 18
    slider_color = (180, 180, 180)
    posuvnik_color = (255, 200, 100)
    font_color = (0, 0, 0)

    if popisek == "FPS limit":
        if value > 0.99:
            zobrazena_hodnota = 270
        else:
            zobrazena_hodnota = int(30 + value * 240)
        vykresli_text(screen, f"{popisek} {zobrazena_hodnota} {jednotka}", font_color, (margin_x, y))
    else:
        if value > 0.99:
            vykresli_text(screen, f"{popisek} 100 {jednotka}", font_color, (margin_x, y))
        else:
            vykresli_text(screen, f"{popisek} {round(value*100)} {jednotka}", font_color, (margin_x, y))

    text_sirka, text_vyska = get_font(50, "Arial").size(f"{popisek} {max_text} {jednotka}")
    x = 1.5 * margin_x + text_sirka
    y += text_vyska / 2 
    pygame.draw.rect(screen, slider_color, (x, y, posuvnik_delka, slider_vyska), border_radius=4)
    
    posuvnik_x = x + int(value * posuvnik_delka)
    posuvnik_y = y + slider_vyska // 2
    pygame.draw.circle(screen, posuvnik_color, (posuvnik_x, posuvnik_y), posuvnik_polomer)

    return pygame.Rect(x, y - posuvnik_polomer, posuvnik_delka, posuvnik_polomer * 2)

def vykresli_zakliknuti(screen, y, popisek, zaklikly):
    velikost = 36
    barva_okraj = (120, 120, 120)
    if zaklikly:
        barva_vypln = (220, 255, 220) 
    else:
        barva_vypln = (240, 240, 240)
    barva_fajfka = (0, 180, 0)
    font_color = (0, 0, 0)

    vykresli_text(screen, popisek, font_color, (margin_x, y))
    text_sirka, text_vyska = get_font(50, "Arial").size(f"{popisek}")
    x = 1.5 * margin_x + text_sirka
    y += (text_vyska - velikost) / 2
    pygame.draw.rect(screen, barva_vypln, (x, y, velikost, velikost), border_radius=6)
    pygame.draw.rect(screen, barva_okraj, (x, y, velikost, velikost), 2, border_radius=6)
    if zaklikly:
        margin_fajfky = velikost//5
        pygame.draw.line(screen, barva_fajfka, (x+margin_fajfky, y+velikost//2), (x+velikost//2, y+velikost-margin_fajfky), 5)
        pygame.draw.line(screen, barva_fajfka, (x+velikost//2, y+velikost-margin_fajfky), (x+velikost-margin_fajfky, y+margin_fajfky), 5)
    
    return pygame.Rect(x, y, velikost, velikost)

def menu_nastaveni():
    bezi = True
    secret_code = ""
    zadavani_kodu = False
    zprava = ""
    zprava_cas = 0

    while bezi:
        screen.blit(obloha_img, (0, 0))
        vykresli_text(screen, "Settings", (0, 0, 0), (config.obrazovka_sirka//2, 100), "center", velikost=125, podrtzeny=True)

        slider_rect_sound = vykresli_slider(screen, 170, 300, config.volume_sound, "Sound volume:")
        slider_rect_music = vykresli_slider(screen, 245, 300, config.volume_music, "Music volume:")

        checkbox_rect_potato = vykresli_zakliknuti(screen, 320, "Potato PC (disables extra details):", config.potato_pc)
        checkbox_rect_fps = vykresli_zakliknuti(screen, 395, "Show FPS counter:", config.fps)
        slider_rect_fps_limit = vykresli_slider(screen, 470, 300, config.fps_limit, "FPS limit", 300, "FPS:")
        checkbox_rect_fullscreen = vykresli_zakliknuti(screen, 545, "Fullscreen:", config.fullscreen)

        tlacitko_reset_staty = pygame.Rect(margin_x, 630,300,80)
        vykresli_tlacitko(screen, "Reset stats", tlacitko_reset_staty, barva_pozadi=(255, 200, 100), barva_textu=(0,0,0))
        
        vykresli_text(screen, "Secret code:", (0, 0, 0), (margin_x, 750))
        code_sirka, code_vyska = get_font(50, "Arial").size("Secret code:")
        kod_rect = pygame.Rect(2 * margin_x + code_sirka, 750, 350, 60)
        pygame.draw.rect(screen, (240, 240, 255), kod_rect)
        pygame.draw.rect(screen, (0,0,0), kod_rect, 2)
        if zadavani_kodu:
            vykresli_text(screen, secret_code, (0,0,0), (kod_rect.x + margin_x, kod_rect.centery - code_vyska/2))
        else:
            vykresli_text(screen, "Click to type...", (0,0,0), (kod_rect.x + margin_x, kod_rect.centery - code_vyska/2))
        if zprava:
            if len(zprava) < 29:
                vykresli_text(screen, zprava, (200, 0, 0), (config.obrazovka_sirka-margin_x,200), zarovnat="right", velikost=100)
            else:
                vykresli_text(screen, zprava, (200, 0, 0), (config.obrazovka_sirka-margin_x,200), zarovnat="right")
            if (pygame.time.get_ticks() / 1000) - zprava_cas > 3:
                zprava = ""

        tlacitko_reset = pygame.Rect(2 * margin_x + 300, 630, 300, 80)
        vykresli_tlacitko(screen, "Reset settings", tlacitko_reset, barva_pozadi=(255, 200, 100), barva_textu=(0,0,0))

        tlacitko_zpet = pygame.Rect(margin_x, config.obrazovka_vyska - 120, 200, 80)
        vykresli_tlacitko(screen, "Back", tlacitko_zpet, barva_pozadi=(255, 100, 100), barva_textu=(0,0,0))

        vykresli_text(screen, "Credits:", (0, 0, 0), (margin_x, 825))
        vykresli_text(screen, "Ondra - physics, antialiasing, playtester; Rosta - bug fix stones, playtester; Martin - playtester", (0, 0, 0), (margin_x, 900), velikost=30)
        vykresli_text(screen, "", (0, 0, 0), (margin_x, 900))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                config.uloz_config()
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if tlacitko_zpet.collidepoint(event.pos):
                    bezi = False
                elif slider_rect_sound.collidepoint(event.pos):
                    config.volume_sound = min(max((event.pos[0] - slider_rect_sound.x) / slider_rect_sound.width, 0), 1)
                elif slider_rect_music.collidepoint(event.pos):
                    config.volume_music = min(max((event.pos[0] - slider_rect_music.x) / slider_rect_music.width, 0), 1)
                elif checkbox_rect_potato.collidepoint(event.pos):
                    config.potato_pc = not config.potato_pc
                elif checkbox_rect_fps.collidepoint(event.pos):
                    config.fps = not config.fps
                elif slider_rect_fps_limit.collidepoint(event.pos):
                    config.fps_limit = min(max((event.pos[0] - slider_rect_fps_limit.x)/ slider_rect_fps_limit.width,0),1)
                elif checkbox_rect_fullscreen.collidepoint(event.pos):
                    config.fullscreen = not config.fullscreen
                    if config.fullscreen:
                        pygame.display.set_mode((config.obrazovka_sirka, config.obrazovka_vyska), pygame.FULLSCREEN)
                    else:
                        pygame.display.set_mode((config.obrazovka_sirka, config.obrazovka_vyska))
                elif tlacitko_reset.collidepoint(event.pos):
                    config.volume_sound = 0.5
                    config.volume_music = 0.5
                    config.potato_pc = False
                    config.fps = False
                    config.fps_limit = 0.125
                    config.fullscreen = False
                    pygame.display.set_mode((config.obrazovka_sirka, config.obrazovka_vyska))
                    secret_code = ""
                    zprava = "Settings reset successfully!"
                    zprava_cas = pygame.time.get_ticks() / 1000

                elif tlacitko_reset_staty.collidepoint(event.pos):
                    config.prachy = 0
                    config.vybrane_kolo = 0
                    config.vybrane_jidlo = 0
                    config.kola_odemcena = [True, False, False]
                    config.jidla_odemcena = [True, False, False]
                    config.kola_upgrady = [[0, 0], [0, 0], [0, 0]]
                    config.rekordy = [0,0,0,0]
                    zprava = "Stats reset successfully!"
                    zprava_cas = pygame.time.get_ticks() / 1000

                elif kod_rect.collidepoint(event.pos):
                    zadavani_kodu = True
                    secret_code = ""
                    zprava = ""
                else:
                    zadavani_kodu = False
            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    if slider_rect_sound.collidepoint(event.pos):
                        config.volume_sound = min(max((event.pos[0] - slider_rect_sound.x) / slider_rect_sound.width, 0), 1)
                    elif slider_rect_music.collidepoint(event.pos):
                        config.volume_music = min(max((event.pos[0] - slider_rect_music.x) / slider_rect_music.width, 0), 1)
                    elif slider_rect_fps_limit.collidepoint(event.pos):
                        config.fps_limit = min(max((event.pos[0] - slider_rect_fps_limit.x)/ slider_rect_fps_limit.width,0),1)
            elif event.type == pygame.KEYDOWN:
                if zadavani_kodu:
                    if event.key == pygame.K_RETURN:
                        if secret_code == "sparkyjegay":
                            config.prachy += 1000000
                            zprava = "+ 1 milion"
                        else:
                            zprava = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                        zadavani_kodu = False
                        zprava_cas = pygame.time.get_ticks() / 1000

                    elif event.key == pygame.K_BACKSPACE:
                        secret_code = secret_code[:-1]
                    else:
                        if len(secret_code) < 14 and event.unicode.isprintable():
                            secret_code += event.unicode
                elif event.key == pygame.K_ESCAPE:
                    bezi = False
menu()

# if __name__ == "__main__":
#     import cProfile
#     import pstats

#     profiler = cProfile.Profile()
#     profiler.enable()
#     menu()
#     profiler.disable()
#     stats = pstats.Stats(profiler).sort_stats('cumtime')
#     stats.print_stats(30)
#     pygame.quit()
