from pdb import set_trace
from flask import Flask, render_template, redirect, session, flash, request
from flask_debugtoolbar import DebugToolbarExtension
from models import Feedback, connect_db, db, User
from forms import LoginForm, RegisterForm, FeedbackForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///user_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "EvieCutie"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

@app.before_request
def check_logged_in():
    """Check if the user is logged in"""
    if "username" not in session and request.endpoint not in ("main_page", "register", "log_in", "logout_user"):
        flash("Please login first!", "danger")
        return redirect("/")

@app.route("/")
def main_page():
    """Direct user to the register form"""
    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Show register form and create a new user"""
    form = RegisterForm()
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k not in ["csrf_token", "username", "password", "page_not_found"]}
        username = form.username.data
        password = form.password.data
        username_password= User.register(username, password)
        new_user = User(username=username_password.username, password=username_password.password, **data)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append("Username taken.  Please pick another")
            return redirect("/register")
        session["username"] = new_user.username
        flash("Welcome! Successfully Created Your Account!", "success")
        return redirect(f"/users/{new_user.username}")
    else:
        return render_template("register_form.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def log_in():
    """Show log in form and validate the username and password"""
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", "info")
            session['username'] = user.username
            return redirect(f"/users/{user.username}")
        else:
            return redirect("/register")
    else:
        return render_template("login_form.html", form=form)

@app.route("/logout")
def logout_user():
    """Log user out"""
    session.pop("username")
    flash("Goodbye!", "info")
    return redirect("/")

#######users routes########

@app.route("/users/<username>")
def show_user_page(username):
    """Show the user's info and prevent user from seeing another 
    user's info by typing the username in the URL manually"""

    current_user = session["username"]
    user = User.query.filter_by(username=current_user).first_or_404()
    feedbacks = Feedback.query.filter_by(username=current_user).all()

    if username != session["username"]: ##try to refactor the code but the result is wrong
        flash("Sorry, that's not your profile", "danger")
        return redirect(f"/users/{current_user}")
    
    return render_template("user_details.html", user=user, feedbacks=feedbacks)

@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    """Delete user and prevent the user from delete another user"""
    current_user = session["username"]

    if username != current_user: ##try to refactor the code but the result is wrong
        flash("Sorry, you can't delete another user", "danger")
        return redirect(f"/users/{current_user}")

    user = User.query.filter_by(username=username).first_or_404()
    db.session.delete(user)
    db.session.commit()
    session.pop("username")
    flash("User has been deleted", "success")
    return redirect("/")

@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):
    """Show feedback form and prevent user from 
    adding feedback using another user's account"""

    form = FeedbackForm()
    current_user = session["username"]
    user = User.query.filter_by(username=current_user).first()

    if username != session["username"]: ##try to refactor the code but the result is wrong
        flash("Sorry, you can't add feedback using another user's account", "danger")
        return redirect(f"/users/{current_user}")

    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k not in ["csrf_token"]}
        new_feedback = Feedback(username=current_user, **data)
        db.session.add(new_feedback)
        db.session.commit()
        flash("Thank you for your feedback!", "success")
        return redirect(f"/users/{current_user}")
    else:
        return render_template("feedback_form.html", user=user, form=form)
    
#######feedback route########

@app.route("/feedback/<feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    """Show update feedback form and prevent 
    the user from updating another user's feedback"""

    feedback = Feedback.query.get_or_404(feedback_id)
    form = FeedbackForm(obj=feedback)
    user = feedback.username
    
    if user != session["username"]: ##try to refactor the code but the result is wrong
        flash("Sorry, you can't update another user's feedback", "danger")
        return redirect(f"/users/{user}")

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        flash("Feedback has been updated!", "success")
        return redirect(f"/users/{user}")

    return render_template("feedback_details.html", feedback=feedback, form=form)

@app.route("/feedback/<feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Delete feedback and prevent the user from deleting another user's feedback"""
    feedback = Feedback.query.get_or_404(feedback_id)
    user = feedback.username

    if user != session["username"]: ##try to refactor the code but the result is wrong
        flash("Sorry, you can't delete another user's feedback", "danger")
        return redirect(f"/users/{user}")

    db.session.delete(feedback)
    db.session.commit()
    return redirect(f"/users/{user}")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404