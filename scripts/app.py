from flask import Flask, render_template_string, request, redirect, url_for
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date

app = Flask(__name__)

# Database setup
engine = create_engine('sqlite:///users.db', echo=True)
Base = declarative_base()

# User Model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(50))
    role = Column(String(20))
    date_of_birth = Column(Date)
    
    def calculate_age(self):
        if self.date_of_birth:
            today = date.today()
            age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            return age
        return None

# Create tables
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>User Management</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h1 class="mb-4">User Management System</h1>
        
        <div class="card mb-4">
            <div class="card-header">
                <h2 class="h5 mb-0">Add New User</h2>
            </div>
            <div class="card-body">
                <form method="POST" action="{{ url_for('add_user') }}" class="form-inline">
                    <input type="text" name="name" placeholder="Name" class="form-control mr-2 mb-2" required>
                    <input type="email" name="email" placeholder="Email" class="form-control mr-2 mb-2" required>
                    <input type="text" name="role" placeholder="Role" class="form-control mr-2 mb-2" required>
                    <input type="date" name="date_of_birth" class="form-control mr-2 mb-2" required>
                    <button type="submit" class="btn btn-primary mb-2">Add User</button>
                </form>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h2 class="h5 mb-0">Users List</h2>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped table-bordered">
                        <thead class="thead-dark">
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Role</th>
                                <th>Date of Birth</th>
                                <th>Age</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for user in users %}
                            <tr>
                                <td>{{ user.id }}</td>
                                <td>{{ user.name }}</td>
                                <td>{{ user.email }}</td>
                                <td><span class="badge badge-info">{{ user.role }}</span></td>
                                <td>{{ user.date_of_birth.strftime('%Y-%m-%d') if user.date_of_birth else 'Not provided' }}</td>
                                <td>{{ user.calculate_age() if user.calculate_age() is not none else 'N/A' }}</td>
                                <td>
                                    <a href="{{ url_for('edit_user', id=user.id) }}" class="btn btn-sm btn-primary">
                                        <i class="fas fa-edit"></i> Edit
                                    </a>
                                    <a href="{{ url_for('delete_user', id=user.id) }}" class="btn btn-sm btn-danger" 
                                       onclick="return confirm('Are you sure you want to delete this user?')">
                                        <i class="fas fa-trash"></i> Delete
                                    </a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.min.js"></script>
</body>
</html>
'''

EDIT_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Edit User</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <div class="card">
            <div class="card-header">
                <h1 class="h4 mb-0">Edit User</h1>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="form-group">
                        <label>Name</label>
                        <input type="text" name="name" value="{{ user.name }}" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" name="email" value="{{ user.email }}" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label>Role</label>
                        <input type="text" name="role" value="{{ user.role }}" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label>Date of Birth</label>
                        <input type="date" name="date_of_birth" value="{{ user.date_of_birth.strftime('%Y-%m-%d') if user.date_of_birth else '' }}" class="form-control" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Update</button>
                    <a href="{{ url_for('index') }}" class="btn btn-secondary">Back to Users List</a>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
'''

# Routes
@app.route('/')
def index():
    session = Session()
    users = session.query(User).all()
    session.close()
    return render_template_string(HTML_TEMPLATE, users=users)

@app.route('/add_user', methods=['POST'])
def add_user():
    session = Session()
    date_of_birth = None
    if request.form['date_of_birth']:
        date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()

    new_user = User(
        name=request.form['name'],
        email=request.form['email'],
        role=request.form['role'],
        date_of_birth=date_of_birth
    )
    session.add(new_user)
    session.commit()
    session.close()
    return redirect(url_for('index'))

@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    session = Session()
    user = session.query(User).get(id)
    
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.role = request.form['role']
        
        date_of_birth = None
        if request.form['date_of_birth']:
            date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
        user.date_of_birth = date_of_birth
        
        session.commit()
        session.close()
        return redirect(url_for('index'))
    
    return render_template_string(EDIT_TEMPLATE, user=user)

@app.route('/delete_user/<int:id>')
def delete_user(id):
    session = Session()
    user = session.query(User).get(id)
    session.delete(user)
    session.commit()
    session.close()
    return redirect(url_for('index'))

# Add sample data if database is empty
def add_sample_data():
    session = Session()
    if session.query(User).count() == 0:
        sample_users = [
            User(name='John Doe', email='john@example.com', role='Admin', 
                 date_of_birth=datetime.strptime('1985-05-15', '%Y-%m-%d').date()),
            User(name='Jane Smith', email='jane@example.com', role='User', 
                 date_of_birth=datetime.strptime('1990-10-20', '%Y-%m-%d').date()),
            User(name='Bob Wilson', email='bob@example.com', role='Manager', 
                 date_of_birth=datetime.strptime('1982-03-30', '%Y-%m-%d').date())
        ]
        session.add_all(sample_users)
        session.commit()
    session.close()

if __name__ == '__main__':
    add_sample_data()
    app.run(debug=True)
