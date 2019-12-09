from handlers.mt.base import MtHandler
from methods.image import get_image_url
from models.history import MARK_CATEGORIES, PERIOD_CATEGORY, EVENT_CATEGORY, PERSON_CATEGORY
from models.text import Text, Paragraph


class TextListHandler(MtHandler):
    def get(self):
        mark_id = self.request.get_range('mark_id')
        category = self.request.get_range('category')
        out_category = self.request.get_range('out_category')
        text_id = self.request.get_range('text_id')
        text = Text.get_by_id(text_id)
        if not text:
            self.abort(400)
        if out_category not in MARK_CATEGORIES:
            self.abort(400)
        if out_category == PERIOD_CATEGORY:
            back_link = "/mt/materials/periods/list"
        elif out_category == EVENT_CATEGORY:
            back_link = '/mt/materials/events/list?mark_id=%s&category=%s' % (mark_id, category)
        elif out_category == PERSON_CATEGORY:
            back_link = '/mt/materials/persons/list?mark_id=%s&category=%s' % (mark_id, category)
        for index, paragraph in enumerate(text.paragraphs):
            paragraph.change_url = '/mt/materials/text/change?parent_mark_id=%s&parent_category=%s&text_id=%s&index=%s' % (mark_id, category, text_id, index)
        self.render('/materials/text_list.html',
                    paragraphs=text.paragraphs,
                    back_link=back_link,
                    add_link='/mt/materials/text/add?parent_mark_id=%s&parent_category=%s&text_id=%s' % (mark_id, category, text_id))


class TextAddHandler(MtHandler):
    def get(self):
        parent_mark_id = self.request.get_range('parent_mark_id')
        parent_category = self.request.get_range('parent_category')
        text_id = self.request.get_range('text_id')
        text = Text.get_by_id(text_id)
        if not text:
            self.abort(400)
        back_link = '/mt/materials/text/list?mark_id=%s&category=%s&text_id=%s' % (parent_mark_id, parent_category, text_id)
        self.render('/materials/text_add.html',
                    text=text,
                    back_link=back_link)

    def post(self):
        parent_mark_id = self.request.get_range('parent_mark_id')
        parent_category = self.request.get_range('parent_category')
        text_id = self.request.get_range('text_id')
        text = Text.get_by_id(text_id)
        if not text:
            self.abort(400)
        paragraph = Paragraph()
        paragraph.header = self.request.get('header')
        paragraph.text = self.request.get('text')
        paragraph.image = self.request.get('image')
        if 'lh3.googleusercontent.com' not in paragraph.image:
            paragraph.image = get_image_url('paragraph', 0, url=paragraph.image)
        paragraph.image_description = self.request.get('image_description')
        text.paragraphs.append(paragraph)
        text.put()
        self.redirect('/mt/materials/text/list?mark_id=%s&category=%s&text_id=%s' % (parent_mark_id, parent_category, text_id))


class TextChangeHandler(MtHandler):
    def get(self):
        parent_mark_id = self.request.get_range('parent_mark_id')
        parent_category = self.request.get_range('parent_category')
        text_id = self.request.get_range('text_id')
        text = Text.get_by_id(text_id)
        if not text:
            self.abort(400)
        index = self.request.get_range('index')
        if not index < len(text.paragraphs):
            self.abort(400)
        back_link = '/mt/materials/text/list?mark_id=%s&category=%s&text_id=%s' % (parent_mark_id, parent_category, text_id)
        self.render('/materials/text_add.html',
                    index=index, paragraph=text.paragraphs[index],
                    text=text,
                    back_link=back_link)

    def post(self):
        parent_mark_id = self.request.get_range('parent_mark_id')
        parent_category = self.request.get_range('parent_category')
        text_id = self.request.get_range('text_id')
        text = Text.get_by_id(text_id)
        if not text:
            self.abort(400)
        index = self.request.get_range('index')
        if not index < len(text.paragraphs):
            self.abort(400)
        text.paragraphs[index].header = self.request.get('header')
        text.paragraphs[index].text = self.request.get('text')
        text.paragraphs[index].image = self.request.get('image')
        if 'lh3.googleusercontent.com' not in text.paragraphs[index].image:
            text.paragraphs[index].image = get_image_url('paragraph', 0, url=text.paragraphs[index].image)
        text.paragraphs[index].image_description = self.request.get('image_description')
        text.put()
        self.redirect('/mt/materials/text/list?mark_id=%s&category=%s&text_id=%s' % (parent_mark_id, parent_category, text_id))
