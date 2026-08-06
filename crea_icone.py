# -*- coding: utf-8 -*-
"""Genera le icone della PWA Gobbo nella palette brand.

Si lancia una volta sola (o quando cambia il disegno):
    python crea_icone.py
"""

from pathlib import Path
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent

BLU = (27, 84, 155)       # #1B549B
RAME = (159, 122, 108)    # #9F7A6C
BIANCO = (255, 255, 255)


def disegna(lato: int, margine: float) -> Image.Image:
    """Righe di testo stilizzate, quella 'in lettura' in rame."""
    s = 8  # supersampling per bordi puliti
    img = Image.new("RGBA", (lato * s, lato * s), BLU + (255,))
    d = ImageDraw.Draw(img)
    L = lato * s

    m = L * margine
    utile = L - 2 * m
    righe = [0.92, 0.74, 1.00, 0.62, 0.85, 0.48]  # larghezze relative
    evidenziata = 2

    altezza = utile / (len(righe) * 2 - 1)
    raggio = altezza / 2

    for i, larghezza in enumerate(righe):
        y = m + i * altezza * 2
        x1 = m
        x2 = m + utile * larghezza
        colore = RAME + (255,) if i == evidenziata else BIANCO + (235,)
        d.rounded_rectangle([x1, y, x2, y + altezza], radius=raggio, fill=colore)

    return img.resize((lato, lato), Image.LANCZOS)


def con_angoli(img: Image.Image, raggio_rel: float) -> Image.Image:
    lato = img.width
    maschera = Image.new("L", (lato * 4, lato * 4), 0)
    ImageDraw.Draw(maschera).rounded_rectangle(
        [0, 0, lato * 4 - 1, lato * 4 - 1], radius=int(lato * 4 * raggio_rel), fill=255
    )
    maschera = maschera.resize((lato, lato), Image.LANCZOS)
    fuori = Image.new("RGBA", (lato, lato), (0, 0, 0, 0))
    fuori.paste(img, (0, 0), maschera)
    return fuori


def main() -> None:
    # icone "any": angoli arrotondati, disegno pieno
    for lato in (192, 512):
        con_angoli(disegna(lato, 0.20), 0.22).save(BASE / f"icon-{lato}.png")

    # maskable: quadrata piena, disegno più stretto (Android ritaglia i bordi)
    disegna(512, 0.30).convert("RGB").save(BASE / "icon-512-maskable.png")

    # apple touch icon: quadrata, iOS arrotonda da sé
    disegna(180, 0.20).convert("RGB").save(BASE / "apple-touch-icon.png")

    print("Icone create:")
    for n in ("icon-192.png", "icon-512.png", "icon-512-maskable.png", "apple-touch-icon.png"):
        p = BASE / n
        print(f"  {n}  ({p.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
