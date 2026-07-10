# Palimpsests: Modeling Hypertextual Relations from Classics to Fanfiction

A knowledge-representation project that models how literary and media works are
**transformed, inherited, and imitated** across texts, times, and cultures — from
Homer to Joyce, from Austen to fan fiction.

Developed for the *Knowledge Representation & Extraction* course (Prof. Aldo
Gangemi), DHDK Master's Programme, University of Bologna, A.Y. 2024–25.

## Overview

A *palimpsest* is a manuscript whose original text has been scraped away and
written over — yet traces of what came before persist beneath the surface.
Following Gérard Genette's *Palimpsestes* (1982), we use the metaphor to model
**hypertextual relations**: the structured creative dialogue between an earlier
work (the *hypotext*) and a later one (the *hypertext*).

The project encodes this formally in an **OWL 2 ontology** grounded in Aldo
Gangemi's **CreOn** (Creative Ontology), producing a machine-queryable knowledge
graph of literary derivation.

### At a glance

- **34** works across **18** hypotext–hypertext pairs
- **67** modelled creative operations
- **3** creative strategies — Transformation, Inheritance, Imitation
- **13** narrative-element types
- Corpus span: Homer's *Odyssey* (c. 800 BCE) → *ThreeBodyX* (2020s)
- Cultures: Western, Chinese, and Japanese

## The model

Each **operation** is an individual typed directly as one **CreativeStrategy**
subclass. An operation links an original work to a transformative work and acts
on a narrative element, turning a `sourceElement` (in the original) into a
`targetElement` (in the derivative).

- **Transformation** — an element is changed. E.g. *Odyssey* → *Ulysses*: a
  decade-spanning ancient epic is compressed onto a single day in modern Dublin.
- **Inheritance** — an element is carried over unchanged (source and target are
  the *same* individual). E.g. the plot skeleton of *Pride and Prejudice*
  inherited near-verbatim by *Pride and Prejudice and Zombies*.
- **Imitation** — an element is reused as a recognizable prototype. E.g.
  *Romeo and Juliet* → *West Side Story*: the lovers reused as Tony and Maria.

Narrative elements are organised in a class hierarchy (Character,
BackgroundSetting, StoryStructure, Relation, ContentDomain, MediumType, …).
Works are typed `:Work`, declared `owl:equivalentClass creon:CreativeProduct`,
and linked to Wikidata through `:externalRef`.

### A few of the pairs

| # | Hypotext | Hypertext |
|---|----------|-----------|
| 01 | *Water Margin* | *Jin Ping Mei* |
| 03 | *Canon of Sherlock Holmes* | *Sherlock* |
| 09 | *The Wonderful Wizard of Oz* | *Wicked* |
| 12 | *Odyssey* | *Ulysses* |
| 13 | *Romeo and Juliet* | *West Side Story* |
| 14 | *Emma* | *Clueless* |
| 15 | *Dracula* | *Nosferatu* |

## Competency questions (SPARQL 1.1)

The ontology and dataset together answer three competency questions, each with a
parameterised variant:

1. **Source derivation** — Which original work does a given derivative derive from?
2. **Creative strategies** — Which creative strategies does a derivative work employ?
3. **Preserved & reconstructed elements** — Which parts of the source were
   preserved (Inheritance) or reconstructed (Transformation / Imitation) in the
   derivative?

## Repository contents

- **`index.html`** — interactive documentation website. Self-contained: all data
  is embedded, so it opens offline with no server or build step.
- **`palimpsests.ttl`** — the OWL 2 ontology and 67-operation knowledge base
  (Turtle), modelled in Protégé following OWL 2 DL semantics.
- **`csv_to_ttl.py`** — converts the operations spreadsheet into Turtle.
- **`Operations_Audited.csv`** — the audited / normalised operations; the source
  used to generate the ontology.
- **`Items CSV - Origin.Operation.csv`** — the original, hand-authored operations.
- **`material/`** — book covers and case-study art, Protégé OntoGraf exports
  (`*.graph`), the core ontology-pattern diagram (`ex2.drawio.svg`), overview
  graphs (`graf1.png`, `graf2_ne.png`), and the strategy × narrative-element
  correlation data (`correlation.csv`, `correlation_matrix.csv`).

## Usage

**View the site** — open `index.html` in any modern browser. No server required.

**Regenerate the Turtle** from the audited CSV:

```bash
python csv_to_ttl.py
```

This reads `Operations_Audited.csv` and writes `output1.ttl`; the committed
`palimpsests.ttl` is the finalised ontology.

## Theoretical grounding

- **Gérard Genette**, *Palimpsestes* (1982) — hypertextuality; the three creative
  strategies map onto his taxonomy of hypertextual relations.
- **Julia Kristeva** — intertextuality, operationalised here at the level of
  individual narrative elements.
- **Aldo Gangemi** — **CreOn**, a foundational ontology of creativity grounded in
  DOLCE, extended in this project to the domain of literary derivation.

## Tools

Protégé 5.5 (OWL 2 DL, HermiT reasoner) · SPARQL 1.1 · Wikidata · Turtle / OWL 2.
