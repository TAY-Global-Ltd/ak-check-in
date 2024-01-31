from PIL import Image

if __name__ == '__main__':
    filename = r'logos/ak-logo.png'
    img = Image.open(filename)
    img.save('logos/favicon.ico')