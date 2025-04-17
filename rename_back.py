import os
import csv
import shutil


def restore_original_filenames(
    intermediate_directory, final_directory, csv_filepath="intermediate/mapping.csv"
):
    """
    Na podstawie pliku CSV przywraca oryginalne nazwy plików
    z katalogu 'intermediate' i przenosi je do katalogu 'final'.
    """
    if not os.path.isdir(intermediate_directory):
        print(f"Katalog '{intermediate_directory}' nie istnieje.")
        return

    if not os.path.exists(final_directory):
        os.makedirs(final_directory)
        print(f"Utworzono katalog: {final_directory}")

    if not os.path.isfile(csv_filepath):
        print(f"Plik CSV z mapowaniem '{csv_filepath}' nie istnieje.")
        return

    name_map = {}
    try:
        with open(csv_filepath, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=";")
            for row in reader:
                original_name = row.get("original_name")
                new_name = row.get("new_name")
                if original_name and new_name:
                    name_map[new_name] = original_name
                else:
                    print(f"Ostrzeżenie: Niekompletny wiersz w CSV: {row}")
    except FileNotFoundError:
        print(f"Nie znaleziono pliku CSV: {csv_filepath}")
        return
    except Exception as e:
        print(f"Wystąpił błąd podczas odczytu pliku CSV: {e}")
        return

    print("Rozpoczynanie przywracania oryginalnych nazw plików...")
    moved_count = 0
    not_found_count = 0

    for filename in os.listdir(intermediate_directory):
        intermediate_path = os.path.join(intermediate_directory, filename)
        if os.path.isfile(intermediate_path):
            if filename in name_map:
                original_name = name_map[filename]
                final_path = os.path.join(final_directory, original_name)
                try:
                    shutil.move(intermediate_path, final_path)
                    print(
                        f"Przeniesiono '{filename}' do '{original_name}' w '{final_directory}'"
                    )
                    moved_count += 1
                except OSError as e:
                    print(f"Nie można przenieść '{filename}': {e}")
            else:
                print(
                    f"Ostrzeżenie: Nie znaleziono oryginalnej nazwy dla '{filename}' w pliku CSV."
                )
                not_found_count += 1

    print(f"\nPrzeniesiono {moved_count} plików do katalogu '{final_directory}'.")
    if not_found_count > 0:
        print(
            f"Nie znaleziono informacji o oryginalnej nazwie dla {not_found_count} plików."
        )


if __name__ == "__main__":
    intermediate_dir = "intermediate"
    final_dir = "final"
    csv_file_path = os.path.join(
        intermediate_dir, "mapping.csv"
    )  # Domyślna ścieżka do pliku CSV

    restore_original_filenames(intermediate_dir, final_dir, csv_file_path)
