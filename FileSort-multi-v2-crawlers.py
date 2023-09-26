# Separate thread for each folder + for each file copy operation (0.0910041332244873)

from pathlib import Path
import argparse, shutil, logging, sys
from threading import Thread
from time import time

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
### REQUEST REFERENCE: py FileSort-multi-v2-crawlers.py -s C:\Users\Professional\Desktop\sort_test -r no
### TRUE CLI SETTINGS START
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--source", required=True, help="Source folder")
SORTED_DEFAULT_PATH = Path(sys.argv[2]  + "/_SORTED")
parser.add_argument("-d", "--destination", default=SORTED_DEFAULT_PATH)
parser.add_argument("-r", "--sremove", default="no", help="Removes source folder and files during sorting if 'yes'") # description="Removes source folder and files during sorting if 'yes'"
# parser.add_argument("-u", "--usort", default="yes", help="Sorting unknown extension files during if 'yes'") # description="Sorting unknown extension files during if 'yes'"
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

timer = time()
files = []
extensions = []

# COPY FUNCTION FOR FILES
def copy_file(file: Path, folder_path: Path, new_name: str) -> None:
    logger.debug(f"COPY FILE: {file.name}")
    if ARGUMENTS["sremove"].casefold() == "yes":
        shutil.move(file, folder_path / new_name)
    else:
        shutil.copy(file, folder_path / new_name)

# CRAWLER THAT CREATES A FOLDERS LIST WITH PATH OBJECTS
def dir_list_crawler(path: Path):
    logger.debug(f'Crawling: {path}')
    folders = []
    folders.append(path)
    for el in path.iterdir():
        if el.is_dir():
            folders.append(el)
            dir_list_crawler(el)

    return folders

def file_xerox(path: Path):
    logger.debug(f'Looking for files in: {path}')
    threads = []
    for el in path.iterdir():
        if el.is_file():
            logger.debug(f"Working with folders for file: {el.name}")
            ext = el.suffix
            new_path = ARGUMENTS["destination"] / ext
            new_path.mkdir(exist_ok=True, parents=True)
            files.append(el)
            extensions.append(el.suffix)
            th = Thread(target=copy_file, args=(el, new_path, new_path / el.name))
            threads.append(th)
            th.start()

    return threads



# MAIN FUNC
def main(folder_name: str) -> None:
    # STARTING FROM MAIN FOLDER READING
    logger.debug("STARTED SORTING")

    dir_list = dir_list_crawler(folder_name)
    print(f'FOUND FOLLOWING FOLDERS: {dir_list}')
    # VER2: CREATING A SEPARATED THREADS FOR EACH FOLDER
    threads = []
    for folder in dir_list:  
        th = Thread(target=dir_list_crawler, args=(folder,))
        th.start()
        threads.append(th)

    # VER2: CREATING A SEPARATED THREADS FOR FOLDER TO COPY FILES
    for folder in dir_list:
        threads + file_xerox(folder)
        # th = Thread(target=file_xerox, args=(folder,))
        # th.start()
        # threads.append(th)


    # WAIT FOR ALL THREADS TO FINISH
    [th.join() for th in threads]
    set_ext = set(extensions)

    logger.debug('=' * 10)
    logger.debug('My master, I have found {} files!'.format(len(files)))
    logger.debug('With {} extensions: {} '.format(len(set_ext), set_ext))
    logger.debug(f"COMPLETED in {time() - timer}")


# EXECUTE
if __name__ == "__main__":
        main(ARGUMENTS["source"])
