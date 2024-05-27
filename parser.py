from typing import List, Tuple, Any, Dict

Token = Tuple[str, str, int, int]  # Token type: (type, value, line, column)
Node = Any  # Define node as any for now


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> List[Node]:
        return self.program()

    def program(self) -> List[Node]:
        statements = []
        while self.pos < len(self.tokens):
            statements.append(self.statement())
        return statements

    def statement(self) -> Node:
        token = self.tokens[self.pos]
        if token[1] == 'RENDEL':
            return self.parse_variable_declaration()
        elif token[1] == 'UTASÍTÁSOK':
            return self.parse_function_declaration()
        elif token[1] == 'MEGHÍV':
            return self.parse_function_call()
        elif token[1] == 'HA':
            return self.parse_if_statement()
        elif token[1] == 'CIKLUS':
            return self.parse_for_loop()
        elif token[1] == 'MINDEGYIKEN':
            return self.parse_foreach_loop()
        elif token[1] == 'AMÍG':
            return self.parse_while_loop()
        elif token[1] == 'UTÁNA':
            return self.parse_do_while_loop()
        elif token[1] == 'VISSZAAD':
            return self.parse_return_statement()
        else:
            self.error(f'Váratlan token: {token}')

    def parse_variable_declaration(self) -> Node:
        self.pos += 1
        if self.tokens[self.pos][1] == 'LISTA':
            return self.parse_list_declaration()
        elif self.tokens[self.pos][1] == 'ÉRTÉKPÁR':
            return self.parse_dict_declaration()
        else:
            var_type = self.expect('KEYWORD')[1]  # SZÁM, SZÖVEG, or LOGIKAI
            var = self.expect('ID')[1]
            self.expect('ASSIGN')
            expr = self.expression()
            self.expect('END')
            return ('assign', var_type, var, expr)

    def parse_list_declaration(self) -> Node:
        self.pos += 1
        self.expect('LESS')
        elem_type = self.expect('KEYWORD')[1]
        self.expect('GREATER')
        var = self.expect('ID')[1]
        self.expect('ASSIGN')
        self.expect('LBRACKET')
        elements = []
        while self.tokens[self.pos][0] != 'RBRACKET':
            elements.append(self.expression())
            if self.tokens[self.pos][0] == 'COMMA':
                self.pos += 1
        self.pos += 1  # Skip RBRACKET
        self.expect('END')
        return ('list_assign', elem_type, var, elements)

    def parse_dict_declaration(self) -> Node:
        self.pos += 1
        self.expect('LESS')
        key_type = self.expect('KEYWORD')[1]
        self.expect('COMMA')
        value_type = self.expect('KEYWORD')[1]
        self.expect('GREATER')
        var = self.expect('ID')[1]
        self.expect('ASSIGN')
        self.expect('LBRACE')
        elements = {}
        while self.tokens[self.pos][0] != 'RBRACE':
            key = self.expect('STRING')[1][1:-1]  # Remove quotes
            self.expect('COLON')
            value = self.expression()
            elements[key] = value
            if self.tokens[self.pos][0] == 'COMMA':
                self.pos += 1
        self.pos += 1  # Skip RBRACE
        self.expect('END')
        return ('dict_assign', key_type, value_type, var, elements)

    def parse_function_declaration(self) -> Node:
        self.pos += 1
        func_name = self.expect('ID')[1]
        self.expect('LPAREN')
        params = []
        while self.tokens[self.pos][0] != 'RPAREN':
            param_type = self.expect('KEYWORD')[1]
            if param_type == 'LISTA':
                self.expect('LESS')
                elem_type = self.expect('KEYWORD')[1]
                self.expect('GREATER')
                param_type = f'LISTA<{elem_type}>'
            elif param_type == 'ÉRTÉKPÁR':
                self.expect('LESS')
                key_type = self.expect('KEYWORD')[1]
                self.expect('COMMA')
                value_type = self.expect('KEYWORD')[1]
                self.expect('GREATER')
                param_type = f'ÉRTÉKPÁR<{key_type},{value_type}>'
            param_name = self.expect('ID')[1]
            params.append((param_type, param_name))
            if self.tokens[self.pos][0] == 'COMMA':
                self.pos += 1
        self.pos += 1  # Skip RPAREN
        self.expect('VISSZATÉR')
        return_type = self.expect('KEYWORD')[1]
        self.expect('LBRACE')
        body = []
        while self.tokens[self.pos][0] != 'RBRACE':
            body.append(self.statement())
        self.pos += 1  # Skip RBRACE
        self.expect('END')
        return ('function', func_name, params, return_type, body)

    def parse_function_call(self) -> Node:
        self.pos += 1
        func_name = self.expect('ID')[1] if self.tokens[self.pos][0] == 'ID' else self.expect('KEYWORD')[1]
        self.expect('LPAREN')
        args = []
        while self.tokens[self.pos][0] != 'RPAREN':
            args.append(self.expression())
            if self.tokens[self.pos][0] == 'COMMA':
                self.pos += 1
        self.pos += 1  # Skip RPAREN
        self.expect('END')
        return ('call', func_name, args)

    def parse_if_statement(self) -> Node:
        self.pos += 1
        condition = self.expression()
        self.expect('AKKOR')
        true_branch = self.parse_block()
        false_branch = []

        # Handle elif and else branches
        while self.pos < len(self.tokens) and self.tokens[self.pos][1] in ('KÜLÖNBEN', 'VÉGÜL'):
            if self.tokens[self.pos][1] == 'KÜLÖNBEN':
                self.pos += 1
                if self.tokens[self.pos][0] != 'AKKOR':
                    condition = self.expression()
                    self.expect('AKKOR')
                false_branch.append(('elif', condition, self.parse_block()))
            elif self.tokens[self.pos][1] == 'VÉGÜL':
                self.pos += 1
                self.expect('AKKOR')
                false_branch.append(('else', self.parse_block()))

        self.expect('END')
        return ('if', condition, true_branch, false_branch)

    def parse_for_loop(self) -> Node:
        self.pos += 1
        self.expect('LPAREN')
        init_type = self.expect('KEYWORD')[1]
        var_name = self.expect('ID')[1]
        self.expect('ASSIGN')
        init_value = self.expression()
        self.expect('END')
        condition = self.expression()
        self.expect('END')
        update = self.expression()
        self.expect('RPAREN')
        body = self.parse_block()
        self.expect('END')  # Expect END after the block
        return ('for', init_type, var_name, init_value, condition, update, body)

    def parse_foreach_loop(self) -> Node:
        self.pos += 1
        self.expect('LPAREN')
        var_name = self.expect('ID')[1]
        self.expect('BENNE')
        container = self.expect('ID')[1]
        self.expect('RPAREN')
        body = self.parse_block()
        self.expect('END')  # Expect END after the block
        return ('foreach', var_name, container, body)

    def parse_while_loop(self) -> Node:
        self.pos += 1
        self.expect('LPAREN')
        condition = self.expression()
        self.expect('RPAREN')
        body = self.parse_block()
        self.expect('END')  # Expect END after the block
        return ('while', condition, body)

    def parse_do_while_loop(self) -> Node:
        self.pos += 1
        body = self.parse_block()
        self.expect('AMÍG')
        self.expect('LPAREN')
        condition = self.expression()
        self.expect('RPAREN')
        self.expect('END')  # Expect END after the block
        return ('do_while', body, condition)

    def parse_return_statement(self) -> Node:
        self.pos += 1
        expr = self.expression()
        self.expect('END')
        return ('return', expr)

    def parse_block(self) -> List[Node]:
        statements = []
        if self.tokens[self.pos][0] == 'LBRACE':
            self.pos += 1
            while self.tokens[self.pos][0] != 'RBRACE':
                statements.append(self.statement())
            self.pos += 1  # Skip RBRACE
        else:
            statements.append(self.statement())
        return statements

    def expression(self) -> Node:
        left = self.term()
        while self.pos < len(self.tokens) and self.tokens[self.pos][1] in ('MEG', '+', 'KIVON', '-', 'SZOR', '*', 'OSZT', '/', 'NEM', 'EGYENLŐ', 'UGYANAZ', 'KISEBB', 'NAGYOBB'):
            op = self.tokens[self.pos][1]
            self.pos += 1
            if op == 'NEM' and self.tokens[self.pos][1] == 'UGYANAZ':
                self.pos += 1
                op = 'NEM UGYANAZ'
            right = self.term()
            left = (op, left, right)
        return left

    def term(self) -> Node:
        left = self.factor()
        while self.pos < len(self.tokens) and self.tokens[self.pos][1] in ('SZOR', '*', 'OSZT', '/'):
            op = self.tokens[self.pos][1]
            self.pos += 1
            right = self.factor()
            left = (op, left, right)
        return left

    def factor(self) -> Node:
        token = self.tokens[self.pos]
        if token[0] == 'NUMBER':
            self.pos += 1
            if '.' in token[1]:
                return ('float', float(token[1]))
            else:
                return ('number', int(token[1]))
        elif token[0] == 'STRING':
            self.pos += 1
            return ('string', token[1][1:-1])  # Remove quotes
        elif token[0] == 'KEYWORD' and token[1] in ('LIGAZ', 'LHAMIS'):
            self.pos += 1
            return ('boolean', token[1] == 'LIGAZ')
        elif token[0] == 'ID':
            self.pos += 1
            if self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'LBRACKET':
                self.pos += 1
                index = self.expression()
                self.expect('RBRACKET')
                return ('index', token[1], index)
            elif self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'LPAREN':
                self.pos += 1
                args = []
                while self.tokens[self.pos][0] != 'RPAREN':
                    args.append(self.expression())
                    if self.tokens[self.pos][0] == 'COMMA':
                        self.pos += 1
                self.pos += 1  # Skip RPAREN
                return ('call', token[1], args)
            return ('var', token[1])
        elif token[1] == 'MEGHÍV':
            self.pos += 1
            func_name = self.expect('ID')[1] if self.tokens[self.pos][0] == 'ID' else self.expect('KEYWORD')[1]
            self.expect('LPAREN')
            args = []
            while self.tokens[self.pos][0] != 'RPAREN':
                args.append(self.expression())
                if self.tokens[self.pos][0] == 'COMMA':
                    self.pos += 1
            self.pos += 1  # Skip RPAREN
            return ('call', func_name, args)
        elif token[0] == 'LPAREN':
            self.pos += 1
            expr = self.expression()
            self.expect('RPAREN')
            return expr
        else:
            self.error(f'Váratlan token: {token}')

    def expect(self, kind: str) -> Token:
        token = self.tokens[self.pos]
        if token[0] != kind and token[1] != kind:
            self.error(f'Elvárt {kind}, de kapott {token}')
        self.pos += 1
        return token

    def error(self, message: str) -> None:
        token = self.tokens[self.pos]
        raise RuntimeError(f'Hiba: {message} a sorban {token[2]}, oszlopban {token[3]}')
