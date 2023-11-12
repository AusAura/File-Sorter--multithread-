# Extension File Sorter (multithreads version) 
## by Oleksandr Smyrnov

### Usage: run the script in CLI.
EXAMPLE: py FileSort-multi-v1-dirwalker.py -s C:\Users\Professional\Desktop\sort_test -r no

# Summary:

- **Sorter works in 3 modes (3 different files respectively):**

1) **Dirwalker:** separate thread for literally each operation of crawl and copy. The slowest version.

(This is the update of the previous version without changing the structure too much: https://github.com/AusAura/Extension-File-Sorter)
(Versions 2 and 3 were made almost from scratch)

2) **Crawlers:** separate thread for each folder + for each file copy operation. The fastest version.
3) **Crawlers v2:** separate thread for each folder crawl + for all copy operation in 1 folder.

- All files in the folder and subfolders are sorted by pre-set extensions.
- Empty folders and old files can be deleted.

- (for 'dirwalker' version only) Folders: 'documents', 'archives', 'video', 'music', 'unknown'. These folders are excluded from sorting.
- (for 'dirwalker' version only) Folder 'unknown' is for files with unknown extensions.
- (for 'dirwalker' version only) You can either sort or not sort 'unknown' files. Select the option at the beginning of thescript execution.
- (for 'dirwalker' version only) You can add your own extensions (and sorting folders for them) to the code in main() function.
- (for 'dirwalker' version only) Archives will be extracted to the 'archives' folder.
- (for 'dirwalker' version only) At the end, script displaying lists of known and uknown extensions and files.

## Available arguments:

- Taking **'-s' or '--source':** the only obligatory command line argument for the source folder.
- **"-d", "--destination":** set destination (target) folder. By default, it is in the 'source'/_SORTED.
- **"-r", "--sremove":** remove source folder and files while executing if 'yes' (set to 'no' by default).
- (for 'dirwalker' version only) **"-u", "--usort":** sort unknown extension files as well while executing if 'yes' (set to 'yes' by default)





