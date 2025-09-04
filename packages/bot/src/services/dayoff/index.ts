import { TimePeriod } from '../../Interface'

const checkDayOff = ( timePeriods: TimePeriod[] ) => {
    const isWeekend = ( dateStr: string ): boolean => {
        const d = new Date( dateStr )
        const day = d.getDay() // 0 = Sunday, 6 = Saturday
        return day === 0 || day === 6
    }

    for ( const period of timePeriods ) {
        if ( !period.start_date || !period.end_date ) {
            return { is_dayoff: "False" } // thiếu dữ liệu thì mặc định False
        }

        const start = new Date( period.start_date )
        const end = new Date( period.end_date )

        // duyệt qua toàn bộ ngày trong khoảng
        for ( let d = new Date( start ); d <= end; d.setDate( d.getDate() + 1 ) ) {
            const dateStr = d.toISOString().split( 'T' )[ 0 ]
            if ( !isWeekend( dateStr ) ) {
                return { is_dayoff: "False" }
            }
        }
    }

    return { is_dayoff: "True" }
}

export default {
    checkDayOff,
}
