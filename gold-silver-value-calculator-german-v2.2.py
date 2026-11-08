#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import re
import queue
import threading
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from decimal import Decimal, InvalidOperation, localcontext

import requests

__author__ = "Volker Andreas Müller"
__credits__ = "Developed with assistance from ChatGPT by OpenAI"
__version__ = "2.2"

GRAMM_PRO_UNZE = Decimal("31.1034768")
KURS_URL = "https://gsr.linuga.org/v1/latest"
AKTUALISIERUNGSINTERVALL_MS = 15 * 60 * 1000

if getattr(sys, "frozen", False):
    PROGRAMM_ORDNER = os.path.dirname(sys.executable)
else:
    PROGRAMM_ORDNER = os.path.dirname(os.path.abspath(__file__))

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
        "800",
        "750",
        "720",
        "700",
        "680",
        "650",
        "640",
        "625",
        "600",
        "500",
        "400",
        "350",
        "300",
	"333",
        "250",
        "200",
        "100",
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
        "333",
    ],
}

gold_preis = None
silber_preis = None
kursabruf_laeuft = False
kursantworten = queue.Queue()
geschlossen = False


def zeitstempel_lesen(zeit):
    if not isinstance(zeit, str) or not zeit.strip():
        raise ValueError("Der Kurszeitstempel fehlt oder ist ungültig.")

    datum = datetime.fromisoformat(zeit.strip().replace("Z", "+00:00"))
    if datum.tzinfo is None:
        datum = datum.replace(tzinfo=timezone.utc)
    return datum


def kursstand_formatieren(zeit):
    datum = zeitstempel_lesen(zeit)
    try:
        return datum.astimezone(
            ZoneInfo("Europe/Berlin")
        ).strftime("%d.%m.%Y, %H:%M Uhr")
    except ZoneInfoNotFoundError:
        return datum.astimezone(
            timezone.utc
        ).strftime("%d.%m.%Y, %H:%M UTC")


def zahl_deutsch_formatieren(wert, nachkommastellen=2):
    return (
        f"{wert:,.{nachkommastellen}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def positive_zahl(wert, name):
    try:
        if isinstance(wert, bool):
            raise ValueError()

        zahl = Decimal(str(wert))
        if (
            not zahl.is_finite()
            or zahl <= 0
            or zahl > Decimal("1e15")
        ):
            raise ValueError()

        return zahl
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(
            f"{name} muss eine endliche Zahl größer als 0 "
            "und höchstens 10¹⁵ sein."
        ) from None


def eingabe_lesen(text, name):
    """Erlaubt 1234,56, 1.234,56 und 1234.56.

    Ein Punkt ohne Komma ist immer ein Dezimalpunkt.
    Tausender deshalb beispielsweise als 1.234,00 eingeben.
    """
    text = text.strip()

    if "," in text:
        if not re.fullmatch(
            r"(?:[0-9]+|[0-9]{1,3}(?:\.[0-9]{3})+),[0-9]+",
            text,
        ):
            raise ValueError(
                f"{name}: Bitte beispielsweise "
                "1234,56 oder 1.234,56 eingeben."
            )
        text = text.replace(".", "").replace(",", ".")
    elif not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", text):
        raise ValueError(f"{name}: Bitte eine gültige Zahl eingeben.")

    return positive_zahl(text, name)


def ergebnis_verwerfen(event=None):
    if ergebnis_variable.get():
        ergebnis_variable.set("")
        status_variable.set("Eingaben geändert. Bitte neu berechnen.")


def preisfeld_aktualisieren():
    preis = (
        silber_preis
        if metall_variable.get() == "Silber"
        else gold_preis
    )

    if preis is None:
        unzenpreis_eingabe.delete(0, tk.END)
        return

    ergebnis_verwerfen()
    unzenpreis_eingabe.delete(0, tk.END)
    unzenpreis_eingabe.insert(
        0, format(preis, "f").replace(".", ",")
    )


def feinheiten_aktualisieren(event=None):
    metall = metall_variable.get()
    feinheit_auswahl["values"] = FEINHEITEN[metall]
    feinheit_variable.set(FEINHEITEN[metall][0])
    ergebnis_variable.set("")
    preisfeld_aktualisieren()


def kursdaten_laden():
    """Netzwerk und Validierung ohne Zugriff auf Tkinter."""
    antwort = requests.get(
        KURS_URL,
        headers={"Accept": "application/json"},
        timeout=(5, 10),
    )
    antwort.raise_for_status()
    daten = antwort.json(parse_float=Decimal)

    if not isinstance(daten, dict) or daten.get("status") != "success":
        raise ValueError(
            "Der Kursserver meldet einen Fehler "
            "oder liefert ungültige Daten."
        )

    if daten.get("currency") != "EUR" or daten.get("unit") != "toz":
        raise ValueError("Erwartet werden EUR pro Feinunze (toz).")

    metals = daten.get("metals")
    if not isinstance(metals, dict):
        raise ValueError("Die Metallpreise fehlen.")

    gold = positive_zahl(metals.get("gold"), "Goldpreis")
    silber = positive_zahl(metals.get("silver"), "Silberpreis")
    zeit = daten.get("updated_at")
    stand = zeitstempel_lesen(zeit)

    if stand > datetime.now(timezone.utc) + timedelta(minutes=5):
        raise ValueError("Der Kurszeitstempel liegt in der Zukunft.")

    return gold, silber, zeit


def kursdaten_abrufen():
    global kursabruf_laeuft

    if kursabruf_laeuft or geschlossen:
        return

    kursabruf_laeuft = True
    status_variable.set("Kurs wird geladen …")

    def abrufen():
        try:
            kursantworten.put((True, kursdaten_laden()))
        except (
            requests.RequestException,
            ValueError,
            TypeError,
            OverflowError,
        ) as fehler:
            kursantworten.put((False, str(fehler)))

    threading.Thread(target=abrufen, daemon=True).start()


def kursantworten_verarbeiten():
    global gold_preis, silber_preis, kursabruf_laeuft

    if geschlossen:
        return

    try:
        erfolgreich, antwort = kursantworten.get_nowait()
    except queue.Empty:
        pass
    else:
        kursabruf_laeuft = False

        if erfolgreich:
            gold, silber, zeit = antwort

            # Erst nach vollständiger Validierung gemeinsam übernehmen.
            gold_preis, silber_preis = gold, silber
            kursstand_variable.set(
                "Kursstand: " + kursstand_formatieren(zeit)
            )
            preisfeld_aktualisieren()

            status_variable.set("Kurse erfolgreich geladen.")
            
        else:
            status_variable.set(
                "Kursabruf fehlgeschlagen. "
                "Vorhandene Kurse bleiben erhalten."
            )
            if gold_preis is None and silber_preis is None:
                messagebox.showerror(
                    "Fehler beim Kursabruf",
                    "Kurse nicht verfügbar. Preise können manuell "
                    "eingegeben werden.\n\n" + antwort,
                )

    fenster.after(50, kursantworten_verarbeiten)


def automatischen_kursabruf_planen():
    if geschlossen:
        return

    kursdaten_abrufen()
    fenster.after(
        AKTUALISIERUNGSINTERVALL_MS,
        automatischen_kursabruf_planen,
    )


def berechnen():
    ergebnis_variable.set("")

    try:
        preis = eingabe_lesen(
            unzenpreis_eingabe.get(), "Preis pro Feinunze"
        )
        gewicht = eingabe_lesen(gewicht_eingabe.get(), "Gewicht")
        feinheit_text = feinheit_variable.get()

        if feinheit_text not in FEINHEITEN[metall_variable.get()]:
            raise ValueError("Bitte eine gültige Feinheit auswählen.")

        with localcontext() as kontext:
            kontext.prec = 40
            feingewicht = gewicht * Decimal(feinheit_text) / 1000
            feinunzen = feingewicht / GRAMM_PRO_UNZE
            metallwert = feinunzen * preis

            ergebnis_variable.set(
                f"{zahl_deutsch_formatieren(metallwert, 2)} €\n\n"
                f"Feingewicht: "
                f"{zahl_deutsch_formatieren(feingewicht, 2)} g\n"
                f"Feinunzen: {zahl_deutsch_formatieren(feinunzen, 4)}"
            )

        status_variable.set("Metallwert wurde berechnet.")
    except (ValueError, InvalidOperation) as fehler:
        status_variable.set("Ungültige Eingabe.")
        messagebox.showerror("Ungültige Eingabe", str(fehler))


def eingaben_loeschen():
    gewicht_eingabe.delete(0, tk.END)
    metall_variable.set("Silber")
    feinheiten_aktualisieren()
    ergebnis_variable.set("")
    status_variable.set("Bereit.")
    gewicht_eingabe.focus()


def vordergrund_umschalten():
    fenster.attributes("-topmost", immer_vorne_variable.get())


def schliessen():
    global geschlossen
    geschlossen = True
    fenster.destroy()


def main():
    global fenster, metall_variable, feinheit_variable
    global ergebnis_variable, status_variable, kursstand_variable
    global unzenpreis_eingabe, gewicht_eingabe, feinheit_auswahl
    global immer_vorne_variable

    fenster = tk.Tk()
    fenster.title("Gold- und Silberrechner")
    fenster.geometry("600x735")
    fenster.resizable(True, True)
    fenster.attributes("-topmost", True)

    icon_datei = os.path.join(PROGRAMM_ORDNER, "gold-silber-icon.png")
    if os.path.exists(icon_datei):
        try:
            icon = tk.PhotoImage(file=icon_datei)
            fenster.iconphoto(True, icon)
        except tk.TclError:
            pass

    hauptbereich = ttk.Frame(fenster, padding=25)
    hauptbereich.pack(fill="both", expand=True)

    ttk.Label(
        hauptbereich,
        text="Gold- und Silberrechner",
        font=("Arial", 19, "bold"),
    ).pack(pady=(0, 20))

    formular = ttk.Frame(hauptbereich)
    formular.pack(fill="x", padx=20)
    formular.columnconfigure(1, weight=1)

    ttk.Label(formular, text="Metall:").grid(
        row=0, column=0, sticky="w", padx=5, pady=9
    )
    metall_variable = tk.StringVar(value="Silber")
    metall_auswahl = ttk.Combobox(
        formular,
        textvariable=metall_variable,
        values=["Silber", "Gold"],
        state="readonly",
        width=25,
    )
    metall_auswahl.grid(
        row=0, column=1, sticky="ew", padx=5, pady=9
    )
    metall_auswahl.bind(
        "<<ComboboxSelected>>", feinheiten_aktualisieren
    )

    ttk.Label(formular, text="Preis pro Feinunze in €:").grid(
        row=1, column=0, sticky="w", padx=5, pady=9
    )
    unzenpreis_variable = tk.StringVar()
    unzenpreis_eingabe = ttk.Entry(
        formular, textvariable=unzenpreis_variable, width=28
    )
    unzenpreis_eingabe.grid(
        row=1, column=1, sticky="ew", padx=5, pady=9
    )

    kursstand_variable = tk.StringVar(value="")
    ttk.Label(
        formular,
        textvariable=kursstand_variable,
        anchor="center",
    ).grid(
        row=2, column=0, columnspan=2,
        sticky="ew", padx=5, pady=(0, 5),
    )

    ttk.Label(formular, text="Gewicht des Gegenstands in g:").grid(
        row=3, column=0, sticky="w", padx=5, pady=9
    )
    gewicht_variable = tk.StringVar()
    gewicht_eingabe = ttk.Entry(
        formular, textvariable=gewicht_variable, width=28
    )
    gewicht_eingabe.grid(
        row=3, column=1, sticky="ew", padx=5, pady=9
    )

    ttk.Label(formular, text="Feinheit:").grid(
        row=4, column=0, sticky="w", padx=5, pady=9
    )
    feinheit_variable = tk.StringVar()
    ergebnis_variable = tk.StringVar()
    feinheit_auswahl = ttk.Combobox(
        formular,
        textvariable=feinheit_variable,
        state="readonly",
        width=25,
    )
    feinheit_auswahl.grid(
        row=4, column=1, sticky="ew", padx=5, pady=9
    )

    button_bereich = ttk.Frame(hauptbereich)
    button_bereich.pack(pady=(20, 10))

    ttk.Button(
        button_bereich, text="Berechnen", command=berechnen
    ).grid(row=0, column=0, padx=8)
    ttk.Button(
        button_bereich,
        text="Zurücksetzen",
        command=eingaben_loeschen,
    ).grid(row=0, column=1, padx=8)
    ttk.Button(
        button_bereich, text="Beenden", command=schliessen
    ).grid(row=0, column=2, padx=8)

    immer_vorne_variable = tk.BooleanVar(value=True)
    ttk.Checkbutton(
        hauptbereich,
        text="Fenster immer im Vordergrund halten",
        variable=immer_vorne_variable,
        command=vordergrund_umschalten,
    ).pack(pady=10)

    ergebnis_rahmen = ttk.LabelFrame(
        hauptbereich, text="Ergebnis", padding=15
    )
    ergebnis_rahmen.pack(fill="x", padx=20, pady=10)
    ttk.Label(
        ergebnis_rahmen,
        textvariable=ergebnis_variable,
        font=("Arial", 16, "bold"),
        justify="center",
    ).pack()

    ttk.Label(
        hauptbereich,
        text=(
            "Berechnet wird der theoretische Materialwert.\n"
            "Sammlerwert, Verarbeitung und Händlerabschläge "
            "sind nicht enthalten."
        ),
        justify="center",
    ).pack(pady=8)

    ttk.Label(
        hauptbereich,
        text=f"Version {__version__}\nKursdaten: Metals.Dev",
        justify="center",
    ).pack(pady=(4, 8))

    status_variable = tk.StringVar(value="Bereit.")
    ttk.Label(
        hauptbereich,
        textvariable=status_variable,
        relief="sunken",
        anchor="w",
    ).pack(fill="x", pady=(8, 0))

    unzenpreis_variable.trace_add(
        "write", lambda *args: ergebnis_verwerfen()
    )
    gewicht_variable.trace_add(
        "write", lambda *args: ergebnis_verwerfen()
    )
    feinheit_variable.trace_add(
        "write", lambda *args: ergebnis_verwerfen()
    )

    feinheiten_aktualisieren()
    fenster.bind("<Return>", lambda event: berechnen())
    gewicht_eingabe.focus()
    fenster.after(100, automatischen_kursabruf_planen)
    fenster.protocol("WM_DELETE_WINDOW", schliessen)
    fenster.after(50, kursantworten_verarbeiten)
    fenster.mainloop()


if __name__ == "__main__":
    main()
