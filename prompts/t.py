attendance_data = {{ attendance_data }}

def is_data_empty( attendance_data ):
    if not attendance_data or "data" not in attendance_data or not attendance_data["data"]:
        return "Yes"
    
    return "No"

print( is_data_empty( attendance_data ) )
