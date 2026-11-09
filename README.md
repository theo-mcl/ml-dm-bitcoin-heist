# Détection d'adresses Bitcoin liées à des rançongiciels

Projet de machine learning de Théo Michel et Théo Rico. À partir du jeu de données BitcoinHeist (UCI), nous cherchons à repérer les adresses ayant reçu des rançons, avec Random Forest et XGBoost.

## Contenu

| Fichier | Rôle |
|---|---|
| `notebook.ipynb` | Le notebook de l'étude : code, résultats, graphiques et commentaires. |
| `functions.py` | Fonctions utilisées par le notebook (affichage, métriques). |
| `requirements.txt` | Bibliothèques Python nécessaires. |
| `article.pdf` | Article de référence du jeu de données. |
| `video_michel_rico.mp4` | Vidéo de présentation du projet. |

Le jeu de données (`BitcoinHeistData.csv`, 236 Mo) n'est pas inclus, à cause de sa taille. Il est public et se télécharge sur l'UCI Machine Learning Repository : <https://archive.ics.uci.edu/dataset/526/bitcoinheistransomwareaddressdataset>

## Lire le notebook sans l'exécuter

Le notebook est enregistré avec toutes ses sorties (tableaux, graphiques, résultats). Il suffit de l'ouvrir dans Jupyter, VS Code ou sur GitHub pour tout consulter : aucune installation ni exécution n'est nécessaire.

## Réexécuter le notebook

1. Installer les dépendances :
   ```
   pip install -r requirements.txt
   ```
2. Télécharger `BitcoinHeistData.csv` (lien ci-dessus) et le placer dans le même dossier que le notebook et `functions.py`.
3. Ouvrir `notebook.ipynb` dans Jupyter et lancer « Exécuter tout ».

L'exécution complète prend environ 30 minutes et demande environ 4 Go de mémoire libre : toutes les forêts aléatoires sont réentraînées. Le notebook enregistre au passage des modèles (`*.joblib`) et des résultats intermédiaires (`rf_experiments/`) dans le dossier. S'ils sont présents et à jour, une exécution suivante les réutilise et va plus vite.

Le notebook a été réexécuté entièrement dans un environnement neuf (Python 3.14, versions récentes des bibliothèques) : toutes les cellules passent et les résultats sont identiques, à quelques écarts près sur la troisième décimale.
