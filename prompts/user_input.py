def get_user_input( input ):
    user_id, user_input = input.split( "|", 1 )
    return user_input

human_input = "{{ human_input }}"
print( get_user_input( human_input ) )