import tkinter as tk
import typing
import jedi


def load_pyfile_code(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content.strip()
    except FileNotFoundError:
        print(f'File could not be found: {pyfile}')
    except PermissionError:
        print(f'Permission Denied for {pyfile}')
    except Exception as e:
        print(f'{type(e).__name__}: {str(e)}')
    return ''



def get_suggestions(pyfile: str, interpreter_path: str) -> dict:
    completions = {}
    try:
        py_script = jedi.Script(code=load_pyfile_code(path=pyfile), environment=jedi.create_environment(interpreter_path) if interpreter_path else None)
        script_completions = py_script.complete()
        for script_completion in script_completions:
            completion_type = script_completion.type
            completions_dict_key = f'{script_completion.name}     [{completion_type}]'
            if completion_type not in ('statement', 'keyword'):
                docstring = script_completion.docstring(raw=True)
                signatures = script_completion.get_signatures()
                completions[completions_dict_key] = ([signature.to_string() for signature in signatures], docstring)
            else:
                completions[completions_dict_key] = ([None], None)
    except jedi.api.environment.InvalidPythonEnvironment as e:
        print(f'Failed to get environment, {str(e)}')
    except Exception as e:
        print(f'{type(e).__name__}: {str(e)}')
    return completions



def create_button(btn_frame: tk.Frame, text: str, command: typing.Callable[[], None], column: int) -> None:
    btn = tk.Button(btn_frame, text=text, command=command)
    btn.grid(row=0, column=column)



def main():
    print('\n\nSuggestioner\n------------\n\nPress "e" anywhere to Exit\n')
    while True:
        pyfile = input('\nEnter python file path: ')
        interpreter_path = input('Enter interpreter root directory path [If Not Given Current Env Will Be Used]: ')
        suggestions = None
        if "e" in (pyfile, interpreter_path):
            break

        def load_list() -> None:
            nonlocal suggestions
            suggestions = get_suggestions(pyfile=pyfile, interpreter_path=interpreter_path)
            tk_list.delete(0, tk.END)
            for suggestion in suggestions:
                tk_list.insert(tk.END, suggestion)

        def show_selected_item_details(event) -> None:
            index = tk_list.curselection()
            if index:
                item = tk_list.get(index)
                signatures_list, docstring = suggestions[item]
                if not signatures_list:
                    signatures_list.append(None)
                final_details_show = 'SIGNATURE\n\n'
                for signature in signatures_list:
                    final_details_show += f'{signature}' if signature else '[Not Available]'
                    final_details_show += '\n\n'
                final_details_show += f'\nDOCSTRING\n\n'
                final_details_show += f'{docstring}' if docstring else '[Not Available]'
                tk_text_widget.configure(state='normal')
                tk_text_widget.delete('0.1', tk.END)
                tk_text_widget.insert('0.1', final_details_show)
                tk_text_widget.configure(state='disabled')

        def list_scroll(direction: str) -> None:
            if direction == 'up':
                tk_list.yview_scroll(1, 'units')
            elif direction == 'down':
                tk_list.yview_scroll(-1, 'units')
            elif direction == 'right':
                tk_list.xview_scroll(1, 'units')
            elif direction == 'left':
                tk_list.xview_scroll(-1, 'units')

        def text_widget_scroll(direction: str) -> None:
            if direction == 'down':
                tk_text_widget.yview_scroll(-1, 'units')
            elif direction == 'up':
                tk_text_widget.yview_scroll(1, 'units')

        window = tk.Tk()
        window.geometry('420x600')
        window.title('Suggestioner')

        btn_frame = tk.Frame(window)
        btn_frame.pack()
        for btn_text, btn_command, btn_column in [['load', load_list, 0], ['down', lambda: list_scroll('down'), 1], ['up', lambda: list_scroll('up'), 2], ['left', lambda: list_scroll('left'), 3], ['right', lambda: list_scroll('right'), 4]]:
            create_button(btn_frame=btn_frame, text=btn_text, command=btn_command, column=btn_column)

        tk_list = tk.Listbox(window, height=22, width=40)
        tk_list.pack(pady=(0, 20))
        tk_list.bind('<<ListboxSelect>>', show_selected_item_details)

        text_widget_btn_frame = tk.Frame(window)
        text_widget_btn_frame.pack()
        for btn_text, btn_command, btn_column in [['down', lambda: text_widget_scroll('down'), 0], ['up', lambda: text_widget_scroll('up'), 1]]:
            create_button(btn_frame=text_widget_btn_frame, text=btn_text, command=btn_command, column=btn_column)

        tk_text_widget = tk.Text(window)
        tk_text_widget.pack(fill=tk.BOTH, expand=True)
        tk_text_widget.configure(font=('TkDefaultFont', 11))
        window.mainloop()

if __name__ == '__main__':
    main()