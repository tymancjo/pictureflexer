from pictureprocesor import folders as fd

if __name__ == "__main__":
    source_directory = "src"  # Zmień na ścieżkę do Twojego katalogu źródłowego
    intermediate_directory = "intermediate"
    csv_file = "mapping.csv"

    fd.copy_files_to_intermediate_with_hashed_names(
        source_directory, intermediate_directory, csv_file
    )
