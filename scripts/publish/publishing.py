"""Functionality for publishing emails via SendGrid"""


from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from jinja2 import Template


def publish(all_articles, from_email, to_email, sendgrid_api_key):
    with open('email_template.html', 'r') as f:
        template = Template(f.read())

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject='Today\'s News',
        html_content=template.render(all_articles=all_articles))
    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        print(response.status_code)
    except Exception as e:
        print(e.message)


# For testing purposes:
# all_articles = {
#     'source_one': [
#         {'title': 'This is an article1', 'url': 'https://google.com'},
#         {'title': 'This is an article2', 'url': 'https://google.com'},
#         {'title': 'This is an article3', 'url': 'https://google.com'},
#     ],
#     'source_two': [
#         {'title': 'This too is an article1', 'url': 'https://google.com'},
#         {'title': 'This too is an article2', 'url': 'https://google.com'},
#         {'title': 'This too is an article3', 'url': 'https://google.com'},
#     ]
# }
#
# publish(all_articles)
