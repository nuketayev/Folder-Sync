import os
import logging
import time
import shutil
import hashlib
import argparse

def check_permissions(path):
    if not os.path.exists(path):
        return True
    if not os.access(path, os.R_OK):
        logging.error(f"Read permission denied: {path}")
        return False
    if not os.access(path, os.W_OK):
        logging.error(f"Write permission denied: {path}")
        return False
    return True

def checksum(path, hash):
    try:
        if hash == 'SHA256':
            hash_object = hashlib.sha256()
        elif hash == 'MD5':
            hash_object = hashlib.md5()

        with open(path, "rb") as file:
            while True:
                chunk = file.read(4096)
                if not chunk:
                    break
                hash_object.update(chunk)
        file_hash = hash_object.hexdigest()
        return file_hash
    except Exception as e:
        logging.error(f"Error calculating checksum for {path}: {e}")
        return None

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
            try:
                if not os.path.exists(replica_item_path) or checksum(replica_item_path, hash) != checksum(source_item_path, hash):
                    if check_permissions(source_item_path) and check_permissions(replica_item_path):
                        shutil.copy2(source_item_path, replica_item_path)
                        logging.info(f"Copied/Updated file {replica_item_path}")
            except Exception as e:
                logging.error(f"Error copying file {source_item_path} to {replica_item_path}: {e}")

    # Remove files/directories in replica that are not in source
    for item in replica_items:
        source_item_path = os.path.join(source, item)
        replica_item_path = os.path.join(replica, item)

        if not os.path.exists(source_item_path):
            try:
                if check_permissions(replica_item_path):
                    if os.path.isdir(replica_item_path):
                        shutil.rmtree(replica_item_path)
                        logging.info(f"Removed directory: {replica_item_path}. There is no {item} directory in the source.")
                    else:
                        os.remove(replica_item_path)
                        logging.info(f"Removed file: {replica_item_path}. There is no {item} file in the source.")
            except Exception as e:
                logging.error(f"Error removing {replica_item_path}: {e}")

def setup_logging(logfile_path):
    # If path is to a directory, create a sync_folders.log file inside.
    if os.path.isdir(logfile_path):
        logfile_path = os.path.join(logfile_path, "sync_folders.log")
    # Setup logging to file and console.
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
    parser.add_argument('interval', type=float, help='Interval in seconds between each synchornization')
    parser.add_argument('log', help='Path where log file will be created')
    parser.add_argument('-ha', '--hash', choices=['MD5', 'SHA256'], default='SHA256',
                    help="Hash function (MD5 for speed, SHA256 for accuracy). Default is SHA256.")
    args = parser.parse_args()

    if args.interval <= 0:
        print("Interval must be a positive number.")
        exit(1)
    if args.source == args.replica:
        print("Source and replica paths must be different.")
        exit(1)

    setup_logging(args.log)
    logging.info(f"\nSource path: {args.source}\nReplica path: {args.replica}\nHash function: {args.hash}\n")

    if not os.path.isdir(args.source):
        logging.error(f"Source path is not a directory: {args.source}")
        return
    if not os.path.isdir(args.replica):
        logging.error(f"Replica path is not a directory: {args.replica}")
        return

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
