# -*- coding: utf-8 -*-
"""Trasforma il testo copiato negli appunti in un copione del Gobbo.

Uso: copi il testo (da ChatGPT, da Word, da dove vuoi) con Ctrl+C,
poi doppio clic su NUOVO COPIONE.bat. Ti chiede il titolo e basta.

Non serve GitHub: il copione compare subito sul telefono ricaricando la pagina.
"""

from __future__ import annotations

import re
import subprocess
import sys
import unicodedata
from datetime import date
from pathlib import Path

for flusso in (sys.stdout, sys.stderr):
    try:
        flusso.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
from pubblica import conta_parole, costruisci_indice, scrivi_indice  # noqa: E402

FORMATI = ["polarizzante", "reazione", "yapping", "reel", ""]


def dagli_appunti() -> str:
    """Legge gli appunti di Windows senza librerie esterne.

    PowerShell scrive nella codifica della console, non in UTF-8: senza imporgliela
    le lettere accentate tornano storpiate («Perché» diventa «PerchÃ©»).
    """
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "[Console]::OutputEncoding=[Text.Encoding]::UTF8; Get-Clipboard -Raw"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return (r.stdout or "").replace("\r\n", "\n").strip()


def ripulisci(testo: str) -> str:
    """Toglie le scorie tipiche di un copia-incolla da ChatGPT."""
    righe = []
    for riga in testo.split("\n"):
        r = riga.rstrip()
        r = re.sub(r"^\s*#{1,6}\s*", "", r)          # titoli markdown
        r = re.sub(r"^\s*[-*•]\s+", "", r)           # elenchi puntati
        r = re.sub(r"^\s*\d+[.)]\s+", "", r)         # elenchi numerati
        r = r.replace("**", "**")                    # il grassetto lo teniamo
        righe.append(r)
    fuori = "\n".join(righe)
    fuori = re.sub(r"\n{3,}", "\n\n", fuori)         # righe vuote di troppo
    return fuori.strip()


def sigla(titolo: str) -> str:
    t = unicodedata.normalize("NFKD", titolo.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return (t or "copione")[:50]


def chiedi(domanda: str, predefinito: str = "") -> str:
    try:
        r = input(domanda).strip()
    except EOFError:
        r = ""
    return r or predefinito


def main() -> int:
    print("Nuovo copione per il Gobbo\n")

    testo = dagli_appunti()
    if not testo:
        print("Gli appunti sono vuoti.")
        print("Vai dove hai il testo (ChatGPT, Word, una mail), selezionalo tutto,")
        print("premi Ctrl+C, e poi rilancia questo programma.")
        return 1

    testo = ripulisci(testo)
    parole = conta_parole(testo)
    anteprima = " ".join(testo.split())[:90]
    print(f"Ho trovato negli appunti {parole} parole, circa {round(parole/140*60)} secondi di parlato.")
    print(f"Comincia con: «{anteprima}…»\n")

    if parole < 15:
        print("Sono pochissime parole: forse hai copiato solo un pezzo.")
        if chiedi("Vado avanti lo stesso? [s/N] ").lower() not in ("s", "si", "sì"):
            print("Non ho creato niente.")
            return 1

    # Il titolo si propone dalla prima riga, ma ripulita: gli asterischi del
    # grassetto e la punteggiatura di coda finivano dentro al titolo.
    prima = next((r.strip() for r in testo.split("\n") if r.strip()), "copione")
    prima = re.sub(r"[*_`]+", "", prima).strip(" .:;,–—-")
    if len(prima) > 60:
        taglio = prima[:60].rsplit(" ", 1)[0]
        prima = taglio or prima[:60]
    titolo = chiedi(f"Titolo [{prima}]: ", prima)

    print("\nFormato: 1 polarizzante · 2 reazione · 3 yapping · 4 reel · Invio per nessuno")
    scelta = chiedi("Numero: ", "5")
    formato = FORMATI[int(scelta) - 1] if scelta.isdigit() and 1 <= int(scelta) <= 5 else ""

    nome = f"{date.today().isoformat()}-{sigla(titolo)}.md"
    percorso = BASE / "scripts" / nome
    if percorso.exists():
        if chiedi(f"\n{nome} esiste già. Lo sovrascrivo? [s/N] ").lower() not in ("s", "si", "sì"):
            print("Non ho toccato niente.")
            return 1

    testa = f"---\ntitolo: {titolo}\n"
    if formato:
        testa += f"formato: {formato}\n"
    testa += "---\n\n"
    percorso.write_text(testa + testo + "\n", encoding="utf-8", newline="\n")

    scrivi_indice(costruisci_indice())

    print(f"\nCreato: scripts\\{nome}")
    print(f"Titolo: {titolo}" + (f"  [{formato}]" if formato else ""))
    print(f"Durata: {parole} parole, circa {round(parole/140*60)} secondi a 140 parole al minuto")
    print("\nAdesso sul telefono: ricarica la pagina del Gobbo e il copione è nell'elenco.")
    print("(In Safari: tira giù la pagina con il dito, oppure tocca «Aggiorna copioni».)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as errore:
        print(f"\nErrore: {errore}")
        sys.exit(1)
