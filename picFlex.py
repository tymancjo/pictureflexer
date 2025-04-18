import os
from pictureprocesor import folders as fd
from pictureprocesor import pictureprocesor as pp



if __name__ == "__main__":

    source_directory = "src"  # Zmień na ścieżkę do Twojego katalogu źródłowego
    intermediate_directory = "intermediate"
    csv_file = "mapping.csv"


    fd.copy_files_to_intermediate_with_hashed_names(
        source_directory, intermediate_directory, csv_file
    )


    src_folder = "intermediate"
    output_folder = "out"
    final_width = 1600
    final_height = 1500

    pp.proces_images(src_folder,output_folder,final_width,final_height)


    intermediate_dir = "out"
    final_dir = "final"
    csv_file_path = os.path.join(
        "intermediate", "mapping.csv"
    )  

    fd.restore_original_filenames(intermediate_dir, final_dir, csv_file_path)
    fd.convert_images_to_jpg(final_dir)