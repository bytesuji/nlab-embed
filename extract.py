import os
import re
import sqlite3
import sys

from bs4 import BeautifulSoup
from pathlib import Path
from pdfminer.high_level import extract_text
from tqdm import tqdm

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}

def is_html(file_path):
    extension = Path(file_path).suffix.lower()
    if extension == ".html":
        return True

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
        return bool(re.search(r'(?i)<!DOCTYPE html', content))

def extract_text_from_html(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
        soup = BeautifulSoup(content, features="html.parser")
        text = soup.get_text()
        return text

def extract_text_from_pdf(file_path):
    text = extract_text(file_path)
    return text

def get_all_files_in_directory(path):
    return [os.path.join(dp, f) for dp, dn, filenames in os.walk(path) for f in filenames]

def create_database_and_table():
    conn = sqlite3.connect('file_contents.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS files
                     (path TEXT, content TEXT)''')
    conn.commit()
    return conn

def insert_into_database(conn, path, content):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO files VALUES (?, ?)", (path, content))
    conn.commit()

def main():
    folder_path = sys.argv[1] if len(sys.argv) > 1 else "."
    files = get_all_files_in_directory(folder_path)
    conn = create_database_and_table()

    for file_path in tqdm(files, desc="Processing files"):
        extension = Path(file_path).suffix.lower()
        if extension in IMAGE_EXTENSIONS:
            continue

        try:
            if extension == ".pdf":
                content = extract_text_from_pdf(file_path)
            elif is_html(file_path):
                content = extract_text_from_html(file_path)
            else:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()

            insert_into_database(conn, file_path, content.strip().replace('\n\n\n', '\n'))

        except Exception as e:
            print(f"Error processing {file_path}: {e}", file=sys.stderr)
            continue

    conn.close()

if __name__ == "__main__":
    main()
