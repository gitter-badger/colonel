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

"""Module providing the :class:`.ConlluLexerBuilder` class and related
exception classes.
"""

from ply.lex import LexToken, TOKEN, Lexer, lex  # type: ignore
from colonel.upostag import UposTag


class LexerError(Exception):
    """Generic error class for :class:`.ConlluLexerBuilder`."""
    pass


class IllegalCharacterError(LexerError):
    """Exception raised by :class:`.ConlluLexerBuilder` when a lexer error
    caused by invalid input is encountered.

    An exception instance must be initialized with the :class:`.LexToken` which
    the lexer was not able to process, so that :attr:`line_number` and
    :attr:`column_number` can be extracted; a short error message is also
    generated by the constructor.
    """

    def __init__(self, token: LexToken) -> None:
        #: Line number containing the illegal character, or the start of an
        #: illegal sequence.
        self.line_number: int = token.lexer.lineno

        #: Column position, associated with :attr:`line_number`, containing the
        #: illegal character, or the start of an illegal sequence.
        self.column_number: int = ConlluLexerBuilder.find_column(token)

        super(IllegalCharacterError, self).__init__(
            "Illegal character %s at (or sequence from) %s:%s" %
            (repr(token.value[0]), self.line_number, self.column_number)
        )


# We disable pylint invalid names complaints due to PLY lexer naming convention
# pylint: disable=invalid-name

class ConlluLexerBuilder:
    """Class containing *PLY Lex* rules for processing the *CoNLL-U* format and
    for creating new related *PLY* :class:`.Lexer` instances.

    Usually you can simply invoke the class method :meth:`build` which returns
    a *PLY* :class:`.Lexer`; such lexer instance is ready to process your
    input, making use of the rules provided by the :class:`ConlluLexerBuilder`
    class itself.
    """

    states = (
        ('v0', 'exclusive'), ('v1', 'exclusive'), ('v2', 'exclusive'),
        ('v3', 'exclusive'), ('v4', 'exclusive'), ('v5', 'exclusive'),
        ('v6', 'exclusive'), ('v7', 'exclusive'), ('v8', 'exclusive'),
        ('v9', 'exclusive'),
        ('c1', 'exclusive'), ('c2', 'exclusive'), ('c3', 'exclusive'),
        ('c4', 'exclusive'), ('c5', 'exclusive'), ('c6', 'exclusive'),
        ('c7', 'exclusive'), ('c8', 'exclusive'), ('c9', 'exclusive'),
    )

    tokens = (
        'NEWLINE', 'TAB', 'COMMENT', 'INTEGER_ID', 'RANGE_ID', 'DECIMAL_ID',
        'FORM', 'LEMMA', 'UPOS', 'XPOS', 'FEATS', 'HEAD', 'DEPREL', 'DEPS',
        'MISC',
    )

    #: Pattern for the name of a morphological feature (left part)
    _feat_name = r'[A-Z0-9][A-Z0-9a-z]*(\[[a-z0-9]+\])?'

    #: Pattern for a single value of a morphological feature (right part)
    _feat_value = r'[A-Z0-9][a-zA-Z0-9]*'

    #: Pattern for a list of values of a morphological feature (right part)
    _feat_values = r'{0}(,{0})*'.format(_feat_value)

    #: Pattern for a single morphological feature name+values pair
    _feat_pair = r'{0}={1}'.format(_feat_name, _feat_values)

    #: Pattern for a nullable list of morphological features
    _feats = r'({0}([|]{0})*)|_'.format(_feat_pair)

    #: Pattern for the head part of a head+deprel pair (left part)
    _dep_head = r'([1-9][0-9]+|[0-9])'

    #: Pattern for the deprel part of a head+deprel pair (right part)
    _dep_deprel = r'[^\n\t ]+'

    #: Pattern for a head+deprel pair
    _dep_pair = r'{0}:{1}'.format(_dep_head, _dep_deprel)

    #: Pattern for a nullable list of head+deprel pairs
    _deps = r'({0}([|]{0})*)|_'.format(_dep_pair)

    #: Pattern for a nullable Universal part-of-speech tag
    _upos = r'({0}|_)'.format('|'.join(tag.name for tag in UposTag))

    def t_v0_v1_v2_v3_v4_v5_v6_v7_v8_TAB(self, token: LexToken) -> LexToken:
        r'\t'
        self._tab_count += 1
        token.lexer.begin(f'c{self._tab_count}')
        return token

    @staticmethod
    def t_COMMENT(token: LexToken) -> LexToken:
        r'[#][^\n]*'
        token.value = token.value[1:].strip()
        return token

    @staticmethod
    def t_RANGE_ID(token: LexToken) -> LexToken:
        r'[1-9][0-9]*-[1-9][0-9]*'
        token.value = tuple(map(int, token.value.split('-')))
        token.lexer.begin('v0')
        return token

    @staticmethod
    def t_DECIMAL_ID(token: LexToken) -> LexToken:
        r'([1-9][0-9]+|[0-9])\.[1-9][0-9]*'
        token.value = tuple(map(int, token.value.split('.')))
        token.lexer.begin('v0')
        return token

    @staticmethod
    def t_INTEGER_ID(token: LexToken) -> LexToken:
        r'[1-9][0-9]*'
        token.value = int(token.value)
        token.lexer.begin('v0')
        return token

    @staticmethod
    def t_c1_FORM(token: LexToken) -> LexToken:
        r'[^\n\t]+'
        token.lexer.begin('v1')
        return token

    @staticmethod
    def t_c2_LEMMA(token: LexToken) -> LexToken:
        r'[^\n\t]+'
        token.lexer.begin('v2')
        return token

    @staticmethod
    @TOKEN(_upos)
    def t_c3_UPOS(token: LexToken) -> LexToken:
        # pylint: disable=missing-docstring
        token.value = None if token.value == '_' else token.value
        token.lexer.begin('v3')
        return token

    @staticmethod
    def t_c4_XPOS(token: LexToken) -> LexToken:
        r'[^\n\t ]+'
        token.value = None if token.value == '_' else token.value
        token.lexer.begin('v4')
        return token

    @staticmethod
    @TOKEN(_feats)
    def t_c5_FEATS(token: LexToken) -> LexToken:
        # pylint: disable=missing-docstring
        token.value = None if token.value == '_' else tuple(
            (x[:x.index('=')], tuple(x[x.index('=')+1:].split(',')))
            for x in token.value.split('|')
        )
        token.lexer.begin('v5')
        return token

    @staticmethod
    def t_c6_HEAD(token: LexToken) -> LexToken:
        r'([1-9][0-9]+|[0-9])|_'
        token.value = None if token.value == '_' else int(token.value)
        token.lexer.begin('v6')
        return token

    @staticmethod
    def t_c7_DEPREL(token: LexToken) -> LexToken:
        r'[^\n\t ]+'
        token.value = None if token.value == '_' else token.value
        token.lexer.begin('v7')
        return token

    @staticmethod
    @TOKEN(_deps)
    def t_c8_DEPS(token: LexToken) -> LexToken:
        # pylint: disable=missing-docstring
        token.value = None if token.value == '_' else tuple(
            (int(x[:x.index(':')]), x[x.index(':')+1:])
            for x in token.value.split('|')
        )
        token.lexer.begin('v8')
        return token

    @staticmethod
    def t_c9_MISC(token: LexToken) -> LexToken:
        r'[^\n\t ]+'
        token.value = None if token.value == '_' else token.value
        token.lexer.begin('v9')
        return token

    def t_INITIAL_v9_NEWLINE(self, token: LexToken) -> LexToken:
        r'\n'
        token.lexer.lineno += 1
        self._tab_count = 0
        token.lexer.begin('INITIAL')
        return token

    @staticmethod
    def t_ANY_error(token: LexToken) -> None:
        # pylint: disable=missing-docstring
        raise IllegalCharacterError(token)

    @staticmethod
    def find_column(token: LexToken) -> int:
        """Given a :class:`.LexToken`, it returns the related column number.
        """
        line_start = token.lexer.lexdata.rfind('\n', 0, token.lexpos) + 1
        return (token.lexpos - line_start) + 1

    def __init__(self) -> None:
        self.lexer: Lexer = lex(module=self)
        self._tab_count = 0

    @classmethod
    def build(cls) -> Lexer:
        """Returns a *PLY* :class:`Lexer` instance for *CoNLL-U* processing.

        The returned lexer makes use of the rules defined by
        :class:`ConlluLexerBuilder`.
        """
        return cls().lexer
