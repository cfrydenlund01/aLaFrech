"""Tkinter based GUI for French practice activities."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .data import ACCENTED_CHARACTERS, VOCABULARY, categories
from .exercises import ConjugationExercise, ExerciseRegistry, FlashcardExercise, EXERCISES


class AccentToolbar(ttk.Frame):
    """Toolbar that inserts accented characters into a linked entry widget."""

    def __init__(self, master: tk.Misc, target: tk.Entry, *, characters: tuple[str, ...] | None = None) -> None:
        super().__init__(master, padding=(4, 2))
        self.target = target
        self.characters = characters or tuple(ACCENTED_CHARACTERS)
        self._build_buttons()

    def _build_buttons(self) -> None:
        for char in self.characters:
            button = ttk.Button(self, text=char, width=3)
            button.configure(command=lambda value=char: self._insert(value))
            button.pack(side=tk.LEFT, padx=1)

    def _insert(self, value: str) -> None:
        self.target.insert(tk.INSERT, value)
        self.target.focus_set()


class StatsBar(ttk.Frame):
    """Simple bar displaying exercise statistics."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=(4, 2))
        self.accuracy_var = tk.StringVar(value="Accuracy: 0%")
        self.streak_var = tk.StringVar(value="Streak: 0")
        ttk.Label(self, textvariable=self.accuracy_var).pack(side=tk.LEFT, padx=4)
        ttk.Label(self, textvariable=self.streak_var).pack(side=tk.LEFT, padx=4)

    def update_state(self, accuracy: float, streak: int) -> None:
        self.accuracy_var.set(f"Accuracy: {accuracy:.0%}")
        self.streak_var.set(f"Streak: {streak}")


class FlashcardTab(ttk.Frame):
    """Tab widget that wires the flashcard exercise into the UI."""

    def __init__(self, master: tk.Misc, exercise: FlashcardExercise) -> None:
        super().__init__(master, padding=12)
        self.exercise = exercise
        self.prompt_var = tk.StringVar(value="Press Next to start")
        self.feedback_var = tk.StringVar()
        self.answer_var = tk.StringVar()
        self.category_var = tk.StringVar(value="all")

        self._build()

    def _build(self) -> None:
        ttk.Label(self, text="Category:").grid(row=0, column=0, sticky="w")
        cat_values = ["all", *categories(VOCABULARY)]
        ttk.OptionMenu(self, self.category_var, self.category_var.get(), *cat_values, command=self._change_category).grid(
            row=0, column=1, sticky="w"
        )

        ttk.Label(self, textvariable=self.prompt_var, font=("Helvetica", 16, "bold")).grid(
            row=1, column=0, columnspan=3, pady=(12, 8)
        )

        answer_entry = ttk.Entry(self, textvariable=self.answer_var, width=30)
        answer_entry.grid(row=2, column=0, columnspan=2, pady=4, sticky="we")
        AccentToolbar(self, answer_entry).grid(row=3, column=0, columnspan=2, sticky="w")

        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=2, rowspan=2, padx=(8, 0), sticky="ns")
        ttk.Button(button_frame, text="Check", command=self._check_answer).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Reveal", command=self._reveal_answer).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Next", command=self._next).pack(fill=tk.X, pady=2)

        ttk.Label(self, textvariable=self.feedback_var, foreground="steelblue").grid(
            row=4, column=0, columnspan=3, pady=(8, 0), sticky="w"
        )

        self.stats = StatsBar(self)
        self.stats.grid(row=5, column=0, columnspan=3, sticky="we", pady=(12, 0))

        for i in range(3):
            self.columnconfigure(i, weight=1)

    def _change_category(self, category: str) -> None:
        self.exercise.category = category
        self._next()

    def _next(self) -> None:
        item = self.exercise.next_prompt()
        self.prompt_var.set(f"Translate: {item.french}")
        self.answer_var.set("")
        self.feedback_var.set("")

    def _check_answer(self) -> None:
        if not self.answer_var.get():
            self.feedback_var.set("Type your answer first.")
            return
        correct = self.exercise.check_answer(self.answer_var.get())
        if correct:
            self.feedback_var.set("Correct! 🎉")
            self._next()
        else:
            assert self.exercise.current_item is not None
            self.feedback_var.set(f"Not quite. Answer: {self.exercise.current_item.english}")
        self._refresh_stats()

    def _reveal_answer(self) -> None:
        if self.exercise.current_item:
            self.feedback_var.set(f"Answer: {self.exercise.current_item.english}")

    def _refresh_stats(self) -> None:
        state = self.exercise.state
        self.stats.update_state(state.accuracy, state.current_streak)


class ConjugationTab(ttk.Frame):
    """Tab widget that provides verb conjugation practice."""

    def __init__(self, master: tk.Misc, exercise: ConjugationExercise) -> None:
        super().__init__(master, padding=12)
        self.exercise = exercise
        self.verb_var = tk.StringVar(value="Press Next")
        self.pronoun_var = tk.StringVar(value="je")
        self.feedback_var = tk.StringVar()
        self.answer_var = tk.StringVar()

        self._build()

    def _build(self) -> None:
        ttk.Label(self, textvariable=self.verb_var, font=("Helvetica", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 8)
        )
        ttk.Label(self, textvariable=self.pronoun_var, font=("Helvetica", 14)).grid(row=1, column=0, sticky="w")

        answer_entry = ttk.Entry(self, textvariable=self.answer_var, width=20)
        answer_entry.grid(row=1, column=1, padx=(4, 0), sticky="we")
        AccentToolbar(self, answer_entry, characters=("é", "è", "ê", "ç")).grid(
            row=2, column=0, columnspan=2, sticky="w"
        )

        ttk.Button(self, text="Check", command=self._check).grid(row=3, column=0, pady=6, sticky="we")
        ttk.Button(self, text="Next Pronoun", command=self._cycle_pronoun).grid(row=3, column=1, pady=6, sticky="we")
        ttk.Button(self, text="New Verb", command=self._next).grid(row=4, column=0, columnspan=2, sticky="we")

        ttk.Label(self, textvariable=self.feedback_var, foreground="seagreen").grid(
            row=5, column=0, columnspan=2, sticky="w"
        )

        self.stats = StatsBar(self)
        self.stats.grid(row=6, column=0, columnspan=2, sticky="we", pady=(12, 0))

        self.columnconfigure(1, weight=1)

    def _next(self) -> None:
        verb, pronoun = self.exercise.next_prompt()
        self.verb_var.set(f"Verb: {verb}")
        self.pronoun_var.set(f"Pronoun: {pronoun}")
        self.answer_var.set("")
        self.feedback_var.set("")

    def _cycle_pronoun(self) -> None:
        verb, pronoun = self.exercise.cycle_prompt()
        self.verb_var.set(f"Verb: {verb}")
        self.pronoun_var.set(f"Pronoun: {pronoun}")
        self.answer_var.set("")
        self.feedback_var.set("")

    def _check(self) -> None:
        if not self.answer_var.get():
            self.feedback_var.set("Enter a conjugation first.")
            return
        correct = self.exercise.check_answer(self.answer_var.get())
        if correct:
            self.feedback_var.set("Great job! ✅")
        else:
            assert self.exercise.current_pattern is not None
            expected = self.exercise.current_pattern.answers[self.exercise.current_index]
            self.feedback_var.set(f"Try again. Answer: {expected}")
        self._refresh_stats()

    def _refresh_stats(self) -> None:
        state = self.exercise.state
        self.stats.update_state(state.accuracy, state.current_streak)


class FrenchPracticeApp(tk.Tk):
    """Main application window."""

    def __init__(self, registry: ExerciseRegistry | None = None) -> None:
        super().__init__()
        self.title("aLaFrech - French Practice")
        self.geometry("520x420")
        self.resizable(True, False)
        self.registry = registry or EXERCISES
        self._build_menu()
        self._build_tabs()

    def _build_menu(self) -> None:
        menu_bar = tk.Menu(self)
        help_menu = tk.Menu(menu_bar, tearoff=False)
        help_menu.add_command(label="About", command=self._show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menu_bar)

    def _build_tabs(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        for name in self.registry.names():
            exercise = self.registry.create(name)
            if isinstance(exercise, FlashcardExercise):
                tab = FlashcardTab(notebook, exercise)
            elif isinstance(exercise, ConjugationExercise):
                tab = ConjugationTab(notebook, exercise)
            else:
                continue
            notebook.add(tab, text=name)

    def _show_about(self) -> None:
        messagebox.showinfo(
            "About aLaFrech",
            "Practice French vocabulary and conjugations with a friendly GUI."
            "\nDeveloped as a modular example app.",
        )


def main() -> None:
    """Entry point used by ``python -m french_practice``."""

    app = FrenchPracticeApp()
    app.mainloop()


if __name__ == "__main__":
    main()
