emps

# BitcoinHeist — Résumé explicatif de l’article

**Article :** *BitcoinHeist: Topological Data Analysis for Ransomware Detection on the Bitcoin Blockchain*.

**Auteurs :** Cuneyt Gurcan Akcora, Yitao Li, Yulia R. Gel et Murat Kantarcioglu.

# Intro

Les auteurs expliquent pourquoi Bitcoin facilite les paiements demandés par les ransomwares : les paiements peuvent se faire à distance, sans intermédiaire central, et sans révéler directement l’identité du destinataire.

Depuis **CryptoLocker en 2013** ces demandes de paiement se sont beaucoup développées.

**Bitcoin est pseudonyme, mais pas intraçable.** Les transactions sont publiques ; ce qui n’est pas directement indiqué, c’est l’identité réelle des personnes derrière les adresses. On peut donc analyser les mouvements de fonds, même si les techniques de dissimulation compliquent leur interprétation.

Le but de l’article est d’identifier les **adresses Bitcoin utilisées pour recevoir, stocker et transférer des bitcoins liés à des rançons**. Les auteurs présentent leur travail comme une première utilisation de techniques avancées d’analyse de données pour cette tâche.

Leur contribution principale : construire des caractéristiques à partir du graphe Bitcoin et utiliser la **Topological Data Analysis, ou TDA**, pour retrouver des ressemblances entre comportements.

2 objectifs :

- Détecter de nouvelles adresses appartenant à une famille de ransomware déjà connue.
- Détecter des adresses liées à une famille qui n’avait pas encore été observée.

**Les faux positifs restent nombreux**.

# Related work

**Taint analysis :** suivre les fonds à partir de transactions ou d’adresses suspectes, pour étudier des activités comme le blanchiment (laundering) ou l’extorsion (blackmailing). L’idée est de regarder où vont les fonds et quelles autres adresses leur sont liées.

Des études cherchent aussi à associer les adresses à des utilisateurs. C’est difficile : les adresses ne donnent pas directement une identité et les utilisateurs peuvent employer des techniques de mélange, ou *mixing*, pour brouiller les flux.

D’autres travaux détectent les ransomwares en analysant leur code ou leur comportement sur les machines. Ils ne répondent pas à la même question que cet article, qui analyse les **paiements sur la blockchain**.

Enfin, les études Montreal, Princeton et Padua ont étudié les rançons en cryptomonnaies et fourni des adresses associées à des ransomwares. Elles servent ici de sources d’étiquettes.

Les approches antérieures décrites utilisent des heuristiques : des règles supposées raisonnables sur les transactions. Les auteurs cherchent à aller au-delà avec des caractéristiques comportementales et des modèles.

# Background

## Ransomware et Tor

Un ransomware est un logiciel malveillant qui bloque l’accès à des ressources, souvent en chiffrant des fichiers, puis demande une rançon. Il peut arriver par une pièce jointe, un site compromis ou une autre voie d’infection. Après le chiffrement, les attaquants demandent généralement un paiement et promettent un outil ou une clé de déchiffrement.

Tor est un réseau utilisé pour masquer certains éléments de la communication, notamment pour contacter des infrastructures des attaquants. Tor et Bitcoin jouent donc des rôles différents : communication d’un côté, paiement de l’autre.

## Bitcoin Graph

Une transaction peut avoir plusieurs entrées et plusieurs sorties. Elle rassemble des fonds disponibles en entrée et les redistribue vers des sorties.

Deux représentations classiques :

- **Transaction graph :** les nœuds sont des transactions ; on les relie quand une transaction dépense une sortie d’une transaction précédente. Les adresses ne sont pas représentées comme nœuds.
- **Address graph :** les nœuds sont des adresses. Mais on perd la transaction qui les relie. Relier toutes les adresses d’entrée à toutes celles de sortie peut créer beaucoup de connexions artificielles.

Ces représentations ne sont pas inutiles, mais chacune perd une partie de l’information. Les auteurs choisissent donc un **graphe hétérogène avec deux types de nœuds : adresses et transactions**.

Leur notation :

- $G=(V,E,B)$ : le graphe.
- $V$ : ensemble des nœuds.
- $E$ : ensemble des arêtes orientées.
- $B=\{\mathrm{Address},\mathrm{Transaction}\}$ : types de nœuds.
- $\Gamma_a^i$ : voisins entrants d’une adresse, ici les transactions qui lui versent des fonds. Prédecesseur, (in-neighbors)
- $\Gamma_a^o$ : voisins sortants, ici les transactions auxquelles elle fournit des fonds. Succésseur, (out-neighbors)

Une arête relie une adresse et une transaction.

# Methodology

1. Quelles caractéristiques du réseau Bitcoin permettent de détecter des comportements associés aux ransomwares ?
2. Une famille donnée garde-t-elle le même comportement dans le temps ?
3. À quel point différentes familles ont-elles des comportements similaires ?
4. Peut-on détecter des paiements non signalés aux autorités ou aux sociétés d’analyse de blockchain ?
5. À partir des familles déjà connues, peut-on repérer l’apparition d’une nouvelle famille ?

On distinguera donc **retrouver de nouvelles adresses d’une famille connue** et **repérer une famille encore inconnue**. Une adresse Bitcoin publique n’est pas une transaction « cachée » : elle peut surtout être inconnue comme adresse de ransomware.

## Notations

| Notation                                                                                                                                                     | Signification                                                                |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| $a_u$                                                                                                                                                      | Une adresse Bitcoin.                                                         |
| $\mathbf{x}_u$                                                                                                                                             | Son vecteur de features                                                      |
| $y_u$                                                                                                                                                      | Son label, par exemple`white`                                              |
| $t_u$                                                                                                                                                      | Date de première apparition de l’adresse sur la blockchain.                |
| $a_u^t$                                                                                                                                                    | Adresse au temps t                                                           |
| $f_1,\ldots,f_n$                                                                                                                                          | Familles connues jusqu'au temps t                                            |
| $f_0$                                                                                                                                                      | Adresses non connues comme appartenant à ces familles, supposées`white`. |
| $X_t$             | Ensemble des vecteurs de caractéristiques disponibles jusqu’à t ; l’article les dispose en colonnes d’une matrice$D\times l$. |                                                                              |
| $Y_t$                                                                                                                                                      | Étiquettes correspondantes.                                                 |

`white` n’est pas une preuve d’innocence, juste l'adresse n'est pas encore connue comme Ransomware.

Une adresse peut apparaître plusieurs jours et avoir des caractéristiques différentes à chaque apparition. Il faut distinguer **adresse unique** et **observation d’une adresse dans une fenêtre temporelle**.

Les auteurs construisent des graphes sur des fenêtres de 24 heures, avec UTC−6 comme référence.

Cela permet d’étudier les déplacements de fonds à l’intérieur d’une journée. Bitcoin vise en moyenne un bloc toutes les dix minutes, soit environ 144 blocs par jour.

Des mouvements rapides peuvent être intéressants à examiner, mais ne prouvent pas un blanchiment. Les horaires peuvent aussi apporter des indices sur les habitudes d’activité, sans permettre de localiser avec certitude un utilisateur.

## Starter transactions

Une **starter transaction** est une transaction qui ne reçoit pas de fonds provenant d’une transaction antérieure **dans la fenêtre étudiée**. Ses entrées viennent d’avant cette fenêtre.

## Les six features

### Income

Montant total reçu par l’adresse $u$ sur la fenêtre. Cela décrit les entrées de fonds, **pas son solde**, ni son bénéfice, ni le montant qui reste après ses dépenses.

### Neighbors

Nombre de transactions qui ont l’adresse $u$ parmi leurs sorties, donc qui la paient sur la fenêtre.

### Weight

Les auteurs partent d’un poids de 1 pour chaque starter transaction et suivent sa propagation vers les adresses suivantes. Les contributions qui atteignent une même adresse s’additionnent. Une starter transaction avec deux sorties transmet un poids de 0,5 à chacune, indépendamment des montants affichés. Il faut donc comprendre cette mesure comme un **poids structurel de propagation**, pas comme le nombre de bitcoins reçus. Elle aide à quantifier les comportements de regroupement, ou *merge*.

Un poids peut dépasser 1 quand plusieurs contributions convergent. Ce n’est pas une probabilité.

### Length

Nombre de transactions non-starter sur la plus longue chaîne allant d’une starter transaction à l’adresse $u$. Une chaîne est un chemin orienté sans cycle. `length = 0` signifie que l’adresse est directement une sortie d’une starter transaction. Permet de quantifier les étapes de circulation, notamment les tours de mélange, ou *mixing rounds,* pour cacher l'origine du coin.

### Count

Nombre de **starter transactions distinctes** qui peuvent atteindre l’adresse $u$ par une chaîne. Décrit combien de points de départ convergent vers cette adresse.

### Loop

Nombre de starter transactions qui peuvent atteindre $u$ par **plus d’un chemin orienté**. L’idée : des fonds ou contributions partent d’une même origine, se séparent, puis rejoignent une même adresse.

*Attention pour une reproduction : le texte du toy example contient notamment une coquille sur `count`. Il parle de trois starters alors qu’il en cite deux, puis donne correctement `count = 2`. Il ne faut pas confondre ses trois chemins avec ses deux transactions de départ. Le code d’extraction reste à vérifier avant de reproduire exactement les valeurs du dataset.*

## Standardisation

Les auteurs indiquent qu’ils standardisent les caractéristiques : moyenne nulle et variance unitaire.

$$
z=\frac{x-\mu}{\sigma}
$$

## Modèles de comparaison

### Similarity search

Comparer les caractéristiques des adresses du jour à celles d’adresses de ransomware connues sur les jours précédents.

### Heuristiques

- **Co-spending :** supposer que deux adresses utilisées en entrée d’une même transaction sont contrôlées par le même utilisateur.
- **Transition :** propager cette supposition ; si A et B sont associés, puis B et C, regrouper A, B et C.

### Approches non supervisées

**DBSCAN :** former des groupes dans les zones denses et laisser des outliers comme bruit. Un point atypique n’est pas automatiquement un ransomware.

**Clustering :** k-means par exemple

### Tree-based algorithms

- **Random Forest :** plusieurs arbres construits avec de l’aléa, dont les décisions sont combinées.
- **XGBoost :** arbres ajoutés progressivement pour améliorer les prédictions de l’ensemble.

# Topological Data Analysis — TDA

## L’idée

Une adresse devient un point décrit par six coordonnées : ses six features. Toutes les adresses forment donc un **nuage de points en six dimensions**. Un clustering classique cherche surtout à découper ce nuage en groupes. La TDA cherche aussi à comprendre **comment les groupes s’organisent et se raccordent** : zones denses, branches, connexions, éventuellement cycles.

**Analogie explicative :** on observe un paysage. On peut identifier des villages séparément, mais aussi regarder les routes et les passages qui les relient. Mapper cherche à fournir cette deuxième vue pour le nuage de données.

L’article emploie **Mapper**, une méthode de TDA. Il ne faut pas assimiler toute la TDA à Mapper, ni croire que le modèle repère uniquement des cycles.

## Deux graphes à bien distinguer

| Graphe Bitcoin                              | Graphe Mapper                                                       |
| ------------------------------------------- | ------------------------------------------------------------------- |
| Nœuds : adresses et transactions.          | Nœuds : groupes d’observations ayant des profils similaires.      |
| Arêtes : entrées et sorties de fonds.     | Arêtes : groupes qui partagent au moins une observation.           |
| Sert à calculer les six caractéristiques. | Sert à représenter l’organisation du nuage de caractéristiques. |

**Une arête de Mapper ne signifie donc pas qu’il y a eu un paiement entre deux adresses.** Elle exprime un recouvrement entre groupes.

## Construction de Mapper

### 1. Choix d'un filtre

Un filtre, ou *lens*, associe à chaque point une valeur numérique :

$$
\xi:\mathbb{R}^{6}\rightarrow\mathbb{R}
$$

Par exemple, choisir `length`. On utilise cette valeur pour organiser les points le long d’un axe.

### 2. Découpage des valeurs du filtre en intervalles qui se recouvrent

**Exemple inventé par chatGPT :** intervalles [0, 4], [3, 7] et [6, 10]. Une observation avec `length = 3,5` appartient aux deux premiers intervalles.

### 3. Clustering dans chaque intervalle

Les auteurs utilisent le **single linkage**. C’est un clustering hiérarchique où la distance entre deux groupes est déterminée par leurs points les plus proches. Un même intervalle peut contenir plusieurs groupes séparés. Les auteurs choisissent leur nombre en examinant les distances auxquelles ils fusionnent : une fusion nécessitant une distance nettement plus grande peut indiquer deux groupes distincts.

### 4. Transformation des groupes en nœuds et les reliage

Chaque groupe devient un nœud. Deux nœuds sont reliés s’ils partagent au moins une observation, ce qui peut arriver grâce au recouvrement des intervalles. 

### 5. Utilisation des étiquettes connues pour interpréter les groupes

Un groupe peut contenir :

- Des observations passées d’adresses de ransomware.
- Des observations passées d’adresses `white`.
- Des observations actuelles dont l’étiquette n’est pas utilisée pour la prédiction.

Si une adresse actuelle partage des groupes avec suffisamment d’exemples malveillants connus, elle peut recevoir un score de suspicion. **Mapper seul n’est donc pas un classifieur supervisé.** La construction des groupes repose sur les caractéristiques ; la règle de suspicion utilise ensuite les étiquettes passées.

## Pourquoi construire six graphes Mapper ?

Les auteurs choisissent successivement chacune des six features comme filtre. Ils obtiennent six graphes pour une fenêtre donnée. Chaque filtre organise le nuage sous un angle différent. Une adresse peut apparaître suspecte dans plusieurs de ces vues, ce qui augmente son score. La méthode ne résume donc pas la décision à « grand income = ransomware » : elle regarde les groupes et leur composition sous plusieurs découpages.

## Score de suspicion et seuils

Chaque adresse actuelle commence avec un score de 0. Pour chaque graphe, puis chaque groupe, les auteurs vérifient deux conditions.

**Seuil d’inclusion $\varepsilon_1$ :** le groupe doit contenir suffisamment d’adresses de ransomware connues. Dans l’algorithme imprimé :

$$
|A_c\cap RS|\geq\varepsilon_1|RS|
$$

où $A_c$ est l’ensemble des adresses du groupe et $RS$ l’ensemble des adresses de ransomware connues utilisé.

**Seuil de taille $\varepsilon_2$ :** éviter de signaler un groupe trop grand, donc peu sélectif. L’algorithme imprime :

$$
|A_c|\leq\varepsilon_2|CT.V|
$$



Lorsque les deux conditions sont satisfaites, le score des adresses actuelles du groupe augmente de 1. Une adresse peut gagner plusieurs points, y compris à cause du recouvrement des groupes.

**Seuil quantile $q$ :** conserver les adresses dont le score est au moins égal au quantile choisi. Avec $q=0,9$, on vise les scores les plus élevés, approximativement le décile supérieur.

Les auteurs peuvent rendre le système plus restrictif avec un $q$ plus élevé, un $\varepsilon_1$ plus élevé et un $\varepsilon_2$ plus faible.

**Le score de suspicion n’est pas une probabilité calibrée.** Un score élevé signifie que l’adresse a rencontré davantage de groupes jugés informatifs ; il ne donne pas directement un pourcentage de risque.

## Ce que la TDA apporte ici

Mapper peut conserver des raccordements entre groupes que l’on perdrait avec un simple partitionnement. Les auteurs présentent aussi la TDA comme une façon d’étudier des formes à plusieurs résolutions et de résister à certaines perturbations des données.

Il faut néanmoins vérifier la stabilité : le résultat dépend du filtre, de la mise à l’échelle, des intervalles, de leur recouvrement, du clustering et des seuils. 

# Ransomware behavior — Analyse des comportements

## Données utilisées

Les auteurs analysent le graphe Bitcoin de janvier 2009 à décembre 2018, découpé en journées.

Ils filtrent les arêtes transférant moins de **0,3 BTC**, en supposant que les rançons sont rarement inférieures. Ils réutilisent ensuite le graphe complet pour certaines vérifications, car se sont rendus comtpe qu'ils en avaient oublié.

Des adresses réapparaissent plusieurs jours : une adresse CryptoLocker apparaît dans 420 fenêtres. Les auteurs signalent aussi quatre adresses dont les étiquettes de famille se contredisent entre les sources Padua et Montreal.

## Patterns fréquents

Les auteurs appellent **pattern** une combinaison des six valeurs de features. Ils calculent environ 48 000 observations d’adresses de ransomware et trouvent environ 30 000 combinaisons distinctes. Certaines combinaisons reviennent fréquemment.

Des patterns comportent `length = 0`, `weight = 0,5` ou `weight = 1`. Ils sont compatibles avec des paiements directs depuis une starter transaction, éventuellement avec une deuxième sortie de monnaie rendue.

Le tableau I compare aussi les rangs de fréquence des patterns entre populations. Cela soutient une différence statistique entre les rangs examinés, sans garantir une séparation prédictive ni une différence importante pour chaque variable.

Les distributions de `count` et `loop` sont particulièrement asymétriques à droite pour les ransomwares : beaucoup de petites valeurs, quelques grandes valeurs. **C’est une justification pour examiner des graphiques logarithmiques, sans supprimer automatiquement les extrêmes.** L'asymétrie existe aussi pour la `length`et `weight`.

## Visualisation avec t-SNE

t-SNE (t-stochastic neighbors) représente les six dimensions dans un graphique en deux dimensions, en essayant de préserver des voisinages locaux. Les auteurs font varier la **perplexité**, qui règle en partie l’échelle du voisinage considéré. Ils voient plusieurs petits groupes au sein d’une même famille et des regroupements entre familles. Une famille ne possède donc pas un profil unique. On observe qu'en augmentant la perplexité, des adresses tendent à se regrouper.

Cette visualisation aide à explorer, pas à prouver qu’un classifieur fonctionnera.

## Similarité entre familles

Les auteurs regroupent les observations et regardent les familles présentes dans les clusters. Ils définissent la **pureté d’une famille** comme la proportion de ses observations situées dans des clusters ne contenant que cette famille, en excluant les clusters à un seul point. CryptoLocker et CryptoWall se retrouvent souvent ensemble. Cela laisse à suggérer que ces ressemblances pourraient refléter des comportements partagés par les opérateurs.

## Évolution dans le temps

Les auteurs trouvent des patterns répétés dans certaines familles, mais pas un comportement global uniforme et permanent. Certains sous-groupes semblent suffisamment stables pour aider à détecter de nouvelles adresses. D’autres évoluent.

**Important** : Pour notre travail, il conviendra de prendre en compte que les comportement ont changé au cours du temps. 

# Ransomware detection and prediction — Expériences

## Déséquilibre et fenêtres glissantes

Les adresses de ransomware sont rares par rapport aux autres adresses. Les auteurs utilisent de petits échantillons pour l’apprentissage, avec $N\in\{300,600,1000\}$ observations/adresses par classe selon le protocole et les données disponibles. Pour limiter l’effet des comportements anciens, ils apprennent sur les dernières fenêtres journalières.

Les modèles principaux utilisent notamment Random Forest avec 500 arbres, XGBoost avec 25 itérations et Mapper avec 80 intervalles et un recouvrement paramétré à 40 dans le package utilisé .

## Métriques

| Terme | Signification                                                  |
| ----- | -------------------------------------------------------------- |
| TP    | Adresse de ransomware correctement signalée.                  |
| FP    | Adresse étiquetée`white`, mais signalée comme ransomware. |
| FN    | Adresse de ransomware manquée.                                |
| TN    | Adresse étiquetée`white`, correctement non signalée.      |

$$
\mathrm{Précision}=\frac{TP}{TP+FP}
\qquad
\mathrm{Rappel}=\frac{TP}{TP+FN}
$$

La précision répond à « parmi les alertes, combien sont confirmées par les étiquettes ? ». Le rappel répond à « parmi les cas connus, combien retrouve-t-on ? ».

$$
F_1=2\frac{\mathrm{Précision}\times\mathrm{Rappel}}{\mathrm{Précision}+\mathrm{Rappel}}
$$

Les auteurs rapportent aussi un indicateur nommé **PLR (Positive Likelihood Ratio)**, défini dans leur article par :

$$
PLR_{\mathrm{article}}=\frac{TP}{FP}
$$

Plus il est grand, moins il y a de fausses alertes par vraie détection. Son inverse $FP/TP$ exprime directement la charge de vérification inutile. Les résultats dépendent aussi de la fiabilité des étiquettes : un FP est ici un désaccord avec `white`, pas la preuve définitive d’une adresse innocente.

## Expérience 1 — Nouvelles adresses d’une famille connue

Pour une famille donnée :

1. Prendre un historique antérieur à la journée à prédire.
2. Prélever des exemples de cette famille et des exemples `white`.
3. Dans la journée future, prendre les adresses de cette famille et un échantillon de 1 000 `white`.
4. Retirer les adresses de ransomware déjà vues dans l’historique.
5. Évaluer la détection des nouvelles adresses.

Ils apprennent un modèle par famille. Ils soulignent que les réglages utiles diffèrent selon les familles.

### Résultats principaux

| Famille      | Méthode TDA retenue | Précision | Rappel | Fenêtres avec au moins une prédiction |
| ------------ | -------------------- | ---------: | -----: | --------------------------------------: |
| Locky        | TDA                  |     16,1 % | 90,0 % |                                      11 |
| CryptoWall   | TDA                  |      6,6 % | 58,3 % |                                      15 |
| CryptoLocker | TDA                  |      4,3 % | 67,4 % |                                      34 |
| Cerber       | TDA                  |      3,5 % | 28,9 % |                                      29 |
| CryptXXX     | TDA                  |      3,0 % | 22,1 % |                                      14 |

**Lecture de Locky :** le modèle retrouve beaucoup des cas évalués, mais environ 84 % de ses alertes ne sont pas confirmées par les étiquettes. Un rappel élevé peut donc coexister avec une faible précision.

Les auteurs rapportent en moyenne **16,59 faux positifs par vrai positif** pour les meilleurs modèles TDA, contre **27,44** pour les meilleurs modèles non-TDA de leur comparaison.

La recherche par correspondances exactes retrouve aussi des cas, mais génère au total plus de 21 000 faux positifs dans l’expérience décrite.

### Attention aux fenêtres évaluées

TDA et DBSCAN peuvent ne produire des prédictions que dans certaines fenêtres. Le nombre de fenêtres diffère parfois beaucoup entre les méthodes du tableau. **Une bonne précision sur les journées où l’on décide de prédire n’implique pas une bonne couverture de toutes les journées.** Pour comparer les méthodes, il faut aussi compter les cas manqués pendant les abstentions.

### Effet des seuils

Rendre les paramètres plus restrictifs réduit généralement le nombre de signalements. Cela peut améliorer la précision, au prix du rappel et de la couverture temporelle. 

Dans leur expérience sur les familles connues, augmenter $q$ fait notamment diminuer le rappel moyen ; le gain de précision n’est pas systématique.

## Expérience 2 — Nouvelle famille

Les auteurs regroupent les familles passées dans une classe unique « ransomware », puis essaient de détecter des adresses d’une famille absente de l’apprentissage. **Il ne s’agit pas de deviner le nom de la nouvelle famille.** Le modèle signale une adresse comme potentiellement liée à un ransomware. Une investigation supplémentaire est nécessaire pour établir qu’il s’agit d’une nouvelle famille plutôt que d’une famille connue.

### Au tout début de l’apparition

Ils étudient l’émergence de 25 familles. CryptoLocker, première famille de leur chronologie, ne peut pas être traitée de cette manière puisqu’il n’existe pas encore d’exemples antérieurs de ransomware pour apprendre. Le modèle retenu dans cette expérience obtient 26 TP pour 21 075 FP, soit environ **810,57 faux positifs par vrai positif**. **C’est un résultat très limité pour un usage opérationnel.** Les auteurs l’expliquent notamment par la rareté des données au premier jour d’apparition : la plupart des familles ont très peu d’adresses à ce moment-là. 

### Quand davantage d’adresses deviennent disponibles

Ils refont l’expérience à partir de la première fenêtre où une famille possède au moins dix adresses. Cinq familles restent dans cette comparaison. Les éventuelles adresses déjà observées de la famille cible sont exclues de l’apprentissage.

Ce protocole est moins proche d’une détection dès le tout premier signal, mais fournit davantage de cas à évaluer.

Dans les tableaux VII et VIII :

- TDA fournit les meilleurs résultats sur plusieurs familles, mais pas toutes.
- DBSCAN est le meilleur pour DMALocker selon certains critères.
- Random Forest et XGBoost échouent dans la configuration de nouvelle famille présentée au tableau VII. Cela ne prouve pas qu’ils échouent pour toute classification de ransomware.
- Pour CryptXXX, un réglage TDA signale seulement deux adresses : une vraie et une fausse. La précision vaut 50 %, mais le rappel seulement 2,6 %.
- Les auteurs rapportent environ 27,53 faux positifs par vrai positif en moyenne pour les meilleurs modèles du tableau VIII.

**L’exemple CryptXXX montre pourquoi il faut toujours lire précision, rappel et effectifs ensemble.** Une bonne précision peut correspondre à une seule vraie détection.

### Paramètres et historique

Augmenter $q$ améliore légèrement la précision moyenne dans cette expérience, mais diminue le rappel. Des historiques plus courts donnent parfois de meilleurs résultats, et davantage d’exemples d’apprentissage peuvent aider.

Cela rejoint l’analyse des comportements : les features évoluent dans le temps, donc un historique trop ancien peut devenir peu pertinent.

# Address elimination — Réduire les signalements

Après TDA, les auteurs ajoutent des heuristiques pour limiter le nombre d’adresses à examiner.

Dans l’expérience de départ de cette section, ils obtiennent 3 211 signalements, dont 92 associés à des adresses connues comme ransomware.

## 1. Shape elimination

Ils distinguent deux activités :

- **Front payments :** paiements initiaux des victimes.
- **Mixing transactions :** mouvements ultérieurs pour regrouper, déplacer ou vendre les fonds.

Pour se concentrer sur les paiements initiaux, ils privilégient certaines formes : transactions avec N adresses d’entrée et une ou deux sorties, notées N-to-1 ou N-to-2.

Cela réduit les signalements de 3 211 à 2 350, mais retire aussi 16 des 92 cas connus : il en reste 76.

**Réduire les faux positifs peut aussi éliminer de vrais cas.** Cette hypothèse structurelle n’est pas une règle universelle sur les paiements de rançon.

## 2. Graph elimination

Ils calculent la distance aux adresses de ransomware connues, avec une recherche en largeur, ou **BFS**. La distance est le nombre d’arêtes du plus court chemin dans le graphe utilisé.

Les adresses signalées qui sont accessibles depuis les adresses connues tendent à être plus proches que les autres adresses accessibles. Les auteurs rapportent un test de Kolmogorov-Smirnov significatif entre les distributions examinées.

Ils conservent les adresses à une distance d’au plus quatre arêtes. Cela laisse 617 signalements, dont huit cas connus.

**Cette proximité est un indice, pas une preuve de malveillance.** Et le filtre perd beaucoup de cas : huit des 92 cas connus du départ subsistent à ce stade.

## 3. Multisig elimination

Les auteurs éliminent ensuite certaines adresses selon leur type, en s’appuyant sur la rareté des adresses qu’ils appellent multisig dans leurs exemples connus.

Dans le comptage final d’adresses uniques, ils conservent huit adresses connues comme ransomware et 331 autres adresses suspectes.

**Précaution technique :** l’article assimile les adresses commençant par `3` aux adresses multisig. C’est une simplification : ces adresses sont de type P2SH, qui peut porter différents scripts, dont du multisig. Le préfixe seul ne suffit pas à démontrer la condition de dépense. [Documentation Bitcoin sur P2SH](https://developer.bitcoin.org/devguide/transactions.html#p2sh-scripts).

Les auteurs reconnaissent eux-mêmes que cette heuristique peut perdre son intérêt si les opérateurs changent leurs pratiques.

## Ce que ces filtres démontrent

Ils réduisent la liste à vérifier, mais ne valident pas les 331 adresses restantes. Être signalée plusieurs jours et survivre aux filtres constitue un faisceau d’indices, pas une confirmation indépendante.

Il faut aussi distinguer les **signalements sur plusieurs fenêtres** et les **adresses uniques**. Les nombres de la section ne doivent pas tous être interprétés comme s’ils avaient exactement le même dénominateur.

# Conclusion de l’article

Les auteurs proposent un cadre fondé sur des caractéristiques du graphe et TDA Mapper pour détecter des adresses Bitcoin associées à des ransomwares.

Les résultats soutiennent l’utilité de certains patterns et montrent des gains par rapport à plusieurs méthodes de comparaison, avec de fortes différences entre familles.

La détection de nouvelles familles reste particulièrement difficile. La méthode produit encore beaucoup de fausses alertes et dépend de la quantité d’exemples disponibles, des réglages et de la période étudiée.

Les auteurs proposent ensuite de combiner cette approche avec d’autres sources : nouvelles adresses obtenues en analysant les ransomwares et renseignements sur les menaces, ou *threat intelligence*.

# Ce que je retiens pour notre étude

- Une ligne correspond à une activité d’adresse dans une fenêtre, pas nécessairement à une adresse unique ni à une transaction unique.
- `white` signifie non identifié comme ransomware ; les labels peuvent être incomplets ou contradictoires.
- Les six features décrivent des montants, des chemins et des regroupements. Leurs noms ne suffisent pas à comprendre leurs contraintes.
- `weight` peut dépasser 1 ; `looped` peut dépasser 1 ; des valeurs extrêmes plausibles ne doivent pas être supprimées automatiquement.
- Les distributions peuvent être très asymétriques. Comparer des graphiques bruts et `log1p` est utile, tout en conservant les statistiques brutes pour l’audit.
- Une ressemblance de comportement ne prouve ni une identité commune ni une activité malveillante.
- L’évaluation doit respecter le temps et contrôler les adresses déjà vues. Un découpage aléatoire par lignes peut rendre le problème artificiellement facile.
- Les caractéristiques de toute une journée ne sont disponibles qu’après cette journée. Une détection fondée sur elles ne prouve pas une capacité d’anticipation avant le paiement.
- Les effectifs, le rappel, la précision, les fausses alertes et la couverture des périodes doivent être présentés ensemble.
- Les meilleures configurations rapportées ne garantissent pas une performance future ; une validation de sélection et un test final séparé sont nécessaires pour notre comparaison.
- Les filtres sur les montants et l’échantillonnage des `white` modifient la population évaluée. La précision du dataset ne se transpose pas directement à toute la blockchain.
- Le CSV de features suffit à tester des modèles tabulaires et éventuellement Mapper. Les filtres BFS, N-to-1/N-to-2 et les heuristiques de co-spending demandent le graphe ou les transactions brutes supplémentaires.
- Random Forest et XGBoost restent des modèles à comparer dans notre étude. Leur échec dans un protocole particulier de nouvelle famille ne décide pas de leur performance sur notre question.
- Le papier fourni date de 2019 : il constitue une base méthodologique, pas un état de l’art actuel.

# Repères de lecture

| Partie de l’article                          | Ce qu’elle apporte                                         |
| --------------------------------------------- | ----------------------------------------------------------- |
| Sections I–III                               | Objectif, travaux antérieurs, contexte et graphe Bitcoin.  |
| Section IV-A, figure 1                        | Six features et exemple de calcul.                          |
| Section IV-B                                  | Méthodes de comparaison.                                   |
| Section IV-C, figure 2, algorithme 1          | Mapper et règles de suspicion.                             |
| Section V, figures 3–6, tableaux I–IV et XI | Distributions, patterns, familles et évolution temporelle. |
| Section VI-A, tableau V                       | Détection de nouvelles adresses d’une famille connue.     |
| Section VI-B, tableaux VI–IX                 | Expériences sur de nouvelles familles.                     |
| Section VII, figure 12                        | Filtres pour réduire les signalements.                     |
| Section VIII                                  | Conclusions et pistes futures.                              |

Les deux références techniques complémentaires sur le PLR standard et P2SH servent uniquement à expliciter des points de vocabulaire ; elles ne changent pas les résultats rapportés dans l’article.
