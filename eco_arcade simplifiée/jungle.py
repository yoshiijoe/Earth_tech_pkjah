import random
import pygame
from config import W, H, clamp, lerp_col, sprite

# ── Constantes ────────────────────────────────────────────────────────────────
ROAD_W      = int(W * 0.50)
ROAD_X      = W // 2 - ROAD_W // 2
TRASH_KINDS = ["bottle", "can", "bag", "tire", "box"]
TEMPS_TOTAL = 70.0


# ── Spawn helpers ─────────────────────────────────────────────────────────────
def spawner_dechet_jungle(state, y=None):
    """Ajoute un déchet sur la route (CM2 : append)."""
    k = random.choice(TRASH_KINDS)              # CM3 : random.choice
    x = random.uniform(ROAD_X + 60, ROAD_X + ROAD_W - 60)
    if y is None:
        pos_y = -40.0
    else:
        pos_y = float(y)
    state["trash"].append({
        "x":    x,
        "y":    pos_y,
        "rot":  random.uniform(0, 360),
        "rots": random.uniform(-40, 40),
        "img":  sprite("trash_" + k),
    })


def spawner_singe(state):
    """Ajoute un singe obstacle (CM2 : append)."""
    x = random.uniform(ROAD_X + 70, ROAD_X + ROAD_W - 70)
    state["monkeys"].append({
        "x":   x,
        "y":   -50.0,
        "img": state["monkey_img"],
    })


# ── Création de l'état (CM5 : dictionnaire) ───────────────────────────────────
def creer_jungle(data):
    """Initialise et retourne le dictionnaire d'état du jeu Jungle."""
    # Fond statique dessiné une seule fois
    bg = pygame.Surface((W, H))
    bg.fill((35, 120, 45))
    pygame.draw.rect(bg, (42, 42, 52),    (ROAD_X, 0, ROAD_W, H))
    pygame.draw.rect(bg, (210, 170, 20),  (ROAD_X, 0, 8, H))
    pygame.draw.rect(bg, (210, 170, 20),  (ROAD_X + ROAD_W - 8, 0, 8, H))

    state = {
        "font":        pygame.font.Font(None, 28),
        "bg":          bg,
        "car_img":     sprite("car"),
        "monkey_img":  sprite("monkey"),
        # Voiture
        "car_x":       float(W // 2),
        "car_vx":      0.0,
        # Entités (CM2 : listes)
        "trash":       [],
        "monkeys":     [],
        "float_texts": [],
        # Stats
        "score":       0,
        "lives":       3,
        "time_left":   TEMPS_TOTAL,
        "diff":        0.0,
        "scroll":      0.0,
        "spawn_t":     0.0,
        "inv_t":       0.0,
        "details":     [],
    }

    for _ in range(3):      # CM1 : for
        spawner_dechet_jungle(state, y=random.uniform(-300, -40))

    return state


# ── Gestion des événements ─────────────────────────────────────────────────────
def gerer_jungle(state, event):
    """
    Gère un événement pygame.
    Retourne 'menu', 'pause' ou None.
    CM1 : if/elif
    """
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            return "menu"
        elif event.key == pygame.K_p:
            return "pause"
    return None


# ── Mise à jour ────────────────────────────────────────────────────────────────
def mettre_a_jour_jungle(state, dt):
    """
    Met à jour toute la physique du jeu Jungle.
    Retourne 'fin' si la partie est terminée, sinon None.
    CM1 : if/elif, for  |  CM2 : append, remove, len
    """
    state["time_left"] -= dt
    state["diff"]      += dt
    if state["inv_t"] > 0:
        state["inv_t"] -= dt

    # — Fin de partie —
    if state["time_left"] <= 0 or state["lives"] <= 0:
        state["details"] = [("Vies restantes", str(state["lives"]))]
        return "fin"

    vitesse = 150.0 + state["diff"] * 2.5
    state["scroll"] = (state["scroll"] + vitesse * dt) % 60

    # — Voiture —
    keys = pygame.key.get_pressed()
    ax = 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        ax -= 2200
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        ax += 2200
    state["car_vx"] = clamp(state["car_vx"] * (1 - 9 * dt) + ax * dt, -560, 560)
    state["car_x"]  = clamp(
        state["car_x"] + state["car_vx"] * dt,
        ROAD_X + 100, ROAD_X + ROAD_W - 100
    )

    car_rect = pygame.Rect(0, 0, 148, 100)
    car_rect.center = (int(state["car_x"]), H - 120)
    bac_rect = pygame.Rect(car_rect.left + 20, car_rect.top + 2,
                           car_rect.width - 40, 26)

    # — Déchets —
    for t in state["trash"][:]:     # CM1 : for  |  CM2 : copie de liste
        t["y"]   += vitesse * dt
        t["rot"] += t["rots"] * dt
        tr = pygame.Rect(0, 0, 52, 52)
        tr.center = (int(t["x"]), int(t["y"]))
        if bac_rect.colliderect(tr):
            state["score"] += 1
            state["float_texts"].append([t["x"], t["y"] - 20, "+1", 0.0, (70, 210, 140)])
            state["trash"].remove(t)    # CM2 : remove
        elif t["y"] > H + 60:
            state["trash"].remove(t)

    # — Singes —
    for m in state["monkeys"][:]:
        m["y"] += vitesse * 1.1 * dt
        mr = pygame.Rect(0, 0, 28, 28)
        mr.center = (int(m["x"]), int(m["y"]))
        if state["inv_t"] <= 0 and car_rect.colliderect(mr):
            state["lives"] -= 1
            state["inv_t"] = 1.2
            state["monkeys"].remove(m)
        elif m["y"] > H + 60:
            state["monkeys"].remove(m)

    # — Spawn —
    state["spawn_t"] += dt
    seuil = max(0.6, 1.1 - state["diff"] * 0.01)
    if state["spawn_t"] >= seuil:
        state["spawn_t"] = 0.0
        if random.random() < 0.7 and len(state["trash"]) < 9:      # CM2 : len
            spawner_dechet_jungle(state)
        if random.random() < 0.3 and len(state["monkeys"]) < 6:
            spawner_singe(state)

    # — Textes flottants —
    for ft in state["float_texts"][:]:
        ft[1] -= 45 * dt
        ft[3] += dt
        if ft[3] > 1.0:
            state["float_texts"].remove(ft)

    return None


# ── Dessin ─────────────────────────────────────────────────────────────────────
def dessiner_jungle(screen, state):
    """
    Affiche tout le jeu Jungle.
    CM1 : for  |  CM2 : itération de liste
    """
    screen.blit(state["bg"], (0, 0))

    # Tirets de route animés
    y = int(-state["scroll"])
    while y < H:                    # CM1 : while
        pygame.draw.rect(screen, (230, 230, 240), (W // 2 - 5, y, 10, 32), border_radius=3)
        y += 60

    for t in state["trash"]:
        img = pygame.transform.rotate(t["img"], t["rot"])
        screen.blit(img, img.get_rect(center=(int(t["x"]), int(t["y"]))))

    for m in state["monkeys"]:
        screen.blit(m["img"], (int(m["x"] - 27), int(m["y"] - 28)))

    # Voiture (clignotement si invincible)
    if state["inv_t"] <= 0 or int(state["inv_t"] * 12) % 2 == 0:
        screen.blit(state["car_img"], (int(state["car_x"] - 90), H - 120 - 67))

    for ft in state["float_texts"]:
        a = int(255 * (1 - ft[3]))
        s = state["font"].render(ft[2], True, ft[4])
        s.set_alpha(a)
        screen.blit(s, (int(ft[0]), int(ft[1])))

    # HUD
    pygame.draw.rect(screen, (255, 255, 255), (0, 0, W, 28))
    screen.blit(state["font"].render("Score: " + str(state["score"]), True, (20, 20, 20)),
                (10, 4))
    screen.blit(state["font"].render("Vies: " + str(state["lives"]), True, (200, 50, 50)),
                (W - 130, 4))
    tpct = max(0, state["time_left"] / TEMPS_TOTAL)
    pygame.draw.rect(screen, (200, 200, 210), (W // 2 - 75, 7, 150, 14), border_radius=7)
    pygame.draw.rect(screen, lerp_col((255, 60, 60), (70, 210, 140), tpct),
                     (W // 2 - 75, 7, int(150 * tpct), 14), border_radius=7)
    screen.blit(state["font"].render(str(int(state["time_left"])) + "s", True, (20, 20, 20)),
                (W // 2 + 83, 4))