from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from functools import wraps
import sqlite3
import os
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

app = Flask(__name__)
app.secret_key = 'academy_secret_key_2024'

# Admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

# Database setup
def init_db():
    conn = sqlite3.connect('academy.db')
    c = conn.cursor()
    
    # Students table
    c.execute('''CREATE TABLE IF NOT EXISTS students
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  class TEXT NOT NULL,
                  monthly_fee REAL NOT NULL,
                  date_added TEXT NOT NULL)''')
    
    # Student payments table
    c.execute('''CREATE TABLE IF NOT EXISTS student_payments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  student_id INTEGER,
                  amount REAL NOT NULL,
                  payment_method TEXT NOT NULL,
                  payment_date TEXT NOT NULL,
                  month_year TEXT NOT NULL,
                  FOREIGN KEY (student_id) REFERENCES students(id))''')
    
    # Teachers table
    c.execute('''CREATE TABLE IF NOT EXISTS teachers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  monthly_salary REAL NOT NULL,
                  date_added TEXT NOT NULL)''')
    
    # Teacher salary payments table
    c.execute('''CREATE TABLE IF NOT EXISTS teacher_payments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  teacher_id INTEGER,
                  amount REAL NOT NULL,
                  payment_date TEXT NOT NULL,
                  month_year TEXT NOT NULL,
                  FOREIGN KEY (teacher_id) REFERENCES teachers(id))''')
    
    conn.commit()
    conn.close()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Invalid credentials'})
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect('academy.db')
    c = conn.cursor()
    
    # Get statistics
    c.execute('SELECT COUNT(*) FROM students')
    total_students = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM teachers')
    total_teachers = c.fetchone()[0]
    
    c.execute('SELECT SUM(amount) FROM student_payments')
    total_collected = c.fetchone()[0] or 0
    
    c.execute('SELECT SUM(amount) FROM teacher_payments')
    total_salaries_paid = c.fetchone()[0] or 0
    conn.close()
    return render_template('dashboard.html', 
                         total_students=total_students,
                         total_teachers=total_teachers,
                         total_collected=total_collected,
                         total_salaries_paid=total_salaries_paid)

@app.route('/students')
@login_required
def students():
    conn = sqlite3.connect('academy.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    class_filter = request.args.get('class', '')
    
    if class_filter:
        c.execute('SELECT * FROM students WHERE class = ? ORDER BY name', (class_filter,))
    else:
        c.execute('SELECT * FROM students ORDER BY name')
    
    students = c.fetchall()
    
    # Calculate payment info for each student
    students_data = []
    for student in students:
        c.execute('SELECT SUM(amount) FROM student_payments WHERE student_id = ?', (student['id'],))
        total_paid = c.fetchone()[0] or 0
        
        # Calculate months since enrollment
        date_added = datetime.strptime(student['date_added'], '%Y-%m-%d')
        months_enrolled = ((datetime.now().year - date_added.year) * 12 + 
                          datetime.now().month - date_added.month) + 1
        
        total_due = student['monthly_fee'] * months_enrolled
        pending_amount = total_due - total_paid
        paid_months = int(total_paid / student['monthly_fee']) if student['monthly_fee'] > 0 else 0
        pending_months = months_enrolled - paid_months
        
        students_data.append({
            'id': student['id'],
            'name': student['name'],
            'class': student['class'],
            'monthly_fee': student['monthly_fee'],
            'total_paid': total_paid,
            'pending_amount': pending_amount,
            'paid_months': paid_months,
            'pending_months': pending_months
        })
    
    conn.close()
    
    classes = ['5th Grade', '6th Grade', '7th Grade', '8th Grade', '9th Grade', 
               '10th Grade', '11th Grade (1st Year)', '12th Grade (2nd Year)']
    
    return render_template('students.html', students=students_data, 
                         classes=classes, selected_class=class_filter)

@app.route('/students/add', methods=['POST'])
@login_required
def add_student():
    name = request.form.get('name')
    class_name = request.form.get('class')
    monthly_fee = float(request.form.get('monthly_fee'))
    
    conn = sqlite3.connect('academy.db')
    c = conn.cursor()
    c.execute('INSERT INTO students (name, class, monthly_fee, date_added) VALUES (?, ?, ?, ?)',
              (name, class_name, monthly_fee, datetime.now().strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/students/edit/<int:id>', methods=['POST'])
@login_required
def edit_student(id):
    name = request.form.get('name')
    class_name = request.form.get('class')
    monthly_fee = float(request.form.get('monthly_fee'))
    
    conn = sqlite3.connect('academy.db')
    c = conn.cursor()
    c.execute('UPDATE students SET name = ?, class = ?, monthly_fee = ? WHERE id = ?',
              (name, class_name, monthly_fee, id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/students/delete/<int:id>', methods=['POST'])
@login_required
def delete_student(id):
    conn = sqlite3.connect('academy.db')
    c = conn.cursor()
    c.execute('DELETE FROM student_payments WHERE student_id = ?', (id,))
    c.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/students/<int:id>/payment', methods=['POST'])
@login_required
def add_student_payment(id):
    amount = float(request.form.get('amount'))
    payment_method = request.form.get('payment_method')
    month_year = request.form.get('month_year')
    
    conn = sqlite3.connect('academy.db')
    c = conn.cursor()
    c.execute('INSERT INTO student_payments (student_id, amount, payment_method, payment_date, month_year) VALUES (?, ?, ?, ?, ?)',
              (id, amount, payment_method, datetime.now().strftime('%Y-%m-%d'), month_year))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/students/<int:id>/receipt')
@login_required
def student_receipt(id):
    conn = sqlite3.connect('academy.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('SELECT * FROM students WHERE id = ?', (id,))
    student = c.fetchone()
    
    c.execute('SELECT * FROM student_payments WHERE student_id = ? ORDER BY payment_date DESC', (id,))
    payments = c.fetchall()
    
    c.execute('SELECT SUM(amount) FROM student_payments WHERE student_id = ?', (id,))
    total_paid = c.fetchone()[0] or 0
    
    conn.close()
    
    # Create PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header
    p.setFont("Helvetica-Bold", 24)
    p.drawString(1*inch, height - 1*inch, "Academy Management System")
    
    p.setFont("Helvetica-Bold", 18)
    p.drawString(1*inch, height - 1.5*inch, "Student Fee Receipt")
    
    # Student info
    p.setFont("Helvetica-Bold", 12)
    y = height - 2.2*inch
    p.drawString(1*inch, y, f"Student Name: {student['name']}")
    y -= 0.3*inch
    p.drawString(1*inch, y, f"Class: {student['class']}")
    y -= 0.3*inch
    p.drawString(1*inch, y, f"Monthly Fee: Rs. {student['monthly_fee']:.2f}")
    y -= 0.3*inch
    p.drawString(1*inch, y, f"Total Paid: Rs. {total_paid:.2f}")
    
    # Payment history
    y -= 0.6*inch
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1*inch, y, "Payment History:")
    
    y -= 0.4*inch
    p.setFont("Helvetica", 10)
    for payment in payments:
        p.drawString(1*inch, y, f"{payment['payment_date']} - Rs. {payment['amount']:.2f} - {payment['payment_method']} - {payment['month_year']}")
        y -= 0.25*inch
        if y < 1*inch:
            break
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'receipt_{student["name"]}.pdf', mimetype='application/pdf')

@app.route('/teachers')
@login_required
def teachers():
    conn = sqlite3.connect('academy.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('SELECT * FROM teachers ORDER BY name')
    teachers = c.fetchall()
    
    teachers_data = []
    for teacher in teachers:
        c.execute('SELECT SUM(amount) FROM teacher_payments WHERE teacher_id = ?', (teacher['id'],))
        total_paid = c.fetchone()[0] or 0
        
        date_added = datetime.strptime(teacher['date_added'], '%Y-%m-%d')
        months_employed = ((datetime.now().year - date_added.year) * 12 + 
                          datetime.now().month - date_added.month) + 1
        
        total_due = teacher['monthly_salary'] * months_employed
        pending_amount = total_due - total_paid
        paid_months = int(total_paid / teacher['monthly_salary']) if teacher['monthly_salary'] > 0 else 0
        pending_months = months_employed - paid_months
        
        teachers_data.append({
            'id': teacher['id'],
            'name': teacher['name'],
            'monthly_salary': teacher['monthly_salary'],
            'total_paid': total_paid,
            'pending_amount': pending_amount,
            'paid_months': paid_months,
            'pending_months': pending_months
        })
    
    conn.close()
    
    return render_template('teachers.html', teachers=teachers_data)

@app.route('/teachers/add', methods=['POST'])
@login_required
def add_teacher():
    name = request.form.get('name')
    monthly_salary = float(request.form.get('monthly_salary'))
    
    conn = sqlite3.connect('academy.db')
    c = conn.cursor()
    c.execute('INSERT INTO teachers (name, monthly_salary, date_added) VALUES (?, ?, ?)',
              (name, monthly_salary, datetime.now().strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/teachers/edit/<int:id>', methods=['POST'])
@login_required
def edit_teacher(id):
    name = request.form.get('name')
    monthly_salary = float(request.form.get('monthly_salary'))
    
    conn = sqlite3.connect('academy.db')
    c = conn.cursor()
    c.execute('UPDATE teachers SET name = ?, monthly_salary = ? WHERE id = ?',
              (name, monthly_salary, id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/teachers/delete/<int:id>', methods=['POST'])
@login_required
def delete_teacher(id):
    conn = sqlite3.connect('academy.db')
    c = conn.cursor()
    c.execute('DELETE FROM teacher_payments WHERE teacher_id = ?', (id,))
    c.execute('DELETE FROM teachers WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/teachers/<int:id>/payment', methods=['POST'])
@login_required
def add_teacher_payment(id):
    amount = float(request.form.get('amount'))
    month_year = request.form.get('month_year')
    
    conn = sqlite3.connect('academy.db')
    c = conn.cursor()
    c.execute('INSERT INTO teacher_payments (teacher_id, amount, payment_date, month_year) VALUES (?, ?, ?, ?)',
              (id, amount, datetime.now().strftime('%Y-%m-%d'), month_year))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/reports')
@login_required
def reports():
    conn = sqlite3.connect('academy.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Class-level summary
    classes = ['5th Grade', '6th Grade', '7th Grade', '8th Grade', '9th Grade', 
               '10th Grade', '11th Grade (1st Year)', '12th Grade (2nd Year)']
    
    class_summary = []
    for class_name in classes:
        c.execute('SELECT * FROM students WHERE class = ?', (class_name,))
        students = c.fetchall()
        
        total_collected = 0
        total_pending = 0
        
        for student in students:
            c.execute('SELECT SUM(amount) FROM student_payments WHERE student_id = ?', (student['id'],))
            paid = c.fetchone()[0] or 0
            total_collected += paid
            
            date_added = datetime.strptime(student['date_added'], '%Y-%m-%d')
            months_enrolled = ((datetime.now().year - date_added.year) * 12 + 
                              datetime.now().month - date_added.month) + 1
            total_due = student['monthly_fee'] * months_enrolled
            total_pending += (total_due - paid)
        
        if len(students) > 0:
            class_summary.append({
                'class': class_name,
                'students': len(students),
                'collected': total_collected,
                'pending': total_pending
            })
    
    conn.close()
    
    return render_template('reports.html', class_summary=class_summary)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)