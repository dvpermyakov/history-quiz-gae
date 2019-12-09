from google.appengine.ext import ndb


class Paragraph(ndb.Model):
    header = ndb.StringProperty(required=True)
    text = ndb.StringProperty(required=True)
    image = ndb.StringProperty(default="")
    image_description = ndb.StringProperty(default="")

    def dict(self):
        return {
            'header': self.header,
            'text': self.text,
            'image': self.image,
            'image_description': self.image_description
        }


class Text(ndb.Model):
    paragraphs = ndb.StructuredProperty(Paragraph, repeated=True)

    def dict(self):
        return {
            'paragraphs': [paragraph.dict() for paragraph in self.paragraphs]
        }
