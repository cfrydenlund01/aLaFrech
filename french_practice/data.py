"""Static data sets that power the French practice application."""

from __future__ import annotations

from dataclasses import dataclass
from random import choice
from typing import Iterable, List, Sequence


@dataclass(frozen=True)
class VocabularyItem:
    """Single vocabulary entry used by the flashcard exercise."""

    french: str
    english: str
    category: str = "general"


VOCABULARY: Sequence[VocabularyItem] = (
    VocabularyItem("bonjour", "hello", "greetings"),
    VocabularyItem("au revoir", "goodbye", "greetings"),
    VocabularyItem("s'il vous plaît", "please", "greetings"),
    VocabularyItem("merci", "thank you", "greetings"),
    VocabularyItem("pardon", "sorry", "greetings"),
    VocabularyItem("pain", "bread", "food"),
    VocabularyItem("fromage", "cheese", "food"),
    VocabularyItem("eau", "water", "food"),
    VocabularyItem("pomme", "apple", "food"),
    VocabularyItem("vin", "wine", "food"),
    VocabularyItem("maison", "house", "home"),
    VocabularyItem("chaise", "chair", "home"),
    VocabularyItem("porte", "door", "home"),
    VocabularyItem("fenêtre", "window", "home"),
    VocabularyItem("cuisine", "kitchen", "home"),
    VocabularyItem("chat", "cat", "animals"),
    VocabularyItem("chien", "dog", "animals"),
    VocabularyItem("oiseau", "bird", "animals"),
    VocabularyItem("poisson", "fish", "animals"),
    VocabularyItem("cheval", "horse", "animals"),
)


@dataclass(frozen=True)
class ConjugationPattern:
    """Verb conjugation pattern for present tense practice."""

    infinitive: str
    je: str
    tu: str
    il: str
    nous: str
    vous: str
    ils: str

    @property
    def pronouns(self) -> Sequence[str]:
        return ("je", "tu", "il/elle", "nous", "vous", "ils/elles")

    @property
    def answers(self) -> Sequence[str]:
        return (self.je, self.tu, self.il, self.nous, self.vous, self.ils)


PRESENT_TENSE: Sequence[ConjugationPattern] = (
    ConjugationPattern("parler", "parle", "parles", "parle", "parlons", "parlez", "parlent"),
    ConjugationPattern("finir", "finis", "finis", "finit", "finissons", "finissez", "finissent"),
    ConjugationPattern("avoir", "ai", "as", "a", "avons", "avez", "ont"),
    ConjugationPattern("être", "suis", "es", "est", "sommes", "êtes", "sont"),
    ConjugationPattern("aller", "vais", "vas", "va", "allons", "allez", "vont"),
)


ACCENTED_CHARACTERS: Sequence[str] = (
    "à",
    "â",
    "ä",
    "ç",
    "é",
    "è",
    "ê",
    "ë",
    "î",
    "ï",
    "ô",
    "ù",
    "û",
    "ü",
)


def categories(items: Iterable[VocabularyItem]) -> List[str]:
    """Return the unique category names in the provided sequence."""

    seen: List[str] = []
    for item in items:
        if item.category not in seen:
            seen.append(item.category)
    return seen


def random_vocabulary_item(category: str | None = None) -> VocabularyItem:
    """Return a vocabulary item, optionally filtered by category."""

    if not category or category == "all":
        return choice(VOCABULARY)
    filtered = [item for item in VOCABULARY if item.category == category]
    if not filtered:
        return choice(VOCABULARY)
    return choice(filtered)


def random_conjugation_pattern() -> ConjugationPattern:
    """Select a random conjugation pattern."""

    return choice(PRESENT_TENSE)
