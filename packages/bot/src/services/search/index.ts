import { DataSource } from 'typeorm'
import { 
    SearchTimeRequest, TimeData, TimePeriod, SearchLateRequest, LateData, SearchAttendanceRequest, 
    AttendanceData 
} from '../../Interface'
import logger from '../../utils/logger'
import { getRunningExpressApp } from '../../utils/getRunningExpressApp'
import { InternalError } from '../../errors/internal_error'
import { StatusCodes } from 'http-status-codes'

const searchTimeService = async ( request: SearchTimeRequest ) => {
    try {
        const appServer = getRunningExpressApp()
        const dataSource: DataSource = appServer.AppDataSource

        const paramValues: any[] = [ request.user_email ] // $1

        const dateConditions: string[] = []
        
        request.time_query.forEach((dateRange, index) => {
            if (!dateRange.start_date || !dateRange.end_date) {
                throw new InternalError(StatusCodes.INTERNAL_SERVER_ERROR, `Date range ${index} missing start_date or end_date`)
            }
            const startPlaceholder = 2 + index * 2   // $2, $4, ...
            const endPlaceholder = 3 + index * 2     // $3, $5, ...
            dateConditions.push(`(a.date >= $${startPlaceholder} AND a.date <= $${endPlaceholder})`)
            paramValues.push(`${dateRange.start_date}`, `${dateRange.end_date}`)
        })

        let whereClause = dateConditions.length ? dateConditions.join(' OR ') : 'TRUE'

        const sqlQuery = `
        SELECT
            TO_CHAR(a.date, 'YYYY-MM-DD') as date,
            TO_CHAR(a.raw_check_in, 'HH24:MI') as raw_check_in,
            TO_CHAR(a.raw_check_out, 'HH24:MI') as raw_check_out
        FROM attendance a
        JOIN employees e ON a.employee_id = e.employee_id
        WHERE
            e.email = $1
            AND (${ whereClause })
        ORDER BY a.date ASC
        `

        const rawRecords = await dataSource.query( sqlQuery, paramValues )

        const timeDataList: TimeData[] = rawRecords.map( ( record: any ) => {
            return {
                date: record.date,
                checkin_time: record.raw_check_in,
                checkout_time: record.raw_check_out,
            }
        } )

        logger.info( `Found ${ timeDataList.length } attendance records for user: ${ request.user_email }` )

        return {
            data: timeDataList
        }

    } catch ( error ) {
        logger.error( 'Error in searchTimeService:', error )
        throw error
    }
}

const searchViolationService = async ( request: SearchLateRequest ) => {
    try {
        const appServer = getRunningExpressApp()
        const dataSource: DataSource = appServer.AppDataSource

        const paramValues: any[] = [ request.user_email ] // $1

        const dateConditions: string[] = []
        
        request.time_query.forEach((dateRange, index) => {
            if (!dateRange.start_date || !dateRange.end_date) {
                throw new InternalError(StatusCodes.INTERNAL_SERVER_ERROR, `Date range ${index} missing start_date or end_date`)
            }
            const startPlaceholder = 2 + index * 2   // $2, $4, ...
            const endPlaceholder = 3 + index * 2     // $3, $5, ...
            dateConditions.push(`(a.date >= $${startPlaceholder} AND a.date <= $${endPlaceholder})`)
            paramValues.push(`${dateRange.start_date}`, `${dateRange.end_date}`)
        })

        let whereClause = dateConditions.length ? dateConditions.join(' OR ') : 'TRUE'

        const sqlQuery = `
        SELECT
            TO_CHAR(a.date, 'YYYY-MM-DD') as date,
            a.late_minutes as checkin_violation,
            a.early_minutes as checkin_violation,
            a.penalty_hours as deduction_hours 
        FROM attendance a
        JOIN employees e ON a.employee_id = e.employee_id
        WHERE
            e.email = $1
            AND (${ whereClause })
        ORDER BY a.date ASC
        `

        logger.info( `Executing search_late query for user: ${ request.user_email }` )
        logger.debug( `SQL Query: ${ sqlQuery }` )
        logger.debug( `Parameters: ${ JSON.stringify( paramValues ) }` )

        const rawRecords = await dataSource.query( sqlQuery, paramValues )

        const violationDataList: LateData[] = rawRecords.map( ( record: any ) => {
            let total_violation: number = record.checkin_violation + record.checkout_violation
            
            return {
                date: record.date,
                checkin_violation: record.checkin_violation,
                checkout_violation: record.checkout_violation,
                total_violation: total_violation,
                deduction_hours: record.deduction_hours,
            }
        } )

        logger.info( `Found ${ violationDataList.length } attendance records for user: ${ request.user_email }` )

        return {
            data: violationDataList
        }

    } catch ( error ) {
        logger.error( 'Error in searchLateService:', error )
        throw error
    }
}

const searchAttendanceService = async ( request: SearchAttendanceRequest ) => {
    try {
        const appServer = getRunningExpressApp()
        const dataSource: DataSource = appServer.AppDataSource

        const paramValues: any[] = [ request.user_email ] // $1
        const dateConditions: string[] = []
        
        request.time_query.forEach((dateRange, index) => {
            if (!dateRange.start_date || !dateRange.end_date) {
                throw new InternalError(StatusCodes.INTERNAL_SERVER_ERROR, `Date range ${index} missing start_date or end_date`)
            }
            const startPlaceholder = 2 + index * 2   // $2, $4, ...
            const endPlaceholder = 3 + index * 2     // $3, $5, ...
            dateConditions.push(`(a.date >= $${startPlaceholder} AND a.date <= $${endPlaceholder})`)
            paramValues.push(`${dateRange.start_date}`, `${dateRange.end_date}`)
        })

        let whereClause = dateConditions.length ? dateConditions.join(' OR ') : 'TRUE'

        const sqlQuery = `
        SELECT
            TO_CHAR(a.date, 'YYYY-MM-DD') as date,
            a.penalty_hours as deduction_hours 
        FROM attendance a
        JOIN employees e ON a.employee_id = e.employee_id
        WHERE
            e.email = $1
            AND (${ whereClause })
        ORDER BY a.date ASC
        `

        logger.info( `Executing search_attendance query for user: ${ request.user_email }` )
        logger.debug( `SQL Query: ${ sqlQuery }` )
        logger.debug( `Parameters: ${ JSON.stringify( paramValues ) }` )

        const rawRecords = await dataSource.query( sqlQuery, paramValues )

        const attendanceDataList: AttendanceData[] = rawRecords.map( ( record: any ) => {
            const actualHours = 8 - record.deduction_hours
            const workingDays = actualHours / 8
            
            return {
                date: record.date,
                deductionHours: record.deduction_hours,
                actualHours: actualHours,
                workingDays: workingDays,
            }
        } )

        logger.info( `Found ${ attendanceDataList.length } attendance records for user: ${ request.user_email }` )

        return {
            data: attendanceDataList
        }

    } catch ( error ) {
        logger.error( 'Error in searchAttendanceService:', error )
        throw error
    }
}

export default {
    searchTimeService,
    searchViolationService,
    searchAttendanceService
}
