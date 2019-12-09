# coding=utf-8
from handlers.mt.base import MtHandler
from methods.image import get_image_url
from methods.mapping import sorted_history_marks, get_date_from_html, get_html_date_from_str
from methods.strings import DEFAULT_PERIODS_STRING, DEFAULT_EVENTS_STRING, DEFAULT_PERSONS_STRING
from models.history import HistoryPeriod, HistoryCountry, MARK_CATEGORIES, PERIOD_CATEGORY, HistoryEvent, HistoryPerson, \
    HistoryPersonTitle, EVENT_CATEGORY, PERSON_CATEGORY
from models.test import Test
from models.text import Text


def set_add_defaults(mark, country_key):
    text = Text()
    text.put()
    mark.text = text.key
    test = Test()
    test.put()
    mark.test = test.key
    mark.country = country_key


def get_mark_values(request, mark):
    mark.image = request.get('image')
    if 'lh3.googleusercontent.com' not in mark.image:
        mark.image = get_image_url('mark', 0, url=mark.image)
    mark.available = bool(request.get('available'))
    mark.sort_index = request.get_range('sort_index')
    mark.name = request.get('name')
    mark.description = request.get('description')
    mark.group_title = request.get('group_title')
    mark.start = get_date_from_html(request.get('start'))
    mark.end = get_date_from_html(request.get('end'))
    return mark


def get_dependencies(mark):
    dependencies = []
    for dependency in mark.dependencies:
        dependency = dependency.get()
        if dependency:
            dependencies.append(dependency.name)
    return dependencies


class CountryListHandler(MtHandler):
    def get(self):
        countries = HistoryCountry.query().fetch()
        for country in countries:
            country.link = '/mt/materials/periods/list?country_id=%s' % country.key.id()

        self.render('/materials/country_list.html',
                    countries=countries,
                    add_link="/mt/materials/countries/add")


class CountryAddHandler(MtHandler):
    def get(self):
        self.render('/materials/country_add.html',
                    back_link="/mt/materials/countries/list")

    def post(self):
        country = HistoryCountry()
        country.name = self.request.get('name')
        country.put()
        self.redirect('/mt/materials/countries/list')


class HistoryPeriodListHandler(MtHandler):
    def get(self):
        country_id = self.request.get_range('country_id')
        country = HistoryCountry.get_by_id(country_id)
        if not country:
            self.abort(400)

        periods = sorted_history_marks(HistoryPeriod.query(HistoryPeriod.country == country.key).fetch())
        for period in periods:
            period.change_url = "/mt/materials/periods/change?period_id=%s" % period.key.id()
            period.extra = {
                'Личности'.decode("utf-8"): "/mt/materials/persons/list?mark_id=%s&category=0" % period.key.id(),
                'События'.decode("utf-8"): "/mt/materials/events/list?mark_id=%s&category=0" % period.key.id(),
            }
            period.dependencies_obj = get_dependencies(period)

        self.render('/materials/mark_list.html',
                    marks=periods,
                    parent_mark_id=None,
                    parent_category=None,
                    category=PERIOD_CATEGORY,
                    back_link="",
                    add_link="/mt/materials/periods/add?country_id=%s" % country.key.id())


class HistoryPeriodAddHandler(MtHandler):
    def get(self):
        country_id = self.request.get_range('country_id')
        country = HistoryCountry.get_by_id(country_id)
        if not country:
            self.abort(400)
        self.render('/materials/mark_add.html',
                    country=country,
                    default_category=DEFAULT_PERIODS_STRING.decode("utf-8"),
                    back_link="/mt/materials/periods/list?country_id=%s" % country.key.id())

    def post(self):
        country_id = self.request.get_range('country_id')
        country = HistoryCountry.get_by_id(country_id)
        if not country:
            self.abort(400)
        period = HistoryPeriod()
        period.category = PERIOD_CATEGORY
        get_mark_values(self.request, period)
        if period.available:
            period.developing = False
        else:
            period.developing = True
        set_add_defaults(period, country.key)
        period.put()
        country.put()
        self.redirect('/mt/materials/periods/list?country_id=%s' % country.key.id())


class HistoryPeriodChangeHandler(MtHandler):
    def get(self):
        period_id = self.request.get_range('period_id')
        period = HistoryPeriod.get_by_id(period_id)
        if not period:
            self.abort(400)
        period.start_str = get_html_date_from_str(period.start)
        period.end_str = get_html_date_from_str(period.end)
        self.render('/materials/mark_add.html',
                    country=period.country.get(),
                    mark=period,
                    default_category=DEFAULT_PERIODS_STRING.decode("utf-8"),
                    back_link="/mt/materials/periods/list")

    def post(self):
        country_id = self.request.get_range('country_id')
        country = HistoryCountry.get_by_id(country_id)
        if not country:
            self.abort(400)
        period_id = self.request.get_range('mark_id')
        period = HistoryPeriod.get_by_id(period_id)
        get_mark_values(self.request, period)
        if period.available:
            period.developing = False
        else:
            period.developing = True
        period.put()
        country.put()
        self.redirect('/mt/materials/periods/list?country_id=%s' % country.key.id())


class HistoryEventListHandler(MtHandler):
    def get(self):
        mark_id = self.request.get_range('mark_id')
        category = self.request.get_range('category')
        if category not in MARK_CATEGORIES:
            self.abort(400)
        events = []
        back_link = ""
        add_link = ""
        if category == PERIOD_CATEGORY:
            period = HistoryPeriod.get_by_id(mark_id)
            events = sorted_history_marks(HistoryEvent.get_by_period(period, consider_avail=False))
            back_link = "/mt/materials/periods/list"
            add_link = "/mt/materials/events/add?parent_mark_id=%s&parent_category=0" % period.key.id()
        for event in events:
            event.change_url = "/mt/materials/events/change?event_id=%s&parent_mark_id=%s&parent_category=%s" % (event.key.id(), mark_id, category)
            event.extra = {
                'Видео'.decode("utf-8"): "/mt/materials/videos/list?mark_id=%s&category=1" % event.key.id(),
            }
            event.dependencies_obj = get_dependencies(event)
        self.render('/materials/mark_list.html',
                    marks=events,
                    parent_mark_id=mark_id,
                    parent_category=category,
                    category=EVENT_CATEGORY,
                    back_link=back_link,
                    add_link=add_link)


class HistoryEventAddHandler(MtHandler):
    def get(self):
        parent_mark_id = self.request.get_range('parent_mark_id')
        parent_category = self.request.get_range('parent_category')
        back_link = '/mt/materials/events/list?parent_mark_id=%s&parent_category=%s' % (parent_mark_id, parent_category)
        self.render('/materials/mark_add.html',
                    parent_mark_id=parent_mark_id, parent_category=parent_category,
                    default_category=DEFAULT_EVENTS_STRING.decode("utf-8"),
                    back_link=back_link)

    def post(self):
        parent_mark_id = self.request.get_range('parent_mark_id')
        parent_category = self.request.get_range('parent_category')
        if parent_category == PERIOD_CATEGORY:
            mark = HistoryPeriod.get_by_id(parent_mark_id)
        event = HistoryEvent()
        event.category = EVENT_CATEGORY
        event.period = mark.key
        get_mark_values(self.request, event)
        set_add_defaults(event, mark.country)
        event.put()
        event.country.get().update()
        self.redirect('/mt/materials/events/list?mark_id=%s&category=%s' % (parent_mark_id, parent_category))


class HistoryEventChangeHandler(MtHandler):
    def get(self):
        parent_mark_id = self.request.get_range('parent_mark_id')
        parent_category = self.request.get_range('parent_category')
        event_id = self.request.get_range('event_id')
        event = HistoryEvent.get_by_id(event_id)
        if not event:
            self.abort(400)
        event.start_str = get_html_date_from_str(event.start)
        event.end_str = get_html_date_from_str(event.end)
        back_link = '/mt/materials/events/list?mark_id=%s&category=%s' % (parent_mark_id, parent_category)
        self.render('/materials/mark_add.html',
                    parent_mark_id=parent_mark_id, parent_category=parent_category,
                    mark=event,
                    default_category=DEFAULT_EVENTS_STRING.decode("utf-8"),
                    back_link=back_link)

    def post(self):
        parent_mark_id = self.request.get_range('parent_mark_id')
        parent_category = self.request.get_range('parent_category')
        event_id = self.request.get_range('mark_id')
        event = HistoryEvent.get_by_id(event_id)
        get_mark_values(self.request, event)
        event.put()
        event.country.get().update()
        self.redirect('/mt/materials/events/list?mark_id=%s&category=%s' % (parent_mark_id, parent_category))


class HistoryPersonListHandler(MtHandler):
    def get(self):
        mark_id = self.request.get_range('mark_id')
        category = self.request.get_range('category')
        if category not in MARK_CATEGORIES:
            self.abort(400)
        persons = []
        back_link = ""
        add_link = ""
        if category == PERIOD_CATEGORY:
            period = HistoryPeriod.get_by_id(mark_id)
            persons = sorted_history_marks(HistoryPerson.get_by_period(period, consider_avail=False))
            back_link = "/mt/materials/periods/list"
            add_link = "/mt/materials/persons/add?parent_mark_id=%s&parent_category=0" % period.key.id()
        for person in persons:
            person.change_url = "/mt/materials/persons/change?person_id=%s&parent_mark_id=%s&parent_category=%s" % (person.key.id(), mark_id, category)
            person.extra = {
                'Видео'.decode("utf-8"): "/mt/materials/videos/list?mark_id=%s&category=2" % person.key.id(),
                'Титулы'.decode("utf-8"): '/mt/materials/persons/titles/list?parent_mark_id=%s&parent_category=%s&person_id=%s' % (mark_id, category, person.key.id())
            }
            person.dependencies_obj = get_dependencies(person)
        self.render('/materials/mark_list.html',
                    marks=persons,
                    parent_mark_id=mark_id,
                    parent_category=category,
                    category=PERSON_CATEGORY,
                    back_link=back_link,
                    add_link=add_link)


class HistoryPersonAddHandler(MtHandler):
    def get(self):
        parent_mark_id = self.request.get_range('parent_mark_id')
        parent_category = self.request.get_range('parent_category')
        back_link = '/mt/materials/persons/list?mark_id=%s&category=%s' % (parent_mark_id, parent_category)
        self.render('/materials/mark_add.html',
                    parent_mark_id=parent_mark_id, parent_category=parent_category,
                    default_category=DEFAULT_PERSONS_STRING.decode("utf-8"),
                    back_link=back_link)

    def post(self):
        parent_mark_id = self.request.get_range('parent_mark_id')
        parent_category = self.request.get_range('parent_category')
        if parent_category == PERIOD_CATEGORY:
            mark = HistoryPeriod.get_by_id(parent_mark_id)
        person = HistoryPerson()
        person.category = PERSON_CATEGORY
        person.period = mark.key
        get_mark_values(self.request, person)
        set_add_defaults(person, mark.country)
        person.put()
        person.country.get().update()
        self.redirect('/mt/materials/persons/list?mark_id=%s&category=%s' % (parent_mark_id, parent_category))


class HistoryPersonChangeHandler(MtHandler):
    def get(self):
        parent_mark_id = self.request.get_range('parent_mark_id')
        parent_category = self.request.get_range('parent_category')
        person_id = self.request.get_range('person_id')
        person = HistoryPerson.get_by_id(person_id)
        if not person:
            self.abort(400)
        person.start_str = get_html_date_from_str(person.start)
        person.end_str = get_html_date_from_str(person.end)
        back_link = '/mt/materials/persons/list?mark_id=%s&category=%s' % (parent_mark_id, parent_category)
        self.render('/materials/mark_add.html',
                    parent_mark_id=parent_mark_id, parent_category=parent_category,
                    mark=person,
                    default_category=DEFAULT_EVENTS_STRING.decode("utf-8"),
                    back_link=back_link)

    def post(self):
        parent_mark_id = self.request.get_range('parent_mark_id')
        parent_category = self.request.get_range('parent_category')
        person_id = self.request.get_range('mark_id')
        person = HistoryPerson.get_by_id(person_id)
        get_mark_values(self.request, person)
        person.put()
        person.country.get().update()
        self.redirect('/mt/materials/persons/list?mark_id=%s&category=%s' % (parent_mark_id, parent_category))


class HistoryPersonTitleListHandler(MtHandler):
    def get(self):
        parent_mark_id = self.request.get_range('parent_mark_id')
        parent_category = self.request.get_range('parent_category')
        person_id = self.request.get_range('person_id')
        person = HistoryPerson.get_by_id(person_id)
        if not person:
            self.abort(400)
        for index, title in enumerate(person.person_titles):
            title.change_url = '/mt/materials/persons/titles/change?parent_mark_id=%s&parent_category=%s&person_id=%s&index=%s' % (parent_mark_id, parent_category, person_id, index)
        self.render('/materials/title_list.html',
                    titles=person.person_titles,
                    back_link='/mt/materials/persons/list?mark_id=%s&category=%s' % (parent_mark_id, parent_category),
                    add_link='/mt/materials/persons/titles/add?parent_mark_id=%s&parent_category=%s&person_id=%s' % (parent_mark_id, parent_category, person_id))


class HistoryPersonTitleAddHandler(MtHandler):
    def get(self):
        parent_mark_id = self.request.get_range('parent_mark_id')
        parent_category = self.request.get_range('parent_category')
        person_id = self.request.get_range('person_id')
        back_link = '/mt/materials/persons/titles/list?parent_mark_id=%s&parent_category=%s&person_id=%s' % (parent_mark_id, parent_category, person_id)
        self.render('/materials/title_add.html',
                    parent_mark_id=parent_mark_id, parent_category=parent_category,
                    back_link=back_link)

    def post(self):
        parent_mark_id = self.request.get_range('parent_mark_id')
        parent_category = self.request.get_range('parent_category')
        person_id = self.request.get_range('person_id')
        person = HistoryPerson.get_by_id(person_id)
        if not person:
            self.abort(400)
        title = HistoryPersonTitle()
        title.name = self.request.get('name')
        title.start = get_date_from_html(self.request.get('start'))
        title.end = get_date_from_html(self.request.get('end'))
        person.person_titles.append(title)
        person.put()
        self.redirect('/mt/materials/persons/titles/list?parent_mark_id=%s&parent_category=%s&person_id=%s' % (parent_mark_id, parent_category, person_id))


class HistoryPersonTitleChangeHandler(MtHandler):
    def get(self):
        index = self.request.get_range('index')
        parent_mark_id = self.request.get_range('parent_mark_id')
        parent_category = self.request.get_range('parent_category')
        person_id = self.request.get_range('person_id')
        person = HistoryPerson.get_by_id(person_id)
        if not person:
            self.abort(400)
        if not index < len(person.person_titles):
            self.abort(400)
        person.person_titles[index].start_str = get_html_date_from_str(person.start)
        person.person_titles[index].end_str = get_html_date_from_str(person.end)
        back_link = '/mt/materials/persons/titles/list?parent_mark_id=%s&parent_category=%s&person_id=%s' % (parent_mark_id, parent_category, person_id)
        self.render('/materials/title_add.html',
                    title=person.person_titles[index],
                    index=index, person_id=person.key.id(),
                    parent_mark_id=parent_mark_id, parent_category=parent_category,
                    back_link=back_link)

    def post(self):
        index = self.request.get_range('index')
        parent_mark_id = self.request.get_range('parent_mark_id')
        parent_category = self.request.get_range('parent_category')
        person_id = self.request.get_range('person_id')
        person = HistoryPerson.get_by_id(person_id)
        person.person_titles[index].name = self.request.get('name')
        person.person_titles[index].start = get_date_from_html(self.request.get('start'))
        person.person_titles[index].end = get_date_from_html(self.request.get('end'))
        person.put()
        self.redirect('/mt/materials/persons/titles/list?parent_mark_id=%s&parent_category=%s&person_id=%s' % (parent_mark_id, parent_category, person_id))


class DependencyAddHandler(MtHandler):
    def get(self):
        mark_id = self.request.get_range('mark_id')
        category = self.request.get_range('category')
        if category == PERIOD_CATEGORY:
            back_link = "/mt/materials/periods/list"
            mark = HistoryPeriod.get_by_id(mark_id)
        elif category == EVENT_CATEGORY:
            back_link = '/mt/materials/events/list?mark_id=%s&category=%s' % (mark_id, category)
            mark = HistoryEvent.get_by_id(mark_id)
        elif category == PERSON_CATEGORY:
            back_link = '/mt/materials/persons/list?mark_id=%s&category=%s' % (mark_id, category)
            mark = HistoryPerson.get_by_id(mark_id)
        options = []
        for mark in HistoryEvent.query().fetch():
            options.append({
                'id': '%s_%s' % (mark.key.id(), EVENT_CATEGORY),
                'name': mark.name
            })
        for mark in HistoryPerson.query().fetch():
            options.append({
                'id': '%s_%s' % (mark.key.id(), PERSON_CATEGORY),
                'name': mark.name
            })
        for mark in HistoryPeriod.query().fetch():
            options.append({
                'id': '%s_%s' % (mark.key.id(), PERIOD_CATEGORY),
                'name': mark.name
            })
        self.render('/materials/dependency_add.html',
                    mark=mark, category=category,
                    options=options,
                    back_link=back_link)

    def post(self):
        dependency_key = self.request.get('dependency').split('_')
        dependency_mark_id, dependency_category = int(dependency_key[0]), int(dependency_key[1])
        if dependency_category == PERIOD_CATEGORY:
            dependency = HistoryPeriod.get_by_id(dependency_mark_id)
        elif dependency_category == EVENT_CATEGORY:
            dependency = HistoryEvent.get_by_id(dependency_mark_id)
        elif dependency_category == PERSON_CATEGORY:
            dependency = HistoryPerson.get_by_id(dependency_mark_id)

        mark_id = self.request.get_range('mark_id')
        category = self.request.get_range('category')
        if category == PERIOD_CATEGORY:
            back_link = "/mt/materials/periods/list"
            mark = HistoryPeriod.get_by_id(mark_id)
        elif category == EVENT_CATEGORY:
            back_link = '/mt/materials/events/list?mark_id=%s&category=%s' % (mark_id, category)
            mark = HistoryEvent.get_by_id(mark_id)
        elif category == PERSON_CATEGORY:
            back_link = '/mt/materials/persons/list?mark_id=%s&category=%s' % (mark_id, category)
            mark = HistoryPerson.get_by_id(mark_id)
        found = False
        for dependency_key in mark.dependencies:
            if dependency_key.get() == dependency.name:
                found = True
        if not found:
            mark.dependencies.append(dependency.key)
            mark.put()
        self.redirect(back_link)
