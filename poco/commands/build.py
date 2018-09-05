from .start import Start


class Build(Start):

    command = "build"
    description = "Run: 'poco build nginx/default' to build containers depends defined project and plan."

    run_command = "build"
    need_checkout = True
