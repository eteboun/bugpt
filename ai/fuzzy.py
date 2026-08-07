from rapidfuzz import fuzz
from typing import TypeVar
from enum import StrEnum

T = TypeVar('T', bound=StrEnum)

def clean_query(query: str,
                removal_terms: set[str],
                threshold: float
                ) -> str:

    words = query.split()
    result: list[str] = []
    index = 0

    time_phrases = sorted(
        removal_terms,
        key=lambda phrase: len(phrase.split()),
        reverse=True,
    )

    while index < len(words):

        longest_phrase_length = 0

        for phrase in time_phrases:
            phrase_length = len(phrase.split())
            candidate_words = words[index:index + phrase_length]

            if len(candidate_words) < phrase_length:
                continue

            candidate = " ".join(candidate_words)

            score = fuzz.ratio(
                candidate.casefold(),
                phrase.casefold(),
            )

            if score >= threshold:
                longest_phrase_length = max(longest_phrase_length, phrase_length)

        if longest_phrase_length > 0:
            index += longest_phrase_length
        else:
            result.append(words[index])
            index += 1

    return " ".join(result)

def rewrite_query(query: str,
                  alias_dict: dict[str, str],
                  threshold: float
                  ) -> str:

    words = query.split()
    result: list[str] = []
    index = 0

    aliases = sorted(
        alias_dict,
        key=lambda alias: len(alias.split()),
        reverse=True,
    )

    while index < len(words):
        best_alias: str | None = None
        best_score = 0.

        for alias in aliases:
            alias_length = len(alias.split())
            candidate_words = words[index:index + alias_length]

            if len(candidate_words) < alias_length:
                continue

            candidate = " ".join(candidate_words)

            score = fuzz.ratio(
                candidate.casefold(),
                alias.casefold(),
            )

            if score >= threshold and score > best_score:
                best_alias = alias
                best_score = score

        if best_alias is None:
            result.append(words[index])
            index += 1
        else:
            result.append(alias_dict[best_alias])
            index += len(best_alias.split())

    return " ".join(result)

def extract_keys(
        query: str,
        key_dict: dict[T, set[str]],
        threshold: float
        ) -> list[T]:

    words = query.split()
    extraction: list[T] = []

    index = 0
    while index < len(words):
        best_value: T | None = None
        best_score = 0.0
        best_word_count = 0

        for t, alias_set in key_dict.items():
            for alias in alias_set:

                alias_length = len(alias.split())
                candidate_words = words[index:index + alias_length]

                if len(candidate_words) < alias_length:
                    continue

                candidate = " ".join(candidate_words)

                score = fuzz.ratio(
                    candidate.casefold(),
                    alias.casefold(),
                )

                if score < threshold:
                    continue

                if score > best_score or (
                    score == best_score and len(alias.split()) > best_word_count
                ):

                    best_value = t
                    best_score = score
                    best_word_count = len(alias.split())

        if best_value:
            if best_value not in extraction:
                extraction.append(best_value)
            index += best_word_count
        else:
            index += 1

    return extraction

def match(query: str,
          aliases: set[str],
          threshold: float,
          ) -> bool:

    words = query.split()
    index = 0

    while index < len(words):

        for alias in aliases:

            alias_length = len(alias.split())
            candidate_words = words[index:index + alias_length]

            if len(candidate_words) < alias_length:
                continue

            candidate = " ".join(candidate_words)

            score = fuzz.ratio(
                candidate.casefold(),
                alias.casefold()
            )

            if score >= threshold:
                return True

        index += 1
    return False