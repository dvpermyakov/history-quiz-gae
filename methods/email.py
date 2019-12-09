from google.appengine.api import app_identity, mail

_EMAIL_DOMAIN = "%s.appspotmail.com" % app_identity.get_application_id()


def send_mail_to_admins(scope, subject, body):
    subject = "[HistoryQuiz] " + subject
    sender = "%s_history_quiz@%s" % (scope, _EMAIL_DOMAIN)

    mail.send_mail_to_admins(sender, subject, body)
