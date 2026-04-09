# PRESENTAZIONE - PyScopone

## Cos'e PyScopone

PyScopone e un progetto Python che implementa il gioco tradizionale dello Scopone con:
- regole fedeli
- AI a difficolta crescente
- interfaccia grafica Pygame moderna

## Obiettivo

L'obiettivo e doppio:
1. didattico: mostrare una architettura software pulita (engine separato dalla UI)
2. pratico: fornire un gioco completo, stabile e testato

## Architettura in breve

Il progetto e organizzato in moduli chiari:
- `engine`: regole partita, turni, punteggio, gestione torneo
- `ai`: strategie Easy / Normal / Expert
- `ui`: scene Pygame, rendering carte, animazioni, audio
- `models`: entita di dominio (`Player`)
- `config`: costanti gioco/UI

Flusso runtime:
1. `SetupScene` configura la partita
2. `MatchScene` gestisce la partita live
3. `ResultsScene` mostra il risultato finale

## AI

- **Easy**: comportamento semplice e casuale
- **Normal**: scelta orientata al valore immediato della presa
- **Expert**: strategia avanzata con analisi del rischio scopa e priorita tattiche

Ogni mossa AI puo essere tracciata con un decision log utile per debugging e spiegazione in demo.

## GUI

La GUI usa Pygame con:
- game loop esplicito (`input -> update -> render`)
- scene separate
- animazioni non bloccanti (tween)
- rendering carte da atlas trevisane
- overlay interattivi (menu, log, scelta presa, fine smazzata)

## Punti forti

- separazione netta tra logica e presentazione
- test automatici su engine, scoring, AI, UI smoke
- supporto 2-player e 4-player
- codice leggibile e facilmente estendibile

## Possibili sviluppi futuri

1. Profili AI aggiuntivi (difensivo/aggressivo)
2. Telemetria partita (metriche avanzate UI+AI)
3. Replay delle mani e storico partite esportabile
4. Ottimizzazioni rendering aggiuntive per hardware low-end

## Messaggio finale per la classe

PyScopone dimostra come un gioco classico possa essere trasformato in un progetto software completo:
- regole corrette
- architettura modulare
- UI moderna
- qualita garantita da test

E un buon esempio di progetto "pronto demo" e "pronto manutenzione".
