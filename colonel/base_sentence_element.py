# Copyright 2018 The NLP Odyssey Authors.
# Copyright 2018 Marco Nicola <marconicola@disroot.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module providing the :class:`.BaseSentenceElement` class."""

from typing import Optional

__all__ = ['BaseSentenceElement']


class BaseSentenceElement:
    """Abstract class containing the minimum information in common with
    all more specific elements being part of a sentence.

    In the context of this library, it is expected that each item of a sentence
    is an instance of a :class:`.BaseSentenceElement` subclass (or, in rare
    cases, at least an instance of :class:`.BaseSentenceElement` itself).

    The generic term *element* is used in order to prevent confusion, while
    each specialized element (i.e. a subclass of :class:`.BaseSentenceElement`)
    will adopt a more appropriate nomenclature, so that, for example, a
    sentence will be formed by *words*, a *tokens* or *nodes*.
    """

    __slots__ = ('form', 'misc')

    def __init__(
            self,
            form: Optional[str] = None,
            misc: Optional[str] = None
    ) -> None:
        #: Word form or punctuation symbol.
        #:
        #: It is compatible with *CoNLL-U* ``FORM`` field.
        self.form: Optional[str] = form

        #: Any other annotation.
        #:
        #: It is compatible with *CoNLL-U* ``MISC`` field.
        self.misc: Optional[str] = misc

    @staticmethod
    def is_valid() -> bool:
        """Returns whether or not the object can be considered valid,
        without considering the context of the sentence in which the word
        itself is possibly inserted.

        An instance of type :class:`.BaseWord` is **always** considered valid,
        independently from the value of :attr:`.form` and :attr:`.misc`.
        """
        return True
