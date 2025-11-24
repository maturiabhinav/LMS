from .extensions import db
from datetime import datetime
import enum
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import func

# Set India timezone
import pytz
india_tz = pytz.timezone('Asia/Kolkata')

def india_time():
    return datetime.now(india_tz)

class RoleEnum(enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    CLIENT_ADMIN = "CLIENT_ADMIN"
    STUDENT = "STUDENT"

class Tenant(db.Model):
    __tablename__ = "tenants"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    subdomain = db.Column(db.String(150), unique=True, nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    created_by = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=india_time)
    users = db.relationship("User", back_populates="tenant", lazy="dynamic")
    students = db.relationship("Student", back_populates="tenant", lazy=True)
    courses = db.relationship("Course", back_populates="tenant", lazy=True)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255))
    role = db.Column(db.Enum(RoleEnum), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=True)  # null for super admin
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=india_time)

    tenant = db.relationship("Tenant", back_populates="users")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_role(self):
        return self.role.value

# -------------------- STUDENT TABLE --------------------
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15))
    department = db.Column(db.String(50))
    year_of_study = db.Column(db.String(10))  # e.g., "2nd Year", "3rd Year"
    profile_pic = db.Column(db.String(255))
    registration_date = db.Column(db.DateTime, default=india_time)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)

    # Relationships
    tenant = db.relationship("Tenant", back_populates="students")
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    assignments = db.relationship('Assignment', backref='student', lazy=True)
    quiz_results = db.relationship('QuizResult', backref='student', lazy=True)
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)

# -------------------- INSTRUCTOR TABLE --------------------
class Instructor(db.Model):
    __tablename__ = 'instructors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(50))
    profile_pic = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=india_time)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)

    # Relationships
    tenant = db.relationship("Tenant")
    courses = db.relationship('Course', backref='instructor', lazy=True)
    feedbacks = db.relationship('AssignmentFeedback', backref='instructor', lazy=True)

# -------------------- COURSE TABLE --------------------
class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True)
    description = db.Column(db.Text)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructors.id'), nullable=False)
    duration = db.Column(db.String(50))
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=india_time)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)

    # Relationships
    tenant = db.relationship("Tenant", back_populates="courses")
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)
    quizzes = db.relationship('Quiz', backref='course', lazy=True)
    assignments = db.relationship('Assignment', backref='course', lazy=True)
    attendance_records = db.relationship('Attendance', backref='course', lazy=True)

# -------------------- ENROLLMENT TABLE --------------------
class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enroll_date = db.Column(db.DateTime, default=india_time)
    status = db.Column(db.String(20), default="Active")

# -------------------- ASSIGNMENT TABLE --------------------
class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    title = db.Column(db.String(100))
    file_path = db.Column(db.String(255))  # uploaded file (PDF, DOCX, Excel)
    deadline = db.Column(db.DateTime)
    submitted_at = db.Column(db.DateTime)
    marks_obtained = db.Column(db.Float)
    feedback = db.Column(db.Text)

# -------------------- ATTENDANCE TABLE --------------------
class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    date = db.Column(db.Date, default=lambda: india_time().date())
    status = db.Column(db.String(10))  # Present / Absent

# -------------------- QUIZ (EXAM) TABLE --------------------
class Quiz(db.Model):
    __tablename__ = "quizzes"
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=india_time)

    # Relationships
    questions = db.relationship('QuizQuestion', backref='quiz', lazy=True)
    results = db.relationship('QuizResult', backref='quiz', lazy=True)

# -------------------- QUIZ QUESTIONS --------------------
class QuizQuestion(db.Model):
    __tablename__ = "quiz_questions"
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255))
    option_b = db.Column(db.String(255))
    option_c = db.Column(db.String(255))
    option_d = db.Column(db.String(255))
    correct_option = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=india_time)

# -------------------- QUIZ RESULTS --------------------
class QuizResult(db.Model):
    __tablename__ = "quiz_results"
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    score = db.Column(db.Float)
    date_taken = db.Column(db.DateTime, default=india_time)

# -------------------- ASSIGNMENT FEEDBACK --------------------
class AssignmentFeedback(db.Model):
    __tablename__ = 'assignment_feedback'
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructors.id'), nullable=False)
    comments = db.Column(db.Text)
    marks_given = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=india_time)