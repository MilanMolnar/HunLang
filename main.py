import sys
from lexer import lex
from parser import Parser
from interpreter import Interpreter
import io


test_code = 'MEGHÍV KIÍR("TEST") VÉGE'


def run(file_path):
    if not file_path.endswith(".hun"):
        print("Invalid file type. Please provide a .hun file.")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return

    try:
        tokens = lex(code)
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = Interpreter()

        for stmt in ast:
            interpreter.eval(stmt)
    except RuntimeError as e:
        print(e)


def run_str(code: str = test_code):  # for webapp collect standard output and return it for visualization
    # Create a StringIO object to capture output
    output = io.StringIO()

    # Save the current state of sys.stdout
    original_stdout = sys.stdout

    # Redirect stdout to the StringIO object
    sys.stdout = output
    try:
        tokens = lex(code)
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = Interpreter()

        for stmt in ast:
            interpreter.eval(stmt)
    except RuntimeError as e:
        print(e)
    # Restore stdout to its original state
    sys.stdout = original_stdout

    # Get all printed content from the buffer
    result = output.getvalue()

    # Close the StringIO object
    output.close()

    return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <file.hun>")
    else:
        run(sys.argv[1])
