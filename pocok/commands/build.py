from .start import Start


class Build(Start):

    command = "build"
    description = "Run: 'pocok build nginx/default' to build containers depends defined project and plan."

    run_command = "build"
    need_checkout = True
