import sys

from typing import List
from codecs import decode


class Lexer:
    # types of tokens
    INT, DOUBLE, BOOL, STRING, WHILE, FOR, IF, ELSE, SWITCH, CASE, BREAK, DEFAULT,\
        SCAN, PRINT, ATOI, ATOB, ATOF, TO_STRING, TRUE, FALSE, PLUS, MINUS, MULT, DIV, MOD, \
        COMMA, SEMICOLON, LBRACKET, RBRACKET, LBRACE, RBRACE, EQUAL, LESS, MORE, AND, OR, NOT, \
        IDENTIFIER, NUM_INT, NUM_DOUBLE, STRING_LITERAL = range(41)

    WHITESPACES = (' ', '\t', '\n')

    SPECIAL_SYMBOLS = {
        '+': PLUS,
        '-': MINUS,
        '*': MULT,
        '/': DIV,
        '%': MOD,
        ',': COMMA,
        ';': SEMICOLON,
        '(': LBRACKET,
        ')': RBRACKET,
        '{': LBRACE,
        '}': RBRACE,
        '=': EQUAL,
        '<': LESS,
        '>': MORE,
        '&': AND,
        '|': OR,
        '!': NOT
    }

    KEYWORDS = {
        "int": INT,
        "double": DOUBLE,
        "bool": BOOL,
        "string": STRING,
        "while": WHILE,
        "for": FOR,
        "if": IF,
        "else": ELSE,
        "switch": SWITCH,
        "case": CASE,
        "break": BREAK,
        "default": DEFAULT,
        "scan": SCAN,
        "print": PRINT,
        "atoi": ATOI,
        "atob": ATOB,
        "atof": ATOF,
        "to_string": TO_STRING,
        "true": TRUE,
        "false": FALSE
    }

    class NoMoreTokens(Exception):
        pass

    class QuotesNotClosed(Exception):
        def __init__(self):
            self.message = "quotes not closed"
            super().__init__(self.message)

    class Token:
        def __init__(self, tp=None, vl=None):
            self.type = tp
            self.value = vl

    def __init__(self, file_name: str):
        with open(file_name) as f:
            self._program_text = f.read()

        self._curr_symbol_index = 0
        self._text_len = len(self._program_text) - 1  # EOF in the end?

        # print("END SYMBOL: " + str(ord(self._program_text[self._text_len])))

    def get_curr_symbol(self) -> str:
        return self._program_text[self._curr_symbol_index]

    def next_symbol(self):
        self._curr_symbol_index += 1

    def program_finished(self) -> bool:
        return self._curr_symbol_index >= self._text_len

    def get_next_token(self) -> Token:
        # get the WHOLE TOKEN
        if self.program_finished():
            raise Lexer.NoMoreTokens()

        curr_sym = self.get_curr_symbol()
        while curr_sym in Lexer.WHITESPACES:
            self.next_symbol()
            curr_sym = self.get_curr_symbol()

            if self.program_finished():
                raise Lexer.NoMoreTokens()

        # print("curr_sym = " + curr_sym)

        if curr_sym in Lexer.SPECIAL_SYMBOLS.keys():
            next_tok = Lexer.Token(Lexer.SPECIAL_SYMBOLS[curr_sym], None)
            self.next_symbol()
        elif curr_sym.isalpha():
            # read a 'word'
            word = curr_sym
            self.next_symbol()
            curr_sym = self.get_curr_symbol()

            while (curr_sym.isalnum() or curr_sym == '_') and not self.program_finished():
                word += curr_sym
                self.next_symbol()
                curr_sym = self.get_curr_symbol()

            # we have the word. what to do now?
            if word in Lexer.KEYWORDS.keys():
                # keyword
                next_tok = Lexer.Token(Lexer.KEYWORDS[word], None)
            else:
                # identifier
                next_tok = Lexer.Token(Lexer.IDENTIFIER, word)
        elif curr_sym == '"':
            # string literal
            # next_tok = Lexer.Token(Lexer.STRING_LITERAL, "some raw string here")
            string_literal = ""

            while True:
                self.next_symbol()
                if self.program_finished():
                    raise Lexer.QuotesNotClosed()

                curr_sym = self.get_curr_symbol()

                if curr_sym == '"':
                    self.next_symbol()
                    break

                string_literal += curr_sym

            next_tok = Lexer.Token(Lexer.STRING_LITERAL, string_literal)
        else:
            next_tok = Lexer.Token(Lexer.INT, curr_sym)
            self.next_symbol()

        return next_tok

    def split_program_into_tokens(self) -> List[Token]:
        ret = []

        while True:
            try:
                ret.append(self.get_next_token())
            except Lexer.NoMoreTokens:
                break
            except Lexer.QuotesNotClosed as err:
                # TODO: replace symbol number with LINE and POSITION IN LINE
                print(f"Lexer error: {err.message} (symbol number: {self._curr_symbol_index})")
                sys.exit(1)

        return ret


def main():
    lexer = Lexer("program.cmm")
    tokens: List[Lexer.Token] = lexer.split_program_into_tokens()

    for tok in tokens:
        print(tok.type)
        print(tok.value)
        print()

    """experiment_string = ""
    experiment_string += "hello"
    experiment_string += "\\"
    experiment_string += "n"
    experiment_string += "world"
    print("\nexperiment string:")
    print(bytes(experiment_string, "utf-8").decode("unicode_escape"))"""


if __name__ == "__main__":
    main()
