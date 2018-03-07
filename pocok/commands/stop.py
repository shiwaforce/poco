from .start import Start


class Stop(Start):

    command = ["stop", "down"]
    description = "Stop project with the default or defined plan."

    run_command = "stop"

    need_checkout = False
