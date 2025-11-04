from heapq import heappush, heappop
import matplotlib.pyplot as plt
from collections import defaultdict
import time

# --- Configuration du taquin ---
ETAT_OBJECTIF = (
    (1, 2, 3),
    (4, 5, 6),
    (7, 8, 0)
)

DEPLACEMENTS = {
    'Haut': (-1, 0),
    'Bas': (1, 0),
    'Gauche': (0, -1),
    'Droite': (0, 1)
}

# --- Fonctions utilitaires ---

def lire_taquin():
    print("Entrez le taquin initial ligne par ligne (avec 0 pour la case vide) :")
    etat = []
    for i in range(3):
        ligne = list(map(int, input().split()))
        etat.append(tuple(ligne))
    return tuple(etat)


def trouver_vide(etat):
    for i in range(3):
        for j in range(3):
            if etat[i][j] == 0:
                return i, j


def trouver_coordonnee(valeur):
    """Retourne la position finale d’une tuile donnée dans l’état objectif."""
    for i in range(3):
        for j in range(3):
            if ETAT_OBJECTIF[i][j] == valeur:
                return i, j
            

def deplacements_possibles(etat):
    """Retourne la liste des déplacements possibles à partir d'un état donné."""
    x, y = trouver_vide(etat)
    deplacements = []

    for move, (dx, dy) in DEPLACEMENTS.items():
        nx, ny = x + dx, y + dy
        if 0 <= nx < 3 and 0 <= ny < 3:
            new_state = [list(row) for row in etat]
            # Échange de la case vide avec la case cible
            new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
            new_state_tuple = tuple(tuple(row) for row in new_state)
            deplacements.append((move, new_state_tuple))

    return deplacements


def heuristique(etat):
    """Heuristique : compte le nombre de tuiles mal placées."""
    mal_places = 0
    for i in range(3):
        for j in range(3):
            if etat[i][j] != 0 and etat[i][j] != ETAT_OBJECTIF[i][j]:
                mal_places += 1
    return mal_places


def heuristique_manhattan(etat):
    """Heuristique 2 : somme des distances de Manhattan."""
    distance = 0
    for x in range(len(etat)):
        for y in range(len(etat[x])):
            valeur = etat[x][y]
            if valeur != 0:
                (goal_x, goal_y) = trouver_coordonnee(valeur)
                distance += abs(x - goal_x) + abs(y - goal_y)
    return distance

def heuristique_manhattan_modifiee(etat, facteur) :
    """
    Heuristique 2 modifiée : distance de Manhattan amplifiée par un facteur entre 1 et 2
    pour accélérer la recherche lorsque la solution est encore éloignée.
    """
    distance = heuristique_manhattan(etat)

    # Si le nombre de coups restants estimé est important, on amplifie.
    # Lorsqu'il reste moins de 5 coups à jouer, on conserve la valeur originale pour préserver la précision.
    if distance >= 5:
        distance *= facteur  
    return distance


def afficher_taquin(etat):
    """Affiche joliment un état du taquin."""
    for i in range(3):
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

def trouver_facteur_optimal(taquins):
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
            chemin_ref, _, open_ref, visited_ref = a_etoile(initial, heuristique_manhattan)
            noeuds_ref = open_ref + visited_ref

            # Résolution avec heuristique amplifiée
            chemin_mod, _, open_mod, visited_mod = a_etoile(
                initial, 
                lambda etat: heuristique_manhattan_modifiee(etat, facteur)
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

def a_etoile(initial, heuristique_fct): # On fait passer la fonction de l'heuristique utilisée en paramètre
    open_set = []
    heappush(open_set, (heuristique_fct(initial), 0, initial, []))
    visited = set()

    while open_set:
        f, g, etat, chemin = heappop(open_set)

        if etat == ETAT_OBJECTIF:
            return chemin, etat, len(open_set), len(visited)

        if etat in visited:
            continue

        visited.add(etat)

        for move, next_state in deplacements_possibles(etat):
            if next_state not in visited:
                new_g = g + 1
                h = heuristique_fct(next_state)
                heappush(open_set, (new_g + h, new_g, next_state, chemin + [(move, next_state)]))

    return None, None, 0, len(visited)


def main():    
    nom_fichier = "taquins.txt"
    taquins = lire_fichier_taquins(nom_fichier)
    print(f"{len(taquins)} taquin(s) chargé(s) depuis le fichier {nom_fichier}\n")

    # --- Recherche du facteur optimal ---
    # facteur_optimal = trouver_facteur_optimal(taquins)
    facteur_optimal = 1.3

    # --- Résolution avec l'heuristique de Manhattan amplifiée ---
    temps_classique = []
    temps_amplifie = []

    valeurs_manhattan_modifiee = []

    for initial in taquins:
        # --- Temps pour heuristique classique ---
        t0 = time.time()
        chemin_ref, _, _, _ = a_etoile(initial, heuristique_manhattan)
        t1 = time.time()
        if chemin_ref is not None:
            temps_classique.append(t1 - t0)

        # --- Temps pour heuristique amplifiée ---
        t0 = time.time()
        chemin_mod, _, _, _ = a_etoile(initial, lambda etat: heuristique_manhattan_modifiee(etat, facteur_optimal))
        t1 = time.time()
        if chemin_mod is not None:
            temps_amplifie.append(t1 - t0)
            h_initial = heuristique_manhattan_modifiee(initial, facteur_optimal)
            valeurs_manhattan_modifiee.append((h_initial, len(chemin_mod)))
    
    # --- Moyenne des temps ---
    if temps_classique and temps_amplifie:
        t_classique_moyen = sum(temps_classique) / len(temps_classique)
        t_amplifie_moyen = sum(temps_amplifie) / len(temps_amplifie)
        gain_temps = (t_classique_moyen - t_amplifie_moyen) / t_classique_moyen * 100

        print(f"\nTemps moyen heuristique classique : {t_classique_moyen:.4f} s")
        print(f"Temps moyen heuristique amplifiée : {t_amplifie_moyen:.4f} s")
        print(f"Gain moyen de temps : {gain_temps:.1f}%\n")

    print("Test terminé avec l'heuristique de Manhattan amplifiée.")

if __name__ == "__main__":
    main()
