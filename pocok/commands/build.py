from .start import Start


class Build(Start):

    command = "build"
    description = "Build containers depends defined project and plan."

    run_command = "build"
    need_checkout = True
