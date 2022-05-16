import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime


class firebase_handler:
    # '''
    # flask
    def __init__(self):
        cred = credentials.Certificate('thehappymidwife-2e3febc76e43.json')
        firebase_admin.initialize_app(cred)

        self.db = firestore.client()
    '''
    # gcloud

    def __init__(self):
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(
            cred, {'projectId': 'thehappymidwife'})

        self.db = firestore.client()
    # '''

    def get_doc(self, collection, document):
        return self.db.collection(collection).document(document).get()

    def set_featured(self, featured_title):
        doc_ref = self.db.collection('featured').document('featured_article')
        doc_ref.set({
            'title': featured_title
        })

    def add_article(self, title, author, body, tags):
        doc_ref = self.db.collection('articles').document(title)
        doc_ref.set({
            'date': datetime.utcnow().strftime('%A %d %B %Y'),
            'author': author,
            'body': body,
            'tags': tags
        })

    def add_tag(self, tag_name):
        tag_names = self.get_doc('tags', 'tag_names').to_dict()['tag_names']
        tag_names.append(tag_name)

        doc_ref = self.db.collection('tags').document('tag_names')
        doc_ref.set({
            'tag_names': tag_names
        })

    def get_filtered_docs(self, tag_filter, doc_count):
        doc_streams = []
        for tag in tag_filter:
            docs_ref = self.db.collection('articles').where(
                'tags', 'array_contains', tag).limit(doc_count)
            doc_stream = docs_ref.stream()
            doc_streams.append(doc_stream)

        output_docs = []
        for doc_stream in doc_streams:
            for doc in doc_stream:
                if doc.id not in [doc.id for doc in output_docs]:
                    output_docs.append(doc)

        return output_docs