# ============================================================
# SECTION 1: Imports and app setup
# ============================================================
# Flask          -> the main class that creates our web app
# render_template-> loads an HTML file from the "templates" folder
# request        -> gives us data sent by the browser (forms, JSON)
# redirect, url_for -> send the user to another page
# jsonify        -> turns Python data into a JSON response (for APIs)
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

# Create the app object. __name__ tells Flask where this project lives.
# This project stores its HTML files in "template" (singular).
app = Flask(__name__, template_folder="template")

SHOP = "shopeasy"   # shop name, passed to every template


# ============================================================
# SECTION 7: Database connection (SQLite + Flask-SQLAlchemy)
# ============================================================
# SQLite stores everything in one small file, so no server is needed.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shop.db"
db = SQLAlchemy(app)   # db is our connection to the database


# A Model = one database table. Each class attribute = one column.
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)      # unique id, auto-increments
    name = db.Column(db.String(100), nullable=False)  # text, cannot be empty
    price = db.Column(db.Float, nullable=False)       # decimal number
    stock = db.Column(db.Integer, default=0)          # whole number

    # Helper used by the API: converts a Product into a dictionary
    def to_dict(self):
        return {"id": self.id, "name": self.name,
                "price": self.price, "stock": self.stock}


# Create the table (if missing) and add starter data (only the first time)
with app.app_context():
    db.create_all()
    if Product.query.count() == 0:
        db.session.add_all([
            Product(name="Running Shoes", price=59.99, stock=10),
            Product(name="Sneakers", price=45.50, stock=0),
            Product(name="Sandals", price=25.00, stock=4),
        ])
        db.session.commit()


# ============================================================
# SECTION 2 + 3: Simple routes and rendering index.html
# ============================================================
# @app.route is a decorator: it connects a URL ("/") to the function below.
@app.route("/")
def home():
    # render_template loads templates/index.html.
    # shop=SHOP makes the variable {{ shop }} available inside the HTML.
    return render_template("index.html", shop=SHOP)


# ============================================================
# SECTION 4: Product page with Jinja2 (data comes from the database)
# ============================================================
@app.route("/product")
def product():
    products = Product.query.all()   # SELECT * FROM product
    return render_template("product.html", shop=SHOP, products=products)


# ============================================================
# SECTION 5: HTTP methods - GET shows the form, POST saves it
# ============================================================
@app.route("/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        # request.form holds the values typed in the HTML form
        new = Product(
            name=request.form["name"],
            price=float(request.form["price"]),
            stock=int(request.form["stock"]),
        )
        db.session.add(new)      # stage the new row
        db.session.commit()      # save it to the database
        return redirect(url_for("product"))   # go back to the product list
    return render_template("add_product.html", shop=SHOP)   # GET: show form


@app.route("/delete/<int:id>", methods=["POST"])   # <int:id> = dynamic URL part
def delete_product(id):
    p = Product.query.get_or_404(id)   # find the product, or show 404
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for("product"))


# ============================================================
# SECTION 6 + 8: REST API (returns JSON, full CRUD on the database)
# ============================================================
# READ all
@app.route("/api/products", methods=["GET"])
def api_list():
    return jsonify([p.to_dict() for p in Product.query.all()])


# READ one
@app.route("/api/products/<int:id>", methods=["GET"])
def api_get(id):
    return jsonify(Product.query.get_or_404(id).to_dict())


# CREATE
@app.route("/api/products", methods=["POST"])
def api_create():
    data = request.get_json()   # JSON sent by the client
    if not data or "name" not in data or "price" not in data:
        return jsonify(error="name and price are required"), 400
    p = Product(name=data["name"], price=data["price"], stock=data.get("stock", 0))
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201   # 201 = Created


# UPDATE
@app.route("/api/products/<int:id>", methods=["PUT"])
def api_update(id):
    p = Product.query.get_or_404(id)
    data = request.get_json()
    p.name = data.get("name", p.name)        # keep old value if not sent
    p.price = data.get("price", p.price)
    p.stock = data.get("stock", p.stock)
    db.session.commit()
    return jsonify(p.to_dict())


# DELETE
@app.route("/api/products/<int:id>", methods=["DELETE"])
def api_delete(id):
    p = Product.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return jsonify(message="deleted")


# ============================================================
# SECTION 9: Run the app
# ============================================================
# This block runs only when you start the file with "python app.py".
# debug=True auto-restarts on changes and shows detailed errors (dev only).
if __name__ == "__main__":
    app.run(debug=True)