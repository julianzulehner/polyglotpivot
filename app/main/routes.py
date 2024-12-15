from app import db
from flask import redirect, render_template, url_for, flash, request, current_app
from app.main.forms import EditProfileForm, AddPostForm
from app.main.forms import AddVocableForm, PracticeForm, ConfigPracticeForm, EmptyForm
from flask_login import current_user, login_required
from urllib.parse import urlsplit
import sqlalchemy as sa 
from app.models import User, Post, Language, Vocable, Session
from datetime import datetime, timezone
from app.main import bp

@bp.route('/')
@bp.route('/index', methods=["GET","POST"])
@login_required
def index():
    if current_user.is_authenticated:
        if not current_user.languages:
            flash(f"Hi {current_user.username}. Nice to see a new face here. \
                  You can configure your profile on this page. If you want you can \
                  Write some nice words about you.\
                  Also, select the languages you would like to study. \
                  You can come back and change your settings anytime. \
                  Welcome to the Polyglotpivot community.", "info")
            return redirect(url_for('auth.edit_profile'))
    form = AddPostForm()
    if form.validate_on_submit():
        new_post = Post(body=form.post.data, author=current_user)
        db.session.add(new_post)
        db.session.commit()
        flash("Post was added, successfully!", 'success')
        form.post.data = ""
        return redirect(url_for("main.index"))
    else:
        flash("This website is under active development.","info")
    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(query ,page=page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    return render_template("index.html", title="Home", posts=posts.items, form=form, next_url=next_url, prev_url=prev_url)

@bp.route("/user/<username>")
@login_required  
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@bp.route("/vocabulary",methods=["GET"])
@login_required
def vocabulary():
    page = request.args.get('page', 1, type=int)
    query = sa.select(Vocable).where(Vocable.user_id == current_user.id)
    vocables = db.paginate(query, page=page, per_page=current_app.config["VOCABLES_PER_PAGE"], error_out=False)
    next_url = url_for('main.vocabulary', page=vocables.next_num) if vocables.has_next else None
    prev_url = url_for('main.vocabulary', page=vocables.prev_num) if vocables.has_prev else None
    return render_template("vocabulary.html",title="Your Vocabulary", vocables=vocables, next_url=next_url, prev_url=prev_url)

@bp.route("/add_vocable", methods=["GET","POST"])
@login_required
def add_vocable():
    form = AddVocableForm()
    if form.validate_on_submit():
        vocable_data = {}
        for language in current_user.languages:
            vocable_data[language.iso] = form[language.iso].data
        new_vocable = Vocable(**vocable_data)
        current_user.vocables.append(new_vocable)
        db.session.add(new_vocable)
        db.session.commit()
        flash("New vocable was added successfully.","success")
        return redirect(url_for('main.add_vocable'))
    return render_template("add_vocable.html", form=form)

@bp.route("/delete_vocable/<vocable_id>",methods=["GET"])
@login_required
def delete_vocable(vocable_id):
    db.session.delete(db.session.get(Vocable,vocable_id))
    db.session.commit()
    return redirect(url_for('main.vocabulary'))

@bp.route("/practice", methods=["GET","POST"])
@login_required
def practice(): 
    form = PracticeForm()
    result = None
    vocable = None
    next_vocable_autofocus = False
    if not current_user.session.target_language_id:
        return redirect(url_for("main.config_practice"))
    
    vocable = db.session.get(Vocable, current_user.session.vocable_id)
    target_language = db.session.get(Language, current_user.session.target_language_id) 
    source_language = db.session.get(Language, current_user.session.source_language_id) 
    if form.submit.data and form.validate():
        if not current_user.session.vocable_id:
            redirect(url_for("main.new_vocable"))
        result = vocable.check_result_and_set_level(form.your_answer.data, target_language) 
        if result:
            flash("Your answer is correct!", "success")
            next_vocable_autofocus = True
        else: 
            flash(f'The right answer would be: "{getattr(vocable, target_language.iso)}"', "danger") 
      
    return render_template("practice.html",form=form,target_language = target_language, source_language = source_language, vocable=vocable, next_vocable_autofocus=next_vocable_autofocus)

@bp.route("/config_practice", methods=["GET","POST"])
@login_required
def config_practice():
    form = ConfigPracticeForm()
    languages = current_user.languages
    language_list = [l.name for l in languages]
    form.source_language.choices=language_list
    form.target_language.choices=language_list
    if form.validate_on_submit():
        current_user.session.source_language_id = db.session.scalar(sa.select(Language.id).where(Language.name == form.source_language.data))
        current_user.session.target_language_id = db.session.scalar(sa.select(Language.id).where(Language.name == form.target_language.data))
        db.session.commit()
        return redirect(url_for("main.practice"))
    return render_template("config_practice.html", form=form)

@bp.route("/new_vocable", methods=["GET"])
@login_required
def new_vocable():
    target_language = db.session.get(Language, current_user.session.target_language_id)
    source_language = db.session.get(Language, current_user.session.source_language_id)
    res = current_user.get_due_vocable(source_language, target_language)
    if res:
        current_user.session.vocable_id = res[0].id
        db.session.commit()
        return redirect(url_for("main.practice"))
    else:
        flash("To practice, you first have to add vocabulary or edit existing" \
            " entries.", "danger")
        return redirect(url_for("main.add_vocable"))

@bp.route("/edit_vocable/<vocable_id>", methods=["GET", "POST"])
@login_required
def edit_vocable(vocable_id):
    vocable = db.session.get(Vocable, vocable_id)
    if vocable.user == current_user:
        form = AddVocableForm(obj=vocable)  # Populate the form with existing data

        if form.validate_on_submit():
            
            # Update the existing vocable with the new form data
            for language in current_user.languages:
                vocable.__setattr__(language.iso, form[language.iso].data)
            db.session.commit()
            flash("Vocable was successfully updated.", "success")
            return redirect(url_for("main.vocabulary"))  # Adjust the redirect URL as needed
    else:
        return redirect(url_for("main.index"))
    return render_template("edit_vocable.html", form=form, vocable_id=vocable_id)
