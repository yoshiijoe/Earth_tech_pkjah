import random
import pygame
from config import W, H, clamp, lerp_col, sprite

# ── Constantes ────────────────────────────────────────────────────────────────
SURF_Y      = 140
TRASH_KINDS = ["bottle", "can", "bag", "tire", "box"]
FISH_KINDS  = ["orange", "blue", "purple"]
TEMPS_TOTAL = 75.0


# ── Spawn helpers ─────────────────────────────────────────────────────────────
def spawner_dechet(state):
    """Ajoute un déchet à la liste (CM2 : append)."""
    k = random.choice(TRASH_KINDS)          # CM3 : random.choice
    y = random.uniform(SURF_Y + 50, H - 60)
    state["trash"].append({
        "x": -50.0,
        "y": y,
        "vx": random.uniform(60, 100),
        "img": sprite("trash_" + k),
    })


def spawner_poisson(state):
    """Ajoute un poisson à la liste (CM2 : append)."""
    y = random.uniform(SURF_Y + 30, H - 50)
    state["fish"].append({
        "x": float(W + 50),
        "y": y,
        "vx": -random.uniform(80, 130),
        "img": sprite("fish_" + random.choice(FISH_KINDS)),
    })


# ── Création de l'état (CM5 : dictionnaire) ───────────────────────────────────
def creer_ocean(data):
    """Initialise et retourne le dictionnaire d'état du jeu Océan."""
    # Surfaces d'arrière-plan
    ciel = pygame.Surface((W, SURF_Y))
    ciel.fill((135, 200, 240))
    mer = pygame.Surface((W, H - SURF_Y))
    mer.fill((25, 85, 150))

    state = {
        "font":        pygame.font.Font(None, 28),
        "ciel":        ciel,
        "mer":         mer,
        "boat_img":    sprite("boat"),
        "gr_img":      sprite("grapple"),
        # Bateau
        "boat_x":      float(W // 2),
        "boat_vx":     0.0,
        # Grappin
        "gr_active":   False,
        "gr_etat":     "idle",   # "idle" | "down" | "up"
        "gr_y":        float(SURF_Y),
        "gr_caught":   None,
        # Entités  (CM2 : listes)
        "trash":       [],
        "fish":        [],
        "float_texts": [],
        # Stats
        "score":       0,
        "lives":       10,
        "time_left":   TEMPS_TOTAL,
        "spawn_t":     0.0,
        "trash_limit": 3,
        "scale_t":     0.0,
        "details":     [],
    }

    for _ in range(2):    # CM1 : for
        spawner_dechet(state)
    for _ in range(3):
        spawner_poisson(state)

    return state


# ── Gestion des événements ─────────────────────────────────────────────────────
def gerer_ocean(state, event):
    """
    Gère un événement pygame.
    Retourne 'menu', 'pause' ou None.
    CM1 : if/elif/else
    """
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            return "menu"
        elif event.key == pygame.K_p:
            return "pause"
        elif event.key == pygame.K_SPACE:
            if not state["gr_active"]:
                state["gr_active"] = True
                state["gr_etat"]   = "down"
                state["gr_y"]      = float(SURF_Y)
                state["gr_caught"] = None
            elif state["gr_etat"] == "down":
                state["gr_etat"] = "up"
    return None


# ── Mise à jour ────────────────────────────────────────────────────────────────
def mettre_a_jour_ocean(state, dt):
    """
    Met à jour toute la physique du jeu.
    Retourne 'fin' si la partie est terminée, sinon None.
    CM1 : if/elif, for, while  |  CM2 : append, remove, len
    """
    state["time_left"] -= dt
    state["scale_t"]   += dt
    if state["scale_t"] >= 10.0:
        state["scale_t"]     = 0.0
        state["trash_limit"] = int(state["trash_limit"] * 1.5)

    # — Fin de partie —
    if state["time_left"] <= 0 or state["lives"] <= 0:
        state["details"] = [("Déchets", str(state["score"] // 10))]
        return "fin"

    # — Bateau —
    keys = pygame.key.get_pressed()
    ax = 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        ax -= 1300
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        ax += 1300
    state["boat_vx"] = clamp(state["boat_vx"] * (1 - 7 * dt) + ax * dt, -300, 300)
    state["boat_x"]  = clamp(state["boat_x"] + state["boat_vx"] * dt, 60, W - 60)

    # — Grappin —
    gr_x = state["boat_x"]
    if state["gr_active"]:
        if state["gr_etat"] == "down":
            state["gr_y"] += 260 * dt
            if state["gr_y"] >= H - 60:
                state["gr_etat"] = "up"

            # Collision déchet
            if state["gr_caught"] is None:
                for t in state["trash"]:    # CM1 : for  |  CM2 : list iteration
                    if abs(gr_x - t["x"]) < 32 and abs(state["gr_y"] - t["y"]) < 32:
                        state["gr_caught"] = t
                        state["gr_etat"]   = "up"
                        break

            # Collision poisson
            for f in state["fish"]:
                if abs(gr_x - f["x"]) < 28 and abs(state["gr_y"] - f["y"]) < 22:
                    state["lives"] -= 1
                    state["gr_etat"] = "up"
                    break

        else:   # "up"
            state["gr_y"] -= 260 * dt
            if state["gr_caught"] is not None:
                state["gr_caught"]["x"] = gr_x
                state["gr_caught"]["y"] = state["gr_y"] + 22
            if state["gr_y"] <= SURF_Y:
                if state["gr_caught"] is not None:
                    if state["gr_caught"] in state["trash"]:
                        state["trash"].remove(state["gr_caught"])   # CM2 : remove
                    state["score"] += 10
                    state["float_texts"].append(
                        [gr_x, SURF_Y - 20, "+10", 0.0, (70, 210, 140)]
                    )
                    state["gr_caught"] = None
                state["gr_active"] = False
                state["gr_etat"]   = "idle"

    # — Déchets —
    for t in state["trash"][:]:     # CM1 : for  |  CM2 : copie de liste
        t["x"] += t["vx"] * dt
        if t["x"] > W + 60:
            state["trash"].remove(t)

    # — Poissons —
    for f in state["fish"][:]:
        f["x"] += f["vx"] * dt
        if f["x"] < -60:
            state["fish"].remove(f)
            continue
        fr = pygame.Rect(0, 0, 40, 28)
        fr.center = (int(f["x"]), int(f["y"]))
        touche = False
        for t in state["trash"]:
            tr = pygame.Rect(0, 0, 46, 46)
            tr.center = (int(t["x"]), int(t["y"]))
            if fr.colliderect(tr):
                touche = True
                break
        if touche:
            state["fish"].remove(f)

    # — Spawn —
    state["spawn_t"] += dt
    if state["spawn_t"] >= 1.5:
        state["spawn_t"] = 0.0
        if len(state["trash"]) < state["trash_limit"]:   # CM2 : len
            spawner_dechet(state)
        if len(state["fish"]) < 6:
            spawner_poisson(state)

    # — Textes flottants —
    for ft in state["float_texts"][:]:
        ft[1] -= 45 * dt
        ft[3] += dt
        if ft[3] > 1.0:
            state["float_texts"].remove(ft)

    return None


# ── Dessin ─────────────────────────────────────────────────────────────────────
def dessiner_ocean(screen, state):
    """
    Affiche tout le jeu Océan.
    CM1 : for  |  CM2 : itération de liste
    """
    screen.blit(state["ciel"], (0, 0))
    screen.blit(state["mer"],  (0, SURF_Y))
    pygame.draw.line(screen, (190, 235, 255), (0, SURF_Y), (W, SURF_Y), 3)

    for f in state["fish"]:
        screen.blit(f["img"], (int(f["x"] - 24), int(f["y"] - 16)))
    for t in state["trash"]:
        screen.blit(t["img"], (int(t["x"] - 27), int(t["y"] - 27)))

    if state["gr_active"]:
        gx = int(state["boat_x"])
        gy = int(state["gr_y"])
        pygame.draw.line(screen, (110, 110, 125), (gx, SURF_Y + 10), (gx, gy), 2)
        screen.blit(state["gr_img"], (gx - 17, gy - 17))

    screen.blit(state["boat_img"], (int(state["boat_x"] - 48), 30))

    for ft in state["float_texts"]:
        a = int(255 * (1 - ft[3]))
        s = state["font"].render(ft[2], True, ft[4])
        s.set_alpha(a)
        screen.blit(s, (int(ft[0] - s.get_width() // 2), int(ft[1])))

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