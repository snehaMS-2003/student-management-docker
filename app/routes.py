import re
from datetime import datetime
from flask import Blueprint, jsonify, request, render_template
from app.database import get_connection
import mysql.connector

routes = Blueprint('routes', __name__)

def validate_student_data(data, is_update=False):
    """Validate student input fields. Returns (errors, sanitized_data)."""
    errors = {}
    name = data.get('name', '').strip() if data.get('name') else ''
    email = data.get('email', '').strip().lower() if data.get('email') else ''
    phone = data.get('phone', '').strip() if data.get('phone') else ''
    department = data.get('department', '').strip() if data.get('department') else ''
    gender = data.get('gender', '').strip() if data.get('gender') else ''
    dob_raw = data.get('date_of_birth', '').strip() if data.get('date_of_birth') else ''

    if not name:
        errors['name'] = 'Full Name is required.'
    elif len(name) < 2 or len(name) > 100:
        errors['name'] = 'Name must be between 2 and 100 characters.'

    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not email:
        errors['email'] = 'Email is required.'
    elif not re.match(email_regex, email):
        errors['email'] = 'Invalid email address format.'

    if not phone:
        errors['phone'] = 'Phone number is required.'
    elif not re.match(r'^[0-9+\-\s()]{7,20}$', phone):
        errors['phone'] = 'Invalid phone number format.'

    if not department:
        errors['department'] = 'Department is required.'

    if gender not in ['Male', 'Female', 'Other']:
        errors['gender'] = 'Gender must be Male, Female, or Other.'

    date_of_birth = None
    if not dob_raw:
        errors['date_of_birth'] = 'Date of birth is required.'
    else:
        try:
            date_of_birth = datetime.strptime(dob_raw, '%Y-%m-%d').date()
            if date_of_birth > datetime.today().date():
                errors['date_of_birth'] = 'Date of birth cannot be in the future.'
        except ValueError:
            errors['date_of_birth'] = 'Date of birth must be in YYYY-MM-DD format.'

    sanitized = {
        'name': name,
        'email': email,
        'phone': phone,
        'department': department,
        'gender': gender,
        'date_of_birth': str(date_of_birth) if date_of_birth else None
    }
    return errors, sanitized

# ----------------- UI Pages -----------------

@routes.route('/')
def dashboard_page():
    return render_template('dashboard.html', active_page='dashboard')

@routes.route('/students')
def students_page():
    return render_template('students.html', active_page='students')

@routes.route('/students/add')
def student_add_page():
    return render_template('student_form.html', active_page='add_student', student_id=None)

@routes.route('/students/edit/<int:student_id>')
def student_edit_page(student_id):
    return render_template('student_form.html', active_page='students', student_id=student_id)

# ----------------- REST API Endpoints -----------------

@routes.route('/api/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Retrieve dashboard metric stats."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS total_students FROM students")
        total_students = cursor.fetchone()['total_students']

        cursor.execute("SELECT COUNT(DISTINCT department) AS total_departments FROM students")
        total_departments = cursor.fetchone()['total_departments']

        cursor.execute("""
            SELECT id, name, email, phone, department, gender, 
                   DATE_FORMAT(date_of_birth, '%Y-%m-%d') AS date_of_birth,
                   DATE_FORMAT(created_at, '%Y-%m-%d %H:%i') AS created_at
            FROM students
            ORDER BY id DESC
            LIMIT 5
        """)
        recent_students = cursor.fetchall()

        cursor.execute("""
            SELECT department, COUNT(*) AS count
            FROM students
            GROUP BY department
            ORDER BY count DESC
        """)
        department_distribution = cursor.fetchall()

        cursor.close()
        return jsonify({
            'success': True,
            'data': {
                'total_students': total_students,
                'total_departments': total_departments,
                'recent_students': recent_students,
                'department_distribution': department_distribution
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f"Database error: {str(e)}"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

@routes.route('/api/students', methods=['GET'])
def get_students():
    """Get all students or filter by search query."""
    search_query = request.args.get('search', '').strip()
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if search_query:
            sql = """
                SELECT id, name, email, phone, department, gender,
                       DATE_FORMAT(date_of_birth, '%Y-%m-%d') AS date_of_birth,
                       DATE_FORMAT(created_at, '%Y-%m-%d %H:%i') AS created_at
                FROM students
                WHERE name LIKE %s OR email LIKE %s OR department LIKE %s
                ORDER BY id DESC
            """
            pattern = f"%{search_query}%"
            cursor.execute(sql, (pattern, pattern, pattern))
        else:
            sql = """
                SELECT id, name, email, phone, department, gender,
                       DATE_FORMAT(date_of_birth, '%Y-%m-%d') AS date_of_birth,
                       DATE_FORMAT(created_at, '%Y-%m-%d %H:%i') AS created_at
                FROM students
                ORDER BY id DESC
            """
            cursor.execute(sql)

        students = cursor.fetchall()
        cursor.close()
        return jsonify({'success': True, 'count': len(students), 'data': students}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f"Database error: {str(e)}"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

@routes.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """Get a single student record by ID."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, name, email, phone, department, gender,
                   DATE_FORMAT(date_of_birth, '%Y-%m-%d') AS date_of_birth,
                   DATE_FORMAT(created_at, '%Y-%m-%d %H:%i') AS created_at
            FROM students
            WHERE id = %s
        """, (student_id,))
        student = cursor.fetchone()
        cursor.close()

        if not student:
            return jsonify({'success': False, 'message': f'Student with ID {student_id} not found.'}), 404

        return jsonify({'success': True, 'data': student}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f"Database error: {str(e)}"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

@routes.route('/api/students', methods=['POST'])
def create_student():
    """Create a new student record."""
    data = request.get_json(silent=True)
    if data is None:
        data = request.form.to_dict()

    if not isinstance(data, dict):
        return jsonify({'success': False, 'message': 'Invalid JSON or form payload.'}), 400

    errors, sanitized = validate_student_data(data)
    if errors:
        return jsonify({'success': False, 'errors': errors, 'message': 'Validation failed.'}), 422

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Check unique email
        cursor.execute("SELECT id FROM students WHERE email = %s", (sanitized['email'],))
        if cursor.fetchone():
            cursor.close()
            return jsonify({'success': False, 'errors': {'email': 'Email is already registered.'}, 'message': 'Email must be unique.'}), 409

        sql = """
            INSERT INTO students (name, email, phone, department, gender, date_of_birth)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            sanitized['name'],
            sanitized['email'],
            sanitized['phone'],
            sanitized['department'],
            sanitized['gender'],
            sanitized['date_of_birth']
        ))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()

        return jsonify({
            'success': True,
            'message': 'Student created successfully.',
            'data': {'id': new_id, **sanitized}
        }), 201

    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f"Database error: {err.msg}"}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f"Server error: {str(e)}"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

@routes.route('/api/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    """Update an existing student record."""
    data = request.get_json(silent=True)
    if data is None:
        data = request.form.to_dict()

    if not isinstance(data, dict):
        return jsonify({'success': False, 'message': 'Invalid payload.'}), 400

    errors, sanitized = validate_student_data(data, is_update=True)
    if errors:
        return jsonify({'success': False, 'errors': errors, 'message': 'Validation failed.'}), 422

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Check student exists
        cursor.execute("SELECT id FROM students WHERE id = %s", (student_id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({'success': False, 'message': f'Student with ID {student_id} not found.'}), 404

        # Check email conflict with other student
        cursor.execute("SELECT id FROM students WHERE email = %s AND id != %s", (sanitized['email'], student_id))
        if cursor.fetchone():
            cursor.close()
            return jsonify({'success': False, 'errors': {'email': 'Email is already in use by another student.'}, 'message': 'Email conflict.'}), 409

        sql = """
            UPDATE students
            SET name = %s, email = %s, phone = %s, department = %s, gender = %s, date_of_birth = %s
            WHERE id = %s
        """
        cursor.execute(sql, (
            sanitized['name'],
            sanitized['email'],
            sanitized['phone'],
            sanitized['department'],
            sanitized['gender'],
            sanitized['date_of_birth'],
            student_id
        ))
        conn.commit()
        cursor.close()

        return jsonify({
            'success': True,
            'message': 'Student updated successfully.',
            'data': {'id': student_id, **sanitized}
        }), 200

    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f"Database error: {err.msg}"}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f"Server error: {str(e)}"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

@routes.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student record."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM students WHERE id = %s", (student_id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({'success': False, 'message': f'Student with ID {student_id} not found.'}), 404

        cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
        conn.commit()
        cursor.close()

        return jsonify({'success': True, 'message': f'Student #{student_id} deleted successfully.'}), 200

    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f"Database error: {err.msg}"}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f"Server error: {str(e)}"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

