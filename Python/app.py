import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Finance Analyzer",
    page_icon="Designer.png",
    layout="wide"
)

# ==================================================
# SESSION
# ==================================================

if "tickers" not in st.session_state:
    st.session_state.tickers = []

if "donnees" not in st.session_state:
    st.session_state.donnees = {}

# ==================================================
# TITRE
# ==================================================

col1, col2 = st.columns([1, 12])

with col1:
    st.image(
        "Designer.png",
        width=90
    )

with col2:
    st.markdown(
        "<h1 style='margin-top:15px;'>Finance Analyzer</h1>",
        unsafe_allow_html=True
    )

# ==================================================
# RECHERCHE
# ==================================================

st.header("Recherche")

recherche = st.text_input(
    "Nom d'un actif, indice, ETF..."
)

if recherche:

    try:

        search = yf.Search(recherche)

        resultats = search.quotes[:20]

        choix = {}

        for r in resultats:

            symbole = r.get(
                "symbol",
                "N/A"
            )

            nom = r.get(
                "shortname",
                "N/A"
            )

            typ = r.get(
                "quoteType",
                "N/A"
            )

            texte = (
                f"{symbole} | "
                f"{typ} | "
                f"{nom}"
            )

            choix[texte] = symbole

        selection = st.multiselect(
            "Résultats",
            list(choix.keys())
        )

        if st.button(
            "Ajouter sélection"
        ):

            for s in selection:

                ticker = choix[s]

                if ticker not in st.session_state.tickers:

                    st.session_state.tickers.append(
                        ticker
                    )

    except Exception as e:

        st.error(
            str(e)
        )

# ==================================================
# SELECTION
# ==================================================

st.header("Actifs sélectionnés")

if len(
    st.session_state.tickers
) == 0:

    st.info(
        "Aucun actif sélectionné."
    )

else:

    st.write(
        st.session_state.tickers
    )

# ==================================================
# PARAMETRES
# ==================================================

annees = st.number_input(
    "Nombre d'années",
    min_value=1,
    max_value=50,
    value=10
)

# ==================================================
# ANALYSE
# ==================================================

if st.button(
    "Analyser"
):

    donnees = {}

    progress = st.progress(
        0
    )

    for i, ticker in enumerate(
        st.session_state.tickers
    ):

        try:

            data = yf.download(
                ticker,
                period=f"{annees}y",
                auto_adjust=True,
                progress=False
            )

            if not data.empty:

                donnees[ticker] = (
                    data["Close"]
                    .squeeze()
                )

        except:
            pass

        progress.progress(
            (i + 1)
            / len(
                st.session_state.tickers
            )
        )

    st.session_state.donnees = (
        donnees
    )

    st.success(
        "Analyse terminée"
    )

# ==================================================
# AFFICHAGE
# ==================================================

if len(
    st.session_state.donnees
) > 0:

    donnees = (
        st.session_state.donnees
    )

    # --------------------------
    # Courbes brutes
    # --------------------------

    st.header(
        "Courbes brutes"
    )

    fig, ax = plt.subplots(
        figsize=(10, 5)
    )

    for ticker, close in donnees.items():

        ax.plot(
            close.index,
            close.values,
            label=ticker
        )

    ax.legend()

    ax.grid(True)

    st.pyplot(fig)

    # --------------------------
    # Base 100
    # --------------------------

    if len(donnees) > 1:

        st.header(
            "Comparaison Base 100"
        )

        date_commune = max(
            serie.index.min()
            for serie in donnees.values()
        )

        fig, ax = plt.subplots(
            figsize=(10, 5)
        )

        for ticker, close in donnees.items():

            close = close.loc[
                date_commune:
            ]

            normalise = (
                close
                / close.iloc[0]
            ) * 100

            ax.plot(
                normalise.index,
                normalise.values,
                label=ticker
            )

        ax.legend()

        ax.grid(True)

        st.pyplot(fig)

    # --------------------------
    # Performances annuelles
    # --------------------------

    st.header(
        "Performances annuelles"
    )

    perf_annuelles = (
        pd.DataFrame()
    )

    for ticker, close in donnees.items():

        annual_close = (
            close
            .resample("YE")
            .last()
        )

        annual_returns = (
            annual_close
            .pct_change()
            * 100
        )

        perf_annuelles[
            ticker
        ] = annual_returns

    perf_annuelles.index = (
        perf_annuelles.index.year
    )

    perf_annuelles = (
        perf_annuelles
        .dropna(
            how="all"
        )
    )

    fig, ax = plt.subplots(
        figsize=(12, 6)
    )

    perf_annuelles.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title(
        "Comparaison des performances annuelles"
    )

    ax.set_xlabel(
        "Année"
    )

    ax.set_ylabel(
        "Performance (%)"
    )

    ax.grid(
        axis="y",
        alpha=0.3
    )

    for container in ax.containers:
        ax.bar_label(
            container,
            fmt="%.1f",
            fontsize=8,
            padding=2
        )

    plt.tight_layout()

    st.pyplot(fig)