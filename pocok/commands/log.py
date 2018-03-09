from .start import Start


class Log(Start):

    command = ["log", "logs"]
    description = "Print docker containers logs of the current project with the default or defined plan."

    run_command = "logs"
    need_checkout = False
