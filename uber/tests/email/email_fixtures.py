from uber.tests import *
from unittest.mock import patch, Mock


class EmailTestsConstants:
    SUBJECT_TO_FIND = 'CoolCon9000: You Need To Know'
    IDENT_TO_FIND = 'you_are_not_him'

E = EmailTestsConstants


sept_15th = localize_datetime(datetime(year=2016, month=9, day=15, hour=12, minute=30))


@pytest.fixture
def set_datebase_now_to_sept_15th(monkeypatch):
    # TODO: would love to be able to do the code below:
    # monkeypatch.setattr(uber.utils, 'localized_now', Mock(return_value=fake_todays_date))
    #
    # However, we can't override bare functions in modules and get it to propagate out to all the app code.
    # We could (and probably should) solve this in a larger sense by moving localized_now()
    # into a Util class and patching that class. For now, do it this way:
    monkeypatch.setattr(DateBase, 'now', Mock(return_value=sept_15th))


@pytest.fixture
def remove_all_email_categories(monkeypatch):
    monkeypatch.setattr(AutomatedEmail, 'instances', OrderedDict())


@pytest.fixture
def render_fake_email(monkeypatch):
    with patch.object(AutomatedEmail, 'render', return_value='this is email text') as mock:
        yield mock


@pytest.fixture
def record_email_was_sent():
    return patch('_record_email_sent', return_value=None)


@pytest.fixture
def add_test_email_categories(remove_all_email_categories):
    AutomatedEmail(
        model=Attendee,
        subject='{EVENT_NAME}: You Need To Know',
        ident='you_are_not_him',
        template='unrest_in_the_house_of_light.html',
        filter=lambda a: a.paid == c.NEED_NOT_PAY,
        when=(),
        sender="thomas.light@200X.com",
        extra_data=None,
        cc="proto@man.com",
        bcc=None,
        post_con=False,
        needs_approval=True,
    )


@pytest.fixture
def amazon_send_email_mock(monkeypatch):
    """
    Patch the actual low-level method that actually sends an email out of our system onto the internet.
    If this is called, you know that an email was really sent by our email subsystem.
    """
    monkeypatch.setattr(AmazonSES, 'sendEmail', Mock(return_value=None))
    return AmazonSES.sendEmail


@pytest.fixture
def log_unsent_because_unapproved(monkeypatch):
    monkeypatch.setattr(SendAllAutomatedEmailsJob, 'log_unsent_because_unapproved', Mock(return_value=None))
    return SendAllAutomatedEmailsJob.log_unsent_because_unapproved


@pytest.fixture
def setup_fake_test_attendees(monkeypatch):
    # replace all email categories in the system with an empty list so we can add to it later
    monkeypatch.setattr(AutomatedEmail, 'queries', {
        Attendee: lambda ignored_param: [
            Attendee(
                placeholder=True,
                first_name="Gambler",
                last_name="Kirkdouglas",
                email="thegambler@protos.com",
                paid=c.NEED_NOT_PAY,
                badge_type=c.GUEST_BADGE,
                id='b699bfd3-1ada-4f47-b07f-cb7939783afa',
            ),
            Attendee(
                placeholder=True,
                first_name="Kilroy",
                last_name="Kilroy",
                email="that_one_robot@ihaveasecret.com",
                paid=c.NEED_NOT_PAY,
                badge_type=c.GUEST_BADGE,
                id='e91e6c7e-699e-4784-b43f-303acc419dd5',
            ),
            Attendee(
                placeholder=False,
                first_name="Reanimator",
                last_name="Lovejoy",
                email="yeswecan@jumpfromanywhere.com",
                paid=c.HAS_PAID,
                badge_type=c.ATTENDEE_BADGE,
                id='c8b35ec5-4385-4ad7-b7db-b6f082f74aeb',
            ),
        ],
        # Group: lambda ignored_param: would need to replace with: session.query(Group).options(subqueryload(Group.attendees))
    })


@pytest.fixture
def email_subsystem_sane_config(monkeypatch):
    monkeypatch.setattr(c, 'DEV_BOX', False)
    monkeypatch.setattr(c, 'SEND_EMAILS', True)


@pytest.fixture
def remove_approved_idents(monkeypatch):
    monkeypatch.setattr(Config, 'EMAIL_APPROVED_IDENTS', {})


@pytest.fixture
def attendee1():
    return AutomatedEmail.queries[Attendee](None)[0]


@pytest.fixture
def set_test_approved_idents(monkeypatch, remove_approved_idents):
    # list of idents of emails which are approved for sending.  this matches AutomatedEmail.ident
    approved_idents = [
        E.IDENT_TO_FIND,
    ]

    monkeypatch.setattr(Config, 'EMAIL_APPROVED_IDENTS', approved_idents)


@pytest.fixture
def set_previously_sent_emails_empty(monkeypatch):
    # include this fixture if we want to act like no emails have ever been previously sent
    monkeypatch.setattr(Config, 'PREVIOUSLY_SENT_EMAILS', set())


@pytest.fixture
def set_previously_sent_emails_to_attendee1(monkeypatch):
    # include this fixture if we want to act like the email category with ident 'you_are_not_him'
    # was previously sent to attendee with ID #78

    # format of this set: (Email.model, Email.fk_id, Email.ident)
    list_of_emails_previously_sent = {
        (Attendee.__name__, 'b699bfd3-1ada-4f47-b07f-cb7939783afa', 'you_are_not_him'),
    }

    monkeypatch.setattr(Config, 'PREVIOUSLY_SENT_EMAILS', list_of_emails_previously_sent)
    return list_of_emails_previously_sent


@pytest.fixture
def reset_unapproved_emails_count(monkeypatch):
    for email_category in AutomatedEmail.instances.values():
        email_category.unapproved_emails_not_sent = None


@pytest.fixture
def email_subsystem_sane_setup(
        email_subsystem_sane_config,
        add_test_email_categories,
        setup_fake_test_attendees,
        set_previously_sent_emails_empty,
        reset_unapproved_emails_count,
        remove_approved_idents,
        amazon_send_email_mock):
    """
    Catch-all test for setting up all email subsytem tests.  This fixture is a catch-all container of all relevant
    email testing fixtures.

    We will reset a bunch of global state and fake database data in each test run
    """
    pass


@pytest.fixture
def get_test_email_category():
    return AutomatedEmail.instances.get(E.IDENT_TO_FIND)
