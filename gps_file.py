import os
import sys
import exifread
import folium
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox

def extract_gps_tags(file_path):
    """Extract GPS tags from image."""
    with open(file_path, 'rb') as f:
        tags = exifread.process_file(f)
        if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
            latitude_ref = str(tags['GPS GPSLatitudeRef'])
            latitude = tags['GPS GPSLatitude'].values
            longitude_ref = str(tags['GPS GPSLongitudeRef'])
            longitude = tags['GPS GPSLongitude'].values
            return latitude_ref, latitude, longitude_ref, longitude
    return None

def generate_map(image_path):
    """Generate HTML map with image at GPS location."""
    m = folium.Map()
    gps_tags = extract_gps_tags(image_path)
    if gps_tags:
        latitude_ref, latitude, longitude_ref, longitude = gps_tags
        latitude_decimal = convert_to_decimal(latitude, latitude_ref)
        longitude_decimal = convert_to_decimal(longitude, longitude_ref)
        img_path = os.path.abspath(image_path)
        popup_html = f'{os.path.basename(image_path)}'
        folium.Marker(location=[latitude_decimal, longitude_decimal], popup=popup_html).add_to(m)

    map_html_path = os.path.join(os.path.dirname(image_path), "map.html")
    m.save(map_html_path)
    return map_html_path

def convert_to_decimal(value, ref):
    """Convert GPS coordinates to decimal."""
    degrees = value[0].num / value[0].den
    minutes = value[1].num / value[1].den
    seconds = value[2].num / value[2].den
    decimal_value = degrees + (minutes / 60) + (seconds / 3600)
    if ref == 'S' or ref == 'W':
        decimal_value *= -1
    return decimal_value

class ImageMapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Map Generator")
        self.setGeometry(100, 100, 800, 600)
        self.select_image()

    def select_image(self):
        options = QFileDialog.Options()
        image_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner une image", "", "Image Files (*.jpg *.jpeg *.png)", options=options)
        if image_path:
            map_html = generate_map(image_path)
            QMessageBox.information(self, "Succès", f"La carte a été générée avec succès : {map_html}")
            sys.exit()
        else:
            sys.exit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageMapApp()
    window.show()
    sys.exit(app.exec_())