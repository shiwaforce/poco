from .start import Start


class Config(Start):

    command = "config"
    description = "Run: 'pocok config nginx/default' to print full Docker compose configuration for a project's plan."

    run_command = "config"
    need_checkout = False
