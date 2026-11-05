import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import warnings
import seaborn as sns

from pathlib import Path

"""
Ajout Portfolio
Chercher good meta avec momentum system
Benchmark MSCI World
MONTECARLO
"""


BASE_DIR = Path(__file__).parent

LOGO = BASE_DIR / "Designer.png"

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Finance Analyzer",
    page_icon=str(LOGO),
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
        str(LOGO),
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

    tickers_selectionnes = st.multiselect(
        "Actifs sélectionnés",
        st.session_state.tickers,
        default=st.session_state.tickers
    )

    st.session_state.tickers = (
        tickers_selectionnes
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

    fig, ax = plt.subplots(
        figsize=(10, 5)
    )

    for ticker, close in donnees.items():

        if isinstance(
                close,
                pd.Series
        ):
            ax.plot(
                close.index,
                close.values,
                label=ticker
            )

    ax.legend()

    ax.grid(True)

    fig_brut=fig

    # --------------------------
    # Base 100
    # --------------------------

    if len(donnees) > 1:

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

        fig_base100 = fig

    # --------------------------
    # Heatmap des corrélations
    # --------------------------

    if len(donnees) > 1:

        prix = pd.DataFrame(
            donnees
        )

        rendements = (
            prix
            .pct_change()
            .dropna()
        )

        correlation = (
            rendements
            .corr()
        )

        fig, ax = plt.subplots(
            figsize=(8, 6)
        )

        sns.heatmap(
            correlation,
            annot=True,
            cmap="RdYlGn",
            vmin=-1,
            vmax=1,
            fmt=".2f",
            ax=ax
        )

        ax.set_title(
            "Corrélation des rendements"
        )

        fig_corr=fig

    # --------------------------
    # Performances annuelles
    # --------------------------

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

    fig_perf=fig

    # --------------------------
    # Statistiques avancées
    # --------------------------

    stats = []

    for ticker, close in donnees.items():

        returns = close.pct_change().dropna()

        # CAGR
        nb_annees = (
                            close.index[-1] -
                            close.index[0]
                    ).days / 365.25

        cagr = (
                       (close.iloc[-1] / close.iloc[0])
                       ** (1 / nb_annees)
                       - 1
               ) * 100

        # Volatilité annualisée
        volatilite = (
                             returns.std()
                             * (252 ** 0.5)
                     ) * 100

        # Sharpe Ratio
        rendement_annuel = (
                returns.mean()
                * 252
        )

        sharpe = (
                rendement_annuel
                / (returns.std() * (252 ** 0.5))
        )

        # Drawdown
        cumulative_max = close.cummax()

        drawdown = (
                close / cumulative_max
                - 1
        )

        max_drawdown = (
                           drawdown.min()
                       ) * 100

        # Sortino Ratio

        downside_returns = (
            returns[
                returns < 0
                ]
        )

        if len(downside_returns) > 0:

            downside_vol = (
                    downside_returns.std()
                    * (252 ** 0.5)
            )

            sortino = (
                    rendement_annuel
                    / downside_vol
            )

        else:

            sortino = None

        # Calmar Ratio

        calmar = (
            cagr
            / abs(max_drawdown)
            if max_drawdown != 0
            else None
        )

        stats.append({

            "Ticker": ticker,

            "CAGR (%)":
                round(cagr, 2),

            "Volatilité (%)":
                round(volatilite, 2),

            "Sharpe":
                round(sharpe, 2),

            "Max Drawdown (%)":
                round(max_drawdown, 2),

            "Sortino":
                round(sortino, 2)
                if sortino is not None
                else None,

            "Calmar":
                round(calmar, 2)
                if calmar is not None
                else None
        })

    stats_df = pd.DataFrame(
        stats
    )


    st.header("Dashboard")

    col1, col2 = st.columns(2)

    if len(donnees) > 1:

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Comparaison en base 100 à la date de création la plus récente")
            st.pyplot(fig_base100)

        with col2:
            st.subheader("Corrélations")
            st.pyplot(fig_corr)

        col3, col4 = st.columns(2)

        with col3:

            titre_col, radio_col = st.columns([2, 5])

            with titre_col:
                st.subheader("Actif sélectionné")

            with radio_col:
                st.write("")  # espace vertical

                ticker_selectionne = st.radio(
                    "",
                    list(donnees.keys()),
                    horizontal=True,
                    label_visibility="collapsed"
                )

            serie = donnees[
                ticker_selectionne
            ]

            fig_indiv, ax = plt.subplots(
                figsize=(8, 5)
            )

            ax.plot(
                serie.index,
                serie.values,
                linewidth=2
            )

            ax.set_title(
                ticker_selectionne
            )

            ax.grid(True)

            st.pyplot(fig_indiv)

        with col4:

            st.subheader(
                "Performances annuelles"
            )

            st.pyplot(
                fig_perf
            )


    else:

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Courbe brute")

            st.pyplot(fig_brut)

        with col2:

            st.subheader("Performances annuelles")

            st.pyplot(fig_perf)

    st.subheader(
        "Statistiques avancées"
    )

    st.dataframe(
        stats_df,
        use_container_width=True
    )