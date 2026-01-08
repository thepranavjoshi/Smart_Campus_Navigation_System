"""
CSV Handler Utility
Safe read/write operations for CSV files
"""
import csv
import os
from threading import Lock

# Thread lock for safe file operations
_csv_lock = Lock()


def read_csv(filepath):
    """
    Read CSV file and return list of dictionaries
    """
    if not os.path.exists(filepath):
        return []
    
    with _csv_lock:
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            print(f"Error reading CSV {filepath}: {e}")
            return []


def write_csv(filepath, data, fieldnames=None):
    """
    Write list of dictionaries to CSV file
    """
    if not data:
        return False
    
    if fieldnames is None:
        fieldnames = data[0].keys()
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with _csv_lock:
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            print(f"Error writing CSV {filepath}: {e}")
            return False


def append_csv(filepath, row, fieldnames=None):
    """
    Append single row to CSV file
    """
    file_exists = os.path.exists(filepath)
    
    if fieldnames is None and file_exists:
        existing = read_csv(filepath)
        if existing:
            fieldnames = existing[0].keys()
    
    if fieldnames is None:
        fieldnames = row.keys()
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with _csv_lock:
        try:
            mode = 'a' if file_exists else 'w'
            with open(filepath, mode, newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(row)
            return True
        except Exception as e:
            print(f"Error appending to CSV {filepath}: {e}")
            return False


def update_csv_row(filepath, key_field, key_value, updates):
    """
    Update a specific row in CSV file
    """
    data = read_csv(filepath)
    if not data:
        return False
    
    updated = False
    for row in data:
        if str(row.get(key_field)) == str(key_value):
            row.update(updates)
            updated = True
            break
    
    if updated:
        return write_csv(filepath, data)
    return False


def delete_csv_row(filepath, key_field, key_value):
    """
    Delete a specific row from CSV file
    """
    data = read_csv(filepath)
    if not data:
        return False
    
    original_len = len(data)
    data = [row for row in data if str(row.get(key_field)) != str(key_value)]
    
    if len(data) < original_len:
        return write_csv(filepath, data)
    return False


def get_next_id(filepath):
    """
    Get next available ID for a CSV file
    """
    data = read_csv(filepath)
    if not data:
        return 1
    
    max_id = max(int(row.get('id', 0)) for row in data)
    return max_id + 1
