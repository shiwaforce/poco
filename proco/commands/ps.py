from .start import Start


class Ps(Start):

    command = "ps"
    description = "Run: 'proco ps nginx/test' to print containers statuses which depends defined project " \
                  "'nginx' and plan 'test' \n  or run: 'proco ps nginx' to print containers statuses which " \
                  "depends defined project 'nginx' and plan 'default'"

    run_command = "ps"
    need_checkout = True
