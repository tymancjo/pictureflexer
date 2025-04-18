import os
import hashlib
import shutil
import csv
from PIL import Image

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
                    name_map[new_name.split('.')[0]] = original_name
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

        if '_final' in filename:
            filename_clean = filename.replace('_final','').split('.')[0]
            filename_clean_ext = filename.replace('_final','').split('.')[1]
        else:
            filename_clean = filename.split('.')[0]
            filename_clean_ext = filename.split('.')[1]

        print(f"{filename=} {filename_clean=}")

        intermediate_path = os.path.join(intermediate_directory, filename)
        if os.path.isfile(intermediate_path):
            if filename_clean in name_map:
                original_name = name_map[filename_clean]
                original_name = f"{original_name.split('.')[0]}.{filename_clean_ext}"
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



def convert_images_to_jpg(directory):
    """Konwertuje wszystkie obrazy (.png, .jpg, .jpeg, .tiff, .bmp)
    w podanym katalogu na format JPG."""
    if not os.path.isdir(directory):
        print(f"Podany katalog '{directory}' nie istnieje.")
        return

    supported_extensions = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']
    converted_count = 0
    conversion_error_count = 0

    for filename in os.listdir(directory):
        if any(filename.lower().endswith(ext) for ext in supported_extensions):
            input_path = os.path.join(directory, filename)
            name_without_ext, _ = os.path.splitext(filename)
            output_filename = f"{name_without_ext}.jpg"
            output_path = os.path.join(directory, output_filename)

            try:
                img = Image.open(input_path)
                img = img.convert("RGB")
                img.save(output_path, "JPEG")
                print(f"Przekonwertowano '{filename}' na '{output_filename}'")
                converted_count += 1
                if input_path != output_path:
                    os.remove(input_path)  # Opcjonalnie usuń oryginalny plik
            except FileNotFoundError:
                print(f"Nie znaleziono pliku '{input_path}'.")
            except Exception as e:
                print(f"Wystąpił błąd podczas konwersji '{filename}' do JPG: {e}")
                conversion_error_count += 1

    print(f"\nPrzekonwertowano {converted_count} obrazów do JPG w katalogu '{directory}'.")
    if conversion_error_count > 0:
        print(f"Wystąpiło {conversion_error_count} błędów podczas konwersji.")