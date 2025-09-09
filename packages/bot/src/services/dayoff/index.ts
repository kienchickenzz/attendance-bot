import { DataSource } from 'typeorm'
import { TimePeriod } from '../../Interface'
import { getRunningExpressApp } from '../../utils/getRunningExpressApp'

const _formatDate = ( date: Date ): string => {
    return date.toISOString().split( 'T' )[ 0 ]
}

const _checkHolidayByDate = async ( dateStr: string, dataSource: DataSource ): Promise<string | false> => {
    try {
        const query = `
            SELECT name 
            FROM holidays 
            WHERE date = $1
        `
        const result = await dataSource.query( query, [ dateStr ] )
        
        if ( result && result.length > 0 ) {
            return result[ 0 ].name
        }
        return false
    } catch ( error ) {
        console.error( 'Error checking holiday:', error )
        return false
    }
}

const checkDayOff = async ( timePeriods: TimePeriod[] ) => {

    const appServer = getRunningExpressApp()
    const dataSource: DataSource = appServer.AppDataSource

    let firstHolidayName: string | null = null
    
    try {
        for ( const period of timePeriods ) {
            if ( !period.start_date || !period.end_date ) {
                return { is_dayoff: "False" } // thiếu dữ liệu thì mặc định False
            }
            
            const start = new Date( period.start_date )
            const end = new Date( period.end_date )

            let dayIndex = 0

            // duyệt qua toàn bộ ngày trong khoảng
            for ( let d = new Date( start ); d <= end; d.setDate( d.getDate() + 1 ) ) {
                const dateStr = _formatDate( d )
                const holidayName = await _checkHolidayByDate( dateStr, dataSource )
                
                if ( !holidayName ) {
                    // Nếu không phải ngày nghỉ thì return False
                    return { is_dayoff: "False" }
                }

                if ( dayIndex === 0 ) {
                    firstHolidayName = holidayName
                }
                dayIndex++
            }
        }

        // Nếu tất cả các ngày đều là ngày nghỉ
        return { is_dayoff: firstHolidayName || "True" }
        
    } catch ( error ) {
        console.error( 'Error in checkDayOff:', error )
        return { is_dayoff: "False" }
    }
}

export default {
    checkDayOff,
}
