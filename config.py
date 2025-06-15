import os
import json

# Nastaveni
volume_sound = 0.5
volume_music = 0.2
potato_pc = False
fps = False
fps_limit = 0.125
fullscreen = False

# Herni veci
vybrane_kolo = 0
vybrane_jidlo = 0
prachy = 0
ztrata_energie = 0.05

# upgrady
ceny_kol = [0, 100, 500]
ceny_jidel = [0, 50, 200]
max_upgrade = 5
cena_upgrade = [50, 100]

kola_odemcena = [True, False, False]
jidla_odemcena = [True, False, False]
kola_upgrady = [[0, 0], [0, 0], [0, 0]]

# odpruzeni
SUS_FRONT = 0.5
SUS_REAR = 0.5
DAMP_FRONT = 0.95
DAMP_REAR = 0.95

# obrazovka
obrazovka_sirka = 1920
obrazovka_vyska = 1080

# fyzika
BIKE_LENGTH = 120
WHEEL_RADIUS = 40
SLAPANI_FROCE = 1
INAIR_FORCE = 0.2
WHEEL_COLLISION_CHECK_SUBDIVISIONS = 50
GRAVITY = (0, 0.2)

# generace
krok = 10
obtiznost_mapy = 10000 # nizsi tezsi
vybrana_mapa = 0

rekordy = [0,0,0,0]

config_file = "config_save.json"

def uloz_config():
    data = {
        "volume_sound": volume_sound,
        "volume_music": volume_music,
        "potato_pc": potato_pc,
        "fps": fps,
        "fps_limit": fps_limit,
        "prachy": prachy,
        "kola_odemcena": kola_odemcena,
        "jidla_odemcena": jidla_odemcena,
        "kola_upgrady": kola_upgrady,
        "vybrane_kolo": vybrane_kolo,
        "vybrane_jidlo": vybrane_jidlo,
        "vybrana_mapa": vybrana_mapa,
        "rekordy": rekordy
    }
    with open(config_file, "w") as f:
        json.dump(data, f)

def nacti_config():
    global volume_sound, volume_music, potato_pc, fps, fps_limit, fullscreen
    global vybrane_kolo, vybrane_jidlo, prachy, ztrata_energie, vybrana_mapa
    global kola_odemcena, jidla_odemcena, kola_upgrady, rekordy

    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            data = json.load(f)
            volume_sound = data.get("volume_sound", volume_sound)
            volume_music = data.get("volume_music", volume_music)
            potato_pc = data.get("potato_pc", potato_pc)
            fps = data.get("fps", fps)
            fps_limit = data.get("fps_limit", fps_limit)
            prachy = data.get("prachy", prachy)
            kola_odemcena = data.get("kola_odemcena", kola_odemcena)
            jidla_odemcena = data.get("jidla_odemcena", jidla_odemcena)
            kola_upgrady = data.get("kola_upgrady", kola_upgrady)
            vybrane_kolo = data.get("vybrane_kolo", vybrane_kolo)
            vybrane_jidlo = data.get("vybrane_jidlo", vybrane_jidlo)
            vybrana_mapa = data.get("vybrana_mapa", vybrana_mapa)
            rekordy = data.get("rekordy", rekordy)
    
    if not kola_odemcena[vybrane_kolo]:
        vybrane_kolo = 0
    if not jidla_odemcena[vybrane_jidlo]:
        vybrane_jidlo = 0

def nastav_upgrady():
    global SLAPANI_FROCE, ztrata_energie
    zaklad_slapani = 1
    zaklad_endurance = 0.1
    SLAPANI_FROCE = zaklad_slapani + kola_upgrady[vybrane_kolo][0] * 0.2
    ztrata_energie = zaklad_endurance * (1 - 0.15 * kola_upgrady[vybrane_kolo][1])

nacti_config()