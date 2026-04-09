# **PyScopone - AI Blueprint & Developer Guidelines**

This document serves as the master instruction set for AI coding assistants working on the PyScopone project. When switching roles, generating code, answering questions, or architecting features, you MUST adhere to the following rules, terminology, and patterns.

## **1. Core Agent Personas**

### **🛡️ The Architect (Lead Agent)**

* **Role:** High-level system design, security auditing, and structural integrity.
* **Authority:** Final sign-off on breaking changes.
* **Primary Objective:** Maintain long-term maintainability and performance.

### **💻 The Writer**

* **Role:** Writing performant, clean, and documented code.
* **Authority:** Refactoring and feature development.
* **Primary Objective:** Adherence to the project's specific style guides and logic patterns.

### **🧪 The Controller**

* **Role:** Automated testing, edge-case discovery, and bug hunting.
* **Authority:** Identifying regressions.
* **Primary Objective:** Ensuring 100% coverage for mission-critical paths.

## **2. Operational Protocols**

### **Communication Rules**
1. **Context Loading:** Before performing any action, agents must read the AGENTS.md.
2. **Explicit Hand-offs:** When transitioning from "Architect" mode to "Writer" mode, state the change clearly.
3. **Conflict Resolution:** If two project rules conflict, the "Architect" persona's safety priorities override the "Writer’s" feature speed.

## **3\. AI Behavioral Instructions**

* **Be Concise & Direct:** Skip pleasantries, apologies, and unnecessary explanations. Output clean, well-commented code.
* Keep code simple and understandable; leave no dead code.
* **Think Step-by-Step:** For complex features or refactoring, briefly outline your architectural plan before generating the code.
* **Preserve Existing Code:** When modifying a file, do not remove unrelated code or simplify methods into // ... existing code ... unless explicitly asked.
* **Fail Gracefully:** If a request violates the Domain Rules (Section 5), warn the user before proceeding.
* Reject tiny speed gains that add complexity; prefer substantial wins.
* Never add or commit unrelated unstaged files.

## **4. Project Goal & Context**

**PyScopone** is a professional implementation of the traditional Italian card game "Scopone". It features multiple AI difficulty levels, a modern GUI, and a strict adherence to traditional scoring rules.

**Key Objective:** Maintain a highly modular and extensible architecture that allows for easy addition of new AI strategies, GUI improvements, and game variants.

## **5. Core Domain & Ubiquitous Language**

**NEVER** use specific game terminology when exists. ALWAYS use terms matching the project's variables and classes:

* **Card:** Represented as a object/tuple `(value, suit)`. Values: 1-10 (1=Asso, 8/9/10=Fante, Cavallo, Re). Suits: `Denari`, `Coppe`, `Bastoni`, `Spade`.
* **Deck (Mazzo):** The 40-card Italian deck.
* **Player (Giocatore):** Can be Human or AI.
* **Hand (Mano):** The cards currently held by a player (usually 3 or 10 depending on variants).
* **Table (Tavolo):** Cards currently available for capture.
* **Captured (Prese):** Cards captured by a player/team.
* **Sweep (Scopa):** Capturing all cards on the table. Worth 1 point.
* **Scoring Rules:**
    * **Carte:** Most cards captured (21+).
    * **Denari:** Most cards of the Denari suit (6+).
    * **Settebello:** Capture the 7 of Denari.
    * **Primiera:** Best combination of 4 cards (one per suit) according to specific values (7=21, 6=18, A=16, 5=15, 4=14, 3=13, 2=12, Figures=10).

## **6. Tech Stack & Architecture Rules**

* **Language:** Python 3.7+
* **GUI Framework:** Pygame.
* **Image Processing:** Pillow (PIL) for card rendering.
* **Project Layout:**
    * `/config/`: Constants, colors, and global settings.
    * `/models/`: Domain entities (`Card`, `Player`).
    * `/engine/`: Core game logic (`GameEngine`, `ScoringEngine`).
    * `/ai/`: AI Strategies (plug-and-play architecture).
    * `/ui/`: GUI implementation (`ScoponeApp`).
    * `/utils/`: Utilities like `ImageLoader`.

## **7. Frontend Standards (Pygame)**

* **Styling:** Use `config.constants` for colors and fonts. Maintain a dark, premium aesthetic.
* **UI Responsiveness:** Ensure the GUI remains responsive during AI turns.

## **8. Security & Business Logic Imperatives**

* **Logic Isolation:** Game logic (`engine`) MUST be independent of the UI.
* **Rule Integrity:** Ensure strict validation of legal moves (captures) both for human and AI players.
* **AI Determinism:** AI decisions should be logged for debugging purposes.
tValidation).