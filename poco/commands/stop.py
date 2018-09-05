from .start import Start


class Stop(Start):

    command = ["stop", "down"]
    description = "Run: 'poco stop nginx/default' or 'poco down nginx/default' to stop nginx project (docker, " \
                  "helm or kubernetes) with the default plan."

    run_command = "stop"

    need_checkout = False
