from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User,Feedback
from forms import RegisterForm,LoginForm,FeedbackForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    return render_template("base.html")

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """
    Show a form that when submitted will register/create a user. 
    This form should accept a username, password, email, first_name, and last_name.
    Make sure you are using WTForms and that your password input hides the characters that the user is typing!
    """
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email=form.email.data
        first_name=form.first_name.data
        last_name=form.last_name.data
        new_user = User.register(username, password,email,first_name,last_name)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken.  Please pick another')
            form.email.errors.append("This email has been registered")
            return render_template('register.html', form=form)
        session['user_username'] = new_user.username
        flash('Welcome! Successfully Created Your Account!', "success")
        return redirect(f"/users/{new_user.username}")

    return render_template('register.html', form=form)





@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", "primary")
            session['user_username'] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)



@app.route('/logout')
def logout_user():
    session.pop('user_username')
    flash("Goodbye!", "info")
    return redirect('/')



@app.route("/users/<username>")
def show_user_info(username):
    if 'user_username' not in session or username != session['user_username']:
        flash("Please login first!", "danger")
        return redirect('/login')
    user = User.query.get(username)
    feedbacks=Feedback.query.filter(username==user.username)
    return render_template("user_info.html", user=user, feedbacks=feedbacks)
    


@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """
    /users/<username>/delete
    Remove the user from the database
    make sure to also delete all of their feedback. 
    Clear any user information in the session
    and redirect to "/"
    Make sure that only the user who is logged in can successfully delete their account
    """
    if 'user_username' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    user=User.query.get_or_404(username)
    if user.username==session["user_username"]:
        db.session.delete(user)
        db.session.commit()
        flash("Account deleted!", "info")
        redirect("/")
    flash("You don't have permission to do that!", "danger")
    return redirect("/register")


@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    """
    Make sure that only the user who is logged in can successfully add feedback
    for get: Display a form to add feedback
    Make sure that only the user who is logged in can see this form
    for post:Add a new piece of feedback and redirect to /users/<username> 
    """
    if "user_username" not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    form = FeedbackForm()
    if form.validate_on_submit():
        title=form.title.data
        content=form.content.data
        username=session["user_username"]
        new_feedback=Feedback(title=title,content=content,username=username)
        db.session.add(new_feedback)
        db.session.commit()
        flash("feedback added", "success")
        return redirect(f"/users/{username}")
    return render_template("add_feedback_form.html", form=form)

@app.route("/feedback/<int:feedback_id>/update",methods=['GET', 'POST'])
def update_feedback(feedback_id):
    """
    for get:Display a form to edit feedback
    Make sure that only the user who has written that feedback can see this form
    for post: Update a specific piece of feedback and redirect to /users/<username>
    Make sure that only the user who has written that feedback can update it**
    """
    if "user_username" not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    feedback=Feedback.query.get_or_404(feedback_id)
    username=feedback.username
    if feedback.username==session["user_username"]:
        form=FeedbackForm(obj=feedback)
        if form.validate_on_submit():
            feedback.title=form.title.data
            feedback.content=form.content.data
            db.session.commit()
            flash("Your feedback has been updated!", "success")
            return redirect(f"/users/{username}")
        else:
            return render_template("edit_feedback.html", form=form, feedback=feedback)

    flash("You don't have permission to do that!", "danger")

@app.route("/feedback/<feedback_id>/delete",methods=["POST"])
def delete_feedback(feedback_id):
    """
    Delete a specific piece of feedback and redirect to /users/<username>
    Make sure that only the user who has written that feedback can delete it
    """
    if "user_username" not in session:
        flash ("Please login first", "danger")
        return redirect("/login")
    feedback=Feedback.query.get_or_404(feedback_id)
    if feedback.username==session["user_username"]:
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedback deleted!", "info")
        return redirect(f"/users/{feedback.username}")
    flash("You don't have permission to do that")
    return redirect(f"/users/{feedback.username}")
