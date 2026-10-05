RATING_ORDER = {
    "EC": 0,
    "E": 1,
    "E10+": 2,
    "T": 3,
    "M": 4,
    "AO": 5,
}

GUEST_MAX_RATING = "E"


def allowed(content_rating, account_max_rating):
    return RATING_ORDER[content_rating] <= RATING_ORDER[account_max_rating]


def guest_allowed(content_rating):
    return allowed(content_rating, GUEST_MAX_RATING)
