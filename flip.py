def flip():
    """A fair coin simulator"""
    from random import choice
    while True:
        r1, r2 = choice([0,1]), choice([0,1])
        if bool(r1) ^ bool(r2):  # exclusive or
            yield r1
