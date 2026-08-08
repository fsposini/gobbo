# -*- coding: utf-8 -*-
"""Gobbo — pubblicazione in un passo solo.

Fa tutto quello che serve perché i copioni scritti sul PC compaiano sul telefono:

  1. legge i file .md in scripts\\  e ne ricava titolo, formato, parole, incipit
  2. riscrive scripts\\index.json (l'elenco che l'app legge)
  3. se sono cambiati index.html o sw.js, alza la versione in tutti e due
     (i due numeri devono coincidere, altrimenti il telefono resta sulla vecchia copia)
  4. commit e push su GitHub

Si lancia con PUBBLICA.bat, oppure:
    python pubblica.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

# La console di Windows parte in cp1252 e si strozza sulle frecce e sugli accenti.
for flusso in (sys.stdout, sys.stderr):
    try:
        flusso.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

BASE = Path(__file__).resolve().parent
CARTELLA_SCRIPT = BASE / "scripts"
INDICE = CARTELLA_SCRIPT / "index.json"
INDEX_HTML = BASE / "index.html"
SW_JS = BASE / "sw.js"

# file che, se cambiano, obbligano ad alzare la versione della cache
GUSCIO = {"index.html", "sw.js", "manifest.webmanifest"}


# --------------------------------------------------------------------------
# utilità
# --------------------------------------------------------------------------
def git(*args: str, controlla: bool = True) -> str:
    r = subprocess.run(
        ["git", *args], cwd=BASE, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if controlla and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} → {r.returncode}\n{r.stderr.strip()}")
    return (r.stdout or "").strip()


def separa_frontmatter(testo: str) -> tuple[dict, str]:
    testo = testo.lstrip("﻿")
    m = re.match(r"^---\r?\n(.*?)\r?\n---[ \t]*\r?\n?", testo, re.S)
    if not m:
        return {}, testo
    meta = {}
    for riga in m.group(1).splitlines():
        c = re.match(r"^([A-Za-zÀ-ÿ_][\w-]*)\s*:\s*(.*)$", riga)
        if c:
            meta[c.group(1).lower()] = c.group(2).strip().strip("\"'")
    return meta, testo[m.end():]


def blocchi_parlati(corpo: str) -> list[str]:
    """Solo i blocchi da leggere ad alta voce: fuori note di regia e stacchi."""
    fuori = []
    for b in re.split(r"\r?\n\s*\r?\n", corpo):
        b = b.strip()
        if not b or b.startswith(">") or b.startswith("#") or re.fullmatch(r"-{3,}", b):
            continue
        fuori.append(b)
    return fuori


def conta_parole(corpo: str) -> int:
    testo = " ".join(blocchi_parlati(corpo)).replace("**", "")
    return len(re.findall(r"[^\W_]+(?:['’-][^\W_]+)*", testo, re.UNICODE))


def incipit(corpo: str, n: int = 130) -> str:
    b = blocchi_parlati(corpo)
    if not b:
        return ""
    t = re.sub(r"\s+", " ", b[0].replace("**", "")).strip()
    return t[:n].rstrip() + "…" if len(t) > n else t


def titolo_da_nome(p: Path) -> str:
    nome = re.sub(r"^\d{4}-\d{2}-\d{2}[-_]", "", p.stem)
    return nome.replace("-", " ").replace("_", " ").strip().capitalize()


def data_da_nome(p: Path) -> str:
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", p.stem)
    return f"{m.group(3)}/{m.group(2)}" if m else ""


# --------------------------------------------------------------------------
# 1-2. indice dei copioni
# --------------------------------------------------------------------------
def controlla_nojekyll() -> None:
    """Senza questo file GitHub Pages passa tutto per Jekyll, che trasforma i
    copioni da .md a .html e li rende irraggiungibili per l'app."""
    f = BASE / ".nojekyll"
    if not f.exists():
        f.write_text("Pubblica i file così come sono: niente Jekyll.\n", encoding="utf-8", newline="\n")
        print("  [!] Mancava .nojekyll, l'ho rimesso: senza, i copioni non si aprono.")


def costruisci_indice() -> list[dict]:
    CARTELLA_SCRIPT.mkdir(exist_ok=True)
    voci = []
    for f in sorted(CARTELLA_SCRIPT.glob("*.md")):
        testo = f.read_text(encoding="utf-8")
        meta, corpo = separa_frontmatter(testo)
        parole = conta_parole(corpo)
        if parole == 0:
            print(f"  [!] {f.name}: nessun testo da leggere, lo salto")
            continue
        voci.append({
            "file": f.name,
            "titolo": meta.get("titolo") or titolo_da_nome(f),
            "formato": meta.get("formato", ""),
            "data": meta.get("data") or data_da_nome(f),
            "parole": parole,
            "incipit": incipit(corpo),
        })
    # i più recenti in cima (il nome inizia con la data)
    voci.sort(key=lambda v: v["file"], reverse=True)
    return voci


def scrivi_indice(voci: list[dict]) -> None:
    dati = {"aggiornato": date.today().isoformat(), "script": voci}
    INDICE.write_text(
        json.dumps(dati, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n"
    )


# --------------------------------------------------------------------------
# 3. versione
# --------------------------------------------------------------------------
def versione_attuale() -> int:
    m = re.search(r'const VERSIONE = "v(\d+)"', INDEX_HTML.read_text(encoding="utf-8"))
    if not m:
        raise RuntimeError("Non trovo 'const VERSIONE' in index.html")
    return int(m.group(1))


def alza_versione(nuova: int) -> None:
    h = INDEX_HTML.read_text(encoding="utf-8")
    h = re.sub(r'const VERSIONE = "v\d+"', f'const VERSIONE = "v{nuova}"', h, count=1)
    INDEX_HTML.write_text(h, encoding="utf-8", newline="\n")

    s = SW_JS.read_text(encoding="utf-8")
    s = re.sub(r'const CACHE = "gobbo-v\d+"', f'const CACHE = "gobbo-v{nuova}"', s, count=1)
    SW_JS.write_text(s, encoding="utf-8", newline="\n")


def guscio_modificato() -> bool:
    stato = git("status", "--porcelain")
    for riga in stato.splitlines():
        nome = riga[3:].strip().strip('"')
        if nome.split("/")[-1] in GUSCIO:
            return True
    return False


# --------------------------------------------------------------------------
# 4. git
# --------------------------------------------------------------------------
NOME_REPO = "gobbo"

# Non serve né 'gh' né alcun login: si riusa la credenziale GitHub che il Gestore
# credenziali di Windows tiene già per 'git push'. Il token non viene mai stampato.
def credenziale_github() -> tuple[str, str] | None:
    r = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        cwd=BASE, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    campi = dict(l.split("=", 1) for l in (r.stdout or "").splitlines() if "=" in l)
    token = campi.get("password", "")
    return (campi.get("username", ""), token) if token else None


def api(metodo: str, percorso: str, token: str, corpo: dict | None = None) -> tuple[int, dict]:
    dati = json.dumps(corpo).encode("utf-8") if corpo is not None else None
    req = urllib.request.Request(
        "https://api.github.com" + percorso, data=dati, method=metodo,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "gobbo-pubblica",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            testo = r.read().decode("utf-8", "replace")
            return r.status, (json.loads(testo) if testo.strip() else {})
    except urllib.error.HTTPError as e:
        testo = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(testo)
        except json.JSONDecodeError:
            return e.code, {"message": testo[:200]}
    except Exception as e:
        return 0, {"message": str(e)}


def spiega_accesso_scaduto() -> None:
    print("\n  L'accesso a GitHub salvato su questo PC non è più valido.")
    print("  Si rimette a posto con un doppio clic, in questa stessa cartella:")
    print("      RINNOVA ACCESSO GITHUB.bat")
    print("  Ti apre GitHub nel browser, accedi, e poi rilanci PUBBLICA.bat.")


def accesso_github() -> tuple[str, str] | None:
    c = credenziale_github()
    if not c:
        spiega_accesso_scaduto()
        return None
    utente, token = c
    stato, dati = api("GET", "/user", token)
    if stato != 200:
        spiega_accesso_scaduto()
        return None
    return dati.get("login") or utente, token


def crea_repo(utente: str, token: str) -> bool:
    """Prima configurazione: repo su GitHub, primo push, GitHub Pages acceso."""
    print("\n  Questa cartella non è ancora collegata a GitHub.")
    print(f"  Posso creare adesso il repository PUBBLICO '{NOME_REPO}' sull'account {utente}")
    print("  e accendere GitHub Pages, così l'app diventa raggiungibile dal telefono.")
    print("  Pubblico vuol dire che comparirà nell'elenco dei tuoi repository su GitHub.")
    try:
        risposta = input("\n  Procedo? [s/N] ").strip().lower()
    except EOFError:  # lanciato senza una finestra interattiva
        risposta = ""
    if risposta not in ("s", "si", "sì"):
        print("  Non ho creato niente. L'indice dei copioni resta aggiornato sul PC.")
        print("  Per creare il repository lancia PUBBLICA.bat con un doppio clic e rispondi 's'.")
        return False

    print("\n  Creo il repository…")
    stato, dati = api("POST", "/user/repos", token, {
        "name": NOME_REPO,
        "private": False,
        "description": "Gobbo — copioni scorrevoli per girare i reel",
        "has_issues": False,
        "has_wiki": False,
    })
    if stato == 201:
        print(f"  Creato: github.com/{utente}/{NOME_REPO}")
    elif stato == 422:
        print("  Esisteva già, lo riuso.")
    else:
        print(f"  Non riuscito (codice {stato}): {dati.get('message', '')}")
        return False

    if not (BASE / ".git").exists():
        git("init")
        git("branch", "-M", "main")
    git("add", "-A")
    if git("status", "--porcelain"):
        git("commit", "-m", "Gobbo — prima versione")
    if not git("remote", controlla=False):
        git("remote", "add", "origin", f"https://github.com/{utente}/{NOME_REPO}.git")

    print("  Invio i file…")
    try:
        git("push", "-u", "origin", "main")
    except RuntimeError as e:
        print(f"  Push non riuscito:\n  {e}")
        return False

    print("  Accendo GitHub Pages…")
    stato, dati = api("POST", f"/repos/{utente}/{NOME_REPO}/pages", token,
                      {"source": {"branch": "main", "path": "/"}})
    if stato not in (201, 204, 409):
        print("  Pages non si è acceso da solo. Fallo a mano, una volta sola:")
        print(f"     https://github.com/{utente}/{NOME_REPO}/settings/pages")
        print("     Source: Deploy from a branch → main → / (root) → Save")
    return True


def repo_pronto() -> bool:
    accesso = accesso_github()
    if not accesso:
        return False
    if not (BASE / ".git").exists() or not git("remote", controlla=False):
        return crea_repo(*accesso)
    return True


def scarica(indirizzo: str) -> tuple[int, str]:
    try:
        req = urllib.request.Request(indirizzo + "?t=" + str(int(time.time())),
                                     headers={"User-Agent": "gobbo-pubblica"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return 0, ""


def pubblicazione_fallita(utente: str, token: str) -> bool:
    """Guarda se l'ultima pubblicazione di GitHub è andata in errore."""
    stato, dati = api("GET", f"/repos/{utente}/{NOME_REPO}/actions/runs?per_page=1", token)
    corse = (dati or {}).get("workflow_runs") or []
    return bool(corse) and corse[0].get("status") == "completed" \
        and corse[0].get("conclusion") == "failure"


def verifica_online(utente: str, token: str, versione: str) -> bool:
    """Aspetta che il sito serva davvero la versione appena inviata.

    Serve perché GitHub a volte costruisce il pacchetto e poi non riesce a
    metterlo online ('Timeout reached, aborting!'): senza questo controllo il
    programma direbbe «fatto» e sul telefono resterebbe la versione vecchia.
    """
    sito = f"https://{utente}.github.io/{NOME_REPO}"
    print(f"\nControllo che il sito serva davvero la {versione}…")
    riprovato = False
    for giro in range(42):                                   # circa 7 minuti
        codice, testo = scarica(sito + "/index.html")
        if codice == 200 and f'const VERSIONE = "{versione}"' in testo:
            print(f"  Confermato: online c'è la {versione}.")
            return True
        if not riprovato and pubblicazione_fallita(utente, token):
            print("  GitHub ha fallito la pubblicazione. La rilancio una volta…")
            api("POST", f"/repos/{utente}/{NOME_REPO}/pages/builds", token, {})
            riprovato = True
        if giro == 6:
            print("  (ci sta mettendo più del solito, continuo ad aspettare)")
        time.sleep(10)

    print(f"  Il sito non serve ancora la {versione}.")
    print("  I tuoi file sono al sicuro su GitHub: è la pubblicazione loro a essere lenta.")
    print("  Rilancia PUBBLICA.bat fra qualche minuto e ricontrolla, oppure guarda qui:")
    print(f"     https://github.com/{utente}/{NOME_REPO}/actions")
    return False


def main() -> int:
    print("Gobbo — pubblicazione\n")

    controlla_nojekyll()
    print("Copioni in scripts\\:")
    voci = costruisci_indice()
    if not voci:
        print("  nessuno. Metti un file .md in scripts\\ e rilancia.")
    for v in voci:
        secondi = round(v["parole"] / 140 * 60)
        etichetta = f"[{v['formato']}] " if v["formato"] else ""
        print(f"  · {etichetta}{v['titolo']} — {v['parole']} parole, ~{secondi}s a 140 ppm")
    scrivi_indice(voci)
    print(f"\nScritto {INDICE.relative_to(BASE)}")

    accesso = accesso_github()
    if not accesso:
        print("\nL'indice è aggiornato sul PC, ma non è stato pubblicato online.")
        return 1
    utente, token = accesso
    if (not (BASE / ".git").exists() or not git("remote", controlla=False)) and not crea_repo(utente, token):
        print("\nL'indice è aggiornato sul PC, ma non è stato pubblicato online.")
        return 1

    if guscio_modificato():
        nuova = versione_attuale() + 1
        alza_versione(nuova)
        print(f"App modificata → versione alzata a v{nuova} (index.html e sw.js allineati)")
    else:
        print(f"App invariata → resto alla v{versione_attuale()}")

    if git("status", "--porcelain"):
        git("add", "-A")
        git("commit", "-m", f"Copioni aggiornati — {len(voci)} in elenco")
        print("\nInvio a GitHub…")
        try:
            git("push")
        except RuntimeError as e:
            print(f"\n  Push non riuscito:\n  {e}")
            print("  Il commit è salvato in locale. Sistema l'accesso a GitHub e rilancia.")
            return 1
        print("Fatto.")
    else:
        print("\nNiente di nuovo da inviare: è già tutto online.")

    versione = f"v{versione_attuale()}"
    online = verifica_online(utente, token, versione)

    print(f"\nIndirizzo dell'app:  https://{utente}.github.io/{NOME_REPO}/")
    if online:
        print(f"Sul telefono: tira giù la pagina per ricaricarla. In alto a destra")
        print(f"deve comparire «{versione}». Poi tocca «Aggiorna copioni».")
    return 0 if online else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as errore:  # messaggio leggibile invece di un traceback
        print(f"\nErrore: {errore}")
        sys.exit(1)
