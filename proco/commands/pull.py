from .start import Start


class Pull(Start):

    command = "pull"
    description = "Run: 'proco pull nginx/default' to pull all necessary images for the project 'nginx' and plan " \
                  "'default'. It is working only with Docker."

    run_command = "pull"
    need_checkout = True
    end_message = "Project pull complete"