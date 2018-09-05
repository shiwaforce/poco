from .start import Start


class Pack(Start):

    command = "pack"
    description = "Run: 'poco pack nginx/default' to pack the nginx project's default plan configuration with docker "\
                  "images into an archive."

    run_command = "pack"
    need_checkout = False
