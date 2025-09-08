attendance_data = {{ attendance_data }}

def process_data( attendance_data ):
    summary_parts = []
    summary_parts.append( "Thời gian check in/out:\n" )

    for index, record in enumerate( attendance_data[ "data" ] ):
        summary_parts.append( f"Ngày: { record.get( 'date', 'không có' ) }" )

        checkin_text = "check in time: "
        checkin_text += record.get( "checkin_time" ) or "không có"
        summary_parts.append( checkin_text )

        checkout_text = "check out time: "
        checkout_text += record.get( "checkout_time" ) or "không có"
        summary_parts.append( checkout_text )

        if index < len( attendance_data[ "data" ] ) - 1:
            summary_parts.append( "" )  # dòng trống giữa các bản ghi

    final_summary = "\n".join( summary_parts )
    return final_summary

print( process_data( attendance_data ) )