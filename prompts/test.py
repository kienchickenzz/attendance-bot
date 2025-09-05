import json

time_result_json = {{ time_result_json }}
user_email = "{{ api_session.data.user_email }}"

def create_query_data( user_email, time_result_json ):
    time_query = time_result_json[ "time_query" ]

    query_data = {
        "user_email": user_email,
        "time_query": time_query
    }
    return json.dumps(query_data)

print( create_query_data( user_email, time_result_json ) )
