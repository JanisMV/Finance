import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

# ==================================================
# SELECTION DES ACTIFS
# ==================================================

tickers = []

while True:

    continuer_recherche = False

    recherche = input(
        "\nNom de l'indice ou actif à rechercher : "
    )

    try:

        search = yf.Search(recherche)

        resultats = search.quotes[:20]

        if len(resultats) == 0:
            print("Aucun résultat trouvé.")
            continue

        print("\nRésultats trouvés :\n")

        for i, r in enumerate(resultats):

            symbole = r.get("symbol", "N/A")
            nom = r.get("shortname", "N/A")

            type_actif = r.get(
                "quoteType",
                "Inconnu"
            )

            traduction = {
                "INDEX": "Indice",
                "ETF": "ETF",
                "EQUITY": "Action",
                "FUTURE": "Future",
                "CURRENCY": "Devise",
                "CRYPTOCURRENCY": "Crypto"
            }

            type_actif = traduction.get(
                type_actif,
                type_actif
            )

            print(
                f"[{i}] {symbole:<15} | "
                f"{type_actif:<12} | "
                f"{nom}"
            )

        choix = input(
            "\nChoix (0,1,2 ou 0+ pour effectuer une autre recherche) : "
        )

        # ------------------------
        # Cas 0+
        # ------------------------

        elements = choix.split(",")

        for element in elements:

            element = element.strip()

            if element.endswith("+"):

                idx = int(element[:-1])

                tickers.append(
                    resultats[idx]["symbol"]
                )

                continuer_recherche = True

            else:

                idx = int(element)

                tickers.append(
                    resultats[idx]["symbol"]
                )

        # IMPORTANT :
        if continuer_recherche:
            continue
        else:
            break

    except Exception as e:

        print(
            "\nErreur lors de la recherche :",
            e
        )

# ==================================================
# PARAMETRES
# ==================================================

annees = int(
    input(
        "\nNombre d'années à analyser : "
    )
)

# ==================================================
# TELECHARGEMENT
# ==================================================

donnees = {}

for ticker in tickers:

    try:

        data = yf.download(
            ticker,
            period=f"{annees}y",
            auto_adjust=True,
            progress=False
        )

        if not data.empty:

            close = data["Close"].squeeze()

            donnees[ticker] = close

            print(
                f"Données récupérées : {ticker}"
            )

    except Exception as e:

        print(
            f"Erreur sur {ticker} :",
            e
        )

# ==================================================
# STATISTIQUES
# ==================================================

for ticker, close in donnees.items():

    annual_close = close.resample(
        "YE"
    ).last()

    annual_returns = (
        annual_close.pct_change()
        * 100
    )

    df_perf = pd.DataFrame({
        "Clôture":
            annual_close.round(2),
        "Performance (%)":
            annual_returns.round(2)
    })

    print(
        "\n=========================="
    )

    print(
        f"{ticker}"
    )

    print(
        "=========================="
    )

    print(df_perf)

    rendement_total = (
        (
            close.iloc[-1]
            / close.iloc[0]
        ) - 1
    ) * 100

    print(
        f"\nRendement total : "
        f"{rendement_total:.2f}%"
    )

# ==================================================
# GRAPHIQUE EVOLUTION
# ==================================================

if input(
        "\nAfficher les courbes brutes ? (o/n) : "
).lower() == "o":

    plt.figure(
        figsize=(13, 7)
    )

    for ticker, close in donnees.items():

        plt.plot(
            close.index,
            close.values,
            label=ticker
        )

    plt.title(
        f"Evolution sur {annees} ans"
    )

    plt.xlabel("Date")
    plt.ylabel("Valeur")

    plt.legend()

    plt.grid(True)

    plt.show()

# ==================================================
# COMPARAISON NORMALISEE
# ==================================================

if len(donnees) > 1:

    if input(
        "\nAfficher la comparaison normalisée (base 100) ? (o/n) : "
    ).lower() == "o":

        plt.figure(
            figsize=(13, 7)
        )

        date_commune = max(
            serie.index.min()
            for serie in donnees.values()
        )

        for ticker, close in donnees.items():

            close = close.loc[date_commune:]

            normalise = (
                close
                / close.iloc[0]
            ) * 100

            plt.plot(
                normalise.index,
                normalise.values,
                label=ticker
            )

        plt.title(
            f"Comparaison des performances ({annees} ans)"
        )

        plt.xlabel("Date")

        plt.ylabel(
            "Base 100"
        )

        plt.legend()

        plt.grid(True)

        plt.show()

# ==================================================
# PERFORMANCE ANNUELLE COMPAREE
# ==================================================

if input(
    "\nAfficher la comparaison des performances annuelles ? (o/n) : "
).lower() == "o":

    perf_annuelles = pd.DataFrame()

    for ticker, close in donnees.items():

        annual_close = close.resample(
            "YE"
        ).last()

        annual_returns = (
            annual_close.pct_change()
            * 100
        )

        perf_annuelles[ticker] = annual_returns

    perf_annuelles.plot(
        kind="bar",
        figsize=(14, 7)
    )

    plt.title(
        "Comparaison des performances annuelles"
    )

    plt.xlabel(
        "Année"
    )

    plt.ylabel(
        "Performance (%)"
    )

    plt.grid(
        axis="y",
        alpha=0.3
    )

    plt.legend(
        title="Actifs"
    )

    plt.tight_layout()

    plt.show()