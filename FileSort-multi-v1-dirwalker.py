from pathlib import Path
import argparse, re, shutil, logging, sys
import concurrent.futures

# LOGGER CONFIGS
logger = logging.getLogger('DEBUG')
logger.setLevel(logging.DEBUG)
formatter_console = logging.Formatter("%(threadName)s | %(message)s")
formatter_file = logging.Formatter("%(threadName)s | %(asctime)s | %(levelname)s | %(message)s")
console_logger_handler = logging.StreamHandler()
console_logger_handler.setLevel(logging.DEBUG)
console_logger_handler.setFormatter(formatter_console)
file_logger_handler = logging.FileHandler('debug.log')
file_logger_handler.setLevel(logging.DEBUG)
file_logger_handler.setFormatter(formatter_file)
logger.addHandler(console_logger_handler)
logger.addHandler(file_logger_handler)

### ARGPARSE CONFIGS
### REQUEST REFERENCE: py FileSort-multi-v1-dirwalker.py -s C:\Users\Professional\Desktop\sort_test -r no
### TRUE CLI SETTINGS START
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--source", required=True, help="Source folder")
SORTED_DEFAULT_PATH = Path(sys.argv[2]  + "/_SORTED")
parser.add_argument("-d", "--destination", default=SORTED_DEFAULT_PATH)
parser.add_argument("-r", "--sremove", default="no", help="Removes source folder and files during sorting if 'yes'") # description="Removes source folder and files during sorting if 'yes'"
parser.add_argument("-u", "--usort", default="yes", help="Sorting unknown extension files during if 'yes'") # description="Sorting unknown extension files during if 'yes'"
ARGUMENTS = vars(parser.parse_args())
### END OF TRUE SETTINGS
### # TEMPORARY DEBUG SETTINGS START
# ARGUMENTS = {}
# ARGUMENTS["source"] = "C:\\Users\\Professional\\Desktop\\sort_test"
# ARGUMENTS["destination"] = "C:\\Users\\Professional\\Desktop\\sort_test\\_SORTED"
# ARGUMENTS["source"] = Path(ARGUMENTS["source"])
# ARGUMENTS["destination"] = Path(ARGUMENTS["destination"])
# ARGUMENTS["sremove"] = 'no'
# ARGUMENTS["usort"] = 'yes'
### # END OF TEMP DEBUG SETTINGS
ARGUMENTS["source"] = Path(ARGUMENTS["source"])
ARGUMENTS["destination"] = Path(ARGUMENTS["destination"])
logger.debug(f"Received arguments: {ARGUMENTS}")


# COPY FUNCTION FOR FILES
def copy_file(file: Path, folder_path: Path, new_name: str) -> None:
    logger.debug(f"WORKING ON: {file.name}")
    if ARGUMENTS["sremove"] == "yes":
        shutil.move(file, folder_path / new_name)
    else:
        shutil.copy(file, folder_path / new_name)

# EXTRACT FUNCTION FOR ARCHIVES
def extract_archive(file: Path, folder_path: Path) -> None:
    logger.debug(f"EXTRACTING {file} to {folder_path / file.stem}")
    shutil.unpack_archive(file, folder_path / file.stem)


# FOLDER CRAWLER FUNCTION
def dir_walk(args: tuple) -> tuple:
    path = args[0]
    SORT_FOLDERS_LIST = args[1]
    file_list_per_category = args[2]
    # LOGGING THE FOLDER + INIT
    logger.debug(f"WALKING {path}")
    sort_unknown_set = set()
    sort_known_set = set()
    unknown = ""

    # IF FOLDER IS ALREADY SORTED (= FILES EXT TYPE), CEASE THE FUNCTION WITHOUT DOING ANYTHING
    if path.name in file_list_per_category:
        return file_list_per_category, sort_unknown_set, sort_known_set

    # CRAWLING EACH FILE AND FOLDER
    for item in path.iterdir():
        # IF FOLDER
        if item.is_dir():
            # IF THIS FOLDER IS EMPTY = REMOVE OR JUST SKIP
            if not any(item.iterdir()) and ARGUMENTS['sremove'] == 'yes':
                logger.debug(f"REMOVING EMPTY {item}")
                item.rmdir()
                continue
            elif not any(item.iterdir()):
                logger.debug(f"{item} is EMPTY!")
                continue

            # CRAWL THIS FOLDER RECURSIVELY
            try:
                # CREATING A SEPARATED THREAD WITH POOL FOR EACH INNER FOLDER
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    args = (item, SORT_FOLDERS_LIST, file_list_per_category)
                    result = tuple(executor.map(dir_walk, (args,)))
                    (
                        file_list_per_category,
                        new_sort_unknown_set,
                        new_sort_known_set,
                    ) = result[0]
                    # UPDATE CURRENT SETS WITH EXT WITH ONES FROM THE INNER FOLDER
                    sort_unknown_set.update(new_sort_unknown_set)
                    sort_known_set.update(new_sort_known_set)
            except OSError as error:
                logger.debug(f"Not possible to perform operation: {error}")
                exit()
            except ValueError as error:
                logger.debug(f"Impossible to walk a file: {error}")
                exit()
        # IF FILE
        else:
            # CREATING A SEPARATED THREAD WITH POOL FOR EACH FILE SORT
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    args = (item, SORT_FOLDERS_LIST, file_list_per_category)
                    # SORTING THE FILE
                    result = tuple(executor.map(sort, (args,)))
                    (
                        file_list_per_category,
                        unknown,
                        known_ext,
                    ) = result[0]
            # UPDATING SETS WITH CURRENT FILE
            if unknown is not None:
                sort_unknown_set.add(unknown)
            if known_ext is not None:
                sort_known_set.update(known_ext)

    # THIS LEVEL EMPTY SOURCE FOLDER REMOVAL, IF SREMOVE = 'YES', OR JUST SKIP
    if not any(path.iterdir()) and path.is_dir and ARGUMENTS['sremove'] == 'yes':
        logger.debug(f"REMOVING EMPTY {path}")
        path.rmdir()
    elif not any(path.iterdir()) and path.is_dir:
        logger.debug(f"{path} IS NOW EMPTY")

    # GETTING OUT FROM THIS LEVEL OF RECURSION
    return file_list_per_category, sort_unknown_set, sort_known_set

#TRANSLATE FROM CYRILLIC TO LATIN SYMBOLS
def name_translate(name: str) -> str:
    CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
    TRANSLATION = (
        "a",
        "b",
        "v",
        "g",
        "d",
        "e",
        "e",
        "j",
        "z",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "r",
        "s",
        "t",
        "u",
        "f",
        "h",
        "ts",
        "ch",
        "sh",
        "sch",
        "",
        "y",
        "",
        "e",
        "yu",
        "u",
        "ja",
        "je",
        "ji",
        "g",
    )
    trans_map = {}

    for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        trans_map[ord(c)] = l
        trans_map[ord(c.upper())] = l.upper()

    return name.translate(trans_map)

#REPLACE UNKNOWN SYMBOLS WITH _
def normalize(name: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9_.]", "_", name)
    return name

#SORTING
def sort(args: tuple) -> tuple:
    # LOGGING FOR EACH FILE + INIT
    file, SORT_FOLDERS_LIST, file_list_per_category = args
    logger.debug(f"SORTING {file}")
    unknown = ""
    known_ext = set()

    # TRANSLATING TO LATIN
    try:
        new_name = name_translate(file.name)
    except TypeError as error:
        logger.debug(f'Translation error in "{file.name}": {error}')

    new_name = normalize(new_name)

    # SUFFIX EXTRACTION
    suffix = file.suffix[1:]
    # ADDING SUFFIX IN FILE TYPE LIST (KNOWN ONES)
    if suffix.casefold() in SORT_FOLDERS_LIST:
        folder_path = ARGUMENTS["destination"] / SORT_FOLDERS_LIST.get(suffix)
        known_ext.add(suffix.casefold())
    # ADDING SUFFIX IN FILE TYPE LIST (UNKNOWNS)
    else:
        # EMPTY SUFFIX CHECK
        if suffix != "":
            unknown = suffix
        else:
            unknown = "*files_without_suffix"

        # CHECKING IF USORT ENABLED, YES = SORTING, NO = RETURN FROM SORT FOR THIS UNKNOWN FILE
        if ARGUMENTS["usort"] == "yes":
            folder_path = ARGUMENTS["destination"] / "unknown"
        else:
            file_list_per_category["unknown"].append(file.name)
            return file_list_per_category, unknown.casefold(), known_ext

    # IF EXT IS KNOWN
    # CHECKING IF IT IS AN ARCHIVE, YES = EXTRACTING
    if SORT_FOLDERS_LIST.get(suffix) == "archives":
        extract_archive(file, folder_path)

    # APPENDING FILE NAME WITH KNOWN EXT, CREATING FOLDER FOR IT IF NOT CREATED, COPY FILE INSIDE
    file_list_per_category[folder_path.name].append(file.name)
    folder_path.mkdir(exist_ok=True, parents=True)
    copy_file(file, folder_path, new_name)

    # EXITING SORT FOR THIS KNOWN FILE
    return file_list_per_category, unknown.casefold(), known_ext


# MAIN FUNC
def main(folder_name: str) -> None:
    # EXTENSION LIST AND DEST. FOLDERS FOR THEM
    SORT_FOLDERS_LIST = {
        "zip": "archives",
        "gz": "archives",
        "tar": "archives",
        "jpeg": "images",
        "png": "images",
        "jpg": "images",
        "svg": "images",
        "avi": "video",
        "mp4": "video",
        "mov": "video",
        "mkv": "video",
        "doc": "documents",
        "docx": "documents",
        "txt": "documents",
        "pdf": "documents",
        "xlsx": "documents",
        "pptx": "documents",
        "mp3": "music",
        "ogg": "music",
        "wav": "music",
        "amr": "music",
    }
    # INITIATING FILE LISTS FOR TRACKING PURPOSES
    file_list_per_category = {
        "archives": [],
        "images": [],
        "video": [],
        "documents": [],
        "music": [],
        "unknown": [],
    }

    # STARTING FROM MAIN FOLDER READING
    logger.debug("STARTED SORTING")
    try:
        file_list_per_category, sort_unknown_list, sort_known_list = dir_walk((
            folder_name, SORT_FOLDERS_LIST, file_list_per_category)
        )
    except FileNotFoundError as error:
        logger.debug(
            f'Source folder "{ARGUMENTS["source"]}" does not exist: {error} OR output folder'
            / f'"{ARGUMENTS["destination"]}" were removed before finish.'
        )
        exit()

    logger.debug('My master, I have found "{}" files!'.format(", ".join(sort_known_list)))

    # LIST PER EACH FILE TYPE
    for item in file_list_per_category:
        logger.debug(
            'Total files in "{:^10}": #{:<5} | files: {:<20}'.format(
                item,
                len(file_list_per_category[item]),
                ", ".join(file_list_per_category[item]),
            )
        )

    # REMOVING TECHNICAL EMPTY ELEMENT IF THERE ARE NO UNKNOWNS
    if "" in sort_unknown_list:
        sort_unknown_list.remove("")

    # UKNOWN FILE TYPES LIST
    logger.debug(" Uknown file types: {:^20}".format(", ".join(sort_unknown_list)))
    logger.debug("COMPLETED")


# EXECUTE
if __name__ == "__main__":
        main(ARGUMENTS["source"])
