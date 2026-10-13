# Notes générales

Le prof a dit que c'est mieux d'afficher des exemples que l'ensemble des données, ça aide à ne pas tirer des conclusions sur les anomalies.
Par exemple, comme dans le BE, on peut regarder sur des cycles, sur des fenêtres.

Garder les labels le dataset c'est une erreur de débutant.s

Dans le notebook1 sur gradient boosting, il fait un encodage du label pour transformer les chaines de caractères en nombre.
Il existe aussi le **one-hot encoding.**

## Etapes de résolution

Afficher les colonnes du dataset, faire du feature engineering, séparer en train/test.


# Random forest et XGBOOST

**La tâche retenue ici** est de prédire le label fourni : `0 = white (non signalé)` et `1 = ransomware signalé`. Ce n'est pas une preuve d'innocence pour les `white`, ni une validation de ransomwares jusqu'ici inconnus. La prédiction porte sur une observation quotidienne d'adresse, pas directement sur une personne ou un fichier malveillant.

Nous disposons de six mesures numériques du graphe et de labels : c'est une classification supervisée sur données tabulaires. Les relations peuvent dépendre de seuils et d'interactions entre mesures ; une faible corrélation marginale n'exclut pas un signal prédictif.

- **Arbres, chapitre 8 :** partitions successives par seuils, adaptées à des relations non linéaires. Un arbre seul peut changer beaucoup si l'échantillon change.
- **Bagging, chapitre 11, puis Random Forest, chapitre 12 :** plusieurs arbres apprennent sur des tirages bootstrap. À chaque nœud, seuls certains attributs choisis aléatoirement sont candidats à la coupure. L'agrégation réduit la variance ; la sélection aléatoire des attributs réduit la corrélation entre les arbres. Les variables n'ont pas besoin d'être normalisées.
- **Boosting, chapitres 9–10 :** XGBoost ajoute des arbres successivement pour réduire une fonction de perte. Profondeur, learning rate, sous-échantillonnage et régularisation contrôlent la complexité. C'est un autre candidat pertinent, à comparer sur le **même découpage**, sans garantie qu'il surpasse Random Forest.

Dans les notations du chapitre 12, $T=\{(x^i,y^i)\}_{i=1}^N$ est le jeu d'entraînement. Chaque arbre $\varphi^b$ apprend sur un bootstrap $T^b$. Le cours écrit l'agrégation comme un vote :

$$
\varphi_B(x)=\arg\max_y \sum_{b=1}^B I(\varphi^b(x)=y).
$$

L'implémentation scikit-learn utilisée dans ce même cours moyenne les probabilités de classe des arbres puis retient la classe la plus probable. Cela peut différer d'un vote strict des classes prédites. Ajouter des arbres stabilise l'ensemble, mais ne supprime ni le bruit des labels, ni la fuite de données, ni tout risque de surapprentissage.

### Ai-je vu mieux dans le cours ?

| Chapitres                                            | Place dans ce projet                                                                                                                                                           |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1 : PCA, clustering, densité                        | Exploration ou détection de structures ; ne garantit pas que les groupes sont des familles de ransomware. DBSCAN est aussi un concurrent dans l'article.                      |
| 2 : prétraitement de texte ; 4 : SVM multi-label    | Le CSV ne contient ni texte ni plusieurs labels simultanés par observation : ces formulations ne sont pas nécessaires ici.                                                   |
| 3 : SVM                                              | Alternative non linéaire à tester ; les échelles demandent un prétraitement et un SVM à noyau sur plusieurs millions de lignes peut être coûteux.                       |
| 5 : Naive Bayes                                      | Baseline simple. L'hypothèse d'indépendance conditionnelle et les distributions supposées des variables sont restrictives pour ces mesures du graphe.                       |
| 6–7 : processus gaussiens, optimisation bayésienne | Le cours présente surtout la régression et l'optimisation. L'optimisation bayésienne peut servir à régler les modèles, pas à démontrer qu'un classifieur est meilleur. |
| 8–12 : arbres et ensembles                          | Random Forest et XGBoost sont les deux candidats prioritaires de cette analyse supervisée. AdaBoost et un arbre seul restent des baselines possibles.                         |
| 13 : Isolation Forest, LOF, One-Class SVM            | Pertinents si la question devient « repérer un comportement inconnu ». Un comportement rare n'est cependant pas automatiquement malveillant.                                |
| 14 : LIME, SHAP                                      | Outils d'explication complémentaires ; ne remplacent pas le classifieur et ne prouvent pas une causalité.                                                                    |

**Lecture de l'article.** La section VI compare effectivement Random Forest et XGBoost (500 arbres RF et 25 itérations XGBoost dans leur protocole). Le tableau V rapporte, par exemple pour Cerber, une précision de 0,033 et un rappel de 0,181 pour XGBoost. Le tableau VII rapporte l'échec des deux méthodes pour une expérience de **nouvelle famille**. Il serait donc incorrect d'affirmer à l'avance que notre problème est « résolu ». La pertinence du modèle et son efficacité mesurée sont deux choses différentes. Mapper/TDA est central dans l'article, mais ne figure pas comme méthode étudiée dans nos chapitres 1–14 ; ses résultats ne sont pas directement comparables à notre découpage.
