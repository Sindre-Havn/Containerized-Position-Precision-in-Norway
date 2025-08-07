import os
from pathlib import Path
from datetime import datetime
import shutil

def delete(path: Path) -> None:
    """
    Delete specific file at path, or recursively delete folder at path."""
    if   os.path.isfile(path):  os.remove(path)
    elif os.path.isdir(path):   shutil.rmtree(path)

def delete_old_data(folder: Path, max_allowed_count: int, file_max_lifetime_hours: float = -1.0) -> None:
    """
    Sort all files/folders inside the 'folder' according to their
    st_atime (previouse access time).
    Then delete these files/folders with the oldest st_atime if there
    are more files/folders inside 'folder' than the 'maximum_allowed_count'.
    If 'file_max_lifetime_hours' is a positive number, then also delete all files/folders
    that have not been accessed in time 'file_max_lifetime_hours'."""
    eph_folders = os.listdir(folder)
    files_and_atime = []
    # Get path and st_atime for every file/folder inside 'folder'.
    for eph in eph_folders:
        try:
            access_timestamp = os.path.getatime(folder / eph)
            last_access_datetime = datetime.fromtimestamp(access_timestamp)
            files_and_atime.append({'path': eph, 'atime':last_access_datetime})

        except FileNotFoundError:
            print(f"Error: The file '{folder / eph}' was not found.")

        except Exception as e:
            print(f"An error occurred: {e}")
            raise # Let flask catch this
    
    sorted_by_atime = sorted(files_and_atime, key=lambda x: x['atime'], reverse=True)
    
    # If too many files/folders, delete least recent used. 
    while len(os.listdir(folder)) > max_allowed_count:
        delete(folder / sorted_by_atime[-1]['path'])

    # Exit function if we dont want to delete files not used.
    if file_max_lifetime_hours < 0:
        return
    
    # Maximum allowed lifetime of file is specified (not -1)
    # -> delete all older files, even if bellow max_allowed_count
    for file in sorted_by_atime:
        if datetime.now() - file['atime'] > datetime.timedelta(hours=file_max_lifetime_hours):
            delete(folder / file['path'])


def update_access_time(file: str) -> None:
    """
    Updates the st_atime attribute of the file/folder to be the current time.
    The st_atime flag hold the 'access time', e.g. when a file was last read.
    This function is needed because 'pandas.read_csv()' dont seem to update it
    when reading files.
    This function indicates when the files was last used, so they may be deleted
    according to last access-time using the 'delete_old_ephemeris' function. 
    """
    try:
        # Get current file stats to retrieve the modification time
        stat_info = os.stat(file)
        current_mtime = stat_info.st_mtime

        # Convert the new_atime datetime object to a Unix timestamp
        new_atime_timestamp = datetime.now().timestamp()

        # Set the access time and keep the modification time
        os.utime(file, (new_atime_timestamp, current_mtime))
        print(f"Access time of '{file}' updated successfully.")
    except FileNotFoundError:
        print(f"Error: File '{file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")