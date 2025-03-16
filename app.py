import os
import logging
import msal
from flask import Flask, request, jsonify, render_template, redirect, session, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from azure.cosmos import CosmosClient, exceptions

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "1234"  # Change this to a secure key
app.config["DEBUG"] = True  # Enable debug mode

# 🔹 Enable logging
logging.basicConfig(level=logging.DEBUG)

# 🔹 Hardcoded Cosmos DB Credentials
ENDPOINT = "https://productscataloguecosmos.documents.azure.com:443/"
KEY = "uKP2wzQIpMKcelyG5eAeNZs5kU5OBYQuzsiNT7aBDeIGmoOYk7vfDeNtD5UZ9sHZwJxN5WJrmKKcACDbudVqlQ=="
DATABASE_NAME = "ProductsDB"
CONTAINER_NAME = "products"

try:
    client = CosmosClient(ENDPOINT, credential=KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)
    logging.info("✅ Successfully connected to Cosmos DB")
except exceptions.CosmosHttpResponseError as e:
    logging.error(f"❌ Cosmos DB Connection Failed: {str(e)}")
    raise

# 🔹 Azure AD Credentials
CLIENT_ID = "e6609120-0b10-459e-8bad-8decc04b3810"
CLIENT_SECRET = "lfL8Q~yFlElMJ.VZbucbkTByLb_2zqw8DYDyIc1M"
TENANT_ID = "624d5c4b-45c5-4122-8cd0-44f0f84e945d"
AUTHORITY = f"https://login.microsoftonline.com/624d5c4b-45c5-4122-8cd0-44f0f84e945d"
REDIRECT_URI = "https://productcatalogue-ell887-asfefaeehgbse0at.eastus2-01.azurewebsites.net/auth/callback"
SCOPE = ["User.Read"]

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, user_id, name):
        self.id = user_id
        self.name = name

@login_manager.user_loader
def load_user(user_id):
    return User(user_id, session.get("user", {}).get("name", "Unknown"))

# 🔹 MSAL Instance for Token Management
msal_app = msal.ConfidentialClientApplication(CLIENT_ID, CLIENT_SECRET, authority=AUTHORITY)

# ------------------- ROUTES -------------------

@app.route("/")
def home():
    """Homepage with login/logout links."""
    user = session.get("user")
    return render_template("index.html", user=user)

@app.route("/login")
def login():
    """Redirects user to Azure AD login."""
    auth_url = msal_app.get_authorization_request_url(SCOPE, redirect_uri=REDIRECT_URI)
    return redirect(auth_url)

@app.route("/auth/callback")
def auth_callback():
    """Handles Azure AD authentication callback."""
    code = request.args.get("code")
    token_response = msal_app.acquire_token_by_authorization_code(code, scopes=SCOPE, redirect_uri=REDIRECT_URI)

    if "id_token_claims" in token_response:
        user_info = token_response["id_token_claims"]
        session["user"] = user_info
        login_user(User(user_info["oid"], user_info.get("name", "User")))
        return redirect(url_for("home"))

    return "Authentication failed", 401

@app.route("/logout")
@login_required
def logout():
    """Logs the user out."""
    session.clear()
    logout_user()
    return redirect(url_for("home"))


@app.route("/clear", methods=["DELETE"])
@login_required
def clear_products():
    """Deletes all products from Cosmos DB using 'id' as the partition key."""
    try:
        items = list(container.read_all_items())

        if not items:
            return jsonify({"message": "No products to delete!"}), 200

        deleted_products = []
        for item in items:
            partition_key = item["productID"]  # Use 'id' as partition key
            container.delete_item(item["id"], partition_key=partition_key)
            deleted_products.append(item["name"])
            logging.info(f"🗑️ Deleted product: {item['name']} (ID: {item['id']})")

        return jsonify({"message": "All products deleted successfully!", "deleted_products": deleted_products}), 200

    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"❌ Error clearing products: {str(e)}")
        return jsonify({"error": "Failed to clear products", "details": str(e)}), 500









@app.route("/protected")
@login_required
def protected():
    """A protected route only accessible after login."""
    return f"Welcome, {session['user']['name']}!"

@app.route("/add", methods=["POST"])
@login_required
def add_product():
    """API to add a product to Cosmos DB (requires login)."""
    try:
        data = request.json
        logging.info(f"📦 Received Product: {data}")
        container.create_item(body=data)
        return jsonify({"message": "Product added"}), 201
    except Exception as e:
        logging.error(f"❌ Error adding product: {str(e)}")
        return jsonify({"error": "Failed to add product", "details": str(e)}), 500

@app.route("/products", methods=["GET"])
@login_required
def get_products():
    """API to fetch all products from Cosmos DB (requires login)."""
    try:
        items = list(container.read_all_items())
        logging.info(f"📦 Retrieved Products: {items}")
        return jsonify(items)
    except Exception as e:
        logging.error(f"❌ Error fetching products: {str(e)}")
        return jsonify({"error": "Failed to fetch products", "details": str(e)}), 500

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8080))  
    app.run(host="0.0.0.0", port=PORT)
