from flask import Flask, render_template, request, flash, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from base64 import b64encode
import base64
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Nerd.db'
app.config['SECRET_KEY'] = ''
db = SQLAlchemy(app)

date = datetime.now()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user_login'

@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))

#------------------------------------
class Home(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	date_posted = db.Column(db.DateTime, default = date)
	title = db.Column(db.String(50))
	body = db.Column(db.String(1000))
	media = db.Column(db.LargeBinary)
	
	def __repr__(self):
		return '<Title %r>' % self.id

class Friend(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	date_posted = db.Column(db.DateTime, default = date)
	name = db.Column(db.String(50))
	surname = db.Column(db.String(50))
	gender = db.Column(db.String(10))
	work = db.Column(db.String(50))
	email = db.Column(db.String(50))
	comment = db.Column(db.String(500))
	photo = db.Column(db.LargeBinary)
	
	def __repr__(self):
		return '<Name %r>' % self.id
		
class Project(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	date_posted = db.Column(db.DateTime, default = date)
	title = db.Column(db.String(50))
	body = db.Column(db.String(1000))
	code = db.Column(db.String(1000))
	media = db.Column(db.LargeBinary)
	
	def __repr__(self):
		return '<Title %r>' % self.id

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key = True)
	date_posted = db.Column(db.DateTime, default = date)
	name = db.Column(db.String(50))
	surname = db.Column(db.String(50))
	email = db.Column(db.String(50))
	password = db.Column(db.String(100))
	photo = db.Column(db.LargeBinary)
	
	@property
	def passwords(self):
		raise AttributeError('Password is not readable...')
		
	@passwords.setter
	def passwords(self, passwords):
		self.password = generate_password_hash(passwords)
		
	def verify_password(self, passwords):
		return check_password_hash(self.password, passwords)
	
	def __repr__(self):
		return '<Name %r>' % self.id
#------------------------------------

@app.route('/')
def home():
	posted = Home.query.all()
	images = []
	for post in posted:
		posts = base64.b64encode(post.media).decode('ascii')
		images.append(posts)
	return render_template('home.html',posted = zip(posted,images))
	
@app.route('/home-add', methods = ['POST', 'GET'])
def add_home():
	if request.method == 'GET':
		return render_template('home add.html')
	else:
		title = request.form['title']
		body = request.form['body']
		media = request.files['media']
		post = Home(title=title,body=body,media=media.read())
		try:
			db.session.add(post)
			db.session.commit()
			flash('Post added successfully!')
			return redirect('/')
		except:
			flash('There was an error, try again...')
			return render_template('home add.html',title=title, body=body)
			
@app.route('/home-delete')
def del_home():
	ids = request.args['type']
	post = Home.query.filter_by(id=ids).first()
	db.session.delete(post)
	db.session.commit()
	flash('Post successfully deleted')
	return redirect('/')
	
@app.route('/home-edit', methods = ['POST', 'GET'])
def edit_home():
	if request.method == 'POST':
		ids = request.form['num']
		posts = Home.query.get(ids)
		posts.title = request.form['title']
		posts.body = request.form['body']
		media = request.files['media']
		posts.media = media.read()
		db.session.commit()
		flash('Post successfully updated...')
		return redirect('/')	
	else:
		ids = request.args['type']
		posts = Home.query.get(ids)
		return render_template('home edit.html', title=posts.title, body=posts.body, num=ids)
#------------------------------------

@app.route('/friends')
def friends():
	posted = Friend.query.order_by(Friend.date_posted)
	images = []
	for post in posted:
		posts = base64.b64encode(post.photo).decode('ascii')
		images.append(posts)
	return render_template('friends.html',post = zip(posted,images))

@app.route('/friend-add', methods = ['POST', 'GET'])
def add_friend():
	if request.method == 'GET':
		return render_template('friend add.html')
	else:
		name = request.form['name']
		surname = request.form['surname']
		gender = request.form['gender']
		work = request.form['work']
		email = request.form['email']
		comment = request.form['comment']
		photo = request.files['photo']
		if not name or not surname or not gender or not work or not email or not comment or not photo :
			flash('All forms are required to be filled...')
			return render_template('add friend.html',name=name, surname=surname, gender=gender, work=work, email=email, comment=comment)
		else:
			friend = Friend(name=name, surname=surname, gender=gender, work=work, email=email, comment=comment, photo=photo.read())
			try:
				db.session.add(friend)
				db.session.commit()
				flash('Friend successfully added')
				return redirect('/friends')
			except:
				flash('There was an error, try again...')
				return render_template('friend add.html',name=name, surname=surname, gender=gender, work=work, email=email, comment=comment)

@app.route('/friend-details')
def friend_details():
	names = request.args['type']
	friends = Friend.query.filter_by(id=names).first()
	photo = base64.b64encode(friends.photo).decode('ascii')
	return render_template('friend details.html', photo=photo,friends=friends)

@app.route('/friend-delete')
def del_friend():
	ids = request.args['type']
	post = Friend.query.filter_by(id=ids).first()
	db.session.delete(post)
	db.session.commit()
	flash('Friend successfully removed')
	return redirect('/friends')
	
@app.route('/friend-edit', methods = ['POST', 'GET'])
def edit_friend():
	if request.method == 'POST':
		ids = request.form['num']
		post = Friend.query.get(ids)
		post.name = request.form['name']
		post.surname = request.form['surname']
		post.gender = request.form['gender']
		post.work = request.form['work']
		post.email = request.form['email']
		post.comment = request.form['comment']
		image = request.files['photo']
		post.photo = image.read()
		db.session.commit()
		flash('Friend details successfully updated...')
		return redirect('/friends')
	else:
		ids = request.args['type']
		posts = Friend.query.get(ids)
		return render_template('friend edit.html', name=posts.name, surname=posts.surname, gender=posts.gender, work=posts.work, email=posts.email, comment=posts.comment, photo=posts.photo, num=ids)
#------------------------------------

@app.route('/projects')
def project():
	posted = Project.query.order_by(Project.date_posted)
	return render_template('project.html',posted = posted)

@app.route('/project-add', methods = ['POST', 'GET'])
def add_project():
	if request.method == 'GET':
		return render_template('project add.html')
	else:
		title = request.form['title']
		body = request.form['body']
		code = request.form['code']
		media = request.files['media']
		post = Project(title=title,body=body, code=code,media=media.read())
		try:
			db.session.add(post)
			db.session.commit()
			flash('Post added successfully!')
			return redirect('/projects')
		except:
			flash('There was an error, try again...')
			return render_template('project add.html',title=title, body=body, code=code)
			
@app.route('/project-details')
def project_details():
	names = request.args['type']
	project = Project.query.filter_by(id=names).first()
	media = base64.b64encode(project.media).decode('ascii')
	return render_template('project details.html', media=media,project=project)
			
@app.route('/project-delete')
def del_project():
	ids = request.args['type']
	post = Project.query.filter_by(id=ids).first()
	db.session.delete(post)
	db.session.commit()
	flash('Post successfully deleted')
	return redirect('/projects')
	
@app.route('/project-edit', methods = ['POST', 'GET'])
def edit_project():
	if request.method == 'GET':
		ids = request.args['type']
		posts = Project.query.get(ids)
		return render_template('project edit.html', num=ids, title=posts.title,body=posts.body, code=posts.code,media=posts.media)
	else:
		ids = request.form['num']
		post = Project.query.get(ids)
		post.title = request.form['title']
		post.body = request.form['body']
		post.code = request.form['code']
		photo = request.files['media']
		post.media = photo.read()
		db.session.commit()
		flash('Project successfully updated')
		return redirect('/projects')				
#------------------------------------

@app.route('/user')
@login_required
def user():
	posted = User.query.order_by(User.date_posted)
	photo = base64.b64encode(current_user.photo).decode('ascii')
	return render_template('user.html', photo=photo, posted=posted)
	
@app.route('/user-add', methods = ['POST', 'GET'])
def add_user():
	if request.method == 'GET':
		return render_template('user add.html')
	else:
		name = request.form['name']
		surname = request.form['surname']
		email = request.form['email']
		pw = request.form['password']
		confirm_pw = request.form['confirm password']
		photo = request.files['photo']
		
		if pw == confirm_pw:
			post = User(name=name, surname=surname, email=email, password=generate_password_hash(pw), photo=photo.read())
			try:
				db.session.add(post)
				db.session.commit()
				flash('Post added successfully!')
				return redirect('/user')
			except:
				flash('There was an error, try again...')
				return render_template('user add.html',name=name, surname=surname, email=email, password=password, photo=photo)
		else:
			flash('Passwords do not match...')
			return render_template('user add.html',name=name, surname=surname, email=email, password=pw, photo=photo)
			
@app.route('/user-del')
def del_user():
	ids = request.args['type']
	post = User.query.filter_by(id=ids).first()
	db.session.delete(post)
	db.session.commit()
	flash(f'{post.name} successfully removed as admin...')
	return redirect('/user')
#-----------------------------------

@app.route('/user-login', methods = ['POST', 'GET'])
def user_login():
	if request.method == 'GET':
		return render_template('user login.html')
	else:
		email = request.form['email']
		password = request.form['password']
		profile = User.query.filter_by(email=email).first()
		if profile:
			passed = check_password_hash(profile.password, password)
			if passed == True:
				login_user(profile)
				flash('You are logged in...')
				return redirect('/user')
			else:
				flash('Password is incorrect...')
				return render_template('user login.html', email=email)
		else:
			flash('User does not exist...')
			return render_template('user login.html')
			
@app.route('/user-logout', methods = ['GET'])
@login_required
def user_logout():
	logout_user()
	flash('You have been logged out...')
	return redirect('user-login')
#------------------------------------

boxed = []
course_unit = []
grade_point = []

@app.route('/cgpa-cal', methods = ['POST', 'GET'])
def box_num():
	if request.method == 'GET':
		return render_template('cal num.html')
	else:
		box = request.form['box']
		boxed.append(box)
		return redirect('/cgpa-cal-entry')

@app.route('/cgpa-cal-entry', methods = ['POST', 'GET'])
def cal_entry():
	if request.method == 'GET':
		for boxes in boxed:
			return render_template('cal entry.html', boxes=int(boxes))
	else:
		CU = request.form.items(multi=True)
		course_unit.append(CU)
		GP = request.form.items(multi=True)
		grade_point.append(GP)
		return redirect('/cgpa-cal-result')
		
@app.route('/cgpa-cal-result')
def cal_result():
	for x, y in zip(grade_point, course_unit):
		cals = sum([int(x) * int(y)]) / sum([int(y)])
		return render_template('cal result.html', result = cals)
		
@app.route('/clear-list', methods = ['GET'])
def clear_list():
	boxed.clear()
	course_unit.clear()
	grade_point.clear()
	return redirect('/cgpa-cal')
#------------------------------------