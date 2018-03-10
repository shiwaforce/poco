from .start import Start


class Ps(Start):

    command = "ps"
    description = "Run: 'pocok ps nginx/test' to print containers statuses which depends defined project " \
                  "'nginx' and plan 'test' \n  or run: 'pocok ps nginx' to print containers statuses which " \
                  "depends defined project 'nginx' and plan 'default'"

    run_command = "ps"
    need_checkout = True
