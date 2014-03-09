from django.core.management.base import BaseCommand
from django.conf import settings
from quitter.models import Profile
from supporter.models import Pledge
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.core.mail.message import EmailMultiAlternatives
from django.utils.timezone import now
from context_processors import settings_variables
from django.http.request import HttpRequest
from django.utils import translation


class Command(BaseCommand):
    help = 'Send reminder emails when goal is reached'

    def handle(self, *args, **options):
        template_html = 'email/honor.html'
        template_text = 'email/honor.txt'
        from_email = settings.DEFAULT_FROM_EMAIL
        quitters = Profile.objects.all()
        for quitter in quitters:
            translation.activate(quitter.language)
            duration = quitter.duration()
            pledges = Pledge.objects.filter(confirmed=True,
                                            honored=False,
                                            days__lte=duration.days)

            self.stdout.write("%d pledges" % (len(pledges)))

            for pledge in pledges:
                if pledge.should_send():
                    subject = u"%(quitter)s has reached your goal" % {'quitter': pledge.beneficiary.quitter.first_name}
                    to = pledge.supporter.email

                    url = 'http://%s%s' % (settings.ALLOWED_HOSTS[0].lstrip('.'),
                                           reverse('pledge_honor', kwargs={'hash': pledge.hash}))

                    context = {'pledge': pledge,
                               'url': url}
                    context.update(settings_variables(HttpRequest()))

                    text_content = render_to_string(template_text, context)
                    html_content = render_to_string(template_html, context)

                    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")
                    self.stdout.write("sending email for %s\n" % (pledge.hash))
                    msg.send()

                    pledge.remind_attempts += 1
                    pledge.last_attempt = now()
                    pledge.save()
                else:
                    self.stdout.write("ignoring email for %s\n" % (pledge.hash))
