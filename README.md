# Projet du module "Bases de l’I.A." 2025 - 2026 

## Contexte du projet

Ce projet s’inscrit dans le cadre du module *Bases de l’Intelligence Artificielle*.  
L’objectif global est d’étudier et d’expérimenter l’algorithme **A\*** (A-star) appliqué au **problème du taquin 3×3**.  

Le but est de résoudre le taquin en un nombre minimal de coups tout en évaluant l’impact du **choix d’heuristique** sur les performances de la recherche.  
Différentes heuristiques sont testées et comparées afin de mesurer leur efficacité à réduire la taille de l’arbre d’exploration, le temps de calcul et le nombre d’états visités.

Le projet se décompose en quatre étapes principales (quatre questions):
1. Étude de l’heuristique des tuiles mal placées (code de base fourni).  
2. Implémentation d’une heuristique plus performante (distance de Manhattan).  
3. Amélioration de l’heuristique pour accélérer la recherche.  
4. Extension éventuelle au taquin 5×5.

Un rapport détaillé accompagne le code et présente les résultats, graphiques et interprétations obtenus.

## Code initial fourni 

Le code initial fourni implémente l’algorithme **A\*** pour résoudre un taquin 3×3.  
Il utilise comme heuristique le **nombre de tuiles mal placées** (c’est-à-dire le nombre de cases qui ne sont pas à leur position finale).

Afin de tester le programme initiale : 

> 1. Ouvrir un terminal dans le répertoire du projet.  

> 2. Lance le script principal :  
```
python3 test\ a\ etoile\ taquin.py 
```

> 3. Saisir le taquin ligne par ligne (avec un espace entre chaque nombre).
```
Entrez le taquin initial ligne par ligne (avec 0 pour la case vide) :
6 2 5
7 4 1
3 8 0
```

> Exemple de sortie correspond au taquin ci-dessus : 
```
Résolution en cours...

Solution trouvée en 23 coups :

6 2 5
7 4 1
3   8
-------
Coup : Haut (heuristique = 7)
6 2 5
7   1
3 4 8
-------
Coup : Gauche (heuristique = 7)
6 2 5
  7 1
3 4 8
-------
Coup : Bas (heuristique = 7)
6 2 5
3 7 1
  4 8
-------
Coup : Droite (heuristique = 7)
6 2 5
3 7 1
4   8
-------
Coup : Haut (heuristique = 7)
6 2 5
3   1
4 7 8
-------
Coup : Haut (heuristique = 8)
6   5
3 2 1
4 7 8
-------
Coup : Gauche (heuristique = 8)
  6 5
3 2 1
4 7 8
-------
Coup : Bas (heuristique = 8)
3 6 5
  2 1
4 7 8
-------
Coup : Droite (heuristique = 8)
3 6 5
2   1
4 7 8
-------
Coup : Droite (heuristique = 8)
3 6 5
2 1  
4 7 8
-------
Coup : Haut (heuristique = 8)
3 6  
2 1 5
4 7 8
-------
Coup : Gauche (heuristique = 8)
3   6
2 1 5
4 7 8
-------
Coup : Gauche (heuristique = 8)
  3 6
2 1 5
4 7 8
-------
Coup : Bas (heuristique = 8)
2 3 6
  1 5
4 7 8
-------
Coup : Droite (heuristique = 8)
2 3 6
1   5
4 7 8
-------
Coup : Droite (heuristique = 7)
2 3 6
1 5  
4 7 8
-------
Coup : Haut (heuristique = 6)
2 3  
1 5 6
4 7 8
-------
Coup : Gauche (heuristique = 5)
2   3
1 5 6
4 7 8
-------
Coup : Gauche (heuristique = 4)
  2 3
1 5 6
4 7 8
-------
Coup : Bas (heuristique = 3)
1 2 3
  5 6
4 7 8
-------
Coup : Bas (heuristique = 2)
1 2 3
4 5 6
  7 8
-------
Coup : Droite (heuristique = 1)
1 2 3
4 5 6
7   8
-------
Coup : Droite (heuristique = 0)
1 2 3
4 5 6
7 8  
-------
🎯 Taquin résolu !
Nombre final d'états dans open : 7169
Nombre d'états visités : 13023
```

## Auteurs 

- Lina AMMAR-BOUDJELAL
- Flore ADVENIER

Promotion 2027 - Groupe 1