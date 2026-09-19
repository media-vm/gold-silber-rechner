#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

__author__ = "Volker Andreas Müller"
__credits__ = "Developed with assistance from ChatGPT by OpenAI"
__version__ = "2.0"

_BUILD_SIGNATURE = (
    "Gold- und Silberrechner | "
    "Author: Volker Andreas Müller | "
    "Developed with assistance from ChatGPT / OpenAI"
)

_BUILD_ID = "VAM-GSR-2.0-CHATGPT-OPENAI-2026"

# Eine Feinunze entspricht diesem Gewicht in Gramm.
GRAMM_PRO_UNZE = 31.1034768

# Kursserver auf dem LinugaVPS.
KURS_URL = "https://gsr.linuga.org/v1/latest"

# Automatischer Kursabruf alle 15 Minuten.
AKTUALISIERUNGSINTERVALL_MS = 15 * 60 * 1000

# Speicherort des Programms / Icons.
if getattr(sys, "frozen", False):
    PROGRAMM_ORDNER = os.path.dirname(sys.executable)
else:
    PROGRAMM_ORDNER = os.path.dirname(os.path.abspath(__file__))


# Verfügbare Feinheiten für Gold und Silber
FEINHEITEN = {
    "Silber": [
        "999",
        "950",
        "935",
        "925",
        "920",
        "900",
        "835",
        "830",
        "800"
    ],
    "Gold": [
        "999",
        "986",
        "965",
        "916",
        "900",
        "750",
        "585",
        "375",
        "333"
    ]
}


# Zuletzt erfolgreich geladene Kurse.
gold_preis = None
silber_preis = None
kursabruf_laeuft = False


def kursstand_formatieren(zeit):
    """Formatiert den UTC-Zeitstempel des Servers in deutsche Ortszeit."""

    try:
        # Python versteht ISO-8601 inklusive +00:00.
        # Ein eventuell vorhandenes Z am Ende wird explizit als UTC behandelt.
        angepasst = zeit.strip()

        if angepasst.endswith("Z"):
            angepasst = angepasst[:-1] + "+00:00"

        datum = datetime.fromisoformat(angepasst)

        if datum.tzinfo is None:
            datum = datum.replace(tzinfo=ZoneInfo("UTC"))

        datum_berlin = datum.astimezone(
            ZoneInfo("Europe/Berlin")
        )

        return datum_berlin.strftime(
            "%d.%m.%Y, %H:%M Uhr"
        )

    except (ValueError, TypeError):
        return zeit


def preisfeld_aktualisieren():
    """Trägt den zuletzt geladenen Kurs des gewählten Metalls ein."""

    metall = metall_variable.get()

    if metall == "Silber":
        preis = silber_preis
    else:
        preis = gold_preis

    if preis is None:
        return

    unzenpreis_eingabe.delete(0, tk.END)
    unzenpreis_eingabe.insert(
        0,
        f"{preis:.2f}".replace(".", ",")
    )


def feinheiten_aktualisieren(event=None):
    """Passt die auswählbaren Feinheiten an das gewählte Metall an."""

    metall = metall_variable.get()

    feinheit_auswahl["values"] = FEINHEITEN[metall]
    feinheit_variable.set(FEINHEITEN[metall][0])

    ergebnis_variable.set("")

    # Falls bereits Kurse geladen wurden, direkt den Kurs
    # des neu ausgewählten Metalls anzeigen.
    preisfeld_aktualisieren()


def kursdaten_abrufen():
    """Ruft Gold-, Silberkurs und Kursstand vom Linuga-Server ab."""

    global gold_preis, silber_preis, kursabruf_laeuft

    if kursabruf_laeuft:
        return

    kursabruf_laeuft = True

    status_variable.set("Kurs wird geladen …")
    fenster.update_idletasks()

    try:
        antwort = requests.get(
            KURS_URL,
            headers={
                "Accept": "application/json"
            },
            timeout=10
        )

        antwort.raise_for_status()
        daten = antwort.json()

        if daten.get("status") != "success":
            raise RuntimeError(
                "Der Kursserver meldet einen Fehler."
            )

        metals = daten["metals"]

        gold_preis = float(
            metals["gold"]
        )

        silber_preis = float(
            metals["silver"]
        )

        aktualisiert = daten["updated_at"]

        kursstand_variable.set(
            "Kursstand: "
            + kursstand_formatieren(
                aktualisiert
            )
        )

        preisfeld_aktualisieren()

        status_variable.set(
            "Kurs erfolgreich vom Linuga-Server abgerufen."
        )

    except requests.Timeout:
        status_variable.set(
            "Zeitüberschreitung beim Kursabruf."
        )

        # Bereits vorhandene Kurse bleiben erhalten.
        if gold_preis is None and silber_preis is None:
            messagebox.showerror(
                "Zeitüberschreitung",
                "Der Kursserver hat nicht rechtzeitig geantwortet."
            )

    except requests.RequestException as fehler:
        status_variable.set(
            "Verbindungsfehler beim Kursabruf."
        )

        if gold_preis is None and silber_preis is None:
            messagebox.showerror(
                "Verbindungsfehler",
                "Der Kurs konnte nicht vom Linuga-Server abgerufen werden.\n\n"
                f"{fehler}"
            )

    except (KeyError, TypeError, ValueError, RuntimeError) as fehler:
        status_variable.set(
            "Fehler beim Verarbeiten der Kursdaten."
        )

        if gold_preis is None and silber_preis is None:
            messagebox.showerror(
                "Fehler beim Kursabruf",
                "Die Kursdaten konnten nicht verarbeitet werden.\n\n"
                f"{fehler}"
            )

    finally:
        kursabruf_laeuft = False


def automatischen_kursabruf_planen():
    """Ruft die Kurse ab und plant den nächsten Abruf in 15 Minuten."""

    kursdaten_abrufen()

    fenster.after(
        AKTUALISIERUNGSINTERVALL_MS,
        automatischen_kursabruf_planen
    )


def berechnen():
    """Berechnet Feingewicht und theoretischen Metallwert."""

    try:
        # Deutsches Dezimalkomma ebenfalls zulassen
        unzenpreis_text = (
            unzenpreis_eingabe
            .get()
            .strip()
            .replace(",", ".")
        )

        gewicht_text = (
            gewicht_eingabe
            .get()
            .strip()
            .replace(",", ".")
        )

        if not unzenpreis_text:
            raise ValueError(
                "Bitte den Preis pro Feinunze eingeben."
            )

        if not gewicht_text:
            raise ValueError(
                "Bitte das Gewicht des Gegenstands eingeben."
            )

        unzenpreis = float(unzenpreis_text)
        gewicht = float(gewicht_text)
        feinheit = int(feinheit_variable.get())

        if unzenpreis <= 0:
            raise ValueError(
                "Der Preis pro Feinunze muss größer als 0 sein."
            )

        if gewicht <= 0:
            raise ValueError(
                "Das Gewicht muss größer als 0 sein."
            )

        # Beispiel:
        # 100 g bei 800er Silber ergeben 80 g Feinsilber.
        feingewicht = gewicht * feinheit / 1000

        # Umrechnung des Feingewichts in Feinunzen
        feinunzen = feingewicht / GRAMM_PRO_UNZE

        # Berechnung des theoretischen Metallwerts
        metallwert = feinunzen * unzenpreis

        ergebnis_variable.set(
            f"{metallwert:.2f} €\n\n"
            f"Feingewicht: {feingewicht:.2f} g\n"
            f"Feinunzen: {feinunzen:.4f}"
        )

        status_variable.set(
            "Metallwert wurde berechnet."
        )

    except ValueError as fehler:
        status_variable.set(
            "Ungültige Eingabe."
        )

        messagebox.showerror(
            "Ungültige Eingabe",
            str(fehler)
        )


def eingaben_loeschen():
    """Setzt Eingaben und Ergebnis zurück, behält aber den Kurs."""

    gewicht_eingabe.delete(
        0,
        tk.END
    )

    metall_variable.set(
        "Silber"
    )

    feinheiten_aktualisieren()

    ergebnis_variable.set(
        ""
    )

    status_variable.set(
        "Bereit."
    )

    gewicht_eingabe.focus()


def vordergrund_umschalten():
    """Schaltet den Modus 'Immer im Vordergrund' ein oder aus."""

    immer_vorne = immer_vorne_variable.get()
    fenster.attributes(
        "-topmost",
        immer_vorne
    )


# ---------------------------------------------------------
# Hauptfenster
# ---------------------------------------------------------

fenster = tk.Tk()

ICON_DATEI = os.path.join(
    PROGRAMM_ORDNER,
    "gold-silber-icon.png"
)

if os.path.exists(ICON_DATEI):
    icon = tk.PhotoImage(
        file=ICON_DATEI
    )
    fenster.iconphoto(
        True,
        icon
    )

fenster.title(
    "Gold- und Silberrechner"
)

fenster.geometry(
    "600x735"
)

fenster.resizable(
    True,
    True
)

# Das Fenster bleibt zunächst immer im Vordergrund.
fenster.attributes(
    "-topmost",
    True
)


# ---------------------------------------------------------
# Hauptbereich
# ---------------------------------------------------------

hauptbereich = ttk.Frame(
    fenster,
    padding=25
)

hauptbereich.pack(
    fill="both",
    expand=True
)


ueberschrift = ttk.Label(
    hauptbereich,
    text="Gold- und Silberrechner",
    font=(
        "Arial",
        19,
        "bold"
    )
)

ueberschrift.pack(
    pady=(0, 20)
)


# ---------------------------------------------------------
# Eingabefelder
# ---------------------------------------------------------

formular = ttk.Frame(
    hauptbereich
)

formular.pack(
    fill="x",
    padx=20
)

formular.columnconfigure(
    1,
    weight=1
)


ttk.Label(
    formular,
    text="Metall:"
).grid(
    row=0,
    column=0,
    sticky="w",
    padx=5,
    pady=9
)


metall_variable = tk.StringVar(
    value="Silber"
)

metall_auswahl = ttk.Combobox(
    formular,
    textvariable=metall_variable,
    values=[
        "Silber",
        "Gold"
    ],
    state="readonly",
    width=25
)

metall_auswahl.grid(
    row=0,
    column=1,
    sticky="ew",
    padx=5,
    pady=9
)

metall_auswahl.bind(
    "<<ComboboxSelected>>",
    feinheiten_aktualisieren
)


ttk.Label(
    formular,
    text="Preis pro Feinunze in €:"
).grid(
    row=1,
    column=0,
    sticky="w",
    padx=5,
    pady=9
)


unzenpreis_eingabe = ttk.Entry(
    formular,
    width=28
)

unzenpreis_eingabe.grid(
    row=1,
    column=1,
    sticky="ew",
    padx=5,
    pady=9
)


kursstand_variable = tk.StringVar(
    value=""
)

kursstand_anzeige = ttk.Label(
    formular,
    textvariable=kursstand_variable,
    anchor="center"
)

kursstand_anzeige.grid(
    row=2,
    column=0,
    columnspan=2,
    sticky="ew",
    padx=5,
    pady=(0, 5)
)


ttk.Label(
    formular,
    text="Gewicht des Gegenstands in g:"
).grid(
    row=3,
    column=0,
    sticky="w",
    padx=5,
    pady=9
)


gewicht_eingabe = ttk.Entry(
    formular,
    width=28
)

gewicht_eingabe.grid(
    row=3,
    column=1,
    sticky="ew",
    padx=5,
    pady=9
)


ttk.Label(
    formular,
    text="Feinheit:"
).grid(
    row=4,
    column=0,
    sticky="w",
    padx=5,
    pady=9
)


feinheit_variable = tk.StringVar()
ergebnis_variable = tk.StringVar()

feinheit_auswahl = ttk.Combobox(
    formular,
    textvariable=feinheit_variable,
    state="readonly",
    width=25
)

feinheit_auswahl.grid(
    row=4,
    column=1,
    sticky="ew",
    padx=5,
    pady=9
)


# ---------------------------------------------------------
# Hauptschaltflächen
# ---------------------------------------------------------

button_bereich = ttk.Frame(
    hauptbereich
)

button_bereich.pack(
    pady=(20, 10)
)


berechnen_button = ttk.Button(
    button_bereich,
    text="Berechnen",
    command=berechnen
)

berechnen_button.grid(
    row=0,
    column=0,
    padx=8
)


loeschen_button = ttk.Button(
    button_bereich,
    text="Zurücksetzen",
    command=eingaben_loeschen
)

loeschen_button.grid(
    row=0,
    column=1,
    padx=8
)


beenden_button = ttk.Button(
    button_bereich,
    text="Beenden",
    command=fenster.destroy
)

beenden_button.grid(
    row=0,
    column=2,
    padx=8
)


# ---------------------------------------------------------
# Vordergrund-Einstellung
# ---------------------------------------------------------

immer_vorne_variable = tk.BooleanVar(
    value=True
)

immer_vorne_checkbox = ttk.Checkbutton(
    hauptbereich,
    text="Fenster immer im Vordergrund halten",
    variable=immer_vorne_variable,
    command=vordergrund_umschalten
)

immer_vorne_checkbox.pack(
    pady=10
)


# ---------------------------------------------------------
# Ergebnisanzeige
# ---------------------------------------------------------

ergebnis_rahmen = ttk.LabelFrame(
    hauptbereich,
    text="Ergebnis",
    padding=15
)

ergebnis_rahmen.pack(
    fill="x",
    padx=20,
    pady=10
)


ergebnis_anzeige = ttk.Label(
    ergebnis_rahmen,
    textvariable=ergebnis_variable,
    font=(
        "Arial",
        16,
        "bold"
    ),
    justify="center"
)

ergebnis_anzeige.pack()


# ---------------------------------------------------------
# Hinweise, Versionsangabe und Statuszeile
# ---------------------------------------------------------

hinweis = ttk.Label(
    hauptbereich,
    text=(
        "Berechnet wird der theoretische Materialwert.\n"
        "Sammlerwert, Verarbeitung und Händlerabschläge "
        "sind nicht enthalten."
    ),
    justify="center"
)

hinweis.pack(
    pady=8
)


versionshinweis = ttk.Label(
    hauptbereich,
    text=(
        "Version 2.0\n"
        "Kursdaten: Metals.Dev"
    ),
    justify="center"
)

versionshinweis.pack(
    pady=(4, 8)
)


status_variable = tk.StringVar(
    value="Bereit."
)

status_anzeige = ttk.Label(
    hauptbereich,
    textvariable=status_variable,
    relief="sunken",
    anchor="w"
)

status_anzeige.pack(
    fill="x",
    pady=(8, 0)
)


# Auswahl initialisieren.
feinheiten_aktualisieren()

# Mit der Eingabetaste kann ebenfalls berechnet werden.
fenster.bind(
    "<Return>",
    lambda event: berechnen()
)

# Das Gewichtsfeld erhält den Eingabefokus.
gewicht_eingabe.focus()

# Sofort nach dem Aufbau der Oberfläche den Kurs laden.
# Danach erfolgt der automatische Abruf alle 15 Minuten.
fenster.after(
    100,
    automatischen_kursabruf_planen
)

# Start der grafischen Anwendung
fenster.mainloop()
