import os
import hashlib
import shutil
import csv


def generate_unique_hash(filename):
    """Generuje unikalny hash SHA-256 na podstawie nazwy pliku."""
    encoded_name = filename.encode("utf-8")
    return hashlib.sha256(encoded_name).hexdigest()


def copy_files_to_intermediate_with_hashed_names(
    source_directory, intermediate_directory, csv_filename="mapping.csv"
):
    """Listuje pliki w katalogu źródłowym, kopiuje je do katalogu 'intermediate'
    pod nazwami będącymi unikalnymi hashami i zapisuje mapowanie do pliku CSV."""
    if not os.path.isdir(source_directory):
        print(f"Podany katalog źródłowy '{source_directory}' nie istnieje.")
        return

    if not os.path.exists(intermediate_directory):
        os.makedirs(intermediate_directory)
        print(f"Utworzono katalog: {intermediate_directory}")

    files = os.listdir(source_directory)
    mapping_data = []  # Lista do przechowywania danych mapowania dla CSV

    for filename in files:
        source_path = os.path.join(source_directory, filename)
        if os.path.isfile(source_path):
            file_base, file_ext = os.path.splitext(filename)
            unique_hash = generate_unique_hash(filename)
            new_filename = f"{unique_hash}{file_ext}"
            destination_path = os.path.join(intermediate_directory, new_filename)

            try:
                shutil.copy2(source_path, destination_path)  # copy2 zachowuje metadane
                mapping_data.append(
                    {"original_name": filename, "new_name": new_filename}
                )
                print(
                    f"Skopiowano '{filename}' do '{new_filename}' w '{intermediate_directory}'"
                )
            except OSError as e:
                print(f"Nie można skopiować '{filename}': {e}")

    # Zapisz mapowanie do pliku CSV
    csv_path = os.path.join(intermediate_directory, csv_filename)
    try:
        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["original_name", "new_name"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")

            writer.writeheader()
            writer.writerows(mapping_data)

        print(f"\nZapisano mapowanie do pliku CSV: {csv_path}")

    except OSError as e:
        print(f"Wystąpił błąd podczas zapisywania pliku CSV: {e}")


if __name__ == "__main__":
    source_directory = "src"  # Zmień na ścieżkę do Twojego katalogu źródłowego
    intermediate_directory = "intermediate"
    csv_file = "mapping.csv"
    copy_files_to_intermediate_with_hashed_names(
        source_directory, intermediate_directory, csv_file
    )
