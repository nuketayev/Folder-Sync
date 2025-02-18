# Folder Sync

## Description

Folder Sync is a program that synchronizes two folders: source and replica. The program maintains a full, identical copy of the source folder at the replica folder. 
Synchronization is one-way: after synchronization, the content of the replica folder is modified to exactly match the content of the source folder. 
Synchronization is performed periodically, and file creation/copying/removal operations are logged to a file and to the console output.

## How to Download and Use

1. Clone the repository:
   ```
   git clone https://github.com/nuketayev/Folder-Sync.git
   ```

2. Navigate to the repository directory:
   ```
   cd Folder-Sync
   ```

3. Run the program with the required command line arguments:
   ```
   python main.py <source_folder> <replica_folder> <interval_in_seconds> <log_file_path> [--hash {MD5,SHA256}]
   ```

   Example:
   ```
   python main.py /path/to/source /path/to/replica 60 /path/to/logfile.log --hash MD5
   ```

   - `<source_folder>`: Path to the source directory
   - `<replica_folder>`: Path to the replica directory
   - `<interval_in_seconds>`: Interval in seconds between each synchronization
   - `<log_file_path>`: Path where the log file will be created
   - `--hash {MD5,SHA256}`: Optional argument to choose the hash algorithm (MD5 for speed, SHA256 for accuracy). Default is SHA256.

## Hash Algorithm Choices

The program uses hash algorithms to calculate checksums for files to determine if they have changed.   
By default the program is using SHA256 algorithm. You can choose between two hash algorithms:

- MD5: Faster but less accurate. Suitable for scenarios where speed is more important than accuracy especially when working with huge files.
- SHA256: Slower but more accurate. Suitable for scenarios where accuracy is more important than speed.

In general SHA256 is 30% slower than the MD5 algorithm, however except large files the difference is too small.

## Modules Used

- `os`: Used for interacting with the operating system, such as checking if a directory exists, creating directories, and listing directory contents.
- `logging`: Used for logging file creation/copying/removal operations to a file and console output.
- `time`: Used for implementing the periodic synchronization interval.
- `shutil`: Used for copying files and removing directories.
- `hashlib`: Used for calculating checksums for files using the chosen hash algorithm.
- `argparse`: Used for parsing command line arguments.