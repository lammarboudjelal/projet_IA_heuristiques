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


def tracer_graphe_moyen(valeurs):
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
    plt.xlabel("Heuristique (nombre de tuiles mal placées)")
    plt.ylabel("Nombre moyen de coups restants (distance moyenne restante)")
    plt.title("Lien entre heuristique et distance réelle moyenne")
    plt.grid(True)
    plt.show()  

# --- Algorithme A* ---

def a_etoile(initial):
    open_set = []
    heappush(open_set, (heuristique(initial), 0, initial, []))
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
                h = heuristique(next_state)
                heappush(open_set, (new_g + h, new_g, next_state, chemin + [(move, next_state)]))

    return None, None, 0, len(visited)


def main():
    # --- Code initial : saisie manuelle ---
    # initial = lire_taquin()
    # print("\nRésolution en cours...\n")

    # chemin, final, taille_open, taille_visited = a_etoile(initial)

    # if chemin is None:
    #     print("Aucune solution trouvée.")
    # else:
    #     print(f"Solution trouvée en {len(chemin)} coups :\n")
    #     etat_courant = initial
    #     afficher_taquin(etat_courant)

    #     for move, etat_suivant in chemin:
    #         print(f"Coup : {move} (heuristique = {heuristique(etat_suivant)})")
    #         afficher_taquin(etat_suivant)
    #         etat_courant = etat_suivant

    #     print("🎯 Taquin résolu !")
    #     print(f"Nombre final d'états dans open : {taille_open}")
    #     print(f"Nombre d'états visités : {taille_visited}")
    
    # --- Nouvelle version : lecture automatique de plusieurs taquins
    nom_fichier = "taquins.txt"
    # nom_fichier = "taquin_test.txt" # Utilisé pour tester individuellement des taquins et afficher leur graphique
    taquins = lire_fichier_taquins(nom_fichier)
    print(f"{len(taquins)} taquin(s) chargé(s) depuis le fichier {nom_fichier}\n")

    toutes_valeurs = [] 

    for i, initial in enumerate(taquins, 1):
        print(f"=== TAQUIN {i} ===")
        afficher_taquin(initial)
        print("Résolution en cours...\n")

        chemin, final, taille_open, taille_visited = a_etoile(initial)

        if chemin is None:
            print("Aucune solution trouvée.\n")
            continue

        print(f"Solution trouvée en {len(chemin)} coups.\n")

        # On collecte les couples (heuristique, coups restants)
        for i, (move, etat_suivant) in enumerate(chemin, start=1):
            h = heuristique(etat_suivant)
            d = len(chemin) - i
            toutes_valeurs.append((h, d))

    # Une fois tous les taquins traités, on trace le graphique moyen
    tracer_graphe_moyen(toutes_valeurs)

if __name__ == "__main__":
    main()
