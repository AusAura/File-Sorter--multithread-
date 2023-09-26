Extension File Sorter (multithreads version) by Oleksandr Smyrnov

- Taking '-s' or '--source' parameter for one obligatory command line argument which indicates the source folder.
- "-d", "--destination": to set destination (target) folder. By default, it is in the 'source'/_SORTED.
- "-r", "--sremove": Removes source folder and files during sorting if 'yes' (set to 'no' by default).
- (for 'dirwalker' version only) "-u", "--usort": Sorting unknown extension files during if 'yes' (set to 'yes' by default)

- All files in the folder and subfolders are sorted by widely-known extensions.

- (for 'dirwalker' version only) Folders: 'documents', 'archives', 'video', 'music', 'unknown'. These folders are excluded from sorting.
- (for 'dirwalker' version only) Folder 'unknown' is for files with unknown extensions.
- (for 'dirwalker' version only) You can either sort or not sort 'unknown' files. Select the option at the beginning of thescript execution.
- (for 'dirwalker' version only) You can add your own extensions and folders to the code in main() function.
- (for 'dirwalker' version only) Archives are extracted to 'archives' folder.
- (for 'dirwalker' version only) At the end, script showing lists known and uknown extensions and files.

- Empty folders and old files can be deleted.
