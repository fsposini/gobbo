# -*- coding: utf-8 -*-
"""Rinnova l'accesso a GitHub salvato su questo PC.

Serve solo se PUBBLICA.bat dice che l'accesso non è più valido.
Se l'accesso funziona già, questo programma non tocca niente e te lo dice.

Il token non viene mai mostrato a schermo.
"""

from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request

for flusso in (sys.stdout, sys.stderr):
    try:
        flusso.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

RICHIESTA = "protocol=https\nhost=github.com\n\n"


def credenziale(azione: str, dati: str = RICHIESTA) -> dict:
    r = subprocess.run(
        ["git", "credential", azione], input=dati,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return dict(l.split("=", 1) for l in (r.stdout or "").splitlines() if "=" in l)


def verifica(token: str) -> str | None:
    """Restituisce il nome dell'account se il token è buono, altrimenti None."""
    if not token:
        return None
    req = urllib.request.Request(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "gobbo-rinnova"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r).get("login")
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        return None


def main() -> int:
    print("Accesso a GitHub — controllo\n")

    attuale = credenziale("fill")
    account = verifica(attuale.get("password", ""))
    if account:
        print(f"L'accesso funziona già: sei collegato come «{account}».")
        print("Non c'è niente da rinnovare. Puoi chiudere questa finestra")
        print("e lanciare PUBBLICA.bat.")
        return 0

    print("L'accesso non è più valido. Lo rinnovo adesso.")
    print("Fra un istante si apre una finestra di GitHub nel browser:")
    print("accedi come al solito e autorizza. Poi torna qui.\n")
    try:
        input("Premi Invio per cominciare… ")
    except EOFError:
        print("(nessuna finestra interattiva: lancia RINNOVA ACCESSO GITHUB.bat con un doppio clic)")
        return 1

    credenziale("reject")
    nuova = credenziale("fill")
    token = nuova.get("password", "")
    account = verifica(token)
    if not account:
        print("\nNon ha funzionato: l'accesso è ancora non valido.")
        print("Riprova, e se insiste dimmelo — non è un problema tuo.")
        return 1

    # 'approve' è il passo che lo salva davvero nel Gestore credenziali di Windows
    credenziale("approve", "".join(f"{k}={v}\n" for k, v in nuova.items()) + "\n")
    print(f"\nFatto: sei collegato come «{account}».")
    print("Ora puoi lanciare PUBBLICA.bat.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as errore:
        print(f"\nErrore: {errore}")
        sys.exit(1)
