from .start import Start


class Stop(Start):

    command = ["stop", "down"]
    description = "Run: 'pocok stop nginx/default' or 'pocok down nginx/default' to stop nginx project (docker, " \
                  "helm or kubernetes) with the default plan."

    run_command = "stop"

    need_checkout = False
