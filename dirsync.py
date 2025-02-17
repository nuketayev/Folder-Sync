import os
import logging
import time
import shutil
import hashlib
import argparse

def hash_calculator(source, hash):
    if hash == 'SHA256':
        hash_func = hashlib.sha256()
    else:
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
        logging.info(f"Directory was succesifully created at {replica}")

    source_items = os.listdir(source)
    replica_items = os.listdir(replica)

    for item in source_items:
        source_item_path = os.path.join(source, item)
        replica_item_path = os.path.join(replica, item)

        if os.path.isdir(source_item_path):
            sync_folders(source_item_path, replica_item_path, hash)
        else:
            if not (os.path.exists(replica_item_path)) or hash_calculator(replica_item_path, hash) != hash_calculator(source_item_path, hash):
                shutil.copy2(source_item_path, replica_item_path)
                logging.info(f"Copied/Updated file {replica_item_path}")
    
    for item in replica_items:
        source_item_path = os.path.join(source, item)
        replica_item_path = os.path.join(replica, item)

        if not os.path.exists(source_item_path):
            if os.path.isdir(replica_item_path):
                shutil.rmtree(replica_item_path)
                logging.INFO(f'Removed directory: {replica_item_path}')
            else:
                os.remove(replica_item_path)
                logging.INFO(f"Removed file: {replica_item_path}. In the {source_item_path} there is no {item}")

def setup_logging(logfile):
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s",
                        handlers=[
                            logging.FileHandler(logfile),
                            logging.StreamHandler()
                        ])

def main():
    parser = argparse.ArgumentParser(prog='SyncFolders', description='Periodical one way two folders synchronization.')
    parser.add_argument('source', help='Path to the source directory')
    parser.add_argument('replica', help='Path to the replica directory')
    parser.add_argument('interval', type=int, help='Interval in seconds between each synchornization')
    parser.add_argument('log', help='Path where log file will be created')
    parser.add_argument('-ha', '--hash', help="Hash function (MD5 / SHA256). Default MD5.")

    args = parser.parse_args()
    
    if args.hash is None:
        hash = 'MD5'
    else:
        hash = args.hash

    setup_logging(args.log)

    try:
        while True:
            logging.info('Stating the synchronization...')
            sync_folders(args.source, args.replica, hash)
            logging.info('Synchronization is completed. Waiting for the interval...')
            time.sleep(args.interval)
    except KeyboardInterrupt:
        logging.info('Sync stopped by the user.')


if __name__ == '__main__':
    main()
