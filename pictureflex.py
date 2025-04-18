from pictureprocesor import pictureprocesor as pp


if __name__ == "__main__":
    src_folder = "intermediate"
    output_folder = "out"
    final_width = 1600
    final_height = 1500

    pp.proces_images(src_folder,output_folder,final_width,final_height)