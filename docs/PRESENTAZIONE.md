# PRESENTAZIONE - PyScopone

## 1. Titolo e contesto

PyScopone e un progetto software in Python che realizza il gioco tradizionale dello Scopone.
Il progetto nasce con due obiettivi: didattico (architettura pulita) e pratico (gioco completo e stabile).

## 2. Problema e obiettivi

### Problema

Nei progetti gioco e comune trovare logica e interfaccia mescolate, con codice difficile da estendere o testare.

### Obiettivi

1. Implementare le regole in modo fedele e verificabile.
2. Separare in modo netto logica di gioco e UI.
3. Offrire piu livelli AI per una difficolta progressiva.

## 3. Soluzione proposta

La soluzione e una applicazione modulare basata su package separati:

1. engine: stato partita, turni, prese legali, scoring, gestione round e torneo.
2. ai: strategie Easy, Normal, Expert con factory di selezione.
3. ui: scene Pygame, rendering, animazioni, log e overlay.
4. models: Player e stato relativo a mano, prese e scope.
5. config: costanti di gioco e costanti UI centralizzate.

## 4. Architettura e flusso runtime

### Componenti principali

1. GameApp: bootstrap applicazione e game loop.
2. SceneManager: gestione transizioni scena.
3. SetupScene: configurazione partita.
4. MatchScene: partita live.
5. ResultsScene: schermata finale.
6. GameEngine: regole e stato.
7. ScoringEngine: calcolo punteggi e primiera.

### Flusso

1. L utente configura partita in SetupScene.
2. MatchScene avvia GameEngine con i parametri scelti.
3. Ogni turno aggiorna Tavolo, Mano, Prese e log decisionale.
4. A fine round/torneo, ResultsScene mostra risultati e vincitore.

## 5. Intelligenza artificiale

1. EasyAI: comportamento semplice e casuale.
2. NormalAI: privilegia il valore immediato della presa.
3. ExpertAI: aggiunge valutazione tattica, rischio Scopa e memoria delle carte già giocate.


## 6. Regole e dominio gestiti

Il dominio rispetta la terminologia del progetto:

1. Card come coppia (value, suit).
2. Mano, Tavolo, Prese e Scopa.
3. Criteri punteggio: Carte, Denari, Settebello, Primiera, Scope.

## 7. Risultati ottenuti

1. Regole implementate in modo consistente.
2. Architettura modulare e facilmente estendibile.
3. Esperienza utente fluida con scene e animazioni.
4. Base solida per evoluzioni future senza riscrivere il core.

## 8. Limiti attuali

1. Assenza di modalita rete/multiplayer online.
2. Nessun sistema replay completo delle mani.
3. Possibili ulteriori ottimizzazioni grafiche su hardware molto lento.

## 9. Sviluppi futuri

1. Satistiche avanzate con database per memorizzarle.
3. Replay completo con storico esportabile.
4. Ottimizzazioni rendering addizionali per dispositivi low-end.

## 12. Conclusione

PyScopone dimostra che un gioco tradizionale puo diventare un progetto software moderno, con:

1. architettura chiara
2. regole affidabili
3. AI progressiva
4. interfaccia reattiva




