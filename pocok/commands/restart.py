from .start import Start


class Restart(Start):

    command = "restart"
    description = "Restart project with the default or defined plan."

    run_command = "restart"

    need_checkout = True
