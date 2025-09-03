import fs from 'fs'
import { processDailyAttendance } from './utils'

const filePath = '../sample-data/data.json'

function _getRawData( filePath, email ) {
    const rawData = fs.readFileSync( filePath, 'utf-8' )
    const jsonData = JSON.parse( rawData )

    const events = jsonData[ 'return_events' ].filter( ev => ev.email === email )

    const groupedByDate = {}
    events.forEach( ev => {
        const [ date, time ] = ev.time.split( ' ' )
        if ( !groupedByDate[ date ] ) {
            groupedByDate[ date ] = []
        }
        groupedByDate[ date ].push( time )
    } )

    return Object.entries( groupedByDate ).map( ( [ date, times ] ) => {
        times.sort( ( a, b ) => a.localeCompare( b ) )

        let checkinTime = null
        let checkoutTime = null

        if ( times.length > 0 ) {
            checkinTime = times[ 0 ] // thời điểm đầu tiên trong ngày
        }
        if ( times.length > 1 ) {
            checkoutTime = times[ times.length - 1 ] // thời điểm cuối cùng trong ngày
        }

        return {
            date,
            checkinTime,
            checkoutTime,
            leaveMorning: false,
            leaveAfternoon: false
        }
    } )
}

async function _processUserData( userEmail ) {
    console.log( `\n🔄 Processing data for: ${ userEmail }` )
    console.log( '=' .repeat( 80 ) )
    
    const rawData = _getRawData( filePath, userEmail )
    
    if ( rawData.length === 0 ) {
        console.log( `⚠️  No data found for ${ userName }` )
        return
    }

    let freeAllowance = 5
    
    for ( let idx = 0; idx < rawData.length; idx++ ) {
        const record = rawData[ idx ]
        const dailyData = {
            date: record.date,
            checkIn: record.checkinTime,
            checkOut: record.checkoutTime,
            isLeaveMorning: record.leaveMorning,
            isLeaveAfternoon: record.leaveAfternoon
        }
        const processedRecord = processDailyAttendance( dailyData, freeAllowance )
        
        console.log(
            `${ idx + 1 }. Date: ${ record.date } | ` +
            `CheckIn: ${ record.checkinTime } | CheckOut: ${ record.checkoutTime } | ` +
            `Violation: ${ processedRecord.violationMinutes } mins | ` +
            `Deduct: ${ processedRecord.deductionHours } hrs | ` +
            `Late morning: ${ processedRecord.isLateMorning ? 'Yes' : 'No' } | ` +
            `Early afternoon: ${ processedRecord.isEarlyAfternoon ? 'Yes' : 'No' } | ` +
            `Free allowance: ${ freeAllowance } → ${ processedRecord.freeAllowance }`
        )
        
        // Cập nhật free allowance cho ngày tiếp theo
        freeAllowance = processedRecord.freeAllowance
    }
    
    console.log(`✅ Completed processing ${rawData.length} records for ${userEmail}`)
}

_processUserData( 'kienchickenz@gmail.com' )
