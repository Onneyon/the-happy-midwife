from datetime import datetime


class card_handler:
    def __init__(self, tags):
        self.tags = tags

    def generate_card(self, doc_dict):
        body_preview = doc_dict['body'].split('</p>')[0].replace('<p>', '')

        tag_string = ''
        doc_dict['tags'].sort()
        for tag in doc_dict['tags']:
            tag_string += '''<div class="chip teal darken-1 white-text" style="font-size:15px;">
            <a style="color: white" href="/articles/sort/{0}/date">{1}</a>
            </div>'''.format(tag, self.tags[tag])

        try:
            doc_dict['author']
        except KeyError:
            doc_dict['author'] = 'Unspecified author'

        return '''<div class="card medium grey lighten-3 center-align">
          <h5 style="padding-top: 1rem;">{0}</h5>
          <div class="card-content" style="padding-top:0px;">
            <h6 class="grey-text text-darken-2">{1}</h6>
            <h6 class="grey-text">{2}</h6>
            <p class="text-black" style="overflow:hidden; display:-webkit-box; -webkit-line-clamp:4; -webkit-box-orient:vertical; line-clamp:4;">
              {3}
            </p>
          </div>
          <div>
            {4}
          </div>
          <div class="card-action black-text">
            <a href="/articles/{5}" class="yellow lighten-2 black-text waves-effect waves-light btn">
            Read more</a>
          </div>
        </div>'''.format(doc_dict['title'], doc_dict['author'], doc_dict['date'], body_preview, tag_string, doc_dict['title'].replace(' ', '-'))

    def get_filtered_cards(self, docs, sorting):
        doc_dicts = []
        ids = []

        for doc in docs:
            if doc.id not in ids:
                doc_dict = doc.to_dict()
                doc_dict['title'] = doc.id
                doc_dicts.append(doc_dict)
                ids.append(doc.id)

        if sorting == 'date':
            doc_dicts.sort(key=lambda x: datetime.strptime(
                x['date'], '%A %d %B %Y'))
            doc_dicts.reverse()
        else:
            doc_dicts.sort(key=lambda x: x['title'])

        return [self.generate_card(doc_dict) for doc_dict in doc_dicts]

    def get_different_card(self, docs, title):
        cards = self.get_filtered_cards(docs, 'date')

        for card in cards:
            if title not in card:
                return card
        return 'Couldn\'t find a different card'
