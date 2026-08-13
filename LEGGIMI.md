# Gobbo — copioni scorrevoli per i reel

App web (PWA) che mostra sul telefono il testo di un reel mentre ti riprendi con la
fotocamera frontale. I copioni si scrivono sul PC, si pubblicano con un doppio clic
e compaiono sul telefono.

**Indirizzo dell'app:** https://fsposini.github.io/gobbo/

Va aperto in **Safari** (non Firefox: solo Safari installa le app sulla schermata Home
e concede la fotocamera senza storie). Il codice QR per aprirlo dal telefono è il file
`APRI SUL TELEFONO.png` in questa cartella: doppio clic e inquadralo.

---

## Come si usa, in due passi

**Sul PC** — copia il testo del copione con Ctrl+C e lancia `NUOVO COPIONE.bat` (o la
scheda «Nuovo copione per i reel» in Home Studio). In alternativa metti a mano un file
`.md` in `scripts\` e lancia `PUBBLICA.bat`.

`PUBBLICA.bat` non si limita a inviare: **controlla che il sito sia davvero aggiornato**
e, se GitHub fallisce la pubblicazione, la rilancia da solo. Finisce solo quando l'indirizzo
online serve la stessa versione che hai sul PC — così «fatto» vuol dire davvero fatto.

**Sul telefono** — apri l'app, tocca «Aggiorna copioni», scegli il copione, premi il
pulsante rosso. Parte un conto alla rovescia di tre secondi, poi il testo scorre e la
registrazione parte insieme.

Alla fine tocca «Salva nel rullino»: iOS apre il pannello di condivisione, scegli
*Salva video* e il file finisce in Foto, pronto per Instagram.

### La prima volta

Nessun login da fare. `PUBBLICA.bat` riusa l'accesso a GitHub che il Gestore credenziali
di Windows tiene già per pubblicare il Respiro Pacer.

Al primo avvio si ferma e chiede il permesso di creare il repository pubblico `gobbo`:
rispondi `s` e Invio. Crea il repository, invia i file, accende GitHub Pages e stampa
l'indirizzo. Quello va aperto in **Safari** sul telefono.

Se un giorno dicesse che l'accesso non è più valido: doppio clic su
`RINNOVA ACCESSO GITHUB.bat`, nella stessa cartella. Ti apre GitHub nel browser, accedi,
e torni a lanciare `PUBBLICA.bat`. Se l'accesso invece funziona già, quel programma te lo
dice e non tocca niente: puoi lanciarlo senza rischi anche solo per controllare.

---

## Come si scrive un copione

Un file di testo normale, con estensione `.md`, dentro `scripts\`.
Nome consigliato: `AAAA-MM-GG-argomento.md` — la data all'inizio serve a tenere i più
recenti in cima all'elenco.

```markdown
---
titolo: Il tuo smartwatch non misura lo stress
formato: polarizzante
---

> Sorriso, poi parti. Inquadratura stretta.

Il tuo orologio ti dice che oggi sei stressato.

Quel numero non misura lo stress. Misura la variabilità fra un battito e l'altro.

---

Sono due cose diverse, e la differenza conta.

Il dato da solo non decide niente. **Decide il contesto.**
```

Cosa fa ogni pezzo:

| Nel file | Sullo schermo |
|---|---|
| `titolo:` e `formato:` in cima, fra le due righe di trattini | Titolo e etichetta nell'elenco. Se manca il titolo lo ricava dal nome del file |
| Riga vuota fra un blocco e l'altro | Separa i paragrafi |
| `> testo` | **Nota di regia**: appare piccola e in rame, non si legge ad alta voce |
| `---` da solo su una riga | Riga tratteggiata: uno stacco, il punto dove prendere fiato |
| `**parola**` | Parola in evidenza, colore rame |
| `# titolo` | Come una nota di regia: etichetta di sezione, non si legge |

Le note di regia e gli stacchi **non vengono contati** nella stima della durata: il conteggio
parole considera solo quello che dirai davvero.

### Chiedere il copione a Claude Code o a ChatGPT

> Scrivimi un copione per un reel da 50 secondi sul tema *[argomento]*, formato
> *polarizzante*, nel formato Gobbo: frontmatter con `titolo` e `formato`, paragrafi corti
> separati da riga vuota, note di regia con `>`, stacchi con `---`, parole chiave con `**`.
> Circa 115 parole, che a 140 parole al minuto fanno 50 secondi.

Il file va salvato in `C:\Users\Federico\Code\gobbo-app\scripts\`.
Con Claude Code basta chiederglielo: conosce già la cartella e il formato.

---

## Far combaciare la velocità con la tua voce

Due cose lavorano insieme. La prima si fa una volta, la seconda da sola.

### Tarare il ritmo (una volta, all'inizio)

In alto a sinistra, accanto alla ✕, c'è **«Tara il ritmo»**. Toccalo: parte un conto alla
rovescia di tre secondi, poi il testo scorre e tu **leggi il copione ad alta voce al tuo
passo naturale**, senza rincorrerlo. Non sta registrando niente: è una prova.

Quando arrivi all'ultima parola tocca **«Fine, ho letto tutto»**. L'app divide le parole
per il tempo che ci hai messo e ti dice il tuo ritmo reale — *«hai letto 118 parole in 54
secondi: il tuo ritmo è 131 parole al minuto»* — e te lo propone. Accetti e da lì in poi il
testo scorre alla tua velocità, non a una velocità inventata.

Il passo di lettura di una persona è abbastanza costante: lo misuri una volta e vale per
tutti i copioni. Se la prima prova viene storta perché il testo scorreva troppo diverso dal
tuo passo, rifalla: la seconda è già allineata.

### La pausa quando smetti di parlare (automatica)

Se ti fermi — cerchi la frase, ti inceppi, prendi fiato — dopo un paio di secondi il testo
si ferma e in alto compare **«non ti sento»**. Appena riprendi a parlare riparte da solo.

Serve a non farti scappare via il copione mentre pensi. **La registrazione non si ferma
mai**: il video continua, si ferma solo il testo, così tagli dopo con calma.

L'app misura soltanto il volume del microfono che sta già usando per registrare: non
riconosce le parole, non chiede permessi in più e non manda niente fuori dal telefono.

Se per qualche motivo il microfono non capisce e il testo resta bloccato più di otto
secondi, l'ascolto **si spegne da solo** e il testo riparte: la pillola diventa «ascolto
spento». È una rete di sicurezza perché una ripresa non si rovini. Puoi disattivare del
tutto la funzione dalle impostazioni.

---

## Le impostazioni

- **Velocità** — parole al minuto. 140 è un parlato naturale, ma conviene lasciarla
  decidere alla taratura qui sopra. Si cambia anche mentre giri, con `−` e `+`.
- **Dimensione** — corpo del testo. Non cambia la durata: la velocità di scorrimento si
  adegua da sola per mantenere le parole al minuto impostate. A 34 px vedi quattro o cinque
  parole per riga, la misura in cui l'occhio legge senza spostarsi e lo sguardo resta verso
  l'obiettivo. Va bene col telefono a mezzo metro; a un metro sali verso 55.
- **Pausa quando smetti di parlare** — spiegata sopra. Si può spegnere.
- **Altezza lettura** — dove sta la riga che stai leggendo, segnata dalle due frecce.
  Più in alto è, più il tuo sguardo resta vicino all'obiettivo. Sull'iPhone 14 Pro
  l'obiettivo è dentro la Dynamic Island, in cima allo schermo.
- **Specchia anteprima** — ti vedi come allo specchio. Non tocca il video registrato,
  che esce sempre nel verso giusto.
- **Modalità solo testo** — spegne fotocamera e registrazione. Serve quando giri col
  telefono principale e usi questo dispositivo come secondo schermo.

---

## Muoversi nel testo

Tre modi, dal più comodo al più preciso.

**Trascinare col dito.** Appoggia il dito in mezzo allo schermo e tira: verso l'alto
il testo va avanti, verso il basso torna indietro, come una pagina vera. Mentre
trascini lo scorrimento automatico si mette da parte e ti lascia comandare; appena
stacchi il dito riprende da dove l'hai lasciato. Funziona anche mentre stai registrando:
se sbagli una frase torni sopra di due righe e la ridici, il video continua e tagli dopo.

**I quattro tasti in basso** — `« 10″`, `‹ 5″`, `5″ ›`, `10″ »` — spostano il testo di
cinque o dieci secondi di parlato. Non sono secondi di video: sono secondi *al tuo ritmo*,
cioè quanto testo ti passa davanti in quel tempo. Se cambi la velocità cambia anche
l'ampiezza del salto, ed è giusto così.

**Un tocco secco** in mezzo allo schermo mette in pausa e riprende, come prima.
Un tocco è un tocco solo se il dito non si sposta: se scivola diventa un trascinamento
e lo scorrimento non si ferma.

Il tasto `↺` riporta il testo all'inizio.

---

## Installare l'app sul telefono

1. Apri l'indirizzo in **Safari** (non Chrome: solo Safari installa le PWA su iOS)
2. Tocca il pulsante Condividi, poi **Aggiungi a Home**
3. Aprila dall'icona blu sulla schermata Home

Alla prima registrazione iOS chiede il permesso per fotocamera e microfono: vanno
concessi entrambi. Se li neghi per sbaglio si riabilitano in
*Impostazioni → Safari → Fotocamera / Microfono*.

Lo schermo resta acceso mentre il gobbo è aperto.

---

## Qualità del video

L'app chiede 1080×1920 a 30 fps in H.264 — la risoluzione nativa dei Reel. Quello che
la fotocamera concede davvero è scritto in alto a destra durante la ripresa: quel numero
è misurato, non stimato.

Rispetto all'app Fotocamera di iOS manca l'elaborazione dell'immagine (Smart HDR,
stabilizzazione piena). In buona luce la differenza si nota poco, in penombra si nota.
Se non convince: attiva «Modalità solo testo», usa questo telefono come gobbo e gira
con un secondo dispositivo.

---

## I file del progetto

| File | A cosa serve |
|---|---|
| `index.html` | Tutta l'app: elenco, impostazioni, gobbo, registrazione |
| `sw.js` | Fa funzionare l'app anche senza rete |
| `manifest.webmanifest` | Nome e icone quando la installi sulla Home |
| `scripts\*.md` | I copioni |
| `scripts\index.json` | L'elenco che legge l'app — **generato, non si scrive a mano** |
| `PUBBLICA.bat` | Il passo unico: aggiorna l'elenco, alza la versione, invia a GitHub |
| `pubblica.py` | Il programma dietro al .bat |
| `crea_icone.py` | Rigenera le icone, solo se cambia il disegno |

### Nota tecnica sul rilascio

Il numero di versione compare in due punti — `const VERSIONE` in `index.html` e
`const CACHE` in `sw.js` — e i due **devono coincidere**, altrimenti il telefono continua
a mostrare la copia vecchia. `pubblica.py` li allinea da solo quando vede che l'app è
cambiata: non vanno toccati a mano.
