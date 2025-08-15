import { 
    generateAttendanceData, 
    processDailyAttendance, 
} from './utils'
import { 
    insertAttendanceData,
    createEmployeeAttendanceTable,
} from './utils/database'
import { processedDataSource } from './DataSource'

async function main() {
    console.log( 'Starting attendance data generation...' )

    // Parse command line arguments
    const args = process.argv.slice(2)
    const startDate = args[0] || '2025-06-01'
    const endDate = args[1] || '2025-08-31'
    const userEmail = args[2] || 'ndkien.ts@cmc.com.vn'

    console.log(`Parameters: startDate=${startDate}, endDate=${endDate}, userEmail=${userEmail}`)

    let freeAllowance = 5 // Nums of ≤ 15 minutes are exempted

    // Initialize database connection
    try {
        await processedDataSource.initialize()
        console.log('✅ Database connected')
        
        // Create employee attendance table if not exists
        console.log('🔧 Creating employee attendance table...')
        await createEmployeeAttendanceTable(processedDataSource)
        console.log('✅ Employee attendance table ready')
        
    } catch (error) {
        console.error('❌ Error setting up database:', error)
        return
    }

    const attendanceRecords = generateAttendanceData(
        startDate,
        endDate,
        'ndkien.ts@cmc.com.vn',
        'Nguyen Duc Kien'
    )

    console.log( `Generated ${ attendanceRecords.length } attendance records` )
    console.log( 'Sample record:', JSON.stringify( attendanceRecords[ 0 ], null, 2 ) )

    console.log( '\nDaily attendance processing:' )
    console.log( '=' .repeat( 100 ) )

    for ( let idx = 0; idx < attendanceRecords.length; idx++ ) {
        const record = attendanceRecords[idx]
        
        // Lưu trữ freeAllowance trước khi xử lý để so sánh
        const previousFreeAllowance = freeAllowance
        
        // Chuẩn bị dữ liệu cho ngày hiện tại
        const dailyData = {
            date: record.date,
            checkIn: record.checkinTime,
            checkOut: record.checkoutTime,
            isLeaveMorning: record.leaveMorning,
            isLeaveAfternoon: record.leaveAfternoon
        }

        // Xử lý chấm công cho ngày này
        const result = processDailyAttendance( dailyData, freeAllowance )

        // Insert vào database
        try {
            await insertAttendanceData(processedDataSource, record, result, userEmail )
        } catch (error) {
            console.error(`Error inserting data for ${record.date}:`, error)
            continue
        }

        const freeAllowanceUsed = previousFreeAllowance > result.freeAllowance
        console.log(
            `${ idx + 1 }. Date: ${ record.date } | ` +
            `CheckIn: ${ record.checkinTime } | CheckOut: ${ record.checkoutTime } | ` +
            `Violation: ${ result.violationMinutes } mins | ` +
            `Deduct: ${ result.deductionHours } hrs | ` +
            `Late morning: ${ result.isLateMorning ? 'Yes' : 'No' } | ` +
            `Early afternoon: ${ result.isEarlyAfternoon ? 'Yes' : 'No' } | ` +
            `Free allowance: ${ previousFreeAllowance } → ${ result.freeAllowance }` +
            ( freeAllowanceUsed ? ' (used)' : '' ) + ' | 💾 Saved to DB'
        )

        // Cập nhật free allowance cho ngày tiếp theo
        freeAllowance = result.freeAllowance
    }

    console.log( '=' .repeat( 100 ) )
    
    try {
        await processedDataSource.destroy()
        console.log('✅ Database connection closed')
    } catch (error) {
        console.error('❌ Error closing database connection:', error)
    }
}

main().catch( console.error )
