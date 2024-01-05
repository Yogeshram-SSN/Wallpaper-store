from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from flask import jsonify
from flask import jsonify, session, render_template
from datetime import datetime, timedelta
import random
app = Flask(__name__, static_url_path="/static")
app.static_folder = "static"
app.secret_key = "your_secret_key"

# Initialize the database if it doesn't exist
conn = sqlite3.connect("homepage.db")
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS customer")
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS customer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        fullname TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        address TEXT NOT NULL,
        usertype TEXT NOT NULL
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
    
# creation of cart table 
sqlite_connection = sqlite3.connect("homepage.db", check_same_thread=False)
cursor = sqlite_connection.cursor()

# Drop tables
cursor.execute("DROP TABLE IF EXISTS carttable")

# Create tables
try:
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS carttable (
        user_name TEXT,
        product_id INTEGER,
        product_name TEXT,
        wallpaper_dimension TEXT,
        quantity INTEGER,
        price  REAL,
        FOREIGN KEY (user_name) REFERENCES customer(username),
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
    
# creation of wishlist table    
sqlite_connection = sqlite3.connect("homepage.db", check_same_thread=False)
cursor = sqlite_connection.cursor()

# Drop tables
cursor.execute("DROP TABLE IF EXISTS wishlisttable")

# Create tables
try:
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS wishlisttable (
        user_name TEXT,
        product_id INTEGER,
        product_name TEXT,
        wallpaper_dimension TEXT,
        price  REAL,
        FOREIGN KEY (user_name) REFERENCES customer(username),
        FOREIGN KEY (product_id, product_name, wallpaper_dimension, price) REFERENCES wallpapers(wallpaper_id, wallpaper_name, dimension, price)
        )
"""
    )
    sqlite_connection.commit()
    print("wishlist table created successfully.")

except sqlite3.Error as e:
    print(f"Error creating wishlist table and adding sample data: {e}")

finally:
    cursor.close()
    sqlite_connection.close()

 #creation of orders table
sqlite_connection = sqlite3.connect("homepage.db", check_same_thread=False)
cursor = sqlite_connection.cursor()

# Drop tables
cursor.execute("DROP TABLE IF EXISTS shippingtable")

# Create tables
try:
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS shippingtable (
        order_date DATE,
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        delivery_date DATE,
        user_name TEXT,
        total_price  REAL,
        address TEXT,
        total_quantity INTEGER,
        FOREIGN KEY (user_name,address) REFERENCES customer(username,address)
        )
"""
    )
    sqlite_connection.commit()
    print("shipping table created successfully.")

except sqlite3.Error as e:
    print(f"Error creating shipping table and adding sample data: {e}")

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


@app.route("/user_home")
def user_home():
    if "username" in session:
        combined_data = get_combined_data()
        base_url = "/static/images/"
        decoded_data = [
            (item[0], item[1], item[2], item[3], item[4], item[5], item[6])
            for item in combined_data
        ]
        return render_template(
            "user_homepage.html", combined_data=decoded_data, base_url=base_url
        )
    else:
        return redirect(url_for("login"))

@app.route("/admin_home")
def admin_home():
    if "username" in session:
        combined_data = get_combined_data()
        base_url = "/static/images/"
        decoded_data = [
            (item[0], item[1], item[2], item[3], item[4], item[5], item[6])
            for item in combined_data
        ]
        return render_template(
            "admin_homepage.html", combined_data=decoded_data, base_url=base_url
        )
    else:
        return redirect(url_for("login"))

def get_user_type(username):
    conn = sqlite3.connect("homepage.db")
    cursor = conn.cursor()
    cursor.execute("SELECT usertype FROM customer WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0]
    else:
        return None

'''@app.route("/")
def login():
   
    return render_template("login.html")'''


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        print(username,password)
        print("hi from login table")
        conn = sqlite3.connect("homepage.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM customer WHERE username=? AND password=?", (username, password)
        )
        print ('hello there')
        user = cursor.fetchall()
        print(user)
        conn.close()

        if user:
            usertype = user[0][7]
            print(usertype)
            session["username"] = username
            if usertype == "admin":
                return redirect(url_for("admin_home"))
            elif usertype == "user":
                return redirect(url_for("user_home"))
        else:
            flash("Invalid username or password.")

    # Handle both GET and failed POST requests here
    return render_template("login.html")

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
    usertype = request.form.get("usertype")
    print('hi register')
    try:
        conn = sqlite3.connect("homepage.db")
        cursor = conn.cursor()
    
        cursor.execute(
            """
            INSERT INTO customer (username, password, fullname, email, phone, address, usertype)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (username, password, fullname, email, phone, address, usertype),
        )

        conn.commit()
        if usertype == 'admin' or usertype == 'user':
            session["username"] = username
            return redirect(url_for(f"{usertype}_home"))
        else:
            flash("Invalid user type.")
            return redirect(url_for("register"))

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        flash("An error occurred during registration.")
        return redirect(url_for("register"))

    finally:
        conn.close()



@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("cart", None)
    return redirect(url_for("login"))


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    print("Received request:", request.get_json())
    sqlite_connection = sqlite3.connect("homepage.db", check_same_thread=False)
    cursor = sqlite_connection.cursor()
    data = request.get_json()
    username = session["username"]
    product_name = data.get('product')
    quantity = data.get('quantity', 1)  # Default to 1 if 'quantity' is not present

    cursor.execute(
        """
        SELECT wallpaper_id, dimension, price
        FROM wallpapers
        WHERE wallpaper_name=?
        """, (product_name,)
    )
    combined_data = cursor.fetchall()
    
    if combined_data:
        product_id = combined_data[0][0]
        wallpaper_dimension = combined_data[0][1]
        price = combined_data[0][2]
        
        cursor.execute("""
            INSERT INTO carttable(user_name, product_id, product_name, wallpaper_dimension, quantity, price)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, product_id, product_name, wallpaper_dimension, quantity, price),
        )

        cursor.execute("""
            SELECT product_name, wallpaper_dimension, quantity, price
            FROM carttable
            WHERE user_name=?
        """, (username,))
        cart_data = cursor.fetchall()
        print(cart_data)
        
        sqlite_connection.commit()
        cursor.close()
        sqlite_connection.close()
        return jsonify(cart_data)
    else:
        cursor.close()
        sqlite_connection.close()
        return "Product not found in the wallpaper table."
def create_availability_trigger():
    try:
        # Connect to the database
        sqlite_connection = sqlite3.connect("homepage.db", check_same_thread=False)
        cursor = sqlite_connection.cursor()

        # Create a trigger
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_availability
            AFTER INSERT ON carttable
            FOR EACH ROW
            BEGIN
                UPDATE wallpapers
                SET availability = availability - NEW.quantity
                WHERE wallpaper_id = NEW.product_id;
            END
        """)

        # Commit the changes
        sqlite_connection.commit()
        print("Trigger created successfully.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        # Close the database connection
        cursor.close()
        sqlite_connection.close()

# Call the function to create the trigger
create_availability_trigger()

@app.route("/cart")
def cart():
    if "username" in session:
        username = session["username"]
        sqlite_connection = sqlite3.connect("homepage.db", check_same_thread=False)
        cursor = sqlite_connection.cursor()
        
        cursor.execute("""
            SELECT product_name, wallpaper_dimension, quantity, price
            FROM carttable
            WHERE user_name=?
        """, (username,))
        cart_items = cursor.fetchall()
        print('in cart function')
        print(cart_items)
        
        base_url = "/static/images/"  # Set your base URL here
        cursor.close()
        sqlite_connection.close()
        total=sum(int(item[2])*int(item[3]) for item in cart_items) 
        print(total)
        
        return render_template("cart2.html", cart_items=cart_items, total=total, base_url=base_url)
    else:
        base_url = "/static/images/"  # Set your base URL here
        return render_template("cart2.html", cart_items=[], base_url=base_url)

@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    product_name = request.json.get("product")
    print(product_name)
    username = session["username"]
    sqlite_connection = sqlite3.connect("homepage.db", check_same_thread=False)
    cursor = sqlite_connection.cursor()
    
    cursor.execute("""
        DELETE FROM carttable
        WHERE user_name=? AND product_name=?
    """, (username, product_name))

    sqlite_connection.commit()
    print('updated table')

    cursor.execute("""
        SELECT product_name, wallpaper_dimension, quantity, price
        FROM carttable
        WHERE user_name=?
    """, (username,))
    cart_items = cursor.fetchall()

    sqlite_connection.close()

    session["cart"] = cart_items

    base_url = "/static/images/"
    return render_template("cart2.html", cart_items=cart_items, base_url=base_url)

@app.route("/payment")
def payment():
    if 'username' in session:
        sqlite_connection = sqlite3.connect("homepage.db", check_same_thread=False)
        cursor = sqlite_connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM carttable
            """
        )
        combined_data = cursor.fetchall()
        subtotal=sum(int(item[4])*int(item[5]) for item in combined_data)
        print(subtotal)
        total = subtotal+12
        return render_template("payment_card.html",subtotal=subtotal, total=total )
    else:
        return redirect(url_for("cart"))
        
@app.route("/payment_success")
def payment_success():
    sqlite_connection = sqlite3.connect("homepage.db", check_same_thread=False)
    cursor = sqlite_connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM carttable
        """
    )
    combined_data = cursor.fetchall()
    print('hi from shipping table')
    print(combined_data)

    if combined_data:
        user_name = combined_data[0][0]
        cursor.execute (""" select address from customer where 
        username=? """, (user_name,))
        address_result = cursor.fetchall()
        print(address_result)
        if address_result:
            address = address_result[0][0]
            total_quantity = sum(item[4] for item in combined_data)

            total = sum(int(item[4]) * int(item[5]) for item in combined_data)
            print(total)
            current_date = datetime.now().strftime("%Y-%m-%d")
            delivery_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")

            cursor.execute(
                """
                INSERT INTO shippingtable(order_date,delivery_date, user_name ,total_price, address ,total_quantity)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (current_date, delivery_date, user_name, total, address, total_quantity),
            )

            cursor.execute(
                """
                SELECT delivery_date, order_id
                FROM shippingtable
                WHERE user_name=?
                """,
                (user_name,),
            )
            shipping_data = cursor.fetchall()
            print(shipping_data)

            dd = shipping_data[0][0]
            order_id = shipping_data[0][1]

            sqlite_connection.commit()
            cursor.close()
            sqlite_connection.close()
            
            invoice_no = random.randint(1,900)
            return render_template("payment_success.html",delivery_date=dd, order_id=order_id,invoice_no=invoice_no)

        else:
            print("No address found for the user.")
            


@app.route("/add_to_wishlist", methods=["POST"])
def add_to_wishlist():
    print("Received request:", request.get_json())
    sqlite_connection = sqlite3.connect("homepage.db", check_same_thread=False)
    cursor = sqlite_connection.cursor()
    data = request.get_json()
    username = session["username"]
    product_name = data.get('product')
    cursor.execute(
        """
        SELECT wallpaper_id, dimension, price
        FROM wallpapers
        WHERE wallpaper_name=?
        """, (product_name,)
    )
    combined_data = cursor.fetchall()
    
    if combined_data:
        product_id = combined_data[0][0]
        wallpaper_dimension = combined_data[0][1]
        price = combined_data[0][2]
        cursor.execute("""
            INSERT INTO wishlisttable(user_name, product_id, product_name, wallpaper_dimension, price)
            VALUES (?, ?, ?, ?, ?)
        """, (username, product_id, product_name, wallpaper_dimension, price),
        )

        cursor.execute("""
            SELECT product_name, wallpaper_dimension, price
            FROM wishlisttable
            WHERE user_name=?
        """, (username,))
        wishlist_data = cursor.fetchall()
        print('hi')
        print(wishlist_data)
        
        sqlite_connection.commit()
        cursor.close()
        sqlite_connection.close()
        return jsonify(wishlist_data)
    else:
        cursor.close()
        sqlite_connection.close()
        return "Product not found in the wallpaper table."

@app.route("/wish")
def wish():
    if "username" in session:
        username = session["username"]
        sqlite_connection = sqlite3.connect("homepage.db", check_same_thread=False)
        cursor = sqlite_connection.cursor()
        
        cursor.execute("""
            SELECT product_name, wallpaper_dimension, price
            FROM wishlisttable
            WHERE user_name=?
        """, (username,))
        wish_items = cursor.fetchall()
        print('in wish function')
        print(wish_items)
        
        base_url = "/static/images/"  # Set your base URL here
        cursor.close()
        sqlite_connection.close()

        
        return render_template("wishlist.html", wish_items=wish_items, base_url=base_url)
    else:
        base_url = "/static/images/"  # Set your base URL here
        return render_template("wishlist.html", wish_items=[], base_url=base_url)
@app.route("/add_item")
def add_item():
    return render_template("add_item.html")

@app.route("/add_item", methods=["POST"])
def add_item_post():
    # Retrieve form data
    wallpaper_id = request.form.get("wallpaper_id")
    wallpaper_name = request.form.get("wallpaper_name")
    dimensions = request.form.get("dimensions")
    material = request.form.get("material")
    price = request.form.get("price")
    availability = request.form.get("availability")
    manufacturer_id = request.form.get("manufacturer_id")
    manu_info = request.form.get("manu_info")
    manu_contact = request.form.get("manu_contact")
    warranty_id = request.form.get("warranty_id")
    warranty = request.form.get("warranty")
    image = request.form.get("image")

    try:
        # Connect to the database
        sqlite_connection = sqlite3.connect("homepage.db", check_same_thread=False)
        cursor = sqlite_connection.cursor()

        # Insert new item into the wallpapers table
        cursor.execute(
            """
            INSERT INTO wallpapers (wallpaper_id, wallpaper_name, dimension, material, price, availability)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (wallpaper_id, wallpaper_name, dimensions, material, price, availability),
        )

        cursor.execute(
        """
        INSERT INTO manufacturer (manufacturer_id, manu_info, manu_contact)
        VALUES (?, ?, ?)
        """,
        (manufacturer_id, manu_info, manu_contact),
        )

        cursor.execute(
        """
        INSERT INTO warranty (warranty_id, warranty, image)
        VALUES (?, ?, ?)
        """,
        (warranty_id, warranty, image),
        )


        # Commit the changes
        sqlite_connection.commit()

        return redirect(url_for("admin_home"))  # Redirect to admin home after successful addition

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return "An error occurred while adding the item."

    finally:
        # Close the database connection
        cursor.close()
        sqlite_connection.close()

@app.route("/delete_item", methods=["GET", "POST"])
def delete_item():
    if request.method == "POST":
        wallpaper_name = request.form.get("wallpaper_name")

        try:
            # Connect to the database
            sqlite_connection = sqlite3.connect("homepage.db", check_same_thread=False)
            cursor = sqlite_connection.cursor()

            # Delete the item from the wallpapers table
            cursor.execute(
                """
                DELETE FROM wallpapers
                WHERE wallpaper_name=?
                """,
                (wallpaper_name,),
            )

            # Commit the changes
            sqlite_connection.commit()

            # Redirect to admin home after successful deletion
            return redirect(url_for("admin_home"))

        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return "An error occurred while deleting the item."

        finally:
            # Close the database connection
            cursor.close()
            sqlite_connection.close()

    return render_template("delete_item.html")
    
if __name__ == "__main__":
    app.run(debug=True, port=5005)