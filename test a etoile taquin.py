from heapq import heappush, heappop
import matplotlib.pyplot as plt
from collections import defaultdict

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

def heuristique_manhattan_modifiee(etat) :
    """
    Heuristique 2 modifiée : distance de Manhattan légèrement amplifiée
    pour accélérer la recherche lorsque la solution est encore éloignée.
    """
    distance = heuristique_manhattan(etat)

    # Si le nombre de coups restants estimé est important, on amplifie légèrement.
    # Lorsqu'il reste moins de 5 coups à jouer, on conserve la valeur originale pour préserver la précision.
    if distance >= 5:
        distance *= 1.1  
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
    # --- Comparaison des deux versions de l'heuristique de manhattan ---
    nom_fichier = "taquins.txt"
    taquins = lire_fichier_taquins(nom_fichier)
    print(f"{len(taquins)} taquin(s) chargé(s) depuis le fichier {nom_fichier}\n")

    gains_noeuds = [] # Liste pour stocker le gain de chaque taquin
    valeurs_manhattan_modifiee = []  # Pour tracer le graphique (h, distance réelle)

    for i, initial in enumerate(taquins, 1):
        print(f"=== TAQUIN {i} ===")
        afficher_taquin(initial)

        # Résolution avec l’heuristique de manhattan
        chemin1, final1, open1, visited1 = a_etoile(initial, heuristique_manhattan)
        noeuds1 = open1 + visited1 # nombre de nœuds explorés avec la distance de Manhattan originale

        # Résolution avec l’heuristique de manhattan modifiée (amplification légère)
        chemin2, final2, open2, visited2 = a_etoile(initial, heuristique_manhattan_modifiee)
        noeuds2 = open2 + visited2 # nombre de nœuds explorés avec la distance de Manhattan modifiée/amplifiée

        if chemin1 is None or chemin2 is None : 
            print("Aucune solution trouvée.")
        else :
            print("\nRésultats comparés :")
            print(f"  - Distance Manhattan originale : {len(chemin1)} coups, {noeuds1} nœuds explorés")
            print(f"  - Distance Manhattan amplifiée : {len(chemin2)} coups, {noeuds2} nœuds explorés")
            
            gain = ((noeuds1 - noeuds2) / noeuds1) * 100
            print(f"=> Réduction du nombre de nœuds : {gain:.1f}%\n")
            gains_noeuds.append(gain)  

            # On stocke les valeurs pour le graphique
            h_initial = heuristique_manhattan_modifiee(initial)
            valeurs_manhattan_modifiee.append((h_initial, len(chemin2)))

    # Calcul et affichage du gain moyen 
    if gains_noeuds:
        gain_moyen = sum(gains_noeuds) / len(gains_noeuds)
        print(f"Gain moyen du nombre de nœuds explorés : {gain_moyen:.1f}%\n")

    # Tracé du graphique illustrant la relation heuristique de Manhattan modifiée / distance réelle
    if valeurs_manhattan_modifiee:
        tracer_graphe_moyen(valeurs_manhattan_modifiee, "Heuristique (distance de Manhattan modifiée/amplifiée)", "Nombre moyen de coups restants (distance moyenne restante)")

    print("Comparaison terminée pour tous les taquins.\n")

if __name__ == "__main__":
    main()
