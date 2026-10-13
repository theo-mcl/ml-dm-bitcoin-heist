from html import escape

import numpy as np
import pandas as pd



def pair_plot(data, n_points=2000, plot_type="seaborn", *, features=None,
              use_log=True, class_mode="binary", diag_kind="hist",
              random_seed=42, height=2.4, save_path=None, show=True):
    """Crée un pair-plot statique ou interactif sans modifier data.

    n_points : maximum de points PAR CLASSE (2000 par défaut).
    plot_type : 'seaborn' pour une figure statique, 'plotly' pour le zoom/survol.
    features : variables à comparer, par défaut les six mesures du graphe.
    use_log : log1p par défaut ; False conserve les unités brutes.
    class_mode : 'binary' (white/autres labels), 'label' (familles originales)
        ou 'none' (sans classes, n_points maximum sur toute la figure).
    diag_kind : 'hist' ou 'kde' pour Seaborn. Diagonale masquée dans Plotly.
    random_seed : graine pour comparer les mêmes points entre les rendus.
    height : taille d'une case en pouces, adaptée en pixels pour Plotly.
    save_path : PNG/PDF/SVG pour Seaborn, HTML autonome pour Plotly.
    show : False crée/exporte la figure sans l'afficher.

    Retourne un PairGrid Seaborn ou une Figure Plotly pour personnalisation.
    Affecter le retour : grid = pair_plot(data), fig = pair_plot(data,
    plot_type='plotly'). La distribution des classes de cet échantillon
    équilibré ne représente pas les proportions du dataset.
    """
    from numbers import Integral
    from pathlib import Path

    # Valider les options avant les calculs pour donner des erreurs explicites.
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data doit être un DataFrame pandas.")
    if plot_type not in {"seaborn", "plotly"}:
        raise ValueError("plot_type doit être seaborn ou plotly.")
    if random_seed is not None and (not isinstance(random_seed, Integral) or random_seed < 0):
        raise ValueError("random_seed doit être un entier non négatif.")
    if class_mode not in {"binary", "label", "none"}:
        raise ValueError("class_mode doit être binary, label ou none.")
    if diag_kind not in {"hist", "kde"}:
        raise ValueError("diag_kind doit être hist ou kde.")
    if not np.isfinite(height) or height <= 0:
        raise ValueError("height doit être positif et fini.")
    if features is None:
        features = ["length", "weight", "count", "looped", "neighbors", "income"]
    elif isinstance(features, str):
        raise ValueError("features doit être une liste de noms.")
    else:
        features = list(features)
    if len(features) < 2 or len(set(features)) != len(features):
        raise ValueError("Choisir au moins deux variables distinctes.")
    if any(col in {"address", "label", "classe"} for col in features):
        raise ValueError("features doit contenir uniquement des mesures numériques.")
    required = features + (["label"] if class_mode != "none" else [])
    absent = [col for col in required if col not in data.columns]
    if absent:
        raise ValueError(f"Colonnes absentes : {absent}")
    path = Path(save_path) if save_path is not None else None
    if path is not None:
        extensions = {".html"} if plot_type == "plotly" else {".png", ".pdf", ".svg"}
        if path.suffix.lower() not in extensions:
            raise ValueError(f"Extensions acceptées : {sorted(extensions)}")

    # Coordonnées temporaires : aucune conversion ne touche au dataset reçu.
    viz = data[features].apply(pd.to_numeric, errors="coerce")
    eligible = viz.notna().all(axis=1) & ~viz.isin([np.inf, -np.inf]).any(axis=1)
    if use_log:
        eligible &= viz.ge(0).all(axis=1)
    if class_mode != "none":
        labels = data["label"]
        missing = labels.isna() | labels.map(
            lambda value: isinstance(value, str) and not value.strip())
        eligible &= ~missing
        viz["classe"] = (
            np.where(labels.eq("white").fillna(False),
                     "White — non identifié", "Ransomware identifié")
            if class_mode == "binary" else labels.astype("string"))

    # Plotly conserve les unités originales au survol, même sur les axes log.
    if plot_type == "plotly":
        for col in ["address", "date", "label"]:
            if col in data.columns and col not in viz.columns:
                viz[col] = data[col]
        for col in features:
            viz[f"{col}_brut"] = viz[col]
    viz = viz.loc[eligible].copy()
    if viz.empty:
        raise ValueError("Aucune ligne traçable pour les variables/échelle choisies.")

    # Échantillonner AVANT log1p conserve les mêmes points entre les échelles.
    # Les classes plus petites sont gardées en entier, sans suréchantillonnage.
    if class_mode == "none":
        viz = viz.sample(n=min(n_points, len(viz)), random_state=random_seed)
    else:
        viz = pd.concat([
            group.sample(n=min(n_points, len(group)), random_state=random_seed)
            for _, group in viz.groupby("classe", observed=True, sort=True)])
    viz = viz.reset_index(drop=True)
    if use_log:
        viz[features] = np.log1p(viz[features])
    axis_labels = {col: f"log1p({col})" if use_log else col for col in features}
    palette = {"White — non identifié": "#2A6F97",
               "Ransomware identifié": "#D1495B"} if class_mode == "binary" else None
    hue = "classe" if class_mode != "none" else None
    title = "Relations entre les mesures des adresses Bitcoin"
    subtitle = "Échelle log1p" if use_log else "Unités brutes"
    subtitle += f" · {len(viz):,} points"
    if hue:
        subtitle += " · échantillon par classe, proportions non représentatives"
    print(f"Lignes exclues du graphique : {len(data) - int(eligible.sum())}")
    print(f"Points affichés : {len(viz)}")
    if hue:
        _display_report({"effectifs_affiches": viz[hue].value_counts().to_frame("nombre")},
                        "Échantillon du pair-plot")
    corner = True
    if plot_type == "seaborn":
        import matplotlib.pyplot as plt
        import seaborn as sns

        # Style local : les autres figures du notebook conservent leur thème.
        # Nuages rasterisés pour alléger PDF/SVG ; textes et axes vectoriels.
        
        with sns.axes_style("whitegrid"), sns.plotting_context("notebook", font_scale=0.9):
            grid = sns.pairplot(
                viz, vars=features, hue=hue, palette=palette, corner=corner,
                diag_kind=diag_kind, height=height,
                plot_kws={"s": 12, "alpha": 0.3, "linewidth": 0, "rasterized": True},
                diag_kws={"bins": 30, "stat": "density", "common_norm": False,
                          "element": "step", "fill": False}
                if diag_kind == "hist" else {"common_norm": False, "fill": False})
            # Changer les titres des axes, sans renommer les colonnes sources.
            for ax in grid.axes.flat:
                if ax is not None:
                    ax.set_xlabel(axis_labels.get(ax.get_xlabel(), ax.get_xlabel()))
                    ax.set_ylabel(axis_labels.get(ax.get_ylabel(), ax.get_ylabel()))
                    ax.tick_params(labelsize=9)
            grid.figure.suptitle(f"{title}\n{subtitle}", fontsize=13, y=0.99)
            grid.figure.subplots_adjust(top=0.90, bottom=0.08, wspace=0.08, hspace=0.08)
            if path is not None:
                grid.figure.savefig(path, dpi=300, bbox_inches="tight")
            if show:
                plt.show()
            else:
                # Empêcher l'affichage automatique de Matplotlib dans Jupyter.
                # L'objet retourné reste disponible pour l'export/personnalisation.
                plt.close(grid.figure)
        return grid

    import plotly.express as px

    # Matrice interactive ; pas d'histogrammes sur la diagonale Plotly.
    hover = {f"{col}_brut": ":,.3f" for col in features}
    hover.update({col: True for col in ["date", "label"] if col in viz.columns})
    fig = px.scatter_matrix(
        viz, dimensions=features, color=hue, color_discrete_map=palette,
        hover_name="address" if "address" in viz.columns else None,
        hover_data=hover, labels=axis_labels,
        title=f"{title}<br><sup>{subtitle}</sup>",
        height=max(650, int(len(features) * height * 100)),
        width=max(750, int(len(features) * height * 100)))
    fig.update_traces(diagonal_visible=False, showupperhalf=not corner,
                      marker={"size": 4, "opacity": 0.4, "line": {"width": 0}})
    fig.update_layout(template="plotly_white", dragmode="zoom", hovermode="closest",
                      font={"size": 11}, legend={"orientation": "h", "y": -0.12},
                      margin={"l": 80, "r": 40, "t": 100, "b": 120})
    config = {"scrollZoom": True, "displaylogo": False, "responsive": True,
              "toImageButtonOptions": {"format": "png", "filename": "pairplot",
                                       "width": 1800, "height": 1600, "scale": 2}}
    if path is not None:
        fig.write_html(path, include_plotlyjs=True, config=config)
    if show:
        fig.show(config=config)
    return fig


def _display_report(report, title, display_mode="auto"):
    """Affiche un rapport en HTML adapté pour Jupyter. Permet de rendre les 
    tableaux entièrement. """

    if display_mode not in {"auto", "html", "text", "none"}:
        raise ValueError("display_mode doit être auto, html, text ou none.")
    if display_mode == "none":
        return

    # IPython reste facultatif : un script Python classique fonctionne aussi.
    # Un noyau Jupyter sait afficher le HTML, contrairement à un terminal.
    use_html = display_mode == "html"
    if display_mode == "auto":
        try:
            from IPython import get_ipython
            use_html = getattr(get_ipython(), "kernel", None) is not None
        except ImportError:
            use_html = False

    # Les compteurs constituent le résumé. Les DataFrames sont les détails.
    summary = pd.DataFrame([
        {"Vérification": key, "Résultat": str(value)}
        for key, value in report.items() if not isinstance(value, pd.DataFrame)
    ])
    tables = [("Bilan", summary)] + [
        (key.replace("_", " ").capitalize(), value)
        for key, value in report.items() if isinstance(value, pd.DataFrame)
    ]
    if use_html:
        from IPython.display import HTML, display
        sections = [f"<h3>{escape(title)}</h3>"]
        for i, (name, table) in enumerate(tables):
            # Échapper les cellules évite qu'un label soit interprété comme HTML.
            # max_rows/max_cols=None garantissent un tableau sans « ... ».
            rendered = table.round(3).to_html(
                index=name != "Bilan" and "colonne" not in table.columns,
                max_rows=None, max_cols=None, escape=True, border=0,
            )
            opened = " open" if i == 0 else ""
            sections.append(
                f"<details{opened}><summary><b>{escape(name)}</b> "
                f"({len(table)} lignes)</summary>"
                '<div style="overflow:auto;max-height:420px;padding:8px;">'
                f"{rendered}</div></details>"
            )
        display(HTML("".join(sections)))
    else:
        # to_string contourne la troncature pandas ; un terminal peut toutefois
        # imposer sa propre limite de sortie, indépendante de cette fonction.
        print(title)
        for name, table in tables:
            print(f"\n{name} :")
            print(table.round(3).to_string(
                index=name != "Bilan" and "colonne" not in table.columns
            ))


def check_label_distribution(data, display_mode="auto"):
    """Affiche la distribution des labels et retourne un rapport séparé."""

    if not data.columns.is_unique:
        raise ValueError("Les noms de colonnes doivent être uniques.")
    if "label" not in data.columns:
        raise ValueError("La colonne label est absente.")
    labels = data["label"]
    # Les chaînes vides ou composées uniquement d'espaces sont aussi absentes.
    missing = labels.isna() | labels.map(
        lambda value: isinstance(value, str) and not value.strip()
    )
    counts = labels.loc[~missing].value_counts()
    distribution = pd.DataFrame({
        "nombre": counts,
        "pourcentage": counts / len(data) * 100 if len(data) else counts * 0,
    })
    report = {
        "Nombre de lignes": len(data),
        "Nombre de labels manquants": int(missing.sum()),
        "Nombre de lignes avec le label white": int(counts.get("white", 0)),
        "Nombre de lignes avec un label autre que white":
            int(counts.sum() - counts.get("white", 0)),
        "distribution_labels": distribution,
    }
    _display_report(report, "Distribution des labels (% de toutes les lignes)",
                    display_mode)
    return report


def check_dataset(data, reference_date="2026-10-01", display_mode="auto"):
    """Affiche et retourne un audit Bitcoin Heist, sans modifier le 
    dataset. Les conversions servent uniquement aux contrôles. Toutes les lignes,
    y compris les doublons, sont comptées. La date par défaut est celle
    fixée dans les notebooks pour la reproductibilité.

    Utilisation dans un notebook : rapport = check_dataset(data).
    Affecter le retour à une variable évite que Jupyter affiche aussi le gros
    dictionnaire brut sous le bilan mis en forme.

    display_mode : "auto" détecte Jupyter, "html" force les tableaux repliables,
    "text" produit un bilan texte et "none" permet un audit sans affichage.
    Le rapport contient les compteurs et les tableaux complets réutilisables.
    La distribution des labels se consulte avec check_label_distribution.
    """
    # 1. Schéma attendu : ces noms sont explicites pour ne pas dépendre de
    # l'ordre des colonnes ou intégrer accidentellement une cible numérique.
    numeric_cols = ["year", "day", "length", "weight", "count",
                    "looped", "neighbors", "income"]
    integer_cols = [col for col in numeric_cols if col != "weight"]
    required_cols = ["address", *numeric_cols, "label"]
    
    report = {}
    def record(name, value):
        report[name] = value

    record("Nombre de lignes", len(data))
    record("Nombre de colonnes", data.shape[1])
    record("Nombre de noms de colonnes dupliqués",
           int(data.columns.duplicated().sum()))
    missing_cols = [col for col in required_cols if col not in data.columns]
    record("Nombre de colonnes requises absentes", len(missing_cols))
    record("Colonnes requises absentes", missing_cols)
    record("Nombre de doublons stricts", int(data.duplicated().sum()))

    # 2. Valeurs manquantes, sur toutes les colonnes et toutes les lignes.
    # On distingue les vrais marqueurs NA des chaînes vides/blanches.
    # Le contrôle est positionnel pour accepter aussi des noms dupliqués.
    # Le masque est indépendant : aucune case du dataset n'est remplacée.
    missing = data.isna().copy()
    for i in range(data.shape[1]):
        blank = data.iloc[:, i].map(
            lambda value: isinstance(value, str) and not value.strip()
        )
        missing.iloc[:, i] = missing.iloc[:, i] | blank
    record("Nombre de valeurs nulles (NaN / None / NA)",
           int(data.isna().sum().sum()))
    record("Nombre de cases vides (valeurs nulles ou chaînes blanches)",
           int(missing.sum().sum()))
    record("Nombre de lignes avec au moins une case vide",
           int(missing.any(axis=1).sum()))
    audit = pd.DataFrame({
        "colonne": data.columns,
        "type": data.dtypes.astype(str).to_numpy(),
        "cases_vides": missing.sum().to_numpy(),
        "valeurs_distinctes": data.nunique().to_numpy(),
    })
    report["audit_colonnes"] = audit

    if not data.columns.is_unique:
        # Un accès data[col] serait ambigu : conserver les contrôles globaux
        # et expliquer pourquoi les contrôles suivants ne sont pas exécutés.
        record("Contrôles non exécutés", "Contrôles par nom : noms dupliqués")
        _display_report(report, "Vérification du dataset", display_mode)
        return report

    # 3. Conversion TEMPORAIRE des variables numériques pour les vérifier.
    # errors="coerce" permet de repérer les textes non convertibles. Les
    # cellules déjà vides ne sont pas comptées une seconde fois comme telles.
    # Les masques par ligne réunissent les anomalies sans compter deux fois
    # une ligne qui aurait plusieurs valeurs problématiques.
    numeric = pd.DataFrame(index=data.index)
    conversion_report = []
    unreadable_rows = pd.Series(False, index=data.index)
    infinite_rows = pd.Series(False, index=data.index)
    for col in numeric_cols:
        if col not in data.columns:
            continue
        converted = pd.to_numeric(data[col], errors="coerce")
        nonconvertible = ~missing[col] & converted.isna()
        infinite = converted.isin([np.inf, -np.inf])
        unreadable_rows |= nonconvertible
        infinite_rows |= infinite
        # Seule cette série temporaire exclut les infinis des calculs.
        numeric[col] = converted.where(~infinite)
        conversion_report.append({
            "colonne": col,
            "non_convertibles": int(nonconvertible.sum()),
            "infinis": int(infinite.sum()),
            "negatifs": int(converted.lt(0).sum()),
            "zeros": int(converted.eq(0).sum()),
            "entiers_fractionnaires": int(
                (numeric[col].notna() & numeric[col].mod(1).ne(0)).sum()
            ) if col in integer_cols else 0,
        })
    conversion = pd.DataFrame(conversion_report)
    report["audit_numerique"] = conversion
    record("Nombre de valeurs non convertibles",
           sum(item["non_convertibles"] for item in conversion_report))
    record("Nombre de valeurs infinies",
           sum(item["infinis"] for item in conversion_report))
    negative_rows = numeric.lt(0).any(axis=1)
    # Les infinis négatifs comptent également comme valeurs négatives.
    for col in numeric.columns:
        negative_rows |= pd.to_numeric(data[col], errors="coerce").eq(-np.inf)
    # weight accepte les décimales ; les autres variables doivent être
    # entières. Les valeurs absentes et infinies sont exclues de ce contrôle.
    integers = numeric[[col for col in integer_cols if col in numeric.columns]]
    fractional_rows = (integers.notna() & integers.mod(1).ne(0)).any(axis=1)
    record("Nombre de lignes avec une valeur négative", int(negative_rows.sum()))
    record("Nombre de lignes avec un entier fractionnaire",
           int(fractional_rows.sum()))
    # Union logique, et non somme des compteurs : une ligne peut cumuler
    # plusieurs anomalies. Les doublons sont signalés séparément.
    invalid_rows = (missing.any(axis=1) | unreadable_rows | infinite_rows
                    | negative_rows | fractional_rows)

    # 4. Dates : day est le numéro du jour dans l'année (1 à 365/366).
    # Vérifier aussi les années bissextiles et la borne de reproductibilité.
    # Sans ces deux colonnes, le contrôle ne peut pas être effectué.
    if {"year", "day"}.issubset(numeric.columns):
        today = pd.Timestamp(reference_date).normalize()
        year, day = numeric["year"], numeric["day"]
        leap = year.mod(4).eq(0) & (
            year.mod(100).ne(0) | year.mod(400).eq(0)
        )
        max_day = pd.Series(np.where(leap, 366, 365), index=data.index)
        valid_year = year.between(2009, today.year) & year.mod(1).eq(0)
        valid_day = day.ge(1) & day.le(max_day) & day.mod(1).eq(0)
        # Ne convertir en entier que les années déjà validées. Int64 est
        # nullable et accepte les valeurs absentes sans modifier la source.
        year_start = pd.to_datetime(
            year.where(valid_year).astype("Int64").astype("string"),
            format="%Y", errors="coerce",
        )
        dates = year_start + pd.to_timedelta(day.where(valid_day) - 1, unit="D")
        # Une date absente relève des manquants. Une date renseignée mais
        # impossible ou future relève de ce compteur spécifique.
        has_date_fields = ~missing[["year", "day"]].any(axis=1)
        invalid_dates = has_date_fields & ~dates.between("2009-01-01", today)
        record("Nombre de lignes avec une date invalide ou future",
               int(invalid_dates.sum()))
        invalid_rows |= invalid_dates
        valid_dates = dates.where(~invalid_dates)
        record("Début de la période valide", valid_dates.min())
        record("Fin de la période valide", valid_dates.max())
        if "address" in data.columns:
            # keep=False compte TOUTES les lignes partageant une clé valide,
            # contrairement au compteur des doublons stricts (keep="first").
            keys = pd.DataFrame({"address": data["address"], "date": valid_dates})
            eligible = ~missing["address"] & valid_dates.notna()
            record("Nombre de lignes partageant une clé adresse-date",
                   int(keys.loc[eligible].duplicated(keep=False).sum()))

    # 5. Cohérence du graphe : les chemins qui bouclent constituent un
    # sous-ensemble des chemins comptés ; looped ne doit pas dépasser count.
    if {"looped", "count"}.issubset(numeric.columns):
        topology_issue = numeric["looped"].gt(numeric["count"])
        record("Nombre de lignes avec looped > count", int(topology_issue.sum()))
        invalid_rows |= topology_issue
    record("Nombre de lignes distinctes avec une anomalie (hors doublons)",
           int(invalid_rows.sum()))

    if "address" in data.columns:
        record("Nombre d'adresses distinctes",
               data.loc[~missing["address"], "address"].nunique())
    # La distribution de la cible est volontairement séparée du contrôle
    # qualité : appeler check_label_distribution(data) pour la consulter.
    # 6. Statistiques descriptives sur les valeurs convertibles et finies.
    # Les doublons et valeurs négatives restent présents : ceci est un audit,
    # pas un nettoyage. Les quantiles décrivent donc le dataset reçu.
    if not numeric.empty:
        stats = numeric.describe(percentiles=[0.01, 0.25, 0.5, 0.75, 0.99]).T
        report["statistiques"] = stats

    # Le rendu arrondit uniquement l'affichage ; les tableaux retournés
    # conservent leurs valeurs précises pour une analyse ultérieure.
    _display_report(report, "Vérification du dataset", display_mode)
    return report



def split_data(X,y,train_size,random_state):
    """Sépare les données en ensembles d'entraînement et de test.

    X : DataFrame
    y : Etiquettes.
    train_size : proportion de l'ensemble d'entraînement (0 < train_size < 1).
    random_state : seed pour la reproductibilité.

    Retourne X_train, X_test, y_train, y_test.
    """
    from sklearn.model_selection import train_test_split

    if not isinstance(X, pd.DataFrame):
        raise TypeError("X doit être un DataFrame pandas.")
    if not isinstance(y, pd.Series):
        raise TypeError("y doit être une Series pandas.")
    if not (0 < train_size < 1):
        raise ValueError("train_size doit être compris entre 0 et 1.")
    
    return train_test_split(X, y, train_size=train_size, random_state=random_state)