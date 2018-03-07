from .start import Start


class Ps(Start):

    command = "ps"
    description = "Print containers statuses which depends defined project and plan."

    run_command = "ps"
    need_checkout = True
