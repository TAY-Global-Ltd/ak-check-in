from PIL import Image

def downsize_image(input_image_path, output_image_path, size):
    with Image.open(input_image_path) as img:
        img.thumbnail(size)
        img.save(output_image_path)


if __name__ == '__main__':
    for resolution in [(960, 960), (640, 640), (480, 480)]:
        output_file = f'logos/ak-logo-{resolution[0]}x{resolution[1]}.png'
        downsize_image('logos/ak-logo.png', output_file, resolution)