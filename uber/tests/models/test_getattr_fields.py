from uber.tests import *


def test_ints():
    assert [] == Attendee().interests_ints
    assert [c.ARCADE] == Attendee(interests=c.ARCADE).interests_ints
    assert [c.ARCADE, c.CONSOLE] == Attendee(interests='{},{}'.format(c.ARCADE, c.CONSOLE)).interests_ints


def test_label():
    assert '' == Attendee(paid=None).paid_label
    assert 'yes' == Attendee(paid=c.HAS_PAID).paid_label
    assert '' == Attendee(paid="none").paid_label


def test_local():
    utcnow = datetime.now(UTC)
    assert UTC == Attendee(registered=utcnow).registered.tzinfo
    assert c.EVENT_TIMEZONE.zone == Attendee(registered=utcnow).registered_local.tzinfo.zone


def test_multi_checks():
    pytest.raises(AttributeError, lambda: Attendee().CONSOLE)
    pytest.raises(AttributeError, lambda: Attendee().NOT_A_REAL_CHOICE)

    assert not AdminAccount().PEOPLE
    assert AdminAccount(access='{},{}'.format(c.PEOPLE, c.STUFF)).PEOPLE
    assert not AdminAccount(access='{},{}'.format(c.PEOPLE, c.STUFF)).ACCOUNTS
