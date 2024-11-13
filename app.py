from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from models.Cashier import Cashier
from models.Manager import Manager
from models.user import User
from services.auth import authenticate_user, migrate_passwords
from services.token_service import create_token, decode_token
from services.database import db
from sqlalchemy import inspect
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask application
app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize database and migration
db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()  # This creates tables if they don't exist

# Routes
@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    passcode = data.get('passcode')

    # Passcode validation: must be between 4 and 6 digits
    if not (4 <= len(passcode) <= 6):
        return jsonify({'message': 'Passcode must be between 4 and 6 digits'}), 400

    user = authenticate_user(username, passcode)

    if user:
        session['user_id'] = user['id']  # Store user ID in session
        session['role'] = user['role']   # Store user role in session

        # Create a token with the user dictionary
        token = create_token(user)  # Generate the token for the user

        return jsonify({"user": user, "role": user['role'], "token": token}), 200
    else:
        return jsonify({'message': 'Invalid Credentials'}), 401



@app.route('/protected', methods=['GET'])
def protected_api():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"message": "Token is missing"}), 403

    token = auth_header.split(" ")[1]  # Bearer <token>
    decoded = decode_token(token)

    if decoded:
        user = Cashier.query.get(decoded['user_id']) or Manager.query.get(decoded['user_id'])
        if user:
            return jsonify({
                "id": user.id,
                "firstname": user.name,
                "lastname": user.last_name,
                "username": user.username,
                "role": "cashier" if isinstance(user, Cashier) else "manager",
                "token": token
            }), 200
    return jsonify({"message": "Invalid or expired token"}), 403

@app.route('/test-db')
def test_db_connection():
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        if tables:
            return jsonify({"message": "Database connection successful!", "tables": tables}), 200
        else:
            return jsonify({"message": "Connected to database, but no tables found."}), 200
    except Exception as e:
        return jsonify({"message": f"Error connecting to database: {str(e)}"}), 500


@app.route('/create_manager', methods=['POST'])
def create_manager():
    data = request.json
    name = data.get('name')
    last_name = data.get('last_name')
    username = data.get('username')
    passcode = data.get('passcode')

    if not name or not last_name or not username or not passcode:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    if Manager.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists", "success": False}), 400

    try:
        new_manager = Manager(name=name, last_name=last_name, username=username, passcode=passcode)
        db.session.add(new_manager)
        db.session.commit()

        return jsonify({"message": "Manager created successfully", "success": True, "manager": {
            "id": new_manager.id,
            "name": new_manager.name,
            "last_name": new_manager.last_name,
            "username": new_manager.username,
            "passcode": new_manager.passcode,
            "date_created": new_manager.date_created
        }}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Failed to save manager: {str(e)}", "success": False}), 500

@app.route('/get_managers', methods=['GET'])
def get_managers():
        # Query the database for all managers
        managers = Manager.query.all()

        # Create a JSON response with manager details
        return jsonify({"managers": [
            {
                "id": manager.id,
                "name": manager.name,
                "last_name": manager.last_name,
                "username": manager.username,
                "passcode": manager.passcode,  # Only include this if passcode should be visible
                "date_created": manager.date_created
            } for manager in managers
        ]}), 200



@app.route('/sales_order')
def sales_order():
    return render_template('sales_order.html')

@app.route('/main')
def main():
    return render_template('main.html')

# Endpoint to add a new user
@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    new_user = User(
        full_name=data['full_name'],
        email_address=data['email_address'],
        username=data['username'],
        password=data['password'],
        user_title=data['user_title'],
        user_level=data['user_level']
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User added successfully!",
        "user": new_user.to_dict()
    })

@app.route('/get_users', methods=['GET'])
def get_users():
    try:
        # Query all users from the database
        users = User.query.all()

        # Convert the users to a list of dictionaries
        users_list = [user.to_dict() for user in users]

        # Return the list of users as a JSON response
        return jsonify(users_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return error if any exception occurs

@app.route('/get_user/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user:
        return jsonify({
            "id": user.id,
            "full_name": user.full_name,
            "email_address": user.email_address,
            "username": user.username,
            "password": user.password,
            "user_title": user.user_title,
            "user_level": user.user_level
        }), 200
    else:
        return jsonify({"error": "User not found"}), 404


@app.route('/update_user/<int:id>', methods=['POST'])
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Update user fields with form data
    user.full_name = request.form.get('full_name')
    user.email_address = request.form.get('email_address')
    user.username = request.form.get('username')
    user.password = request.form.get('password')  # Ensure this is handled securely in production
    user.user_title = request.form.get('user_title')
    user.user_level = request.form.get('user_level')

    # Save changes
    db.session.commit()
    return jsonify({"success": True}), 200



@app.route('/get_cashier_name', methods=['GET'])
def get_cashier_name():
    if 'user_id' in session:
        cashier = db.session.get(Cashier, session['user_id'])
        if cashier:
            return jsonify({
                "name": cashier.name,
                "last_name": cashier.last_name
            }), 200
    return jsonify({"message": "Not authenticated"}), 401


@app.route('/seats')
def seats():
    return render_template('seats.html')

@app.route('/payment')
def payment():
    return render_template('payment.html')

@app.route('/order_history')
def order_history():
    return render_template('order_history.html')

@app.route('/managers')
def manager_dashboard():
    return render_template('managers.html')

@app.route('/dashboard1')
def dashboard1():
    return render_template('dashboard1.html')

@app.route('/user_management')
def user_management():
    return render_template('user_management/um_tab_panel.html')

@app.route('/profile_management')
def profile_management():
    return render_template('profile_management.html')

@app.route('/create_cashier', methods=['POST'])
def create_cashier():
    data = request.json
    name = data.get('name')
    last_name = data.get('last_name')
    username = data.get('username')
    passcode = data.get('passcode')

    if not name or not last_name or not username or not passcode:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    if Cashier.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists", "success": False}), 400

    try:
        new_cashier = Cashier(name=name, last_name=last_name, username=username, passcode=passcode)
        db.session.add(new_cashier)
        db.session.commit()

        return jsonify({"message": "Cashier created successfully", "success": True, "cashier": {
            "id": new_cashier.id,
            "name": new_cashier.name,
            "last_name": new_cashier.last_name,
            "username": new_cashier.username,
            "passcode": new_cashier.passcode,
            "date_created": new_cashier.date_created
        }}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Failed to save cashier: {str(e)}", "success": False}), 500

@app.route('/get_cashiers', methods=['GET'])
def get_cashiers():
    cashiers = Cashier.query.all()
    return jsonify({"cashiers": [
        {
            "id": cashier.id,
            "name": cashier.name,
            "last_name": cashier.last_name,
            "username": cashier.username,
            "passcode": cashier.passcode,
            "date_created": cashier.date_created
        } for cashier in cashiers
    ]}), 200

@app.route('/edit_cashier/<int:cashier_id>', methods=['PUT'])
def edit_cashier(cashier_id):
    data = request.json
    name = data.get('name')
    last_name = data.get('last_name')
    username = data.get('username')
    passcode = data.get('passcode')

    cashier = Cashier.query.get(cashier_id)  # Changed from session to query directly
    if not cashier:
        return jsonify({"message": "Cashier not found", "success": False}), 404

    cashier.name = name
    cashier.last_name = last_name
    cashier.username = username
    cashier.passcode = passcode
    db.session.commit()

    return jsonify({"message": "Cashier updated successfully", "success": True, "cashier": {
        "id": cashier.id,
        "name": cashier.name,
        "last_name": cashier.last_name,
        "username": cashier.username,
        "passcode": cashier.passcode,
        "date_created": cashier.date_created
    }}), 200

@app.route('/delete_cashier/<int:cashier_id>', methods=['DELETE'])
def delete_cashier(cashier_id):
    cashier = Cashier.query.get(cashier_id)
    if not cashier:
        return jsonify({"message": "Cashier not found", "success": False}), 404
    db.session.delete(cashier)
    db.session.commit()
    return jsonify({"message": "Cashier deleted successfully", "success": True}), 200

@app.route('/inventory_management')
def inventory_management():
    return render_template('inventory_management.html')

@app.route('/cashier_summary')
def cashier_summary():
    return render_template('cashier_summary.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/change_passcode', methods=['POST'])
def process_change_passcode():
    data = request.get_json()
    old_passcode = data.get('old_passcode')
    new_passcode = data.get('new_passcode')

    user_id = session.get('user_id')
    user_role = session.get('role')

    if not user_id:
        return jsonify({"message": "User not logged in", "success": False}), 400

    user = Cashier.query.get(user_id) if user_role == 'cashier' else Manager.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found", "success": False}), 404

    if user.passcode != old_passcode:
        return jsonify({"message": "Old passcode is incorrect", "success": False}), 400

    user.passcode = new_passcode
    db.session.commit()

    return jsonify({"message": "Passcode changed successfully!", "success": True}), 200

if __name__ == "__main__":
    with app.app_context():
        migrate_passwords()  # Call the migration function
    app.run(debug=True)
