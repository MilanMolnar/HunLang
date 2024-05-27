TOKEN_SPECIFICATION = [
    ('COMMENT', r'€.*'),                       # Comments
    ('KEYWORD', r'RENDEL|SZÁM|SZÖVEG|LISTA|ÉRTÉKPÁR|LOGIKAI|HA|KÜLÖNBEN|VÉGÜL|AKKOR|UTASÍTÁSOK|VISSZATÉR|VISSZAAD|MEGHÍV|CIKLUS|HOSSZ|KISEBB|NAGYOBB|NÖVEL|AMÍG|NEM|UTÁNA|SEMMI|UGYANAZ|LIGAZ|LHAMIS|MINDEGYIKEN|BENNE'),  # Keywords
    ('NUMBER', r'\d+(\.\d*)?'),               # Integer or decimal number
    ('STRING', r'"[^"]*"'),                   # String literals
    ('ASSIGN', r'EGYENLŐ|='),                 # Assignment operator
    ('END', r'VEGE|VÉGE|;'),                  # Statement terminator
    ('ID', r'[A-Za-z_áéíóöőúüűÍÖÜÓŐÚÉÁŰ]+'),  # Identifiers
    ('OP', r'MEG|\+|KIVON|-|SZOR|\*|OSZT|/'), # Operators: plus, minus, multiply, divide
    ('LBRACKET', r'\['),                      # Left bracket
    ('RBRACKET', r'\]'),                      # Right bracket
    ('LBRACE', r'\{'),                        # Left brace
    ('RBRACE', r'\}'),                        # Right brace
    ('LPAREN', r'\('),                        # Left parenthesis
    ('RPAREN', r'\)'),                        # Right parenthesis
    ('LESS', r'<'),                           # Less than
    ('GREATER', r'>'),                        # Greater than
    ('COMMA', r','),                          # Comma
    ('COLON', r':'),                          # Colon (for dictionary)
    ('SEMICOLON', r';'),                      # Semicolon
    ('SKIP', r'[ \t]'),                       # Skip over spaces and tabs
    ('NEWLINE', r'\n'),                       # Line endings
    ('MISMATCH', r'.'),                       # Any other character
]
