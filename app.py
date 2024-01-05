import sqlite3
from flask import Flask, render_template, url_for


app = Flask(__name__, static_url_path='/static')
app.static_folder = 'static'

sqlite_connection = sqlite3.connect('homepage.db', check_same_thread=False)
cursor = sqlite_connection.cursor()

# Drop tables 
cursor.execute("DROP TABLE IF EXISTS wallpapers")
cursor.execute("DROP TABLE IF EXISTS manufacturer")
cursor.execute("DROP TABLE IF EXISTS warranty")

# Create tables
try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wallpapers (
            wallpaper_id INTEGER PRIMARY KEY,
            wallpaper_name TEXT,
            dimension TEXT,
            material TEXT,
            price REAL,
            availability TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manufacturer (
            manufacturer_id INTEGER PRIMARY KEY,
            manu_info TEXT,
            manu_contact TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS warranty (
            warranty_id INTEGER PRIMARY KEY,
            warranty TEXT,
            image TEXT
        )
    """)

    # insert values
    cursor.execute("""
        INSERT INTO wallpapers (wallpaper_id, wallpaper_name, dimension, material, price, availability)
        VALUES (1, 'Floral Pattern', '1080x720', 'Vinyl', 29.99, 'In Stock'),
               (2, 'Striped Design', '1200x800', 'Paper', 19.99, 'Out of Stock'),
               (3, 'Geometric Shapes', '800x600', 'Fabric', 39.99, 'In Stock'),
               (4, 'Abstract Art', '1600x900', 'Vinyl', 49.99, 'In Stock'),
               (5, 'Nature Scene', '1920x1080', 'Paper', 24.99, 'In Stock'),
               (6, 'Kids Cartoon', '720x480', 'Vinyl', 34.99, 'Out of Stock')
    """)


    cursor.execute("""
        INSERT INTO manufacturer (manufacturer_id, manu_info, manu_contact)
        VALUES (1, 'ABC Wallpapers Inc.', 'contact@abcwallpapers.com'),
               (2, 'XYZ Designs', 'info@xyzdesigns.com'),
               (3, 'Dreamy Interiors', 'dreamy@interiors.com'),
               (4, 'Artistic Decor', 'artistic@decor.com'),
               (5, 'Nature Wallpapers Ltd.', 'info@naturewallpapers.com'),
               (6, 'Kids Room Decor', 'kids@roomdecor.com')
    """)

    cursor.execute("""
        INSERT INTO warranty (warranty_id, warranty, image)
        VALUES (1, '1 year warranty', 'image1.png'),
               (2, '2 year warranty', 'image2.png'),
               (3, '3 year warranty', 'image3.png'),
               (4, '6 months warranty', 'image4.png'),
               (5, '1 year warranty', 'image5.png'),
               (6, 'No warranty', 'image6.png')
    """)

    sqlite_connection.commit()
    print("Tables and sample data created successfully.")

except sqlite3.Error as e:
    print(f"Error creating tables and adding sample data: {e}")

finally:
    cursor.close()
    sqlite_connection.close()

    


def get_combined_data():

    sqlite_connection = sqlite3.connect('homepage.db', check_same_thread=False)
    cursor = sqlite_connection.cursor()


    cursor.execute("""
        SELECT w.warranty_id, w.warranty, w.image, wp.wallpaper_name, wp.material, wp.dimension, wp.price
        FROM warranty w
        JOIN wallpapers wp ON w.warranty_id = wp.wallpaper_id
    """)
    combined_data = cursor.fetchall()

    cursor.close()
    sqlite_connection.close()

    return combined_data


@app.route('/')

def home():
    combined_data = get_combined_data()
    base_url = '/static/images/'
    decoded_data = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in combined_data]
    return render_template('filter.html', combined_data=decoded_data, base_url=base_url)

if __name__ == '__main__':
    app.run(debug=True)