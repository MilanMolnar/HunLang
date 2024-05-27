import re
from tokens import TOKEN_SPECIFICATION


def lex(code: str):
    tokens = []
    line_num = 1
    line_start = 0
    for mo in re.finditer('|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPECIFICATION), code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start
        if kind == 'NEWLINE':
            line_start = mo.end()
            line_num += 1
        elif kind == 'SKIP' or kind == 'COMMENT':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Syntax error: unexpected character {value!r} at line {line_num}, column {column}')
        else:
            tokens.append((kind, value, line_num, column))
    return tokens
