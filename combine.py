from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__, static_url_path="/static")
app.static_folder = "static"
app.secret_key = "your_secret_key"
cartobj = set()
wishobj=set()

# Initialize the database if it doesn't exist
conn = sqlite3.connect("database.db")
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS customer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        fullname TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        address TEXT NOT NULL
    )
"""
)
conn.commit()
conn.close()

# Initialize the wallpaper store database
sqlite_connection = sqlite3.connect("homepage.db", check_same_thread=False)
cursor = sqlite_connection.cursor()

# Drop tables
cursor.execute("DROP TABLE IF EXISTS wallpapers")
cursor.execute("DROP TABLE IF EXISTS manufacturer")
cursor.execute("DROP TABLE IF EXISTS warranty")

# Create tables
try:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS wallpapers (
            wallpaper_id INTEGER PRIMARY KEY,
            wallpaper_name TEXT,
            dimension TEXT,
            material TEXT,
            price REAL,
            availability TEXT
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS manufacturer (
            manufacturer_id INTEGER PRIMARY KEY,
            manu_info TEXT,
            manu_contact TEXT
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS warranty (
            warranty_id INTEGER PRIMARY KEY,
            warranty TEXT,
            image TEXT
        )
    """
    )

    # Insert values
    cursor.execute(
        """
        INSERT INTO wallpapers (wallpaper_id, wallpaper_name, dimension, material, price, availability)
        VALUES (1, 'Floral Pattern', '1080x720', 'Vinyl', 29.99, 'In Stock'),
               (2, 'Striped Design', '1200x800', 'Paper', 19.99, 'Out of Stock'),
               (3, 'Geometric Shapes', '800x600', 'Fabric', 39.99, 'In Stock'),
               (4, 'Abstract Art', '1600x900', 'Vinyl', 49.99, 'In Stock'),
               (5, 'Nature Scene', '1920x1080', 'Paper', 24.99, 'In Stock'),
               (6, 'Kids Cartoon', '720x480', 'Vinyl', 34.99, 'Out of Stock')
    """
    )

    cursor.execute(
        """
        INSERT INTO manufacturer (manufacturer_id, manu_info, manu_contact)
        VALUES (1, 'ABC Wallpapers Inc.', 'contact@abcwallpapers.com'),
               (2, 'XYZ Designs', 'info@xyzdesigns.com'),
               (3, 'Dreamy Interiors', 'dreamy@interiors.com'),
               (4, 'Artistic Decor', 'artistic@decor.com'),
               (5, 'Nature Wallpapers Ltd.', 'info@naturewallpapers.com'),
               (6, 'Kids Room Decor', 'kids@roomdecor.com')
    """
    )

    cursor.execute(
        """
        INSERT INTO warranty (warranty_id, warranty, image)
        VALUES (1, '1 year warranty', 'Floral Pattern.png'),
               (2, '2 year warranty', 'Striped Design.png'),
               (3, '3 year warranty', 'Geometric Shapes.png'),
               (4, '6 months warranty', 'Abstract Art.png'),
               (5, '1 year warranty', 'Nature Scene.png'),
               (6, 'No warranty', 'Kids Cartoon.png')
    """
    )

    sqlite_connection.commit()
    print("Tables and sample data created successfully.")

except sqlite3.Error as e:
    print(f"Error creating tables and adding sample data: {e}")

finally:
    cursor.close()
    sqlite_connection.close()

sqlite_connection = sqlite3.connect("homepage.db", check_same_thread=False)
cursor = sqlite_connection.cursor()

# Drop tables
cursor.execute("DROP TABLE IF EXISTS carttable")

# Create tables
try:
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS carttable (
        user_id INTEGER,
        product_id INTEGER,
        product_name TEXT,
        wallpaper_dimension TEXT,
        quantity INTEGER,
        price  REAL,
        FOREIGN KEY (user_id) REFERENCES customer(id),
        FOREIGN KEY (product_id, product_name, wallpaper_dimension, price) REFERENCES wallpapers(wallpaper_id, wallpaper_name, dimension, price)
        )
"""
    )
    sqlite_connection.commit()
    print("cart table created successfully.")

except sqlite3.Error as e:
    print(f"Error creating cart table and adding sample data: {e}")

finally:
    cursor.close()
    sqlite_connection.close()
    
def get_combined_data():
    sqlite_connection = sqlite3.connect("homepage.db", check_same_thread=False)
    cursor = sqlite_connection.cursor()
    cursor.execute(
        """
        SELECT w.warranty_id, w.warranty, w.image, wp.wallpaper_name, wp.material, wp.dimension, wp.price
        FROM warranty w
        JOIN wallpapers wp ON w.warranty_id = wp.wallpaper_id
    """
    )
    combined_data = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    return combined_data


@app.route("/home")
def home():
    if "username" in session:
        combined_data = get_combined_data()
        base_url = "/static/images/"
        decoded_data = [
            (item[0], item[1], item[2], item[3], item[4], item[5], item[6])
            for item in combined_data
        ]
        return render_template(
            "homepage.html", combined_data=decoded_data, base_url=base_url
        )
    else:
        return redirect(url_for("login"))


@app.route("/")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    username = request.form.get("username")
    password = request.form.get("password")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM customer WHERE username=? AND password=?", (username, password)
    )
    user = cursor.fetchone()

    conn.close()

    if user:
        session["username"] = username
        return redirect(url_for("home"))
    else:
        return redirect(url_for("login"))


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register_post():
    username = request.form.get("username")
    password = request.form.get("password")
    fullname = request.form.get("fullname")
    email = request.form.get("email")
    phone = request.form.get("phone")
    address = request.form.get("address")

    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO customer (username, password, fullname, email, phone, address)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (username, password, fullname, email, phone, address),
        )

        conn.commit()
        session["username"] = username
        return redirect(url_for("home"))

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return "An error occurred during registration."

    finally:
        conn.close()


@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("cart", None)
    return redirect(url_for("login"))


from flask import jsonify


from flask import jsonify, session, render_template

# Your existing routes and other code...


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    global cartobj
    print("here")
    if "cart" not in session:
        session["cart"] = []

    data = request.get_json()
    product_name = data.get("product")

    session["cart"].append(product_name)
    cartobj.add(product_name)

    # Print the cart contents to the console for demonstration purposes
    print("Cart Contents:", session["cart"])

    return jsonify({"success": True})


@app.route("/cart")
def cart():
    if "cart" in session:
        print(cartobj)
        cart_items = session["cart"]
        base_url = "/static/images/"  # Set your base URL here
        print("Cart Items:", cart_items)  # Print the contents of cart_items
        return render_template("cart2.html", product_names=cartobj, base_url=base_url)
    else:
        base_url = "/static/images/"  # Set your base URL here
        return render_template(
            "cart2.html", product_names=[], base_url=base_url
        )  # Pass an empty list if no items

@app.route("/payment")
def payment():
        return render_template("payment_card.html")

@app.route("/payment_success")
def payment_success():
        return render_template("payment_success.html")


@app.route("/add_to_wishlist", methods=["POST"])
def add_to_wishlist():
    global wishobj
    print("here")
    if "wish" not in session:
        session["wish"] = []

    data = request.get_json()
    product_name = data.get("product")

    session["wish"].append(product_name)
    wishobj.add(product_name)

    # Print the cart contents to the console for demonstration purposes
    print("wish Contents:", session["wish"])

    return jsonify({"success": True})


@app.route("/wish")
def wish():
    if "wish" in session:
        print(wishobj)
        wish_items = session["cart"]
        base_url = "/static/images/"  # Set your base URL here
        print("Wish Items:", wish_items)  # Print the contents of cart_items
        return render_template("wishlist.html", product_names=wishobj, base_url=base_url)
    else:
        base_url = "/static/images/"  # Set your base URL here
        return render_template(
            "wishlist.html", product_names=[], base_url=base_url
        )  # Pass an empty list if no items
        
if __name__ == "__main__":
    app.run(debug=True, port=5005)
