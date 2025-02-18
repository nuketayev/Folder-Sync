import os
import logging
import time
import shutil
import hashlib
import argparse

def checksum(source, hash):
    if hash == 'SHA256':
        hash_func = hashlib.sha256()
    elif hash == 'MD5':
        hash_func = hashlib.md5()        

    with open(source, "rb") as file:
        while True:
            chunk = file.read(4096)
            if not chunk:
                break
            hash_func.update(chunk)
    file_hash = hash_func.hexdigest()
    return file_hash

def sync_folders(source, replica, hash):
    if not os.path.exists(replica):
        os.makedirs(replica)
        logging.info(f"Created replica directory: {replica}")

    source_items = os.listdir(source)
    replica_items = os.listdir(replica)

    for item in source_items:
        source_item_path = os.path.join(source, item)
        replica_item_path = os.path.join(replica, item)

        if os.path.isdir(source_item_path):
            sync_folders(source_item_path, replica_item_path, hash)
        else:
            if not (os.path.exists(replica_item_path)) or checksum(replica_item_path, hash) != checksum(source_item_path, hash):
                shutil.copy2(source_item_path, replica_item_path)
                logging.info(f"Copied/Updated file {replica_item_path}")
    
    # Remove files/directories in replica that are not in source
    for item in replica_items:
        source_item_path = os.path.join(source, item)
        replica_item_path = os.path.join(replica, item)

        if not os.path.exists(source_item_path):
            if os.path.isdir(replica_item_path):
                shutil.rmtree(replica_item_path)
                logging.info(f"Removed directory: {replica_item_path}. There is no {item} directory in the source.")
            else:
                os.remove(replica_item_path)
                logging.info(f"Removed file: {replica_item_path}. There is no {item} file in the source.")

def setup_logging(logfile_path):
    # Setup logging to file and console.
    if os.path.isdir(logfile_path):
        logfile_path = os.path.join(logfile_path, "sync_folders.log")

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s",
                        handlers=[
                            logging.FileHandler(logfile_path),
                            logging.StreamHandler()
                        ])

def main():
    # Command line argument parsing
    parser = argparse.ArgumentParser(prog='SyncFolders', description='Periodical one way two folders synchronization.')
    parser.add_argument('source', help='Path to the source directory')
    parser.add_argument('replica', help='Path to the replica directory')
    parser.add_argument('interval', type=int, help='Interval in seconds between each synchornization')
    parser.add_argument('log', help='Path where log file will be created')
    parser.add_argument('-ha', '--hash', choices=['MD5', 'SHA256'], default='SHA256',
                    help="Hash function (MD5 for speed, SHA256 for accuracy). Default is SHA256.")
    args = parser.parse_args()

    setup_logging(args.log)
    logging.info(f"Source path: {args.source}\nReplica path: {args.replica}\nHash function: {args.hash}")

    try:
        while True:
            logging.info("Starting folder synchronization...")
            sync_folders(args.source, args.replica, args.hash)
            logging.info("Synchronization completed. Waiting for the next interval...")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        logging.info("Synchronization stopped by the user.")


if __name__ == '__main__':
    main()
