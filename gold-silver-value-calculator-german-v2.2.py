#!/usr/bin/env python3
import argparse
import locale
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


SPANISCH = {
    "Gold- und Silberrechner": "Calculadora de oro y plata",
    "Silber": "Plata",
    "Gold": "Oro",
    "Der Kurszeitstempel fehlt oder ist ungültig.": "Falta la fecha de la cotización o no es válida.",
    "{name} muss eine endliche Zahl größer als 0 und höchstens 10¹⁵ sein.": "{name}: introduce un número mayor que 0 y menor o igual que 10¹⁵.",
    "{name}: Bitte beispielsweise 1234,56 oder 1.234,56 eingeben.": "{name}: introduce un número como 1234,56, 1.234,56 o 1,234.56.",
    "{name}: Bitte eine gültige Zahl eingeben.": "{name}: introduce un número válido.",
    "Eingaben geändert. Bitte neu berechnen.": "Datos modificados. Vuelve a calcular.",
    "Der Kursserver meldet einen Fehler oder liefert ungültige Daten.": "El servidor de cotizaciones devolvió un error o datos no válidos.",
    "Erwartet werden EUR pro Feinunze (toz).": "Se esperaba un precio en EUR por onza troy (toz).",
    "Die Metallpreise fehlen.": "Faltan los precios de los metales.",
    "Goldpreis": "Precio del oro",
    "Silberpreis": "Precio de la plata",
    "Der Kurszeitstempel liegt in der Zukunft.": "La fecha de la cotización es posterior a la hora actual.",
    "Kurs wird geladen …": "Cargando cotizaciones…",
    "Kursstand: ": "Cotización del ",
    "Kurse erfolgreich geladen.": "Cotizaciones actualizadas.",
    "Kursabruf fehlgeschlagen. Vorhandene Kurse bleiben erhalten.": "No se pudieron actualizar las cotizaciones. Se conservan los precios disponibles.",
    "Fehler beim Kursabruf": "Error al obtener las cotizaciones",
    "Kurse nicht verfügbar. Preise können manuell eingegeben werden.\n\n": "No hay cotizaciones disponibles. Puedes introducir el precio manualmente.",
    "Preis pro Feinunze": "Precio por onza troy",
    "Gewicht": "Peso",
    "Bitte eine gültige Feinheit auswählen.": "Selecciona una pureza válida.",
    "Feingewicht: ": "Peso de metal puro: ",
    "Feinunzen: ": "Onzas troy de metal puro: ",
    "Metallwert wurde berechnet.": "Valor del metal calculado.",
    "Ungültige Eingabe.": "Dato no válido.",
    "Ungültige Eingabe": "Dato no válido",
    "Bereit.": "Listo.",
    "Metall:": "Metal:",
    "Preis pro Feinunze in €:": "Precio por onza troy (€):",
    "Gewicht des Gegenstands in g:": "Peso del objeto (g):",
    "Feinheit:": "Pureza (‰):",
    "Berechnen": "Calcular",
    "Zurücksetzen": "Restablecer",
    "Beenden": "Salir",
    "Fenster immer im Vordergrund halten": "Mantener la ventana encima de las demás",
    "Ergebnis": "Resultado",
    "Berechnet wird der theoretische Materialwert.\nSammlerwert, Verarbeitung und Händlerabschläge sind nicht enthalten.": "Se calcula el valor teórico del metal.\nNo incluye el valor de colección, la mano de obra\nni los márgenes comerciales.",
    "Version {version}\nKursdaten: Metals.Dev": "Versión {version}\nCotizaciones: Metals.Dev",
}
sprache = "de"


def _(text):
    if sprache == "es":
        return SPANISCH[text]
    return text


def systemsprache():
    for variable in ("LC_ALL", "LC_MESSAGES", "LANG"):
        wert = os.environ.get(variable)
        if wert:
            break
    else:
        wert = locale.getlocale()[0] or ""
    sprachcode = re.split(r"[_\-.]", wert.lower(), maxsplit=1)[0]
    return "es" if sprachcode in ("es", "spanish") else "de"


gold_preis = None
silber_preis = None
kursabruf_laeuft = False
kursantworten = queue.Queue()
geschlossen = False


def zeitstempel_lesen(zeit):
    if not isinstance(zeit, str) or not zeit.strip():
        raise ValueError(_("Der Kurszeitstempel fehlt oder ist ungültig."))

    datum = datetime.fromisoformat(zeit.strip().replace("Z", "+00:00"))
    if datum.tzinfo is None:
        datum = datum.replace(tzinfo=timezone.utc)
    return datum


def kursstand_formatieren(zeit):
    datum = zeitstempel_lesen(zeit)
    if sprache == "es":
        return datum.astimezone(timezone.utc).strftime("%d/%m/%Y, %H:%M UTC")
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
            _("{name} muss eine endliche Zahl größer als 0 und höchstens 10¹⁵ sein.").format(name=name)
        ) from None


def eingabe_lesen(text, name):
    """Erlaubt 1234,56, 1.234,56 und 1234.56.

    Ein Punkt ohne Komma ist immer ein Dezimalpunkt.
    Tausender deshalb beispielsweise als 1.234,00 eingeben.
    """
    text = text.strip()

    if sprache == "es" and re.fullmatch(r"[0-9]{1,3}(?:,[0-9]{3})+\.[0-9]+", text):
        text = text.replace(",", "")
    if "," in text:
        if not re.fullmatch(
            r"(?:[0-9]+|[0-9]{1,3}(?:\.[0-9]{3})+),[0-9]+",
            text,
        ):
            raise ValueError(
                _("{name}: Bitte beispielsweise 1234,56 oder 1.234,56 eingeben.").format(name=name)
            )
        text = text.replace(".", "").replace(",", ".")
    elif not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", text):
        raise ValueError(_("{name}: Bitte eine gültige Zahl eingeben.").format(name=name))

    return positive_zahl(text, name)


def ergebnis_verwerfen(event=None):
    if ergebnis_variable.get():
        ergebnis_variable.set("")
        status_variable.set(_("Eingaben geändert. Bitte neu berechnen."))


def preisfeld_aktualisieren():
    preis = (
        silber_preis
        if metall_auswahl.current() == 0
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


def ausgewaehltes_metall():
    return ("Silber", "Gold")[metall_auswahl.current()]


def feinheiten_aktualisieren(event=None):
    metall = ausgewaehltes_metall()
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
            _("Der Kursserver meldet einen Fehler oder liefert ungültige Daten.")
        )

    if daten.get("currency") != "EUR" or daten.get("unit") != "toz":
        raise ValueError(_("Erwartet werden EUR pro Feinunze (toz)."))

    metals = daten.get("metals")
    if not isinstance(metals, dict):
        raise ValueError(_("Die Metallpreise fehlen."))

    gold = positive_zahl(metals.get("gold"), _("Goldpreis"))
    silber = positive_zahl(metals.get("silver"), _("Silberpreis"))
    zeit = daten.get("updated_at")
    stand = zeitstempel_lesen(zeit)

    if stand > datetime.now(timezone.utc) + timedelta(minutes=5):
        raise ValueError(_("Der Kurszeitstempel liegt in der Zukunft."))

    return gold, silber, zeit


def kursdaten_abrufen():
    global kursabruf_laeuft

    if kursabruf_laeuft or geschlossen:
        return

    kursabruf_laeuft = True
    status_variable.set(_("Kurs wird geladen …"))

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
                _("Kursstand: ") + kursstand_formatieren(zeit)
            )
            preisfeld_aktualisieren()

            status_variable.set(_("Kurse erfolgreich geladen."))
            
        else:
            status_variable.set(
                _("Kursabruf fehlgeschlagen. Vorhandene Kurse bleiben erhalten.")
            )
            if gold_preis is None and silber_preis is None:
                messagebox.showerror(
                    _("Fehler beim Kursabruf"),
                    _("Kurse nicht verfügbar. Preise können manuell eingegeben werden.\n\n")
                    + (antwort if sprache == "de" else ""),
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
            unzenpreis_eingabe.get(), _("Preis pro Feinunze")
        )
        gewicht = eingabe_lesen(gewicht_eingabe.get(), _("Gewicht"))
        feinheit_text = feinheit_variable.get()

        if feinheit_text not in FEINHEITEN[ausgewaehltes_metall()]:
            raise ValueError(_("Bitte eine gültige Feinheit auswählen."))

        with localcontext() as kontext:
            kontext.prec = 40
            feingewicht = gewicht * Decimal(feinheit_text) / 1000
            feinunzen = feingewicht / GRAMM_PRO_UNZE
            metallwert = feinunzen * preis

            ergebnis_variable.set(
                f"{zahl_deutsch_formatieren(metallwert, 2)} €\n\n"
                f"{_('Feingewicht: ')}"
                f"{zahl_deutsch_formatieren(feingewicht, 2)} g\n"
                f"{_('Feinunzen: ')}{zahl_deutsch_formatieren(feinunzen, 4)}"
            )

        status_variable.set(_("Metallwert wurde berechnet."))
    except (ValueError, InvalidOperation) as fehler:
        status_variable.set(_("Ungültige Eingabe."))
        messagebox.showerror(_("Ungültige Eingabe"), str(fehler))


def eingaben_loeschen():
    gewicht_eingabe.delete(0, tk.END)
    metall_auswahl.current(0)
    feinheiten_aktualisieren()
    ergebnis_variable.set("")
    status_variable.set(_("Bereit."))
    gewicht_eingabe.focus()


def vordergrund_umschalten():
    fenster.attributes("-topmost", immer_vorne_variable.get())


def schliessen():
    global geschlossen
    geschlossen = True
    fenster.destroy()


def startbenachrichtigung_beenden():
    """Beendet unter X11 auch eine vom Starter geerbte Startbenachrichtigung."""
    if not sys.platform.startswith("linux") or not os.environ.get("DESKTOP_STARTUP_ID"):
        return

    import ctypes
    from ctypes.util import find_library

    xdisplay = display = context = None
    try:
        x11_name = find_library("X11")
        sn_name = find_library("startup-notification-1")
        if not x11_name or not sn_name:
            return
        x11 = ctypes.CDLL(x11_name)
        sn = ctypes.CDLL(sn_name)
        pointer = ctypes.c_void_p
        x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
        x11.XOpenDisplay.restype = pointer
        x11.XDefaultScreen.argtypes = [pointer]
        x11.XDefaultScreen.restype = ctypes.c_int
        x11.XCloseDisplay.argtypes = [pointer]
        x11.XCloseDisplay.restype = ctypes.c_int
        sn.sn_display_new.argtypes = [pointer, pointer, pointer]
        sn.sn_display_new.restype = pointer
        sn.sn_display_unref.argtypes = [pointer]
        sn.sn_display_unref.restype = None
        sn.sn_launchee_context_new_from_environment.argtypes = [pointer, ctypes.c_int]
        sn.sn_launchee_context_new_from_environment.restype = pointer
        sn.sn_launchee_context_complete.argtypes = [pointer]
        sn.sn_launchee_context_complete.restype = None
        sn.sn_launchee_context_unref.argtypes = [pointer]
        sn.sn_launchee_context_unref.restype = None
        xdisplay = x11.XOpenDisplay(None)
        if not xdisplay:
            return
        display = sn.sn_display_new(xdisplay, None, None)
        if not display:
            return
        context = sn.sn_launchee_context_new_from_environment(
            display, x11.XDefaultScreen(xdisplay)
        )
        if context:
            sn.sn_launchee_context_complete(context)
            os.environ.pop("DESKTOP_STARTUP_ID", None)
    except (OSError, AttributeError):
        # Ein fehlender Desktop-Dienst darf den Programmstart nicht verhindern.
        pass
    finally:
        if context:
            sn.sn_launchee_context_unref(context)
        if display:
            sn.sn_display_unref(display)
        if xdisplay:
            x11.XCloseDisplay(xdisplay)


def main():
    global fenster, metall_auswahl, feinheit_variable
    global ergebnis_variable, status_variable, kursstand_variable
    global unzenpreis_eingabe, gewicht_eingabe, feinheit_auswahl
    global immer_vorne_variable

    fenster = tk.Tk()
    fenster.title(_("Gold- und Silberrechner"))
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
        text=_("Gold- und Silberrechner"),
        font=("Arial", 19, "bold"),
    ).pack(pady=(0, 20))

    formular = ttk.Frame(hauptbereich)
    formular.pack(fill="x", padx=20)
    formular.columnconfigure(1, weight=1)

    ttk.Label(formular, text=_("Metall:")).grid(
        row=0, column=0, sticky="w", padx=5, pady=9
    )
    metall_auswahl = ttk.Combobox(
        formular,
        values=[_("Silber"), _("Gold")],
        state="readonly",
        width=25,
    )
    metall_auswahl.current(0)
    metall_auswahl.grid(
        row=0, column=1, sticky="ew", padx=5, pady=9
    )
    metall_auswahl.bind(
        "<<ComboboxSelected>>", feinheiten_aktualisieren
    )

    ttk.Label(formular, text=_("Preis pro Feinunze in €:")).grid(
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

    ttk.Label(formular, text=_("Gewicht des Gegenstands in g:")).grid(
        row=3, column=0, sticky="w", padx=5, pady=9
    )
    gewicht_variable = tk.StringVar()
    gewicht_eingabe = ttk.Entry(
        formular, textvariable=gewicht_variable, width=28
    )
    gewicht_eingabe.grid(
        row=3, column=1, sticky="ew", padx=5, pady=9
    )

    ttk.Label(formular, text=_("Feinheit:")).grid(
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
        button_bereich, text=_("Berechnen"), command=berechnen
    ).grid(row=0, column=0, padx=8)
    ttk.Button(
        button_bereich,
        text=_("Zurücksetzen"),
        command=eingaben_loeschen,
    ).grid(row=0, column=1, padx=8)
    ttk.Button(
        button_bereich, text=_("Beenden"), command=schliessen
    ).grid(row=0, column=2, padx=8)

    immer_vorne_variable = tk.BooleanVar(value=True)
    ttk.Checkbutton(
        hauptbereich,
        text=_("Fenster immer im Vordergrund halten"),
        variable=immer_vorne_variable,
        command=vordergrund_umschalten,
    ).pack(pady=10)

    ergebnis_rahmen = ttk.LabelFrame(
        hauptbereich, text=_("Ergebnis"), padding=15
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
            _("Berechnet wird der theoretische Materialwert.\nSammlerwert, Verarbeitung und Händlerabschläge sind nicht enthalten.")
        ),
        justify="center",
    ).pack(pady=8)

    ttk.Label(
        hauptbereich,
        text=_("Version {version}\nKursdaten: Metals.Dev").format(version=__version__),
        justify="center",
    ).pack(pady=(4, 8))

    status_variable = tk.StringVar(value=_("Bereit."))
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
    fenster.after_idle(startbenachrichtigung_beenden)
    fenster.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", choices=("de", "es"), help="Deutsch / Español")
    sprache = parser.parse_args().lang or systemsprache()
    main()
