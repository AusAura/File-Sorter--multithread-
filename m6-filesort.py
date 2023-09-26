from pathlib import Path
import argparse, re, shutil

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--source', required=True, help='Source folder')
# parser.add_argument('-d', '--destination', default='_SORTED')
ARGUMENTS = vars(parser.parse_args()) 
ARGUMENTS['source'] = Path(ARGUMENTS['source'])
ARGUMENTS['destination'] = ARGUMENTS['source']
# ARGUMENTS['destination'] = Path(ARGUMENTS['destination'])

def main(folder_name: str) -> None:

    SORT_FOLDERS_LIST = {
        'zip': 'archives',
        'gz': 'archives',
        'tar': 'archives',
        'jpeg': 'images',
        'png': 'images',
        'jpg': 'images',
        'svg': 'images',
        'avi': 'video',
        'mp4': 'video',
        'mov': 'video',
        'mkv': 'video',
        'doc': 'documents',
        'docx': 'documents',
        'txt': 'documents',
        'pdf': 'documents',
        'xlsx': 'documents',
        'pptx': 'documents',
        'mp3': 'music',
        'ogg': 'music',
        'wav': 'music',
        'amr': 'music',
    }
    file_list_per_category = {
        'archives': [],
        'images': [],
        'video': [],
        'documents': [],
        'music': [],
        'unknown': [],
    }   

    while True:
        try:
            is_unknown_sorted = int(input('Master, should I move the files of uknown type? (0 - No, 1 - Yes): '))
        except TypeError:
            print(f'I do not understand!')
        except ValueError:
            print(f'I do not understand!')       
        else:
            break 
    
    print('STARTED')

    try:
        file_list_per_category, sort_unknown_list, sort_known_list = dir_walk(folder_name, SORT_FOLDERS_LIST, 
                                                             file_list_per_category, is_unknown_sorted)
    except FileNotFoundError as error:
        print(f'Source folder "{ARGUMENTS["source"]}" does not exist: {error} OR output folder' /
              '"{ARGUMENTS["source"]}" were removed before finish.')
        exit()

    # for format, folder in SORT_FOLDERS_LIST.items():
    #     print('For "{:^10}" < ext: "{:<3}"'.format(folder, format))

    print('My master, I have found "{}" files!'.format(', '.join(sort_known_list)))

    for item in file_list_per_category:
        print('Total files in "{:^10}": #{:<5} | files: {:<20}'.format(item, len(file_list_per_category[item]),
                                                                        ', '.join(file_list_per_category[item])))
   
    if '' in sort_unknown_list:
        sort_unknown_list.remove('')

    print(' Uknown file types: {:^20}'.format(', '.join(sort_unknown_list)))
    print('COMPLETED')


def copy_file(file: Path, folder_path: Path, new_name: str) -> None:
    shutil.move(file, folder_path / new_name)


def extract_archive(file: Path, folder_path: Path) -> None:
    print(f'EXTRACTING {file} to {folder_path / file.stem}')
    shutil.unpack_archive(file, folder_path / file.stem)


def dir_walk(path: Path, SORT_FOLDERS_LIST: dict, file_list_per_category: list, is_unknown_sorted: int) -> tuple:

    print(f'WALKING {path}')
    sort_unknown_set = set()
    sort_known_set = set()
    unknown = ''
    
    if path.name in file_list_per_category:
        return file_list_per_category, sort_unknown_set, sort_known_set

    for item in path.iterdir():

        if item.is_dir():

            if not any(item.iterdir()):
                print(f'REMOVING EMPTY {item}')
                item.rmdir()
                continue

            try:
                file_list_per_category, new_sort_unknown_set, new_sort_known_set = dir_walk(item, SORT_FOLDERS_LIST, 
                                                                        file_list_per_category, is_unknown_sorted)
                sort_unknown_set.update(new_sort_unknown_set)
                sort_known_set.update(new_sort_known_set)
            except OSError as error:
                print(f'Not possible to perform operation: {error}')
                exit()
            except ValueError as error:
                print(f'Impossible to walk a file: {error}')
                exit()
        else:

            file_list_per_category, unknown, known_ext = sort(item, SORT_FOLDERS_LIST, file_list_per_category, 
                                                              is_unknown_sorted)
            if unknown is not None: 
                sort_unknown_set.add(unknown)
            if known_ext is not None:
                sort_known_set.update(known_ext)

    if not any(path.iterdir()) and path.is_dir:
        print(f'REMOVING EMPTY {path}')
        path.rmdir()
    
    return file_list_per_category, sort_unknown_set, sort_known_set


def name_translate(name: str) -> str:
    
    CYRILLIC_SYMBOLS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ'
    TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", 
                   "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "u", 
                   "ja", "je", "ji", "g")
    trans_map = {}

    for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        trans_map[ord(c)] = l
        trans_map[ord(c.upper())] = l.upper()

    return name.translate(trans_map)


def normalize(name: str) -> str:
    name = re.sub(r'[^a-zA-Z0-9_.]', '_', name)
    return name


def sort(file: Path, SORT_FOLDERS_LIST: dict, file_list_per_category: dict, is_unknown_sorted: int) -> tuple:

    print(f'SORTING {file}')
    unknown = ''
    known_ext = set()

    try:
        new_name = name_translate(file.name)
    except TypeError as error:
        print(f'Translation error in "{file.name}": {error}')

    new_name = normalize(new_name)

    suffix = file.suffix[1:]

    if suffix.casefold() in SORT_FOLDERS_LIST:
        folder_path = ARGUMENTS['destination'] / SORT_FOLDERS_LIST.get(suffix)
        known_ext.add(suffix.casefold())

    else:

        if suffix != '':
            unknown = suffix
        else:
            unknown = '*files_without_suffix'

        if is_unknown_sorted:
            folder_path = ARGUMENTS['destination'] / 'unknown'
        else:
            file_list_per_category['unknown'].append(file.name)
            return file_list_per_category, unknown.casefold(), known_ext


    if SORT_FOLDERS_LIST.get(suffix) == 'archives':
        extract_archive(file, folder_path)
    
    file_list_per_category[folder_path.name].append(file.name)
    folder_path.mkdir(exist_ok=True, parents=True)
    copy_file(file, folder_path, new_name)

    return file_list_per_category, unknown.casefold(), known_ext


if __name__ == '__main__':
    try:
        main(ARGUMENTS['source'])
    except:
        print('Unexpected exception!')
        exit()