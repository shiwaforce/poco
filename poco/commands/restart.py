from .start import Start


class Restart(Start):

    command = "restart"
    description = "Run: 'poco restart nginx default' to restart nginx/project (docker, helm or kubernetes) " \
                  "with the default plan."

    run_command = "restart"

    need_checkout = True
