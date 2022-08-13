# Copy current file to : /usr/share/bash-completion/completions/poco

_poco_completion()
{
    local cur_word comp_command

    # COMP_WORDS is an array of words in the current command line.
    # COMP_CWORD is the index of the current word (the one the cursor is
    # in). So COMP_WORDS[COMP_CWORD] is the current word; we also record
    # the previous word here, although this specific script doesn't
    # use it yet.
    cur_word="${COMP_WORDS[COMP_CWORD]}"

    # Ask poco to generate a list of commands os other resources
    comp_command=`poco completion "${COMP_LINE}"`

    # Only perform completion if the current word starts with a dash ('-'),
    # meaning that the user is trying to complete an option.
    COMPREPLY=( $(compgen -W "${comp_command}" -- ${cur_word}) )
    return 0
}

complete -F _poco_completion poco
