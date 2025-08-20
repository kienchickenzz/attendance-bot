import { DataSource } from 'typeorm'
import { SearchTimeRequest, SearchTimeResponse, TimeData, TimePeriod, SearchLateRequest, SearchLateResponse, LateData, SearchAttendanceRequest, SearchAttendanceResponse, AttendanceData } from '../../Interface'
import logger from '../../utils/logger'
import { getRunningExpressApp } from '../../utils/getRunningExpressApp'
import { InternalError } from '../../errors/internal_error'
import { StatusCodes } from 'http-status-codes'

const searchTimeService = async ( request: SearchTimeRequest ): Promise< SearchTimeResponse > => {
    try {
        const appServer = getRunningExpressApp()
        const dataSource: DataSource = appServer.AppDataSource
        
        // Build dynamic query conditions
        const dateConditions: string[] = []
        const queryParams: Record< string, any > = { user_email: request.user_email }

        request.time_query.forEach( ( dateRange: TimePeriod, index: number ) => {
            const startDate = dateRange.start_date
            const endDate = dateRange.end_date

            if ( !startDate || !endDate ) {
                throw new InternalError( 
                    StatusCodes.INTERNAL_SERVER_ERROR,
                    `Date range ${ index } missing start_date or end_date` 
                )
            }

            // Create unique parameter names for each range
            const startParam = `start_datetime_${ index }`
            const endParam = `end_datetime_${ index }`

            queryParams[ startParam ] = startDate
            queryParams[ endParam ] = endDate

            const condition = `(date >= $${ Object.keys( queryParams ).length - 1 } AND date <= $${ Object.keys( queryParams ).length })`
            logger.debug( condition )
            dateConditions.push( condition )
        } )

        // Build the complete SQL query
        const whereClause = dateConditions.join( ' OR ' )
        const sqlQuery = `
            SELECT 
                TO_CHAR(date, 'YYYY-MM-DD') as date,
                checkin_time,
                checkout_time
            FROM employee_attendance 
            WHERE 
                user_email = $1
                AND (${ whereClause })
            ORDER BY date ASC
        `

        // Convert queryParams to array in correct order
        const paramValues = [ request.user_email ]
        request.time_query.forEach( ( dateRange: TimePeriod, index: number) => {
            const startDatetime = `${ dateRange.start_date }`
            const endDatetime = `${ dateRange.end_date }`
            paramValues.push( startDatetime, endDatetime )
        } )

        logger.info( `Executing search_time query for user: ${ request.user_email }` )
        logger.debug( `SQL Query: ${ sqlQuery }` )
        logger.debug( `Parameters: ${ JSON.stringify( paramValues ) }` )

        const rawRecords = await dataSource.query( sqlQuery, paramValues )

        const timeDataList: TimeData[] = rawRecords.map( ( record: any ) => {
            return {
                date: record.date,
                checkin_time: record.checkin_time,
                checkout_time: record.checkout_time,
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

const searchViolationService = async ( request: SearchLateRequest ): Promise< SearchLateResponse > => {
    try {
        const appServer = getRunningExpressApp()
        const dataSource: DataSource = appServer.AppDataSource

        // Build dynamic query conditions (same logic as searchTime)
        const dateConditions: string[] = []
        const queryParams: Record< string, any > = { user_email: request.user_email }

        request.time_query.forEach( ( dateRange: TimePeriod, index: number ) => {
            const startDate = dateRange.start_date
            const endDate = dateRange.end_date

            if ( !startDate || !endDate ) {
                throw new Error( `Date range ${ index } missing start_date or end_date` )
            }

            // Create unique parameter names for each range
            const startParam = `start_datetime_${ index }`
            const endParam = `end_datetime_${ index }`

            queryParams[ startParam ] = startDate
            queryParams[ endParam ] = endDate

            const condition = `(date >= $${ Object.keys( queryParams ).length - 1 } AND date <= $${ Object.keys( queryParams ).length })`
            dateConditions.push( condition )
        } )

        const whereClause = dateConditions.join(' OR ')
        const sqlQuery = `
            SELECT 
                TO_CHAR(date, 'YYYY-MM-DD') as date,
                checkin_violation,
                checkout_violation,
                total_violation,
                deduction_hours
            FROM employee_attendance 
            WHERE 
                user_email = $1
                AND (${ whereClause })
            ORDER BY date ASC
        `

        // Convert queryParams to array in correct order
        const paramValues = [ request.user_email ]
        request.time_query.forEach( ( dateRange: TimePeriod, index: number ) => {
            const startDatetime = `${ dateRange.start_date }`
            const endDatetime = `${ dateRange.end_date }`
            paramValues.push( startDatetime, endDatetime )
        } )

        logger.info( `Executing search_late query for user: ${ request.user_email }` )
        logger.debug( `SQL Query: ${ sqlQuery }` )
        logger.debug( `Parameters: ${ JSON.stringify( paramValues ) }` )

        const rawRecords = await dataSource.query( sqlQuery, paramValues )

        const violationDataList: LateData[] = rawRecords.map( ( record: any ) => {
            return {
                date: record.date,
                checkin_violation: record.checkin_violation,
                checkout_violation: record.checkout_violation,
                total_violation: record.total_violation,
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

const searchAttendanceService = async ( request: SearchAttendanceRequest ): Promise< SearchAttendanceResponse > => {
    try {
        const appServer = getRunningExpressApp()
        const dataSource: DataSource = appServer.AppDataSource

        const dateConditions: string[] = []
        const queryParams: Record< string, any > = { user_email: request.user_email }

        request.time_query.forEach( ( dateRange: TimePeriod, index: number ) => {
            const startDate = dateRange.start_date
            const endDate = dateRange.end_date

            if ( !startDate || !endDate ) {
                throw new Error( `Date range ${ index } missing start_date or end_date` )
            }

            // Create unique parameter names for each range
            const startParam = `start_datetime_${ index }`
            const endParam = `end_datetime_${ index }`

            queryParams[ startParam ] = startDate
            queryParams[ endParam ] = endDate

            const condition = `(date >= $${ Object.keys( queryParams ).length - 1 } AND date <= $${ Object.keys( queryParams ).length })`
            dateConditions.push( condition )
        } )

        const whereClause = dateConditions.join(' OR ')
        const sqlQuery = `
            SELECT 
                TO_CHAR(date, 'YYYY-MM-DD') as date,
                deduction_hours
            FROM employee_attendance 
            WHERE 
                user_email = $1
                AND (${ whereClause })
            ORDER BY date ASC
        `

        // Convert queryParams to array in correct order
        const paramValues = [ request.user_email ]
        request.time_query.forEach( ( dateRange: TimePeriod, index: number ) => {
            const startDatetime = `${ dateRange.start_date }`
            const endDatetime = `${ dateRange.end_date }`
            paramValues.push( startDatetime, endDatetime )
        } )

        logger.info( `Executing search_attendance query for user: ${ request.user_email }` )
        logger.debug( `SQL Query: ${ sqlQuery }` )
        logger.debug( `Parameters: ${ JSON.stringify( paramValues ) }` )

        // TODO: Sửa lại cách endpoint trả về để trả thẳng JSON thay vì qua 1 interface.
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
