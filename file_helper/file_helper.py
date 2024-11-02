import os
from shutil import copy2
from multiprocessing import Pool
from typing import List, Optional


def get_file_paths(path: str, show_errors: bool=True) -> List[str]:
    paths_list = []
    def get_nested_paths(path: str=path, show_errors: bool=show_errors) -> None:
        errors = ''
        try:
            items = os.listdir(path)
            for item in items:
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path):
                    paths_list.append(item_path)
                else:
                    get_nested_paths(item_path, show_errors=show_errors)
        except PermissionError:
            errors += f'Permission is denied for {path}\n'
        except FileNotFoundError:
            errors += f'Failed to find path: {path}\n'
        except Exception as e:
            errors += f'{type(e).__name__}: {str(e)}\n'
        if show_errors and errors:
            print(f'\n{errors}')
    get_nested_paths()
    return paths_list



def get_dir_paths(path: str, ascending: bool=True, include_root_dir: bool=False, show_errors: bool=True) -> List[str]:
    paths_list = [path] if include_root_dir else []
    def get_nested_paths(path: str=path, show_errors: bool=show_errors) -> None:
        errors = ''
        try:
            items = os.listdir(path)
            for item in items:
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    paths_list.append(item_path)
                    get_nested_paths(item_path, show_errors=show_errors)
        except PermissionError:
            errors += f'Permission is denied for {path}\n'
        except FileNotFoundError:
            errors += f'Failed to find path: {path}\n'
        except Exception as e:
            errors += f'{type(e).__name__}: {str(e)}\n'
        if show_errors and errors:
            print(f'\n{errors}')
    get_nested_paths()
    if ascending:
        paths_list.reverse()
    return paths_list
            


def delete_single_file(path: str, show_errors: bool=True) -> None:
    error = None
    try:
        os.remove(path)
    except PermissionError:
        error = f'Permission is denied for {path}\n'
    except FileNotFoundError:
        error = f'Failed to find path: {path}\n'
    except Exception as e:
        error = f'{type(e).__name__}: {str(e)}\n'
    if show_errors and error:
        print(f'\n{error}')
        


def delete_directory(path: str, include_root_dir: bool=True, show_errors: bool=True) -> None:
    errors = ''
    delete_single_file_args = [(file_path, show_errors) for file_path in get_file_paths(path, show_errors=show_errors)]
    with Pool() as pool:
        pool.starmap(delete_single_file, delete_single_file_args)
    for path in get_dir_paths(path, include_root_dir=include_root_dir, show_errors=show_errors):
        try:
            os.rmdir(path)
        except OSError:
            errors += f'The directory should be empty for deletion: {path}\n'
        except PermissionError:
            errors += f'Permission is denied for {path}\n'
        except Exception as e:
            errors += f'{type(e).__name__}: {str(e)}\n'
    if show_errors and errors:
        print(f'\n{errors}')
    
    
    
def delete_item() -> None:
    path = input('Enter item path: ')
    if os.path.exists(path):
        if os.path.isdir(path):
            print('Removing directory...')
            delete_directory(path)
        elif os.path.isfile(path):
            print('Removing file...')
            delete_single_file(path)
    else:
        input('\nThe item path does not exists\n')
    


def copy_single_item(source: str, destination: str, source_main_dir: Optional[str]=None) -> None:
    error = None
    if source_main_dir:
        list_path = source.split(os.sep)
        destination = os.path.join(destination, *(list_path[list_path.index(source_main_dir) + 1:-1]))
    try:
        os.makedirs(destination, exist_ok=True)
        if os.path.isfile(source):
            copy2(source, destination)
    except PermissionError:
        error = f'Permission error occured while copying: {source}\n'
    except FileNotFoundError:
        error = f'Failed to find path: source - {source} Or destination - {destination}\n'
    except Exception as e:
        error = f'{type(e).__name__}: {str(e)}'
    if error:
        print(f'\n{error}')
        
    

def copy_directory(source: str, destination: str) -> None:
    source_main_dir = source.split(os.sep)[-1]
    copy_single_item_args = [(path, destination, source_main_dir) for path in get_dir_paths(source, ascending=False)]
    copy_single_item_args += [(path, destination, source_main_dir) for path in get_file_paths(source)]
    with Pool() as pool:
        pool.starmap(copy_single_item, copy_single_item_args)



def copy_item() -> None:
    source = input('Enter the source path: ').rstrip(os.sep)
    destination = input('Enter the destination path: ')
    if os.path.exists(source):
        os.makedirs(destination, exist_ok=True)
        if os.path.isdir(source):
            print('Copying directory...')
            copy_directory(source, destination)
        elif os.path.isfile(source):
            print('Copying file...')
            copy_single_item(source, destination)
    else:
        input('\nThe source path does not exists\n')



def copy_downloads() -> None:
    current_login = os.getlogin()
    current_drive = os.getcwd()[0]
    source = f'{current_drive}:\\Users\\{current_login}\\Downloads'
    destination = f'{current_drive}:\\Users\\{current_login}\\Documents\\Downloads_Copy'
    if os.path.exists(destination):
        print('Removing Downloads_Copy...')
        delete_directory(destination)
    print('Copying Downloads...')
    os.makedirs(destination, exist_ok=True)
    copy_directory(source, destination)



def remove_temp_files() -> None:
    current_login = os.getlogin()
    current_drive = os.getcwd()[0]
    temp_files_paths = [
        f'{current_drive}:\\Users\\{current_login}\\AppData\\Local\\Temp',
        f'{current_drive}:\\Windows\\Temp' 
    ]
    print('Removing Temporary files...')
    for temp_files_path in temp_files_paths:
        delete_directory(temp_files_path, include_root_dir=False, show_errors=False)
    input('Temporary files removed')



def main() -> None:
    print('\n\nFile Helper\n---- -------\n')
    separator = '===' * 20
    interface = f'''\nType <Drive>:{os.sep} when providing only <Drive> as input\n\nSelect serial no. OR "e" to Exit
1. Copy Downloads
2. Remove Temp Files
3. Copy Item
4. Delete Item'''
    while True:
        print(interface)
        user_choice = input('\nEnter your choice: ')
        match user_choice:
            case 'e':
                exit()
            case '1':
                copy_downloads()
            case '2':
                remove_temp_files()
            case '3':
                copy_item()
            case '4':
                delete_item()
            case _:
                input('Invalid Choice')
        print(separator)



if __name__ == '__main__':
    main()
