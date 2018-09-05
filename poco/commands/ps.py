from .start import Start


class Ps(Start):

    command = "ps"
    description = "Run: 'poco ps nginx/test' to print containers statuses which depends defined project " \
                  "'nginx' and plan 'test' \n  or run: 'poco ps nginx' to print containers statuses which " \
                  "depends defined project 'nginx' and plan 'default'"

    run_command = "ps"
    need_checkout = True
