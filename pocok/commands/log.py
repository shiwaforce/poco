from .start import Start


class Log(Start):

    command = ["log", "logs"]
    description = "Run: 'pocok log nginx/default' or 'pocok logs nginx/default' to print docker containers logs of " \
                  "the nginx project, default plan."

    run_command = "logs"
    need_checkout = False
