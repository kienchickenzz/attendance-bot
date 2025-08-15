import {
    SHIFTCONFIG,
    RULES,
} from '../constants'

function _toMinutes( timeStr ) {
    if ( !timeStr ) return null
    const [ h, m ] = timeStr.split( ":" ).map( Number )
    return h * 60 + m
}

function _diffMinutes( later, earlier ) {
    return Math.max( 0, _toMinutes( later ) - _toMinutes( earlier ) )
}

function _getShiftType( isLeaveMorning, isLeaveAfternoon ) {
    if ( isLeaveMorning && isLeaveAfternoon ) return "leaveFullDay"
    if ( isLeaveMorning ) return "leaveMorning"
    if ( isLeaveAfternoon ) return "leaveAfternoon"
    return "normal"
}

function _formatTime( date ) {
    const hours = String( date.getHours() ).padStart( 2, "0" )
    const minutes = String( date.getMinutes() ).padStart( 2, "0" )
    return `${ hours }:${ minutes }`
}

function _formatDate( date ) {
    const year = date.getFullYear()
    const month = String( date.getMonth() + 1 ).padStart( 2, "0" )
    const day = String( date.getDate() ).padStart( 2, "0" )
    return `${ year }-${ month }-${ day }`
}

function processDailyAttendance( dailyRecord, freeAllowance = 0 ) {
    const { checkIn, checkOut, isLeaveMorning, isLeaveAfternoon } = dailyRecord

    const shiftType = _getShiftType( isLeaveMorning, isLeaveAfternoon )

    if ( shiftType === "leaveFullDay" ) {
        return {
            morningViolation: 0,
            afternoonViolation: 0,
            violationMinutes: 0,
            deductionHours: 0,
            freeAllowance: freeAllowance,
            isLateMorning: false,
            isEarlyAfternoon: false,
        }
    }

    const refIn = SHIFTCONFIG[ shiftType ].checkInReference
    const refOut = SHIFTCONFIG[ shiftType ].checkOutReference
    
    let violationMinutes = 0
    let morningViolation = 0
    let afternoonViolation = 0 

    if ( checkIn && refIn ) {
        morningViolation += _diffMinutes( checkIn, refIn )
        violationMinutes += morningViolation
    }

    if ( checkOut && refOut ) {
        afternoonViolation += _diffMinutes( refOut, checkOut )
        violationMinutes += afternoonViolation
    }

    const isLateMorning = morningViolation > 0
    const isEarlyAfternoon = afternoonViolation > 0

    const rule = RULES.find( ( r ) => violationMinutes >= r.min && violationMinutes <= r.max )
    
    if ( !rule ) {
        return {
            morningViolation: morningViolation,
            afternoonViolation: afternoonViolation,
            violationMinutes: violationMinutes,
            deductionHours: 0,
            freeAllowance: freeAllowance,
            isLateMorning: isLateMorning,
            isEarlyAfternoon: isEarlyAfternoon,
        }
    }

    let deductionHours = rule.deduct( freeAllowance )
    let updatedFreeAllowance = freeAllowance

    if ( rule.min === 1 && rule.max === 15 && freeAllowance > 0 ) {
        updatedFreeAllowance = freeAllowance - 1
    }

    return {
        morningViolation: morningViolation,
        afternoonViolation: afternoonViolation,
        violationMinutes: violationMinutes,
        deductionHours: deductionHours,
        freeAllowance: updatedFreeAllowance,
        isLateMorning: isLateMorning,
        isEarlyAfternoon: isEarlyAfternoon,
    }
}

function generateAttendanceData(
    startDate,
    endDate,
    userEmail = "ndkien.ts@cmc.com.vn",
    userName = "Nguyen Duc Kien"
) {
    const attendanceRecords = []
    let currentDate = new Date( startDate )
    const endDt = new Date( endDate )

    while ( currentDate <= endDt ) {
        if ( currentDate.getDay() >= 1 && currentDate.getDay() <= 5 ) {
            // Random check-in around 8:15
            const checkinBase = new Date( currentDate )
            checkinBase.setHours( 8, 15, 0, 0 )
            const checkinVariation = Math.floor( Math.random() * ( 30 + 15 + 1 ) ) - 15 // -15 to +30 min
            const checkinTime = new Date( checkinBase.getTime() + checkinVariation * 60000 )

            // Random checkout around 17:30
            const checkoutBase = new Date( currentDate )
            checkoutBase.setHours( 17, 30, 0, 0 )
            const checkoutVariation = Math.floor( Math.random() * ( 45 + 20 + 1 ) ) - 20 // -20 to +45 min
            const checkoutTime = new Date( checkoutBase.getTime() + checkoutVariation * 60000 )

            attendanceRecords.push( {
                date: _formatDate( currentDate ),
                userEmail: userEmail,
                userName: userName,
                checkinTime: _formatTime( checkinTime ),
                checkoutTime: _formatTime( checkoutTime ),
                leaveMorning: false,
                leaveAfternoon: false
            } )
        }
        // Move to next day
        currentDate.setDate( currentDate.getDate() + 1 )
    }

    return attendanceRecords
}

export { 
    generateAttendanceData,
    processDailyAttendance,
}
