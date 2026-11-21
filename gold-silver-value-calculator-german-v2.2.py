#!/usr/bin/env python3
import argparse
import locale
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import random
import sys
import re
import queue
import threading
from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from decimal import Decimal, InvalidOperation, localcontext

import requests

__author__ = "Volker Andreas Müller"
__credits__ = "Developed with assistance from ChatGPT by OpenAI"
__version__ = "2.4"

GRAMM_PRO_UNZE = Decimal("31.1034768")
GRAMM_PRO_PFUND = Decimal("453.59237")
SILBER_KILOGRAMM = "Kilogramo (kg)"
GEWICHTSEINHEITEN = {
    "Gramo (g)": Decimal("1"),
    SILBER_KILOGRAMM: Decimal("1000"),
    "Onza troy (oz t)": GRAMM_PRO_UNZE,
    "Onza común (oz)": Decimal("28.349523125"),
    "Libra (lb)": GRAMM_PRO_PFUND,
    "Arroba (25 lb)": 25 * GRAMM_PRO_PFUND,
    "Quintal (100 lb)": 100 * GRAMM_PRO_PFUND,
    "Quintal métrico (100 kg)": Decimal("100000"),
}
GEWICHTSEINHEITEN_EN = {
    "Gram (g)": Decimal("1"),
    "Troy ounce (oz t)": GRAMM_PRO_UNZE,
    "Ounce (oz)": Decimal("28.349523125"),
    "Pound (lb)": GRAMM_PRO_PFUND,
    "Kilogram (kg)": Decimal("1000"),
}
KURS_URL = "https://gsr.linuga.org/v1/latest"
WECHSELKURS_URL = "https://api.frankfurter.dev/v2/rates"
METALLKURSINTERVALL_MS = 15 * 60 * 1000
WECHSELKURSINTERVALL_MS = 2 * 60 * 60 * 1000
WECHSELKURS_WIEDERHOLUNG_MS = 60 * 60 * 1000
WECHSELKURS_STREUUNG_MS = 30 * 60 * 1000
WECHSELKURS_STARTSTREUUNG_MS = 10 * 1000
MAX_WECHSELKURSALTER = timedelta(days=7)

# ISO-Code: (spanische Bezeichnung, Nachkommastellen)
WAEHRUNGEN = {
    "EUR": ("Euro", 2),
    "USD": ("Dólar estadounidense", 2),
    "PAB": ("Balboa panameño", 2),
    "MXN": ("Peso mexicano", 2),
    "COP": ("Peso colombiano", 2),
    "ARS": ("Peso argentino", 2),
    "CLP": ("Peso chileno", 0),
    "PEN": ("Sol peruano", 2),
    "DOP": ("Peso dominicano", 2),
    "GTQ": ("Quetzal guatemalteco", 2),
    "CRC": ("Colón costarricense", 2),
    "HNL": ("Lempira hondureño", 2),
    "NIO": ("Córdoba nicaragüense", 2),
    "BOB": ("Boliviano", 2),
    "PYG": ("Guaraní paraguayo", 0),
    "UYU": ("Peso uruguayo", 2),
    "VES": ("Bolívar venezolano", 2),
    "CUP": ("Peso cubano", 2),
    "XAF": ("Franco CFA de África Central", 0),
}
WAEHRUNGEN_DE = {
    "EUR": ("Euro", 2),
    "CHF": ("Schweizer Franken", 2),
    "USD": ("US-Dollar", 2),
}
WAEHRUNGEN_EN = {
    "USD": ("US dollar", 2),
    "EUR": ("Euro", 2),
    "INR": ("Indian rupee", 2),
    "PKR": ("Pakistani rupee", 2),
    "NGN": ("Nigerian naira", 2),
    "PHP": ("Philippine peso", 2),
    "TZS": ("Tanzanian shilling", 2),
    "GBP": ("Pound sterling", 2),
    "ZAR": ("South African rand", 2),
    "KES": ("Kenyan shilling", 2),
    "UGX": ("Ugandan shilling", 0),
}

RESSOURCEN_ORDNER = getattr(
    sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))
)

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
GOLD_KARAT = {"999": 24, "916": 22, "750": 18, "585": 14, "375": 9}
SILBER_HISTORISCH = "Dineros y granos…"


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
    "Währung:": "Moneda:",
    "Preis pro Feinunze ({code}):": "Precio por onza troy ({code}):",
    "Wechselkurs vom {datum} (Frankfurter)": "Tipo de cambio del {datum} (Frankfurter)",
    "Kein aktueller Wechselkurs. Preis in {code} manuell eingeben.": "Tipo de cambio no disponible. Introduce el precio en {code}.",
    "Manuell eingegebener Preis ({code})": "Precio introducido manualmente ({code})",
    "Kein Metallkurs verfügbar. Preis in {code} manuell eingeben.": "Cotización del metal no disponible. Introduce el precio en {code}.",
    "Gewicht des Gegenstands in g:": "Peso del objeto:",
    "Feinheit:": "Pureza (‰):",
    "Berechnen": "Calcular",
    "Zurücksetzen": "Restablecer",
    "Beenden": "Salir",
    "Fenster immer im Vordergrund halten": "Mantener la ventana encima de las demás",
    "Ergebnis": "Resultado",
    "Berechnet wird der theoretische Materialwert.\nSammlerwert, Verarbeitung und Händlerabschläge sind nicht enthalten.": "Se calcula el valor teórico del metal.\nNo incluye el valor de colección, la mano de obra\nni los márgenes comerciales.",
    "Version {version}\nKursdaten: Metals.Dev": "Versión {version}\nCotizaciones: Metals.Dev",
}
ENGLISCH = {
    "Gold- und Silberrechner": "Gold and Silver Calculator",
    "Silber": "Silver",
    "Gold": "Gold",
    "Der Kurszeitstempel fehlt oder ist ungültig.": "The metal price timestamp is missing or invalid.",
    "{name} muss eine endliche Zahl größer als 0 und höchstens 10¹⁵ sein.": "{name} must be a finite number greater than 0 and no more than 10¹⁵.",
    "{name}: Bitte beispielsweise 1234,56 oder 1.234,56 eingeben.": "{name}: Enter a number such as 1234.56 or 1,234.56.",
    "{name}: Bitte eine gültige Zahl eingeben.": "{name}: Enter a valid number.",
    "Eingaben geändert. Bitte neu berechnen.": "Inputs changed. Calculate again.",
    "Der Kursserver meldet einen Fehler oder liefert ungültige Daten.": "The price service reported an error or returned invalid data.",
    "Erwartet werden EUR pro Feinunze (toz).": "Expected a price in EUR per troy ounce (oz t).",
    "Die Metallpreise fehlen.": "The metal prices are missing.",
    "Goldpreis": "Gold price",
    "Silberpreis": "Silver price",
    "Der Kurszeitstempel liegt in der Zukunft.": "The metal price timestamp is in the future.",
    "Kurs wird geladen …": "Loading metal prices…",
    "Kursstand: ": "Metal prices as of ",
    "Kurse erfolgreich geladen.": "Metal prices updated.",
    "Kursabruf fehlgeschlagen. Vorhandene Kurse bleiben erhalten.": "Could not refresh metal prices. Previously loaded prices are still available.",
    "Fehler beim Kursabruf": "Could not load metal prices",
    "Kurse nicht verfügbar. Preise können manuell eingegeben werden.\n\n": "Metal prices are unavailable. You can enter a price manually.",
    "Preis pro Feinunze": "Price per troy ounce",
    "Gewicht": "Weight",
    "Bitte eine gültige Feinheit auswählen.": "Select a valid purity.",
    "Feingewicht: ": "Pure metal weight: ",
    "Feinunzen: ": "Troy ounces of pure metal: ",
    "Metallwert wurde berechnet.": "Metal value calculated.",
    "Ungültige Eingabe.": "Invalid input.",
    "Ungültige Eingabe": "Invalid input",
    "Bereit.": "Ready.",
    "Metall:": "Metal:",
    "Währung:": "Currency:",
    "Preis pro Feinunze ({code}):": "Price per troy ounce ({code}):",
    "Wechselkurs vom {datum} (Frankfurter)": "Exchange rate as of {datum} (Frankfurter)",
    "Kein aktueller Wechselkurs. Preis in {code} manuell eingeben.": "Exchange rate unavailable. Enter the price in {code} manually.",
    "Manuell eingegebener Preis ({code})": "Manually entered price ({code})",
    "Kein Metallkurs verfügbar. Preis in {code} manuell eingeben.": "Metal price unavailable. Enter the price in {code} manually.",
    "Gewicht des Gegenstands in g:": "Item weight:",
    "Feinheit:": "Purity (‰):",
    "Berechnen": "Calculate",
    "Zurücksetzen": "Reset",
    "Beenden": "Exit",
    "Fenster immer im Vordergrund halten": "Keep window on top",
    "Ergebnis": "Result",
    "Berechnet wird der theoretische Materialwert.\nSammlerwert, Verarbeitung und Händlerabschläge sind nicht enthalten.": "Estimates the value of the metal content.\nThis excludes collectible value, workmanship,\nand dealer margins.",
    "Version {version}\nKursdaten: Metals.Dev": "Version {version}\nMetal prices: Metals.Dev",
}

sprache = "de"


def _(text):
    if sprache == "es":
        return SPANISCH[text]
    if sprache == "en":
        return ENGLISCH[text]
    return text


def systemsprache():
    for variable in ("LC_ALL", "LC_MESSAGES", "LANG"):
        wert = os.environ.get(variable)
        if wert:
            break
    else:
        wert = locale.getlocale()[0] or ""
    sprachcode = re.split(r"[_\-.]", wert.lower(), maxsplit=1)[0]
    return {"es": "es", "spanish": "es", "en": "en", "english": "en"}.get(
        sprachcode, "de"
    )


gold_preis = None
silber_preis = None
kurszeit = None
wechselkurse = {}
manuelle_preise = {}
preis_wird_gesetzt = False
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
    if sprache == "en":
        return datum.astimezone(timezone.utc).strftime("%m/%d/%Y, %I:%M %p UTC")
    try:
        return datum.astimezone(
            ZoneInfo("Europe/Berlin")
        ).strftime("%d.%m.%Y, %H:%M Uhr")
    except ZoneInfoNotFoundError:
        return datum.astimezone(
            timezone.utc
        ).strftime("%d.%m.%Y, %H:%M UTC")


def zahl_formatieren(wert, nachkommastellen=2):
    formatiert = f"{wert:,.{nachkommastellen}f}"
    if sprache == "en":
        return formatiert
    return formatiert.translate(str.maketrans(",.", ".,"))


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
    """Liest Dezimalzahlen mit den Trennzeichen des gewählten Sprachmodus."""
    text = text.strip()

    if sprache == "en":
        if not re.fullmatch(r"(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)(?:\.[0-9]+)?|\.[0-9]+", text):
            raise ValueError(
                _("{name}: Bitte beispielsweise 1234,56 oder 1.234,56 eingeben.").format(name=name)
            )
        return positive_zahl(text.replace(",", ""), name)

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


def waehrungen():
    return {"es": WAEHRUNGEN, "de": WAEHRUNGEN_DE, "en": WAEHRUNGEN_EN}[sprache]


def gewichtseinheiten():
    return GEWICHTSEINHEITEN_EN if sprache == "en" else GEWICHTSEINHEITEN


def ausgewaehlte_waehrung():
    return waehrung_auswahl.get().split(" — ", 1)[0]


def angezeigte_waehrung(code):
    return "€" if sprache == "de" and code == "EUR" else code


def aktueller_wechselkurs(code):
    kurs = wechselkurse.get(code)
    heute = datetime.now(timezone.utc).date()
    if kurs and heute - MAX_WECHSELKURSALTER <= kurs[1] <= heute:
        return kurs
    return None


def preisfeld_aktualisieren():
    global preis_wird_gesetzt

    code = ausgewaehlte_waehrung()
    metall = ausgewaehltes_metall()
    einheit = angezeigte_waehrung(code)
    preis_label_variable.set(_("Preis pro Feinunze ({code}):").format(code=einheit))
    schluessel = (code, metall)
    preis = silber_preis if metall == "Silber" else gold_preis
    devisenkurs = aktueller_wechselkurs(code)
    wert = ""

    if schluessel in manuelle_preise:
        wert = manuelle_preise[schluessel]
        hinweis = _("Manuell eingegebener Preis ({code})").format(code=code)
    elif preis is None:
        hinweis = _("Kein Metallkurs verfügbar. Preis in {code} manuell eingeben.").format(code=code)
    elif code != "EUR" and devisenkurs is None:
        hinweis = _("Kein aktueller Wechselkurs. Preis in {code} manuell eingeben.").format(code=code)
    else:
        hinweis = _("Kursstand: ") + kursstand_formatieren(kurszeit)
        if code != "EUR":
            faktor, datum = devisenkurs
            preis *= faktor
            datumsformat = {"de": "%d.%m.%Y", "es": "%d/%m/%Y", "en": "%m/%d/%Y"}
            datum_text = datum.strftime(datumsformat[sprache])
            hinweis += "\n" + _("Wechselkurs vom {datum} (Frankfurter)").format(datum=datum_text)
        wert = format(preis, "f")
        if sprache != "en":
            wert = wert.replace(".", ",")

    kursstand_variable.set(hinweis)
    if unzenpreis_variable.get() != wert:
        preis_wird_gesetzt = True
        try:
            unzenpreis_variable.set(wert)
        finally:
            preis_wird_gesetzt = False


def preis_manuell_geaendert(*args):
    ergebnis_verwerfen()
    if not preis_wird_gesetzt:
        code = ausgewaehlte_waehrung()
        manuelle_preise[(code, ausgewaehltes_metall())] = unzenpreis_variable.get()
        kursstand_variable.set(_("Manuell eingegebener Preis ({code})").format(code=code))


def waehrung_geaendert(event=None):
    ergebnis_verwerfen()
    preisfeld_aktualisieren()


def ausgewaehltes_metall():
    return ("Silber", "Gold")[metall_auswahl.current()]


def feinheiten_aktualisieren(event=None):
    metall = ausgewaehltes_metall()
    if sprache == "es":
        einheiten = list(GEWICHTSEINHEITEN)
        if metall == "Gold":
            einheiten.remove(SILBER_KILOGRAMM)
            if gewichtseinheit_auswahl.get() == SILBER_KILOGRAMM:
                gewichtseinheit_auswahl.current(0)
                gewicht_eingabe.delete(0, tk.END)
        gewichtseinheit_auswahl["values"] = einheiten

    anzeigen = [feinheit_anzeigen(wert, metall) for wert in FEINHEITEN[metall]]
    if sprache == "es" and metall == "Silber":
        anzeigen.append(SILBER_HISTORISCH)
    feinheit_auswahl["values"] = anzeigen
    feinheit_auswahl.current(0)
    feinheit_variable.set(FEINHEITEN[metall][0])
    ergebnis_variable.set("")
    preisfeld_aktualisieren()


def feinheit_anzeigen(wert, metall):
    if ":" in wert:
        dineros, granos = wert.split(":")
        return f"{dineros} dineros, {granos} granos"
    if metall == "Gold" and wert in GOLD_KARAT:
        einheit = {"de": "Karat", "es": "quilates", "en": "karat"}[sprache]
        return f"{wert} ‰ · {GOLD_KARAT[wert]} {einheit}"
    if metall == "Silber" and wert == "925":
        return {
            "de": "925 ‰ · Sterlingsilber",
            "es": "925 ‰ · Plata de ley (Sterling)",
            "en": "925 ‰ · Sterling silver",
        }[sprache]
    return wert if sprache == "de" else f"{wert} ‰"


def silber_granos(text):
    einheiten = re.fullmatch(r"\s*([0-9]{1,2})\s*:\s*([0-9]{1,2})\s*", text)
    if einheiten:
        dineros, granos = map(int, einheiten.groups())
        gesamt = 24 * dineros + granos
        if 0 <= granos < 24 and 0 < gesamt <= 12 * 24:
            return gesamt
    raise ValueError("Introduce una pureza válida, entre 0:1 y 12:0, con un máximo de 23 granos.")


def feinheit_geaendert(event=None):
    metall = ausgewaehltes_metall()
    if feinheit_auswahl.get() != SILBER_HISTORISCH:
        feinheit_variable.set(FEINHEITEN[metall][feinheit_auswahl.current()])
        return

    vorher = feinheit_variable.get()
    wert = simpledialog.askstring(
        "Pureza histórica de la plata",
        "Introduce dineros y granos separados por dos puntos.\n"
        "Ejemplo: 11:12. La plata pura equivale a 12:0.",
        initialvalue=vorher if ":" in vorher else "",
        parent=fenster,
    )
    if wert is not None:
        try:
            dineros, granos = divmod(silber_granos(wert), 24)
        except ValueError as fehler:
            messagebox.showerror(_("Ungültige Eingabe"), str(fehler), parent=fenster)
        else:
            feinheit_variable.set(f"{dineros}:{granos}")
    feinheit_auswahl.set(feinheit_anzeigen(feinheit_variable.get(), metall))


def feinheitsanteil(wert, metall):
    if wert in FEINHEITEN[metall]:
        return Decimal(wert) / 1000
    if sprache == "es" and metall == "Silber" and ":" in wert:
        return Decimal(silber_granos(wert)) / 288
    raise ValueError(_("Bitte eine gültige Feinheit auswählen."))


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


def wechselkurse_laden():
    devisen = tuple(code for code in waehrungen() if code != "EUR")
    antwort = requests.get(
        WECHSELKURS_URL,
        params={
            "base": "EUR",
            "quotes": ",".join(devisen),
        },
        timeout=(5, 10),
    )
    antwort.raise_for_status()
    daten = antwort.json(parse_float=Decimal)
    if not isinstance(daten, list):
        raise ValueError("Invalid exchange-rate response")

    kurse = {}
    for eintrag in daten:
        if not isinstance(eintrag, dict):
            continue
        code = eintrag.get("quote")
        if (
            eintrag.get("base") != "EUR"
            or not isinstance(code, str)
            or code not in devisen
        ):
            continue
        try:
            datum = date.fromisoformat(eintrag.get("date"))
            faktor = positive_zahl(eintrag.get("rate"), code)
        except (TypeError, ValueError):
            continue
        kurse[code] = faktor, datum
    return kurse


def kursdaten_abrufen():
    global kursabruf_laeuft

    if kursabruf_laeuft or geschlossen:
        return

    kursabruf_laeuft = True
    status_variable.set(_("Kurs wird geladen …"))

    def abrufen():
        try:
            kursantworten.put(("metall", True, kursdaten_laden()))
        except (
            requests.RequestException,
            ValueError,
            TypeError,
            OverflowError,
        ) as fehler:
            kursantworten.put(("metall", False, str(fehler)))

    threading.Thread(target=abrufen, daemon=True).start()


def wechselkurse_abrufen():
    if geschlossen:
        return

    def abrufen():
        try:
            kurse = wechselkurse_laden()
        except (requests.RequestException, ValueError, TypeError, OverflowError):
            kursantworten.put(("waehrung", False, None))
        else:
            kursantworten.put(("waehrung", bool(kurse), kurse))

    threading.Thread(target=abrufen, daemon=True).start()


def kursantworten_verarbeiten():
    global gold_preis, silber_preis, kurszeit, kursabruf_laeuft

    if geschlossen:
        return

    try:
        art, erfolgreich, antwort = kursantworten.get_nowait()
    except queue.Empty:
        pass
    else:
        if art == "waehrung":
            if erfolgreich:
                wechselkurse.update(antwort)
            preisfeld_aktualisieren()
            intervall = WECHSELKURSINTERVALL_MS
            if not erfolgreich:
                intervall = WECHSELKURS_WIEDERHOLUNG_MS + random.randint(
                    0, WECHSELKURS_STREUUNG_MS
                )
            fenster.after(
                intervall,
                wechselkurse_abrufen,
            )
        else:
            kursabruf_laeuft = False

        if art == "metall" and erfolgreich:
            # Erst nach vollständiger Validierung gemeinsam übernehmen.
            gold_preis, silber_preis, kurszeit = antwort
            preisfeld_aktualisieren()
            status_variable.set(_("Kurse erfolgreich geladen."))
            
        elif art == "metall":
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
        METALLKURSINTERVALL_MS,
        automatischen_kursabruf_planen,
    )


def berechnen():
    ergebnis_variable.set("")

    try:
        preis = eingabe_lesen(
            unzenpreis_eingabe.get(), _("Preis pro Feinunze")
        )
        gewicht = eingabe_lesen(gewicht_eingabe.get(), _("Gewicht"))
        with localcontext() as kontext:
            kontext.prec = 40
            if sprache != "de":
                gewicht *= gewichtseinheiten()[gewichtseinheit_auswahl.get()]
            anteil = feinheitsanteil(feinheit_variable.get(), ausgewaehltes_metall())
            feingewicht = gewicht * anteil
            feinunzen = feingewicht / GRAMM_PRO_UNZE
            metallwert = feinunzen * preis
            code = ausgewaehlte_waehrung()
            nachkommastellen = waehrungen()[code][1]
            betrag = zahl_formatieren(metallwert, nachkommastellen)
            anzeige = f"${betrag}" if sprache == "en" and code == "USD" else f"{betrag} {angezeigte_waehrung(code)}"

            ergebnis_variable.set(
                f"{anzeige}\n\n"
                f"{_('Feingewicht: ')}"
                f"{zahl_formatieren(feingewicht, 2)} g\n"
                f"{_('Feinunzen: ')}{zahl_formatieren(feinunzen, 4)}"
            )

        status_variable.set(_("Metallwert wurde berechnet."))
    except (ValueError, InvalidOperation) as fehler:
        status_variable.set(_("Ungültige Eingabe."))
        messagebox.showerror(_("Ungültige Eingabe"), str(fehler))


def eingaben_loeschen():
    manuelle_preise.clear()
    gewicht_eingabe.delete(0, tk.END)
    if sprache != "de":
        gewichtseinheit_auswahl.current(0)
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
    global unzenpreis_eingabe, unzenpreis_variable, gewicht_eingabe, feinheit_auswahl
    global waehrung_auswahl, preis_label_variable
    global gewichtseinheit_auswahl
    global immer_vorne_variable

    fenster = tk.Tk()
    fenster.title(_("Gold- und Silberrechner"))
    fenster.geometry("620x830")
    fenster.resizable(True, True)
    fenster.attributes("-topmost", True)

    png_icon = os.path.join(RESSOURCEN_ORDNER, "gold-silber-icon.png")
    ico_icon = os.path.join(RESSOURCEN_ORDNER, "gold-silber-icon.ico")
    try:
        if sys.platform == "win32" and os.path.isfile(ico_icon):
            fenster.iconbitmap(ico_icon)
        elif os.path.isfile(png_icon):
            icon = tk.PhotoImage(file=png_icon)
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

    ttk.Label(formular, text=_("Währung:")).grid(
        row=1, column=0, sticky="w", padx=5, pady=9
    )
    waehrung_auswahl = ttk.Combobox(
        formular,
        values=[f"{code} — {name}" for code, (name, _) in waehrungen().items()],
        state="readonly",
        width=25,
    )
    waehrung_auswahl.current(0)
    waehrung_auswahl.grid(row=1, column=1, sticky="ew", padx=5, pady=9)
    waehrung_auswahl.bind("<<ComboboxSelected>>", waehrung_geaendert)

    preis_label_variable = tk.StringVar()
    ttk.Label(formular, textvariable=preis_label_variable).grid(
        row=2, column=0, sticky="w", padx=5, pady=9
    )
    unzenpreis_variable = tk.StringVar()
    unzenpreis_eingabe = ttk.Entry(
        formular, textvariable=unzenpreis_variable, width=28
    )
    unzenpreis_eingabe.grid(
        row=2, column=1, sticky="ew", padx=5, pady=9
    )

    kursstand_variable = tk.StringVar(value="")
    ttk.Label(
        formular,
        textvariable=kursstand_variable,
        anchor="center",
        justify="center",
        wraplength=475,
    ).grid(
        row=3, column=0, columnspan=2,
        sticky="ew", padx=5, pady=(0, 5),
    )

    ttk.Label(formular, text=_("Gewicht des Gegenstands in g:")).grid(
        row=4, column=0, sticky="w", padx=5, pady=9
    )
    gewicht_variable = tk.StringVar()
    gewichtsfeld = ttk.Frame(formular)
    gewichtsfeld.grid(
        row=4, column=1, sticky="ew", padx=5, pady=9
    )
    gewicht_eingabe = ttk.Entry(
        gewichtsfeld, textvariable=gewicht_variable, width=28 if sprache == "de" else 10
    )
    gewicht_eingabe.pack(side="left", fill="x", expand=True)
    if sprache != "de":
        gewichtseinheit_auswahl = ttk.Combobox(
            gewichtsfeld,
            values=list(gewichtseinheiten()),
            state="readonly",
            width=24,
        )
        gewichtseinheit_auswahl.current(0)
        gewichtseinheit_auswahl.pack(side="right", padx=(6, 0))
        gewichtseinheit_auswahl.bind("<<ComboboxSelected>>", ergebnis_verwerfen)

    ttk.Label(formular, text=_("Feinheit:")).grid(
        row=5, column=0, sticky="w", padx=5, pady=9
    )
    feinheit_variable = tk.StringVar()
    ergebnis_variable = tk.StringVar()
    feinheit_auswahl = ttk.Combobox(
        formular,
        state="readonly",
        width=25,
    )
    feinheit_auswahl.grid(
        row=5, column=1, sticky="ew", padx=5, pady=9
    )
    feinheit_auswahl.bind("<<ComboboxSelected>>", feinheit_geaendert)

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
        "write", preis_manuell_geaendert
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
    fenster.after(
        100 + random.randint(0, WECHSELKURS_STARTSTREUUNG_MS),
        wechselkurse_abrufen,
    )
    fenster.protocol("WM_DELETE_WINDOW", schliessen)
    fenster.after(50, kursantworten_verarbeiten)
    fenster.after_idle(startbenachrichtigung_beenden)
    fenster.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", choices=("de", "es", "en"), help="Deutsch / Español / English (US)")
    sprache = parser.parse_args().lang or systemsprache()
    main()
