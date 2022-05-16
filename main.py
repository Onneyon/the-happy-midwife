from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField, SelectMultipleField, RadioField
from bcrypt import checkpw

from dbhandler import firebase_handler
from cards import card_handler

app = Flask(__name__)
app.config['SECRET_KEY'] = ''
fb = firebase_handler()

TAGS = {}

CARD_COUNT = 200
logged_in = False

PAGES = {'index.html': ['/', 'Home', 'home'],
         'about.html': ['/about/', 'About', 'person'],
         'articles.html': ['/articles/', 'Blog', 'subject'],
         'contact.html': ['/contact/', 'Contact', 'mail_outline'],
         'links.html': ['/links/', 'Links', 'link']}


class editor_data_form(FlaskForm):
    title = StringField('title')
    author = StringField('author')
    summernote = TextAreaField('summernote')
    select_field = SelectMultipleField('Filter by topic')
    featured = BooleanField('featured')


class editor_login_form(FlaskForm):
    password = StringField('password')


class tag_filter_form(FlaskForm):
    select_field = SelectMultipleField('filter')
    radio_field = RadioField('sorting', choices=[
        ('date', 'Chronological'), ('title', 'Alphabetical')])


def update_tags():
    global TAGS
    TAGS = {}
    for tag_name in fb.get_doc('tags', 'tag_names').to_dict()['tag_names']:
        TAGS[tag_name.lower().replace(' ', '-')] = tag_name
    try:
        ch.tags = TAGS
    except NameError:
        pass


def get_card_from_title(title):
    global fb, ch

    doc = fb.get_doc('articles', title)
    doc_dict = doc.to_dict()
    doc_dict['title'] = doc.id

    return ch.generate_card(doc_dict)


update_tags()
ch = card_handler(TAGS)

for page in PAGES:
    if page == 'articles.html':
        @app.route('/articles/', methods=['GET', 'POST'])
        def articles():
            global TAGS, CARD_COUNT
            update_tags()
            filter_form = tag_filter_form()
            filter_form.select_field.choices = [
                (tag, TAGS[tag]) for tag in TAGS]

            try:
                tag_filter
            except NameError:
                tag_filter = TAGS

            try:
                sorting
            except NameError:
                sorting = 'date'

            if filter_form.validate_on_submit():
                tag_filter = filter_form.select_field.data

                if tag_filter == []:
                    tag_filter = TAGS

                sorting = ''
                sorting = filter_form.radio_field.data
                if sorting == '':
                    sorting = 'date'

            tag_string = ''
            for tag in tag_filter:
                tag_string += tag + '&'
            tag_string = tag_string[:-1]

            return redirect('{0}sort/{1}/{2}'.format(url_for("articles"), tag_string, sorting))

    elif page == 'index.html':
        @app.route('/')
        def home():
            global TAGS, logged_in
            update_tags()

            logged_in = False
            char_count = 500
            doc_count = 20

            featured_title = fb.get_doc(
                'featured', 'featured_article').to_dict()['title']
            featured_card = get_card_from_title(featured_title)

            tag_filter = [tag for tag in TAGS][1:]
            docs = fb.get_filtered_docs(tag_filter, doc_count)
            tag_count = len(tag_filter)

            latest_card = ch.get_different_card(docs, featured_title)

            tag_filter = [[tag for tag in TAGS][0]]
            docs = fb.get_filtered_docs(tag_filter, doc_count)
            tag_count = len(tag_filter)

            guest_card = ch.get_different_card(docs, featured_title)

            return render_template(
                'index.html',
                page_title='Home',
                cards=[latest_card, featured_card, guest_card])

    else:
        exec(
            f"@app.route('{PAGES[page][0]}')\ndef {PAGES[page][1].lower()}(): return render_template('{page}',page_title='{PAGES[page][1]}')")


@app.route('/articles/<string:title>')
def article(title):
    try:
        doc = fb.get_doc('articles', title.replace('-', ' '))
        tag_string = ''
        for tag in doc.to_dict()['tags']:
            tag_string += tag + '&'
        tag_string = tag_string[:-1]

        return render_template(
            'article.html',
            tags=TAGS,
            doc=doc,
            pages=PAGES,
            tag_string=tag_string,
            page_title=doc.id,
            is_article=True)

    except TypeError:
        return redirect(url_for('articles'))


@app.route('/articles/sort/<string:article_tags>/<string:sorting>')
def sorted_articles(article_tags, sorting):
    global TAGS, CARD_COUNT
    update_tags()

    tag_filter = article_tags.split('&')
    filter_form = tag_filter_form()
    filter_form.select_field.choices = [(tag, TAGS[tag]) for tag in TAGS]

    card_string = ''

    docs = fb.get_filtered_docs(tag_filter, CARD_COUNT)
    for card in ch.get_filtered_cards(docs, sorting):
        card_string += card

    if card_string == '':
        return redirect(url_for('articles'))

    return render_template(
        'articles.html',
        page_title='Articles',
        filter_form=filter_form,
        cards=card_string,
        tag_filter=tag_filter)


@app.route('/editor/', methods=['GET', 'POST'])
def editor():
    global PAGES, TAGS, logged_in
    update_tags()

    login_form = editor_login_form()
    editor_form = editor_data_form()
    editor_form.select_field.choices = [(tag, TAGS[tag]) for tag in TAGS]

    if not logged_in:
        if login_form.validate_on_submit():
            logged_in = checkpw(
                login_form.password.data.encode(),
                fb.get_doc('auth', 'password').to_dict()['password'].encode())

        return render_template(
            'editor.html',
            login_form=login_form,
            editor_form=editor_form,
            logged_in=logged_in)
    else:
        if editor_form.validate_on_submit():

            if editor_form.featured.data:
                fb.set_featured(editor_form.title.data)

            tags = editor_form.select_field.data
            if tags == []:
                return render_template(
                    'editor.html',
                    login_form=login_form,
                    editor_form=editor_form,
                    logged_in=logged_in)

            fb.add_article(editor_form.title.data, editor_form.author.data,
                           editor_form.summernote.data, tags)
            logged_in = False
            return redirect(url_for('articles'))

        else:
            return render_template(
                'editor.html',
                login_form=login_form,
                editor_form=editor_form,
                logged_in=logged_in)


# Pass the pages dict to all templates
@app.context_processor
def inject_user():
    return dict(pages=PAGES)


if __name__ == '__main__':
    app.run()
