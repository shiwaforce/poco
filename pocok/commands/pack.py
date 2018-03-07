from .start import Start


class Pack(Start):

    command = "pack"
    description = "Pack the selected project's plan configuration with docker images into an archive."

    run_command = "pack"
    need_checkout = False
