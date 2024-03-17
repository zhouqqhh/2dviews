from PIL import Image
import os

def merge_images(image_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]

    grouped_images = {}
    for img in images:
        prefix = '_'.join(img.split('_')[:2])
        if prefix not in grouped_images:
            grouped_images[prefix] = []
        grouped_images[prefix].append(img)

    for prefix, imgs in grouped_images.items():
        imgs.sort(key=lambda x: (int(x.split('_')[2]), int(x.split('_')[3].split('.')[0])))

        first_image = Image.open(os.path.join(image_folder, imgs[0]))

        max_row_index = max(int(img.split('_')[2]) for img in imgs)
        max_col_index = max(int(img.split('_')[3].split('.')[0]) for img in imgs)

        total_width = first_image.width * (max_col_index + 1)
        total_height = first_image.height * (max_row_index + 1)

        merged_image = Image.new('RGB', (total_width, total_height))

        for img in imgs:
            current_image = Image.open(os.path.join(image_folder, img))
            col = int(img.split('_')[2])
            row = int(img.split('_')[3].split('.')[0])
            x_offset = col * first_image.width
            y_offset = row * first_image.height
            merged_image.paste(current_image, (x_offset, y_offset))

        output_image_path = os.path.join(output_folder, f"{prefix}_merged.jpg")
        merged_image.save(output_image_path)

if __name__ == "__main__":
    image_folder = 'street_view_images'
    output_folder = 'merged_images'

    merge_images(image_folder, output_folder)
