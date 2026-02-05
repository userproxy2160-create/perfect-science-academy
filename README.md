# Academy Management System

A complete Flask-based web application for managing academy students, teachers, fees, and salaries with a modern, professional UI and smooth animations.

## Features

### Student Management
- Add, edit, and delete students
- Assign students to classes (5th Grade → 12th Grade/2nd Year)
- Set individual monthly fees per student
- Record fee payments (full or partial)
- Multiple payment methods: Cash, Easypaisa, JazzCash
- Automatic calculation of paid/pending months and amounts
- Filter students by class
- Generate and download professional PDF receipts
- Export student lists for printing

### Teacher Management
- Add, edit, and delete teachers
- Set monthly salary for each teacher
- Record salary payments per month
- Automatic calculation of paid/pending salaries
- View complete salary payment history

### Reports
- Class-wise fee summary (collected and pending)
- Teacher salary summary
- Printable reports
- Real-time statistics on dashboard

### UI Features
- Modern, clean interface with professional design
- Smooth page transitions and animations
- Card entrance animations
- Button hover effects
- Animated modals
- Pending payment indicators with pulse animation
- Subtle sound effects (toggle on/off)
- Responsive design for mobile and desktop

## File Structure

```
academy_management/
├── app.py
├── requirements.txt
├── academy.db (created automatically)
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── students.html
│   ├── teachers.html
│   └── reports.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        ├── sounds.js
        └── main.js
```

## Setup Instructions

### Local Setup

1. Create the project directory:
```bash
mkdir academy_management
cd academy_management
```

2. Create the folder structure:
```bash
mkdir templates static static/css static/js
```

3. Copy all files to their respective locations

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the application:
```bash
python app.py
```

6. Open your browser and navigate to:
```
http://localhost:5000
```

### Replit Setup

1. Create a new Python Repl
2. Upload all files maintaining the folder structure
3. Click "Run" button
4. The app will automatically install dependencies and start

## Default Login Credentials

- **Username:** admin
- **Password:** admin123

## Usage Guide

### Adding Students
1. Go to "Students" page
2. Click "+ Add Student" button
3. Fill in student name, class, and monthly fee
4. Click "Add Student"

### Recording Fee Payments
1. Find the student in the list
2. Click the 💰 icon
3. Enter payment amount, method, and month
4. Click "Record Payment"

### Generating Receipts
1. Find the student in the list
2. Click the 📄 icon
3. Receipt PDF will open in new tab for viewing/downloading

### Managing Teachers
1. Go to "Teachers" page
2. Add teachers with their monthly salary
3. Record salary payments using the 💰 icon

### Viewing Reports
1. Go to "Reports" page
2. View class-wise fee summary
3. Click "Print Report" to print or save as PDF

## Sound Effects

The app includes subtle sound effects:
- Click sound for buttons
- Success sound for completed actions
- Error sound for invalid inputs

Toggle sounds on/off using the 🔊/🔇 button in the navbar.

## Technical Details

- **Backend:** Python Flask
- **Database:** SQLite
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **PDF Generation:** ReportLab
- **Animations:** Pure CSS animations
- **Sound:** Web Audio API

## Key Features Explained

### Automatic Calculations
- System calculates total months enrolled from date added
- Automatically computes paid months based on payments
- Calculates pending months and amounts
- Updates in real-time

### Payment Tracking
- Records each payment with date and method
- Supports partial payments
- Maintains complete payment history
- Generates professional receipts

### Professional UI
- Modern card-based layout
- Smooth animations and transitions
- Responsive tables
- Color-coded pending indicators
- Clean, minimal design

## Browser Compatibility

Works on all modern browsers:
- Chrome/Edge
- Firefox
- Safari
- Opera

## Notes

- The database is created automatically on first run
- All data is stored locally in SQLite
- Receipts are generated on-the-fly
- Sound effects require user interaction to initialize (browser security)
- Print functionality works with browser's print dialog

## License

Open source - feel free to use and modify for your academy!
