from .start import Start


class Log(Start):

    command = ["log", "logs"]
    description = "Run: 'proco log nginx/default' or 'proco logs nginx/default' to print docker containers logs of " \
                  "the nginx project, default plan."

    run_command = "logs"
    need_checkout = False
