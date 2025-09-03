import fs from 'fs'
import { processDailyAttendance } from './utils'
import { 
    insertAttendanceData,
    createEmployeeAttendanceTable,
} from './utils/database'
import { processedDataSource } from './DataSource'

const filePath = '../data.json'

function _getRawData( filePath, fullName, email ) {
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

async function initializeDatabase() {
    try {
        await processedDataSource.initialize()
        console.log('✅ Database connected')
        
        console.log('🔧 Creating employee attendance table...')
        await createEmployeeAttendanceTable(processedDataSource)
        console.log('✅ Employee attendance table ready')
    } catch (error) {
        console.error('❌ Error setting up database:', error)
        throw error
    }
}

async function closeDatabase() {
    try {
        await processedDataSource.destroy()
        console.log('✅ Database connection closed')
    } catch (error) {
        console.error('❌ Error closing database connection:', error)
        throw error
    }
}

async function _processUserData( userEmail, userName ) {
    console.log( `\n🔄 Processing data for: ${ userName } (${ userEmail })` )
    console.log( '=' .repeat( 80 ) )
    
    const rawData = _getRawData(filePath, userName, userEmail)
    
    if (rawData.length === 0) {
        console.log(`⚠️  No data found for ${userName}`)
        return
    }

    let freeAllowance = 5
    
    for ( let idx = 0; idx < rawData.length; idx++ ) {
        const record = rawData[idx]
        const dailyData = {
            date: record.date,
            checkIn: record.checkinTime,
            checkOut: record.checkoutTime,
            isLeaveMorning: record.leaveMorning,
            isLeaveAfternoon: record.leaveAfternoon
        }
        const processedRecord = processDailyAttendance( dailyData, freeAllowance )
        
        // Prepare combined record for database insertion
        const dbRecord = {
            userEmail: userEmail,
            date: record.date,
            leaveMorning: record.leaveMorning,
            leaveAfternoon: record.leaveAfternoon,
            checkinTime: record.checkinTime,
            checkoutTime: record.checkoutTime,
            freeAllowance: processedRecord.freeAllowance,
            morningViolation: processedRecord.morningViolation,
            afternoonViolation: processedRecord.afternoonViolation,
            violationMinutes: processedRecord.violationMinutes,
            deductionHours: processedRecord.deductionHours
        }

        // Insert into database
        try {
            await insertAttendanceData( processedDataSource, dbRecord )
        } catch (error) {
            console.error(`Error inserting data for ${record.date}:`, error)
            continue
        }
        
        console.log(
            `${ idx + 1 }. Date: ${ record.date } | ` +
            `CheckIn: ${ record.checkinTime } | CheckOut: ${ record.checkoutTime } | ` +
            `Violation: ${ processedRecord.violationMinutes } mins | ` +
            `Deduct: ${ processedRecord.deductionHours } hrs | ` +
            `Late morning: ${ processedRecord.isLateMorning ? 'Yes' : 'No' } | ` +
            `Early afternoon: ${ processedRecord.isEarlyAfternoon ? 'Yes' : 'No' } | ` +
            `Free allowance: ${ freeAllowance } → ${ processedRecord.freeAllowance } | 💾 Saved to DB`
        )
        
        // Cập nhật free allowance cho ngày tiếp theo
        freeAllowance = processedRecord.freeAllowance
    }
    
    console.log(`✅ Completed processing ${rawData.length} records for ${userName}`)
}

async function main() {
    const userEmails = [
        'ndkien.ts@cmc.com.vn', 'ndgiang1@cmc.com.vn', 'pthieu5@cmc.com.vn',
        'dmdat@cmc.com.vn', 'qthung@cmc.com.vn',
    ]
    const userNames = [
        'NGUYỄN ĐỨC KIÊN', 'NGUYỄN ĐÌNH GIANG', 'PHẠM TRUNG HIẾU',
        'DOÃN MINH ĐẠT', 'Quản Thị Hưng',
    ]

    if (userEmails.length !== userNames.length) {
        console.error('❌ Error: userEmails and userNames arrays must have the same length')
        return
    }

    console.log(`📋 Processing ${userEmails.length} users:`)
    userEmails.forEach((email, idx) => {
        console.log(`  ${idx + 1}. ${userNames[idx]} (${email})`)
    })

    try {
        await initializeDatabase()
    } catch (error) {
        return
    }

    // Process each user
    for (let i = 0; i < userEmails.length; i++) {
        try {
            await _processUserData(userEmails[i], userNames[i])
        } catch (error) {
            console.error(`❌ Error processing user ${userNames[i]}:`, error)
            continue
        }
    }
    
    await closeDatabase()
}

main().catch( console.error )
