from json import load
from subprocess import run


interpreter_path_file = 'interpreter_path.json'


def get_interpreter_path() -> None:
    with open(interpreter_path_file, 'r') as file:
        data = load(file)
    interpreter_path = data['default_interpreter_path']
    return interpreter_path
    


def main() -> None:
    try:
        interpreter_path = get_interpreter_path()
        if interpreter_path:
            main_file = 'suggestioner.py'
            command = [interpreter_path, main_file]
            run(command)
        else:
            input(f'Interpreter path not found from the file: {interpreter_path_file}')
    except:
        input(f'There is something wrong with the file: {interpreter_path_file}')
        


if __name__ == '__main__':
    main()