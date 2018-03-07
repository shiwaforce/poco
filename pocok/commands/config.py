from .start import Start


class Config(Start):

    command = "config"
    description = "Print full Docker compose configuration for a project's plan."

    run_command = "config"
    need_checkout = False
