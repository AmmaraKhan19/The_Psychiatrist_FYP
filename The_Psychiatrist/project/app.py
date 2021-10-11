import sys, threading
sys.path.append(sys.path[0]+'/project/lib')
import background_tweet_management, database_management, helper
from flask import g, render_template, redirect, url_for, request, Blueprint, session

main = Blueprint("main", __name__)

######################################
## create flask routes/pages #########
######################################

######################################
## create flask user routes/pages ####
######################################

## API - Sign Up ######
@main.route('/signup', methods=['POST', 'GET'])
def signup():
	title = "Create User"
	if request.method == 'POST':
		new_user_fname = request.form['firstname']
		new_user_lname = request.form['lastname']
		new_user_email = request.form['email']
		new_user_uname = request.form['username']
		new_user_pwd = request.form['password']

		firstname=new_user_fname
		lastname=new_user_lname
		email=new_user_email
		username=new_user_uname
		password=new_user_pwd
		try:
			database_management.write_user_to_db(firstname,lastname,email,username,password)
			helper.log('critical','db',"trying save new user")
			return redirect('/cases')
		except:
			helper.log('critical','db',"could not save user")
			return render_template('signup.html', title=title)
	else:
		helper.log('critical','app',"could not create new user")
		return render_template("signup.html", title=title)

## API - authentication
@main.route('/login', methods=['POST'])
def login():
	if "id" in session:
		g.id = session["id"]
	else:
		g.id = None
	if g.id:
		return redirect(url_for("main.cases"))
	else:
		session.pop("id", None)
		username = request.form.get('username')
		password = request.form.get('password')
		creds_are_valid, user_id = database_management.login_query(username=username,password=password)
		if creds_are_valid:
			helper.log('critical','app','credentials correct')
			session["id"] = user_id
			return redirect(url_for("main.cases"))
		else:
			helper.log('critical','app','credentials incorrect')
			return redirect(url_for("main.index"))

## API - Logout
@main.route('/logout', methods=['GET'])
def logout():
	session.pop("id", None)
	return redirect(url_for('main.index'))

## API - Get all cases
@main.route('/get_cases', methods=['GET'])
def get_cases():
	if "id" in session:
		g.id = session["id"]
	else:
		g.id = None
	if g.id:
		case_table = {"cases": list()}
		cases = database_management.read_cases()
		for case in cases:
			case_table["cases"].append({
				"id" : str(case.id),
				"user_id" : str(case.user_id),
				"tweet_id" : str(case.tweet_id),
				"tweet_text" : str(case.tweet_text),
				"status" : str(case.status)
			})
		return case_table
	else:
		helper.log('critical','app','attempt to get cases without authentication')
		return redirect(url_for("main.index"))

## index page ########################
@main.route('/')
def index():
	title = "Home" 
	return render_template("index.html", title=title)

## case page #########################
@main.route('/cases', methods=['GET'])
def cases():
	title = "Cases"
	if "id" in session:
		g.id = session["id"]
	else:
		g.id = None
	title = "Cases"
	if g.id:
		return render_template("cases.html", title=title)
	else:
		title= "Login"
		return render_template("login.html", title=title)

## update status page ################
@main.route('/update_status/<int:id>', methods=['GET', 'POST'])
def update_status(id):
	case_to_update = database_management.case_status(case_id=id)
	if request.method == 'POST':
		case_to_update_new_status = request.form['status']
		case_to_update.status = case_to_update_new_status
		try:
			database_management.write_status_to_db(case_to_update)
			helper.log('critical','db',"trying to update case status")
			return redirect('/cases')
		except:
			helper.log('critical','db',"could not update case status")
			title = "Update Status"
			return render_template("update_status.html", case_to_update_id=id, status_of_case_to_update=case_to_update.status, title=title)
	else: 
		title = "Update Status"
		return render_template("update_status.html", case_to_update_id=id, status_of_case_to_update=case_to_update.status, title=title)

## delete case record ################
@main.route('/delete/<int:id>')
def delete(id):
	if database_management.delete_case(id):
		return redirect('/cases')
	else:
		helper.log('critical','db',"could not delete record")
		return redirect('/cases')

## contact page ######################
@main.route('/contact')
def contact():
	title = "Contact Us"
	return render_template("contact.html", title=title)


######################################
## create flask admin routes/pages ###
###############################           
# #######

## Admin - authentication
@main.route('/admin_login', methods=['POST', 'GET'])
def admin_login():
	if "id" in session:
		g.id = session["id"]
	else:
		g.id = None
	if g.id:
		return redirect(url_for("admin/dashboard"))
	else:
		session.pop("id", None)
		admin_username = request.form.get('user_name')
		admin_password = request.form.get('pass_word')
		creds_are_valid, user_id = database_management.admin_login_query(username=admin_username,password=admin_password)
		if creds_are_valid:
			helper.log('critical','app','credentials correct')
			session["id"] = user_id
			return redirect(url_for("main.dashboard"))
		else:
			helper.log('critical','app','credentials incorrect')
			return redirect(url_for("main.index"))

# ## Admin - Logout
@main.route('/admin_logout', methods=['GET'])
def admin_logout():
	session.pop("id", None)
	return redirect(url_for('main.index'))

## dashboard page ######################
@main.route('/dashboard')
def dashboard():
	total_users = database_management.count_users()
	total_cases = database_management.count_cases()
	total_solved_cases = database_management.count_closed_cases()
	title = "Admin Dashboard"
	if "id" in session:
		g.id = session["id"]
	else:
		g.id = None
		title = "Admin Dashboard"
	if g.id:
		return render_template("admin/dashboard.html", title=title, total_users=total_users, total_cases=total_cases, total_solved_cases=total_solved_cases)
	else:
		title= "Login"
		return render_template("admin/admin_login.html", title=title)

## Admin - Get all users
@main.route('/get_users', methods=['GET'])
def get_users():
	if "id" in session:
		g.id = session["id"]
	else:
		g.id = None
	if g.id:
		user_table = {"users": list()}
		users = database_management.read_users()
		for user in users:
			user_table["users"].append({
				"id" : str(user.id),
				"first_name" : str(user.first_name),
				"last_name" : str(user.last_name),
				"username" : str(user.username),
				"email" : str(user.email),
				"password" : str(user.password),
				"created_at" : str(user.created_at),
				"role" : str(user.role)
			})
		return user_table
	else:
		helper.log('critical','app','attempt to get cases without authentication')
		return redirect(url_for("main.index"))

## Users page ######################
@main.route('/users')
def users():
	title = "Users"
	if "id" in session:
		g.id = session["id"]
	else:
		g.id = None
		title = "Users"
	if g.id:
		return render_template("admin/users.html", title=title)
	else:
		title= "Login"
		return render_template("login.html", title=title)

## Add user ######################
@main.route('/add_user')
def add_user():
	title = "Create User"
	if request.method == 'POST':
		new_user_fname = request.form['firstname']
		new_user_lname = request.form['lastname']
		new_user_email = request.form['email']
		new_user_uname = request.form['username']
		new_user_pwd = request.form['password']

		firstname=new_user_fname
		lastname=new_user_lname
		email=new_user_email
		username=new_user_uname
		password=new_user_pwd
		try:
			database_management.write_user_to_db(firstname,lastname,email,username,password)
			helper.log('critical','db',"trying save new user")
			return redirect('/users')
		except:
			helper.log('critical','db',"could not save user")
			return render_template('admin/add_user.html', title=title)
	else:
		helper.log('critical','app',"could not create new user")
		return render_template("admin/add_user.html", title=title)

## Edit user record ######################
@main.route('/edit_user/<int:id>', methods=['POST','GET'])
#### these above and below ones need to be edited
def edit_user(id):
	user_to_update = database_management.user_update(user_id=id)
	if request.method == 'POST':
		user_to_update.first_name = str(request.form['first_name'])
		user_to_update.last_name = str(request.form['last_name'])
		user_to_update.username = str(request.form['username'])
		user_to_update.email = str(request.form['email'])
		user_to_update.password = str(request.form['password'])
		user_to_update.role = str(request.form['role'])
		try:
			update_state = database_management.update_user_to_db(user_to_update)
			helper.log('critical','db',"trying to update user info")
			if update_state:
				return redirect(url_for('main.users'))
			else:
				title = "Edit User Information"
				return redirect('/edit_user/'+str(id))
		except:
			helper.log('critical','db',"could not update user info")
			title = "Edit User"
			return render_template("admin/edit_user.html", user_to_update_id=id, fname_of_user_to_update=user_to_update.first_name, lname_of_user_to_update=user_to_update.last_name, uname_of_user_to_update=user_to_update.username, email_of_user_to_update=user_to_update.email, pswrd_of_user_to_update=user_to_update.password, role_of_user_to_update=user_to_update.role, title=title)
	else: 
		title = "Edit User Information"
		return render_template("admin/edit_user.html", user_to_update_id=id, fname_of_user_to_update=user_to_update.first_name, lname_of_user_to_update=user_to_update.last_name, uname_of_user_to_update=user_to_update.username, email_of_user_to_update=user_to_update.email, pswrd_of_user_to_update=user_to_update.password, role_of_user_to_update=user_to_update.role, title=title)

## delete user record ################
@main.route('/delete_user/<int:id>')
def delete_user(id):
	if database_management.delete_user(id):
		return redirect(url_for("main.users"))
	else:
		helper.log('critical','db',"could not delete user record")
		return redirect(url_for("main.users"))


######################################
## create custom error pages #########
######################################

## invalid url ########################
@main.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404
                                    
#server error
@main.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500

## Threading ###############

# prediction_thread = background_tweet_management.prediction()
# prediction_thread.start()
# helper.log("critical","app","prediction thread started in the background")