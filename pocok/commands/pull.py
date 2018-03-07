from .start import Start


class Pull(Start):

    command = "pull"
    description = "Pull all necessary images for the project with the defined or default plan."

    run_command = "pull"
    need_checkout = True
    end_message = "Project pull complete"

