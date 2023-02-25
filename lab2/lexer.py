from typing import List, Tuple
from symbol import Symbol
from warnings import filterwarnings
import sys

filterwarnings("error")


class Lexer:
    # types of tokens
    INT, DOUBLE, BOOL, STRING, WHILE, FOR, IF, ELSE, SWITCH, CASE, BREAK, DEFAULT,\
        SCAN, PRINT, ATOI, ATOB, ATOF, TO_STRING, TRUE, FALSE, PLUS, MINUS, MULT, DIV, MOD, \
        COMMA, SEMICOLON, LBRACKET, RBRACKET, LBRACE, RBRACE, EQUAL, LESS, MORE, AND, OR, NOT, \
        EQUAL_EQUAL, LESS_OR_EQUAL, MORE_OR_EQUAL, NOT_EQUAL, \
        IDENTIFIER, NUM_INT, NUM_DOUBLE, STRING_LITERAL = range(45)

    TYPES_OF_TOKENS = (
        'INT', 'DOUBLE', 'BOOL', 'STRING', 'WHILE', 'FOR', 'IF', 'ELSE', 'SWITCH', 'CASE', 'BREAK', 'DEFAULT',
        'SCAN', 'PRINT', 'ATOI', 'ATOB', 'ATOF', 'TO_STRING', 'TRUE', 'FALSE', 'PLUS', 'MINUS', 'MULT', 'DIV', 'MOD',
        'COMMA', 'SEMICOLON', 'LBRACKET', 'RBRACKET', 'LBRACE', 'RBRACE', 'EQUAL', 'LESS', 'MORE', 'AND', 'OR', 'NOT',
        'EQUAL_EQUAL', 'LESS_OR_EQUAL', 'MORE_OR_EQUAL', 'NOT_EQUAL',
        'IDENTIFIER', 'NUM_INT', 'NUM_DOUBLE', 'STRING_LITERAL'
    )

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
        '==': EQUAL_EQUAL,
        '<': LESS,
        '<=': LESS_OR_EQUAL,
        '>': MORE,
        '>=': MORE_OR_EQUAL,
        '&&': AND,
        '||': OR,
        '!': NOT,
        '!=': NOT_EQUAL
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

    class LexerError(Exception):
        def __init__(self, message, line: int, index: int):
            self.message = message
            self.line = line
            self.index = index
            super().__init__(message)

    class Expected(LexerError):
        def __init__(self, sym: str, line: int, index: int):
            super().__init__(f"'{sym}' expected", line, index)

    class InvalidEscapeSequence(LexerError):
        def __init__(self, msg: str, line: int, index: int):
            """self.message = msg
            self.line = line
            self.index = index"""
            super().__init__(msg, line, index)

    class NoMatchingLeftBrace(LexerError):
        def __init__(self, line: int, index: int):
            """self.message = "no matching left brace"
            self.line = line
            self.index = index"""
            super().__init__("no matching left brace", line, index)

    class QuotesNotClosed(LexerError):
        def __init__(self, line: int, index: int):
            """self.message = "quotes not closed"
            self.line = line
            self.index = index"""
            super().__init__("quotes not closed", line, index)

    class UnknownSymbol(LexerError):
        def __init__(self, symbol: str, line: int, index: int):
            """self.line = line
            self.index = index
            self.message = "unknown symbol: " + symbol"""
            super().__init__("unknown symbol: " + symbol, line, index)

    class Token:
        def __init__(self, type, value, line: int, index: int):
            self.type = type
            self.value = value
            self.line = line
            self.index = index

    def __init__(self, file_name: str):
        with open(file_name) as f:
            self._program_text = f.read()

        self._curr_symbol_index = 0
        self._curr_line = 1
        self._curr_index_in_line = 1
        self._text_len = len(self._program_text) - 1

    def get_curr_symbol(self) -> str:
        return self._program_text[self._curr_symbol_index]

    def next_symbol(self):
        self._curr_symbol_index += 1

        if not self.program_finished():
            self._curr_index_in_line += 1

            if self.get_curr_symbol() == '\n':
                self._curr_line += 1
                self._curr_index_in_line = 0

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

        if curr_sym in ('&', '|'):
            # the next symbol must be the same (we don't have binary operations)
            line, index = self._curr_line, self._curr_index_in_line
            op_sym = curr_sym
            self.next_symbol()
            curr_sym = self.get_curr_symbol()

            if self.program_finished() or curr_sym != op_sym:
                raise Lexer.Expected(op_sym, self._curr_line, self._curr_index_in_line)

            op_sym += curr_sym
            next_tok = Lexer.Token(Lexer.SPECIAL_SYMBOLS[op_sym], None, line, index)
            self.next_symbol()
        elif curr_sym in ('>', '<', '!', '='):
            line, index = self._curr_line, self._curr_index_in_line

            # there can be a '=' after this
            op_sym = curr_sym
            self.next_symbol()
            curr_sym = self.get_curr_symbol()

            if self.program_finished() or curr_sym != '=':
                next_tok = Lexer.Token(Lexer.SPECIAL_SYMBOLS[op_sym], None, line, index)
            else:
                op_sym += curr_sym
                next_tok = Lexer.Token(Lexer.SPECIAL_SYMBOLS[op_sym], None, line, index)
                self.next_symbol()
        elif curr_sym in Lexer.SPECIAL_SYMBOLS.keys():
            line, index = self._curr_line, self._curr_index_in_line

            next_tok = Lexer.Token(Lexer.SPECIAL_SYMBOLS[curr_sym], None, line, index)
            self.next_symbol()
        elif curr_sym.isalpha():
            line, index = self._curr_line, self._curr_index_in_line

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
                next_tok = Lexer.Token(Lexer.KEYWORDS[word], None, line, index)
            else:
                # identifier
                # add WORD into the symbol table
                next_tok = Lexer.Token(Lexer.IDENTIFIER, word, line, index)
        elif curr_sym == '"':
            # string literal
            # next_tok = Lexer.Token(Lexer.STRING_LITERAL, "some raw string here")
            line, index = self._curr_line, self._curr_index_in_line

            string_literal = ""

            while True:
                self.next_symbol()
                if self.program_finished():
                    raise Lexer.QuotesNotClosed(line, index)

                curr_sym = self.get_curr_symbol()

                if curr_sym == '\\':
                    self.next_symbol()
                    if self.program_finished():
                        raise Lexer.QuotesNotClosed(line, index)
                    curr_sym = self.get_curr_symbol()
                    string_literal += '\\' + curr_sym
                    continue

                if curr_sym == '"':
                    self.next_symbol()
                    break

                string_literal += curr_sym

            try:
                _ = bytes(string_literal, "utf-8").decode("unicode_escape")
            except DeprecationWarning as err:
                err_str = str(err)
                msg = err_str[err_str.find("invalid escape sequence"):-1]
                raise Lexer.InvalidEscapeSequence(msg, line, index)

            next_tok = Lexer.Token(Lexer.STRING_LITERAL, string_literal, line, index)
        elif curr_sym.isdigit():
            line, index = self._curr_line, self._curr_index_in_line

            num_str = ""
            has_dot = False

            while True:
                num_str += curr_sym
                self.next_symbol()
                if self.program_finished():
                    break

                curr_sym = self.get_curr_symbol()

                if not curr_sym.isdigit() and curr_sym != '.':
                    break
                if curr_sym == '.':
                    if not has_dot:
                        has_dot = True
                    else:
                        break

            if has_dot:
                next_tok = Lexer.Token(Lexer.NUM_DOUBLE, num_str, line, index)
            else:
                next_tok = Lexer.Token(Lexer.NUM_INT, num_str, line, index)
        else:
            raise Lexer.UnknownSymbol(curr_sym, self._curr_line, self._curr_index_in_line)

        return next_tok

    def index_in_sym_table(self, sym_table: List[Symbol], sym: Symbol) -> int:
        index = 0

        for s in sym_table:
            if s.scope == sym.scope and s.identifier == sym.identifier:
                # they are variables with the same name in the same scope
                return index
            index += 1

        return -1

    def create_symbol_table(self, tokens: List[Token]) -> List[Symbol]:
        # change the list of tokens so the value for identifiers will be an index in the symbol table
        sym_table = []
        level_of_nesting: int = 0
        block_numbers = [0]

        for token in tokens:
            if token.type == Lexer.IDENTIFIER:
                symbol_block_id = str(level_of_nesting) + " " + str(block_numbers[level_of_nesting])

                symbol = Symbol(token.value, symbol_block_id, None)
                index = self.index_in_sym_table(sym_table, symbol)

                if index < 0:
                    # add the symbol to sym_table
                    sym_table.append(symbol)
                    index = len(sym_table) - 1

                token.value = index
            elif token.type == Lexer.LBRACE:
                level_of_nesting += 1
                if level_of_nesting >= len(block_numbers):
                    block_numbers.append(0)
                else:
                    block_numbers[level_of_nesting] += 1
            elif token.type == Lexer.RBRACE:
                level_of_nesting -= 1

                if level_of_nesting < 0:
                    raise Lexer.NoMatchingLeftBrace(token.line, token.index)

        return sym_table

    def split_program_into_tokens(self) -> List[Token]:
        ret = []

        while True:
            try:
                ret.append(self.get_next_token())
            except Lexer.NoMoreTokens:
                break
            except Lexer.LexerError as err:
                print(f"LEXER ERROR:\n\t{err.message} ({err.line}:{err.index})")
                sys.exit(1)

        """
        try:
            symbol_table = self.create_symbol_table(ret)
        except Lexer.NoMatchingLeftBrace as err:
            print(f"LEXER ERROR:\n\t{err.message} ({err.line}:{err.index})")
            sys.exit(1)
        """

        return ret
