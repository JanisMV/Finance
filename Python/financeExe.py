import tkinter as tk
from tkinter import ttk, messagebox

import pandas as pd
import yfinance as yf

import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore")

class FinanceApp:

    def __init__(self, root):

        self.root = root

        root.title("Finance Analyzer")
        root.geometry("1200x800")

        self.resultats = []
        self.tickers = []
        self.donnees = {}

        self.create_widgets()

    def create_widgets(self):

        # -----------------------------
        # Recherche
        # -----------------------------

        recherche_frame = ttk.LabelFrame(
            self.root,
            text="Recherche"
        )

        recherche_frame.pack(
            fill="x",
            padx=10,
            pady=10
        )

        self.recherche_entry = ttk.Entry(
            recherche_frame,
            width=40
        )

        self.recherche_entry.pack(
            side="left",
            padx=5,
            pady=5
        )

        recherche_btn = ttk.Button(
            recherche_frame,
            text="Rechercher",
            command=self.rechercher
        )

        recherche_btn.pack(
            side="left",
            padx=5
        )

        # -----------------------------
        # Résultats
        # -----------------------------

        self.tree = ttk.Treeview(
            self.root,
            columns=(
                "symbole",
                "type",
                "nom"
            ),
            show="headings",
            height=12
        )

        self.tree.heading(
            "symbole",
            text="Symbole"
        )

        self.tree.heading(
            "type",
            text="Type"
        )

        self.tree.heading(
            "nom",
            text="Nom"
        )

        self.tree.pack(
            fill="both",
            expand=True,
            padx=10
        )

        # -----------------------------
        # Boutons sélection
        # -----------------------------

        frame_btn = ttk.Frame(
            self.root
        )

        frame_btn.pack(
            pady=10
        )

        ttk.Button(
            frame_btn,
            text="Ajouter sélection",
            command=self.ajouter_selection
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            frame_btn,
            text="Supprimer sélection",
            command=self.supprimer_selection
        ).pack(
            side="left",
            padx=5
        )

        # -----------------------------
        # Liste des actifs retenus
        # -----------------------------

        select_frame = ttk.LabelFrame(
            self.root,
            text="Actifs sélectionnés"
        )

        select_frame.pack(
            fill="x",
            padx=10,
            pady=10
        )

        self.listbox = tk.Listbox(
            select_frame,
            height=6
        )

        self.listbox.pack(
            fill="x",
            padx=5,
            pady=5
        )

        # -----------------------------
        # Paramètres
        # -----------------------------

        param_frame = ttk.LabelFrame(
            self.root,
            text="Paramètres"
        )

        param_frame.pack(
            fill="x",
            padx=10,
            pady=10
        )

        ttk.Label(
            param_frame,
            text="Nombre d'années :"
        ).pack(
            side="left",
            padx=5
        )

        self.annees_var = tk.StringVar(
            value="10"
        )

        ttk.Entry(
            param_frame,
            textvariable=self.annees_var,
            width=10
        ).pack(
            side="left"
        )

        # -----------------------------
        # Boutons analyse
        # -----------------------------

        analyse_frame = ttk.Frame(
            self.root
        )

        analyse_frame.pack(
            pady=20
        )
        ttk.Button(
            analyse_frame,
            text="Analyser",
            command=self.analyser
        ).pack(
            side="left",
            padx=5
        )
        ttk.Button(
            analyse_frame,
            text="Courbes brutes",
            command=self.graphique_brut
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            analyse_frame,
            text="Base 100",
            command=self.graphique_normalise
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            analyse_frame,
            text="Statistiques",
            command=self.statistiques
        ).pack(
            side="left",
            padx=5
        )

    def rechercher(self):

        mot = self.recherche_entry.get()

        try:

            recherche = yf.Search(mot)

            self.resultats = recherche.quotes[:20]

            for row in self.tree.get_children():
                self.tree.delete(row)

            traduction = {
                "INDEX": "Indice",
                "ETF": "ETF",
                "EQUITY": "Action",
                "CRYPTOCURRENCY": "Crypto",
                "CURRENCY": "Devise",
                "FUTURE": "Future"
            }

            for r in self.resultats:

                symbole = r.get(
                    "symbol",
                    ""
                )

                typ = traduction.get(
                    r.get(
                        "quoteType",
                        ""
                    ),
                    r.get(
                        "quoteType",
                        ""
                    )
                )

                nom = r.get(
                    "shortname",
                    ""
                )

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        symbole,
                        typ,
                        nom
                    )
                )

        except Exception as e:

            messagebox.showerror(
                "Erreur",
                str(e)
            )

    def ajouter_selection(self):

        item = self.tree.focus()

        if not item:
            return

        values = self.tree.item(
            item
        )["values"]

        ticker = values[0]

        self.tickers.append(
            ticker
        )

        self.listbox.insert(
            tk.END,
            ticker
        )

    def supprimer_selection(self):

        selection = (
            self.listbox.curselection()
        )

        if not selection:
            return

        index = selection[0]

        self.listbox.delete(index)

        del self.tickers[index]

    def analyser(self):

        self.donnees = {}

        try:

            annees = int(
                self.annees_var.get()
            )

        except:

            messagebox.showerror(
                "Erreur",
                "Nombre d'années invalide"
            )

            return

        for ticker in self.tickers:

            try:

                data = yf.download(
                    ticker,
                    period=f"{annees}y",
                    auto_adjust=True,
                    progress=False
                )

                if not data.empty:
                    self.donnees[ticker] = (
                        data["Close"]
                        .squeeze()
                    )

            except Exception as e:

                print(
                    f"Erreur sur {ticker}:",
                    e
                )

        popup = tk.Toplevel(self.root)

        popup.title("Analyse terminée")
        popup.geometry("250x100")

        popup.iconbitmap("Designer.ico")

        ttk.Label(
            popup,
            text=f"{len(self.donnees)} actif(s) chargé(s)"
        ).pack(pady=15)

        ttk.Button(
            popup,
            text="OK",
            command=popup.destroy
        ).pack()

    def graphique_brut(self):

        if len(self.donnees) == 0:
            messagebox.showwarning(
                "Attention",
                "Cliquez d'abord sur Analyser"
            )

            return

        donnees = self.donnees

        plt.figure(
            figsize=(12, 6)
        )

        for ticker, close in donnees.items():

            plt.plot(
                close.index,
                close.values,
                label=ticker
            )

        plt.title(
            "Evolution"
        )

        plt.legend()

        plt.grid(True)

        plt.show()

    def graphique_normalise(self):

        if len(self.donnees) == 0:
            messagebox.showwarning(
                "Attention",
                "Cliquez d'abord sur Analyser"
            )

            return

        donnees = self.donnees

        if len(donnees) < 2:
            return

        date_commune = max(
            s.index.min()
            for s in donnees.values()
        )

        plt.figure(
            figsize=(12, 6)
        )

        for ticker, close in donnees.items():

            close = close.loc[
                date_commune:
            ]

            perf = (
                close
                / close.iloc[0]
            ) * 100

            plt.plot(
                perf.index,
                perf.values,
                label=ticker
            )

        plt.title(
            "Comparaison Base 100"
        )

        plt.legend()

        plt.grid(True)

        plt.show()

    def statistiques(self):

        if len(self.donnees) == 0:
            messagebox.showwarning(
                "Attention",
                "Cliquez d'abord sur Analyser"
            )

            return

        donnees = self.donnees

        if len(donnees) == 0:
            return

        perf_annuelles = pd.DataFrame()

        for ticker, close in donnees.items():
            annual_close = close.resample(
                "YE"
            ).last()

            annual_returns = (
                    annual_close.pct_change()
                    * 100
            )

            perf_annuelles[ticker] = (
                annual_returns
            )

        perf_annuelles.index = (
            perf_annuelles.index.year
        )

        perf_annuelles = (
            perf_annuelles.dropna(
                how="all"
            )
        )

        ax = perf_annuelles.plot(
            kind="bar",
            figsize=(12, 6)
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
                fontsize=7
            )

        plt.tight_layout()

        plt.show()

root = tk.Tk()
root.iconbitmap("Designer.ico")

app = FinanceApp(root)

root.mainloop()