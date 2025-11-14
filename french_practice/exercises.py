"""Exercise logic for the French practice toolkit."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, Optional

from .data import ConjugationPattern, VocabularyItem, random_conjugation_pattern, random_vocabulary_item


@dataclass
class ExerciseState:
    """State shared by exercises for tracking streaks and totals."""

    total_attempts: int = 0
    correct_attempts: int = 0
    current_streak: int = 0

    def register_attempt(self, correct: bool) -> None:
        self.total_attempts += 1
        if correct:
            self.correct_attempts += 1
            self.current_streak += 1
        else:
            self.current_streak = 0

    @property
    def accuracy(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return self.correct_attempts / self.total_attempts


@dataclass
class FlashcardExercise:
    """Simple flashcard exercise that prompts for translations."""

    category: Optional[str] = None
    state: ExerciseState = field(default_factory=ExerciseState)
    current_item: VocabularyItem | None = None

    def next_prompt(self) -> VocabularyItem:
        self.current_item = random_vocabulary_item(self.category)
        return self.current_item

    def check_answer(self, answer: str) -> bool:
        if self.current_item is None:
            self.next_prompt()
        assert self.current_item is not None  # for type checkers
        correct = answer.strip().lower() == self.current_item.english.lower()
        self.state.register_attempt(correct)
        return correct


@dataclass
class ConjugationExercise:
    """Select a verb and pronoun to quiz present tense conjugations."""

    state: ExerciseState = field(default_factory=ExerciseState)
    current_pattern: ConjugationPattern | None = None
    current_index: int = 0

    def next_prompt(self) -> tuple[str, str]:
        pattern = random_conjugation_pattern()
        self.current_pattern = pattern
        self.current_index = pattern.pronouns.index("je")
        return pattern.infinitive, pattern.pronouns[self.current_index]

    def cycle_prompt(self) -> tuple[str, str]:
        if self.current_pattern is None:
            return self.next_prompt()
        self.current_index = (self.current_index + 1) % len(self.current_pattern.pronouns)
        return self.current_pattern.infinitive, self.current_pattern.pronouns[self.current_index]

    def check_answer(self, answer: str) -> bool:
        if self.current_pattern is None:
            self.next_prompt()
        assert self.current_pattern is not None
        expected = self.current_pattern.answers[self.current_index]
        correct = answer.strip().lower() == expected.lower()
        self.state.register_attempt(correct)
        return correct


class ExerciseRegistry:
    """Registry of exercises so the GUI can remain decoupled from logic."""

    def __init__(self) -> None:
        self._creators: Dict[str, Callable[[], object]] = {}

    def register(self, name: str, factory: Callable[[], object]) -> None:
        self._creators[name] = factory

    def create(self, name: str) -> object:
        if name not in self._creators:
            raise KeyError(f"Unknown exercise: {name}")
        return self._creators[name]()

    def names(self) -> Iterable[str]:
        return self._creators.keys()


EXERCISES = ExerciseRegistry()
EXERCISES.register("Flashcards", FlashcardExercise)
EXERCISES.register("Conjugation", ConjugationExercise)
