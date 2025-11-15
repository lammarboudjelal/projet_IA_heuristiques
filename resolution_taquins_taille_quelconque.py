from heapq import heappush, heappop
import matplotlib.pyplot as plt
from collections import defaultdict
import time
import random

# --- Configuration des taquins ---

ETAT_OBJECTIF_3 = (
    (1, 2, 3),
    (4, 5, 6),
    (7, 8, 0)
)

ETAT_OBJECTIF_5 = (
    (1, 2, 3, 4, 5),
    (6, 7, 8, 9, 10),
    (11, 12, 13, 14, 15),
    (16, 17, 18, 19, 20),
    (21, 22, 23, 24, 0)
)

DEPLACEMENTS = {
    'Haut': (-1, 0),
    'Bas': (1, 0),
    'Gauche': (0, -1),
    'Droite': (0, 1)
}

DEPLACEMENTS_INVERSES = {
    'Haut': 'Bas',
    'Bas': 'Haut',
    'Gauche': 'Droite',
    'Droite': 'Gauche'
}

# --- Fonctions utilitaires ---

def lire_taquin():
    print("Entrez la taille n du taquin (3 pour 3x3, 5 pour 5x5) : ")
    n = int(input())

    print(f"Entrez le taquin initial {n}x{n} ligne par ligne (0 = case vide) :")

    etat = []
    for i in range(n):
        ligne = list(map(int, input().split()))
        etat.append(tuple(ligne))
    return tuple(etat)


def trouver_vide(etat):
    n = len(etat)
    for i in range(n):
        for j in range(n):
            if etat[i][j] == 0:
                return i, j


def trouver_coordonnee_generale(valeur, objectif):
    """Retourne la position finale d’une tuile donnée dans l’état objectif."""
    for i in range(len(objectif)):
        for j in range(len(objectif[0])):
            if objectif[i][j] == valeur:
                return i, j  


def deplacements_possibles_generaux(etat):
    """Retourne la liste des déplacements possibles à partir d'un état donné."""
    n = len(etat)
    x, y = next((i, j) for i in range(n) for j in range(n) if etat[i][j] == 0)

    deplacements = []
    for move, (dx, dy) in DEPLACEMENTS.items():
        nx, ny = x + dx, y + dy
        if 0 <= nx < n and 0 <= ny < n:
            new_state = [list(row) for row in etat]
            new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
            new_state_tuple = tuple(tuple(row) for row in new_state)
            deplacements.append((move, new_state_tuple))
    return deplacements


def heuristique(etat, objectif):
    """Heuristique : compte le nombre de tuiles mal placées."""
    mal_places = 0
    n = len(etat)
    for i in range(n):
        for j in range(n):
            if etat[i][j] != 0 and etat[i][j] != objectif[i][j]:
                mal_places += 1
    return mal_places


def heuristique_manhattan_generale(etat, objectif):
    """Heuristique 2 : somme des distances de Manhattan."""
    distance = 0
    n = len(etat)
    for x in range(n):
        for y in range(n):
            valeur = etat[x][y]
            if valeur != 0:
                (goal_x, goal_y) = trouver_coordonnee_generale(valeur, objectif)
                distance += abs(x - goal_x) + abs(y - goal_y)
    return distance


def heuristique_manhattan_modifiee(etat, facteur, objectif) :
    """
    Heuristique 2 modifiée : distance de Manhattan amplifiée par un facteur entre 1 et 2
    pour accélérer la recherche lorsque la solution est encore éloignée.
    """
    distance = heuristique_manhattan_generale(etat, objectif)

    # Si le nombre de coups restants estimé est important, on amplifie.
    # Lorsqu'il reste moins de 5 coups à jouer, on conserve la valeur originale pour préserver la précision.
    if distance >= 5:
        distance *= facteur  
    return distance


def afficher_taquin(etat):
    """Affiche joliment un état du taquin."""
    n = len(etat)
    for i in range(n):
        ligne = ' '.join(str(x) if x != 0 else ' ' for x in etat[i])
        print(ligne)
    print("-------")


def lire_fichier_taquins(nom_fichier):
    """
    Lit plusieurs taquins depuis un fichier texte.
    Chaque taquin est séparé par une ligne vide dans le fichier.
    """
    f = open(nom_fichier)
    contenu = f.read()
    blocs = contenu.split("\n\n") # Séparation de chaque taquin
    taquins = []

    for bloc in blocs:
        lignes = []
        # On parcourt chaque ligne du bloc (ex: "1 2 3")
        for ligne in bloc.strip().split("\n"):
            nombres = ligne.split() # ["1", "2", "3"]         
            nombres_int = list(map(int, nombres))  # [1, 2, 3]
            lignes.append(tuple(nombres_int)) # (1, 2, 3)
        taquins.append(tuple(lignes)) # Un taquin = tuple de 3 lignes
    f.close()
    return taquins


def tracer_graphe_moyen(valeurs, x_label, y_label):
    """
    Trace un graphique représentant la moyenne du nombre de coups restants 
    pour chaque valeur d'heuristique (h).
    """  
    # On regroupe toutes les valeurs d (distance réelle) pour chaque h (heuristique)
    groupes = defaultdict(list)
    for h, d in valeurs:
        groupes[h].append(d)

    # On calcule la moyenne de chaque groupe
    h_valeurs = sorted(groupes.keys())  # on trie les valeurs d'heuristique croissantes
    moyennes = []
    for h in h_valeurs:
        moyenne_d = sum(groupes[h]) / len(groupes[h])
        moyennes.append(moyenne_d)

    # On trace la courbe moyenne
    plt.plot(h_valeurs, moyennes, marker='o')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title("Lien entre heuristique et distance réelle moyenne")
    plt.grid(True)
    plt.show()  


def trouver_facteur_optimal(taquins, objectif):
    """
    Cherche le plus grand facteur multiplicateur de la distance de Manhattan qui conserve au moins 90%
    de solutions optimales (nombre minimal de coups) et affiche les résultats à chaque test.
    """
    objectif_optimalite = 0.9
    facteur_max = 2.0
    pas = 0.05
    facteur = 1.0
    facteur_optimal = facteur
    meilleur_gain = 0.0

    while facteur <= facteur_max:
        solutions_optimales = 0
        gains_noeuds = []

        for initial in taquins:
            # Résolution avec heuristique classique
            chemin_ref, _, open_ref, visited_ref = a_etoile(initial, objectif, heuristique_manhattan_generale)
            noeuds_ref = open_ref + visited_ref

            # Résolution avec heuristique amplifiée
            chemin_mod, _, open_mod, visited_mod = a_etoile(
                initial, 
                lambda etat: heuristique_manhattan_modifiee(etat, facteur, objectif)
            )
            noeuds_mod = open_mod + visited_mod

            if chemin_mod is not None and len(chemin_mod) == len(chemin_ref):
                solutions_optimales += 1

            if noeuds_ref > 0:
                gain = (noeuds_ref - noeuds_mod) / noeuds_ref * 100
                gains_noeuds.append(gain)

        total = len(taquins)
        taux_optimalite = solutions_optimales / total * 100
        gain_moyen = sum(gains_noeuds) / len(gains_noeuds) if gains_noeuds else 0.0

        print(f"Test du facteur {facteur:.2f} :")
        print(f"    - Taux d'optimalité : {taux_optimalite:.1f}%")
        print(f"    - Gain moyen noeuds explorés : {gain_moyen:.1f}%\n")

        if taux_optimalite >= objectif_optimalite and gain_moyen >= meilleur_gain:
            facteur_optimal = facteur
            meilleur_gain = gain_moyen
        else:
            # On arrête dès que l'optimalité descend en dessous du seuil
            break

        facteur += pas

    print(f"Facteur optimal retenu : {facteur_optimal:.2f} (Gain moyen {meilleur_gain:.1f}%)\n")
    return facteur_optimal


# --- Algorithme A* ---

def a_etoile(initial, objectif, heuristique_fct): # On fait passer la fonction de l'heuristique utilisée en paramètre
    open_set = []
    heappush(open_set, (heuristique_fct(initial, objectif), 0, initial, []))
    visited = set()

    while open_set:
        f, g, etat, chemin = heappop(open_set)

        if etat == objectif:
            return chemin, etat, len(open_set), len(visited)

        if etat in visited:
            continue

        visited.add(etat)

        for move, next_state in deplacements_possibles_generaux(etat):
            if next_state not in visited:
                new_g = g + 1
                h = heuristique_fct(next_state, objectif)
                heappush(open_set, (new_g + h, new_g, next_state, chemin + [(move, next_state)]))

    return None, None, 0, len(visited)


# --- Algorithme IDA* ---

def ida_star(initial, objectif, heuristique_fct):
    """
    Implémentation de l’algorithme IDA* :
    - profondeur limitée progressive
    - fonction de coût f = g + h
    - exploration en profondeur guidée par l’heuristique
    """
    seuil = heuristique_fct(initial, objectif) # seuil initial = heuristique du départ
    expansions = 0

    def recherche(etat, g, seuil, chemin, last_move):
        nonlocal expansions
        expansions += 1

        f = g + heuristique_fct(etat, objectif)
        if f > seuil: # dépassement du seuil : retourne f minimal dépassé
            return f, None
        if etat == objectif: # état objectif atteint
            return f, chemin

        min_seuil = float("inf")

        for move, new_state in deplacements_possibles_generaux(etat):
            # évite le retour immédiat sur le dernier move
            if last_move is not None and move == DEPLACEMENTS_INVERSES.get(last_move):
                continue
            # évite les cycles déjà présents dans le chemin
            already_in_path = any(new_state == s for (_, s) in chemin)
            if already_in_path:
                continue

            # exploration récursive
            new_f, sol = recherche(new_state, g + 1, seuil, chemin + [(move, new_state)], move)
            if sol is not None:
                return new_f, sol
            if new_f < min_seuil:
                min_seuil = new_f

        return min_seuil, None

    # boucle d'approfondissement : augmente progressivement le seuil
    while True:
        nouveau_seuil, solution = recherche(initial, 0, seuil, [], None)
        if solution is not None:
            return solution, expansions
        if nouveau_seuil == float("inf"):
            return None, expansions
        seuil = nouveau_seuil


# --- Tests : 3 taquins 5x5 pour comparaison ---

def generer_taquin(n, coups):
    """
    Génère un taquin nxn solvable en effectuant un nombre donné de coups aléatoires à partir de l'état objectif.
    """
    etat = [list(range(i*n+1, (i+1)*n+1)) for i in range(n)]
    etat[-1][-1] = 0  # case vide
    x, y = n-1, n-1

    dernier_move = None
    for _ in range(coups):
        moves_possibles = []
        for move, (dx, dy) in DEPLACEMENTS.items():
            if dernier_move is not None and DEPLACEMENTS_INVERSES[dernier_move] == move:
                continue
            nx, ny = x+dx, y+dy
            if 0 <= nx < n and 0 <= ny < n:
                moves_possibles.append((move, nx, ny))
        move, nx, ny = random.choice(moves_possibles)
        etat[x][y], etat[nx][ny] = etat[nx][ny], etat[x][y]
        x, y = nx, ny
        dernier_move = move
    return tuple(tuple(row) for row in etat)

taquin_5x5_simple = generer_taquin(5, 10)
taquin_5x5_intermediaire = generer_taquin(5, 60)
taquin_5x5_difficile = generer_taquin(5, 80)


def main():    
    print("=== Tests comparatifs A* vs IDA* (5x5) ===")

    tests = [
        ("Simple", taquin_5x5_simple),
        ("Intermédiaire", taquin_5x5_intermediaire),
        ("Difficile", taquin_5x5_difficile),
    ]

    for nom, etat in tests:
        print(f"\n--- {nom} ---")
        afficher_taquin(etat)

        # --- IDA* avec heuristique Manhattan standard ---
        t0 = time.time()
        (chemin_i, expansions_i) = ida_star(etat, ETAT_OBJECTIF_5, heuristique_manhattan_generale)
        t1 = time.time()
        duree_i = t1 - t0

        if chemin_i is None:
            print(f"IDA* : aucune solution trouvée (après {expansions_i} expansions). temps = {duree_i:.4f} s")
        else:
            print(f"IDA* : solution en {len(chemin_i)} coups, temps = {duree_i:.4f} s, expansions = {expansions_i}")

        # --- A* avec heuristique Manhattan standard ---
        t0 = time.time()
        chemin_a, _, open_len_a, visited_len_a = a_etoile(etat, ETAT_OBJECTIF_5, heuristique_manhattan_generale)
        t1 = time.time()
        duree_a = t1 - t0

        if chemin_a is None:
            print("A* : aucune solution trouvée (ou mémoire insuffisante).")
        else:
            print(f"A* : solution en {len(chemin_a)} coups, temps = {duree_a:.4f} s, open={open_len_a}, visited={visited_len_a}")

    print("\nTests terminés.")

if __name__ == "__main__":
    main()

