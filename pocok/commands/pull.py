from .start import Start


class Pull(Start):

    command = "pull"
    description = "Run: 'pocok pull nginx/default' to pull all necessary images for the project 'nginx' and plan " \
                  "'default'. It is working only Docker."

    run_command = "pull"
    need_checkout = True
    end_message = "Project pull complete"
