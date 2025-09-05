def get_user_input( input ):
    user_id, user_question = input.split( "|", 1 )
    return user_id

human_input = "{{ human_input }}"
print( get_user_input( human_input ) )