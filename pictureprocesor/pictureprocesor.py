import cv2
import mediapipe as mp
from PIL import Image, ImageDraw
from rembg import remove
import numpy as np
import os
import io
import unicodedata

def crop_head_and_neck(image_path, output_path):
    mp_face_detection = mp.solutions.face_detection
    mp_drawing = mp.solutions.drawing_utils

    with mp_face_detection.FaceDetection(min_detection_confidence=0.4) as face_detection:
        image = cv2.imread(image_path)
        if image is None:
            print(f"Nie można otworzyć obrazu: {image_path}")
            return

        results = face_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = image.shape
                bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                       int(bboxC.width * iw), int(bboxC.height * ih)

                width = bboxC.width *iw
                height = bboxC.height *iw
                left = bboxC.xmin* iw
                right = width + left
                top = bboxC.ymin * ih
                btm = top + height

                # Dodatkowe marginesy, aby uwzględnić szyję (dostosuj według potrzeb)
                left = max(0,left-0.2*width)
                right = min(iw,right+0.2*width)
                top = max(0,top-0.8*height)
                btm = min(ih,btm+0.6*height)

                left = int(left)
                right = int(right)
                top = int(top)
                btm = int(btm)

                cropped_region = image[top:btm,left:right]

                # Zapisz wykadrowany obraz (opcjonalnie)
                cv2.imwrite(output_path, cropped_region)
                return output_path  # Zwróć ścieżkę do wykadrowanego obrazu

        print(f"Nie znaleziono twarzy na obrazie: {image_path}")
        return None


def remove_background_and_paste_on_white(image_path, output_path):
    try:
        with open(image_path, "rb") as i:
            output_bytes = remove(i.read())

        removed_bg_image = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
        width, height = removed_bg_image.size

        # Stwórz białe tło
        white_bg = Image.new("RGB", (width, height), "white")

        # Wklej obraz bez tła na białe tło
        white_bg.paste(removed_bg_image, (0, 0), removed_bg_image)

        white_bg.save(output_path, "PNG")
        return output_path
    except Exception as e:
        print(f"Wystąpił błąd podczas usuwania tła lub łączenia: {e}")
        return None

def resize_image(image_path, output_path, target_width, target_height):
    try:
        img = Image.open(image_path)
        resized_img = img.resize((target_width, target_height))
        resized_img.save(output_path)
        return output_path
    except Exception as e:
        print(f"Wystąpił błąd podczas zmiany rozmiaru obrazu: {e}")
        return None

def resize_image_with_aspect_ratio(image_path, output_path, target_width, target_height):
    try:
        img = Image.open(image_path)
        original_width, original_height = img.size

        aspect_ratio = original_width / original_height

        if target_width / target_height >= aspect_ratio:
            # Dopasuj wysokość, szerokość zostanie wyliczona
            new_height = target_height
            new_width = int(new_height * aspect_ratio)
        else:
            # Dopasuj szerokość, wysokość zostanie wyliczona
            new_width = target_width
            new_height = int(new_width / aspect_ratio)

        resized_img = img.resize((new_width, new_height))

        # Stwórz nowe białe tło o docelowych wymiarach i wycentruj na nim przeskalowany obraz
        new_background = Image.new("RGB", (target_width, target_height), "white")
        paste_x = (target_width - new_width) // 2
        paste_y = (target_height - new_height) // 2
        new_background.paste(resized_img, (paste_x, paste_y))

        new_background.save(output_path)
        return output_path
    except Exception as e:
        print(f"Wystąpił błąd podczas zmiany rozmiaru obrazu: {e}")
        return None

def process_image(input_image_path, output_directory, target_width, target_height):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    base_name = os.path.splitext(os.path.basename(input_image_path))[0]

    # Krok 1: Wykrycie twarzy i kadrowanie
    cropped_output_path = os.path.join(output_directory, f"{base_name}_cropped.jpg")
    cropped_path = crop_head_and_neck(input_image_path, cropped_output_path)

    if cropped_path:
        # Krok 2: Wycięcie osoby z tła i umieszczenie na białym
        removed_bg_output_path = os.path.join(output_directory, f"{base_name}_no_bg.png")
        removed_bg_path = remove_background_and_paste_on_white(cropped_path, removed_bg_output_path)

        if removed_bg_path:
            # Krok 3: Sformatowanie zdjęcia do zadanego rozmiaru
            resized_output_path = os.path.join(output_directory, f"{base_name}_final.png")
            resize_image_with_aspect_ratio(removed_bg_path, resized_output_path, target_width, target_height)
            # resize_image(removed_bg_path, resized_output_path, target_width, target_height)
            print(f"Przetworzono obraz: {input_image_path} -> {resized_output_path}")
        else:
            print(f"Nie udało się usunąć tła dla: {input_image_path}")
    else:
        print(f"Nie udało się wykadrować twarzy dla: {input_image_path}")

def normalize_filename(filename):
    return unicodedata.normalize('NFC', filename)

def proces_images(src_folder,output_folder,final_width,final_height):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(src_folder):

        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_image_path = os.path.join(src_folder, filename)
            base_name = os.path.splitext(filename)[0]
            final_output_path = os.path.join(output_folder, f"{base_name}_final.png")

            print(f"Przetwarzanie obrazu: {input_image_path}")
            process_image(input_image_path, output_folder, final_width, final_height)

    for filename in os.listdir(output_folder):
        if not 'final' in filename.lower():
            image_path = os.path.join(output_folder, filename)
            try:
                os.remove(image_path)
            except FileNotFoundError:
                print(f"{image_path} nie istnieje!")
            except OSError as e:
                print(f"Wystąpił błąd podczas usuwania pliku {file_path}: {e}")

if __name__ == "__main__":
    pass
