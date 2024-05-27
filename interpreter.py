from typing import Any, Dict, List, Callable, Union

Node = List[Any]
VariableType = Union[int, float, str, bool, List[Any], Dict[Any, Any]]
FunctionType = Callable[[List[Any]], Any]


class Interpreter:
    def __init__(self):
        self.vars: Dict[str, VariableType] = {}
        self.functions: Dict[str, FunctionType] = {
            'NÖVEL': self.inbuilt_novel
        }

    def inbuilt_novel(self, args: List[Node]) -> Union[int, float]:
        if len(args) != 2:
            self.error("A NÖVEL két argumentumot vár.")
        value, increment = self.eval(args[0]), self.eval(args[1])
        if not all(isinstance(num, (int, float)) for num in (value, increment)):
            self.error("A NÖVEL numerikus argumentumokat vár.")
        return value + increment

    def eval(self, node: Node) -> Any:
        operations = {
            'assign': self.assign_variable,
            'list_assign': self.assign_list,
            'dict_assign': self.assign_dictionary,
            'call': self.call_function,
            'print': self.print_value,
            'number': lambda x: int(x[1]),
            'float': lambda x: float(x[1]),
            'string': lambda x: x[1],
            'boolean': lambda x: x[1],
            'var': self.access_variable,
            'index': self.access_index,
            'MEG': self.add,
            '+': self.add,
            'KIVON': self.subtract,
            '-': self.subtract,
            'SZOR': self.multiply,
            '*': self.multiply,
            'OSZT': self.divide,
            '/': self.divide,
            'UGYANAZ': self.equal,
            'NEM UGYANAZ': self.not_equal,
            'KISEBB': self.less_than,
            'NAGYOBB': self.greater_than,
            'if': self.if_statement,
            'for': self.for_loop,
            'foreach': self.foreach_loop,
            'while': self.while_loop,
            'do_while': self.do_while_loop,
            'function': self.define_function,
            'return': lambda x: self.eval(x[1])
        }
        if node[0] in operations:
            return operations[node[0]](node)
        else:
            self.error(f'Ismeretlen utasítás: {node[0]}')

    def assign_variable(self, node: Node) -> None:
        var_type, var_name, expr = node[1], node[2], node[3]
        value = self.eval(expr)
        expected_type = {'SZÁM': (int, float), 'SZÖVEG': str, 'LOGIKAI': bool}.get(var_type, None)
        if not isinstance(value, expected_type):
            self.error(f'Típus hiba a változónál: {var_name}')
        self.vars[var_name] = value

    def assign_list(self, node: Node) -> None:
        elem_type, var_name, elements = node[1], node[2], node[3]
        values = [self.eval(elem) for elem in elements]
        expected_type = {'SZÁM': (int, float), 'SZÖVEG': str}.get(elem_type, None)
        if not all(isinstance(value, expected_type) for value in values):
            self.error(f'Típus hiba a listánál: {var_name}')
        self.vars[var_name] = values

    def assign_dictionary(self, node: Node) -> None:
        key_type, value_type, var_name, elements = node[1], node[2], node[3], node[4]
        values = {k: self.eval(v) for k, v in elements.items()}
        expected_value_type = {'SZÁM': (int, float), 'SZÖVEG': str}.get(value_type, None)
        if not all(isinstance(v, expected_value_type) for v in values.values()):
            self.error(f'Típus hiba a szótárnál: {var_name}')
        self.vars[var_name] = values

    def call_function(self, node: Node) -> Any:
        func_name, args = node[1], node[2]
        if func_name == 'KIÍR':
            print(self.eval(args[0]))
        elif func_name == 'HOSSZ':
            arg = self.eval(args[0])
            if isinstance(arg, (str, list, dict)):
                return len(arg)
            else:
                self.error('A HOSSZ csak szövegekre, listákra és szótárakra hívható.')
        elif func_name in self.functions and callable(self.functions[func_name]):
            return self.functions[func_name](args)
        elif func_name in self.functions:
            return self.call_user_defined_function(func_name, args)
        else:
            self.error(f'Ismeretlen függvény: {func_name}')

    def call_user_defined_function(self, func_name: str, args: List[Node]) -> Any:
        func_params, func_return_type, func_body = self.functions[func_name]
        local_vars = self.vars.copy()
        for (param_type, param_name), arg in zip(func_params, args):
            local_vars[param_name] = self.eval(arg)
        old_vars = self.vars
        self.vars = local_vars
        result = None
        for stmt in func_body:
            if stmt[0] == 'return':
                result = self.eval(stmt[1])
                break
            else:
                self.eval(stmt)
        self.vars = old_vars
        if not isinstance(result, {'SZÁM': (int, float), 'SZÖVEG': str, 'LOGIKAI': bool, 'SEMMI': type(None)}.get(func_return_type, None)):
            self.error(f'Típus hiba a függvény visszatérési értékénél: {func_name}')
        return result

    def print_value(self, node: Node) -> None:
        print(self.eval(node[1]))

    def access_variable(self, node: Node) -> Any:
        return self.vars.get(node[1], 0)

    def access_index(self, node: Node) -> Any:
        var_name, index = node[1], self.eval(node[2])
        container = self.vars.get(var_name, [])
        if isinstance(index, int) and isinstance(container, list) and 0 <= index < len(container):
            return container[index]
        elif isinstance(index, str) and isinstance(container, dict):
            return container.get(index, 0)
        else:
            self.error(f'Érvénytelen index vagy változó: {var_name}')

    def add(self, node: Node) -> Any:
        left, right = self.eval(node[1]), self.eval(node[2])
        if isinstance(left, str) and isinstance(right, str):
            return left + right
        elif isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left + right
        else:
            self.error('Nem lehet szöveget és számot összefűzni.')

    def subtract(self, node: Node) -> Union[int, float]:
        left, right = self.eval(node[1]), self.eval(node[2])
        return left - right

    def multiply(self, node: Node) -> Union[int, float]:
        left, right = self.eval(node[1]), self.eval(node[2])
        return left * right

    def divide(self, node: Node) -> float:
        left, right = self.eval(node[1]), self.eval(node[2])
        return left / right

    def equal(self, node: Node) -> bool:
        return self.eval(node[1]) == self.eval(node[2])

    def not_equal(self, node: Node) -> bool:
        return self.eval(node[1]) != self.eval(node[2])

    def less_than(self, node: Node) -> bool:
        return self.eval(node[1]) < self.eval(node[2])

    def greater_than(self, node: Node) -> bool:
        return self.eval(node[1]) > self.eval(node[2])

    def if_statement(self, node: Node) -> None:
        condition, true_branch, false_branch = node[1], node[2], node[3]
        if self.eval(condition):
            for stmt in true_branch:
                self.eval(stmt)
        else:
            for branch in false_branch:
                if branch[0] == 'elif' and self.eval(branch[1]):
                    for stmt in branch[2]:
                        self.eval(stmt)
                    break
                elif branch[0] == 'else':
                    for stmt in branch[1]:
                        self.eval(stmt)
                    break

    def for_loop(self, node: Node) -> None:
        init_type, var_name, init_value, condition, update, body = node[1], node[2], node[3], node[4], node[5], node[6]
        self.vars[var_name] = self.eval(init_value)
        while self.eval(condition):
            for stmt in body:
                self.eval(stmt)
            self.vars[var_name] = self.eval(update)

    def foreach_loop(self, node: Node) -> None:
        var_name, container, body = node[1], node[2], node[3]
        container_val = self.vars.get(container, [])
        if isinstance(container_val, list):
            for item in container_val:
                self.vars[var_name] = item
                for stmt in body:
                    self.eval(stmt)
        elif isinstance(container_val, dict):
            for key, value in container_val.items():
                self.vars[var_name] = {key: value}
                for stmt in body:
                    self.eval(stmt)

    def while_loop(self, node: Node) -> None:
        condition, body = node[1], node[2]
        while self.eval(condition):
            for stmt in body:
                self.eval(stmt)

    def do_while_loop(self, node: Node) -> None:
        body, condition = node[1], node[2]
        while True:
            for stmt in body:
                self.eval(stmt)
            if not self.eval(condition):
                break

    def define_function(self, node: Node) -> None:
        func_name, params, return_type, body = node[1], node[2], node[3], node[4]
        self.functions[func_name] = (params, return_type, body)

    def error(self, message: str) -> None:
        raise RuntimeError(f'Hiba: {message}')
