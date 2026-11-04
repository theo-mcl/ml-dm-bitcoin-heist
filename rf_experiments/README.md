# Expériences Random Forest

Les parties 6 et 7 de `notebook.ipynb` produisent ces résultats. Les calculs utilisent
101 arbres, le critère d'entropie et `n_jobs=2`. Les modèles sont entraînés
successivement et les scores sont calculés par lots de 50 000 observations.

Les tableaux `features.csv`, `tuning.csv` et `stability.csv` décrivent respectivement
l'ajout des ratios, les configurations testées et les trois répétitions par adresse.
`thresholds.csv` présente les seuils de la référence sur validation.
`confirmation_validation.csv` et `exploratory_test.csv` comparent les deux
configurations entraînées sur le même fit complet. Les effectifs désignent des
observations quotidiennes d'adresses, et non des adresses nécessairement distinctes.

`manifest.json` enregistre la configuration et les seuils retenus, les versions,
les graines et les empreintes des données et des partitions. Chaque fichier JSON
portant une clé d'expérience donne également ses paramètres, variables, effectifs,
métriques et durée d'apprentissage. Les durées originales sont conservées quand
un résultat enregistré est réutilisé.

Les fichiers `.npz` contiennent les scores et le `.joblib` du candidat confirmé
contient sa forêt. Ces fichiers volumineux sont ignorés par Git. Le notebook
recalcule un essai si son cache manque ou si les données, les valeurs des variables
construites, les paramètres, la version de scikit-learn ou les partitions changent.
Les données sources ne sont pas modifiées.

Le test de référence avait déjà été examiné avant cette recherche : les résultats
finaux restent exploratoires. Les trois répétitions évaluent une sensibilité aux
séparations d'adresses ; aucune évaluation sur une période future n'est réalisée.
