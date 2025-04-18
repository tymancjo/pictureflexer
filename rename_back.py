import os
from pictureprocesor import folders as fd

if __name__ == "__main__":
    intermediate_dir = "out"
    final_dir = "final"
    csv_file_path = os.path.join(
        "intermediate", "mapping.csv"
    )  # Domyślna ścieżka do pliku CSV

    fd.restore_original_filenames(intermediate_dir, final_dir, csv_file_path)
