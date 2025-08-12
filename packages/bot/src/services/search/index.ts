import { DataSource } from 'typeorm'
import { SearchTimeRequest, SearchTimeResponse, TimeData, TimePeriod, SearchLateRequest, SearchLateResponse, LateData, SearchAttendanceRequest, SearchAttendanceResponse, AttendanceData } from '../../Interface'
import { getInstance } from '../../index'
import logger from '../../utils/logger'

const searchTimeService = async (request: SearchTimeRequest): Promise<SearchTimeResponse> => {
    const appInstance = getInstance()
    if (!appInstance?.AppDataSource) {
        throw new Error('Database connection not available')
    }

    const dataSource: DataSource = appInstance.AppDataSource
    
    try {
        // Build dynamic query conditions
        const dateConditions: string[] = []
        const queryParams: Record<string, any> = { user_email: request.user_email }

        request.time_query.forEach((dateRange: TimePeriod, index: number) => {
            const startDate = dateRange.start_date
            const endDate = dateRange.end_date

            if (!startDate || !endDate) {
                throw new Error(`Date range ${index} missing start_time or end_time`)
            }

            // Convert YYYY-MM-DD to YYYY-MM-DD HH:MM:SS for precise time filtering
            const startDatetimeISO = `${startDate} 00:00:00`
            const endDatetimeISO = `${endDate} 23:59:59`

            // Create unique parameter names for each range
            const startParam = `start_datetime_${index}`
            const endParam = `end_datetime_${index}`

            queryParams[startParam] = startDatetimeISO
            queryParams[endParam] = endDatetimeISO

            const condition = `(checkin_time >= $${Object.keys(queryParams).length - 1} AND checkin_time <= $${Object.keys(queryParams).length})`
            dateConditions.push(condition)
        })

        // Build the complete SQL query
        const whereClause = dateConditions.join(' OR ')
        const sqlQuery = `
            SELECT 
                checkin_time,
                checkout_time
            FROM employee_attendance 
            WHERE 
                user_email = $1
                AND (${whereClause})
            ORDER BY checkin_time ASC
        `

        // Convert queryParams to array in correct order
        const paramValues = [request.user_email]
        request.time_query.forEach((dateRange: TimePeriod, index: number) => {
            const startDatetimeISO = `${dateRange.start_date} 00:00:00`
            const endDatetimeISO = `${dateRange.end_date} 23:59:59`
            paramValues.push(startDatetimeISO, endDatetimeISO)
        })

        logger.info(`Executing search_time query for user: ${request.user_email}`)
        logger.debug(`SQL Query: ${sqlQuery}`)
        logger.debug(`Parameters: ${JSON.stringify(paramValues)}`)

        // Execute query using TypeORM DataSource
        const rawRecords = await dataSource.query(sqlQuery, paramValues)

        // Transform results to match API response format
        const timeDataList: TimeData[] = rawRecords.map((record: any) => {
            const checkinTime = new Date(record.checkin_time)
            const checkoutTime = record.checkout_time ? new Date(record.checkout_time) : null

            // Convert to ISO format with UTC timezone
            const checkinISO = checkinTime.toISOString()
            const checkoutISO = checkoutTime ? checkoutTime.toISOString() : checkinTime.toISOString() // fallback if null

            // Extract date in YYYY-MM-DD format
            const date = checkinISO.substring(0, 10)

            return {
                date,
                checkin_time: checkinISO,
                checkout_time: checkoutISO
            }
        })

        logger.info(`Found ${timeDataList.length} attendance records for user: ${request.user_email}`)

        return {
            data: timeDataList
        }

    } catch (error) {
        logger.error('Error in searchTimeService:', error)
        throw error
    }
}

const searchLateService = async (request: SearchLateRequest): Promise<SearchLateResponse> => {
    const appInstance = getInstance()
    if (!appInstance?.AppDataSource) {
        throw new Error('Database connection not available')
    }

    const dataSource: DataSource = appInstance.AppDataSource
    
    try {
        // Build dynamic query conditions (same logic as searchTime)
        const dateConditions: string[] = []
        const queryParams: Record<string, any> = { user_email: request.user_email }

        request.time_query.forEach((dateRange: TimePeriod, index: number) => {
            const startDate = dateRange.start_date
            const endDate = dateRange.end_date

            if (!startDate || !endDate) {
                throw new Error(`Date range ${index} missing start_time or end_time`)
            }

            // Convert YYYY-MM-DD to YYYY-MM-DD HH:MM:SS for precise time filtering
            const startDatetimeISO = `${startDate} 00:00:00`
            const endDatetimeISO = `${endDate} 23:59:59`

            // Create unique parameter names for each range
            const startParam = `start_datetime_${index}`
            const endParam = `end_datetime_${index}`

            queryParams[startParam] = startDatetimeISO
            queryParams[endParam] = endDatetimeISO

            const condition = `(checkin_time >= $${Object.keys(queryParams).length - 1} AND checkin_time <= $${Object.keys(queryParams).length})`
            dateConditions.push(condition)
        })

        // Build the complete SQL query for search_late
        const whereClause = dateConditions.join(' OR ')
        const sqlQuery = `
            SELECT 
                DATE(checkin_time) as attendance_date,
                is_late
            FROM employee_attendance 
            WHERE 
                user_email = $1
                AND (${whereClause})
            ORDER BY checkin_time ASC
        `

        // Convert queryParams to array in correct order
        const paramValues = [request.user_email]
        request.time_query.forEach((dateRange: TimePeriod, index: number) => {
            const startDatetimeISO = `${dateRange.start_date } 00:00:00`
            const endDatetimeISO = `${dateRange.end_date} 23:59:59`
            paramValues.push(startDatetimeISO, endDatetimeISO)
        })

        logger.info(`Executing search_late query for user: ${request.user_email}`)
        logger.debug(`SQL Query: ${sqlQuery}`)
        logger.debug(`Parameters: ${JSON.stringify(paramValues)}`)

        // Execute query using TypeORM DataSource
        const rawRecords = await dataSource.query(sqlQuery, paramValues)

        // Transform results to match API response format
        const lateDataList: LateData[] = rawRecords.map((record: any) => {
            // attendance_date is already in YYYY-MM-DD format from PostgreSQL DATE()
            const attendanceDate = record.attendance_date
            const isLate = record.is_late

            // Convert date to string format if needed
            let dateString: string
            if (typeof attendanceDate === 'string') {
                dateString = attendanceDate
            } else if (attendanceDate instanceof Date) {
                // Format as YYYY-MM-DD
                dateString = attendanceDate.toISOString().substring(0, 10)
            } else {
                // Fallback formatting
                dateString = new Date(attendanceDate).toISOString().substring(0, 10)
            }

            return {
                date: dateString,
                is_late: Boolean(isLate)
            }
        })

        logger.info(`Found ${lateDataList.length} late attendance records for user: ${request.user_email}`)

        return {
            data: lateDataList
        }

    } catch (error) {
        logger.error('Error in searchLateService:', error)
        throw error
    }
}

const searchAttendanceService = async (request: SearchAttendanceRequest): Promise<SearchAttendanceResponse> => {
    const appInstance = getInstance()
    if (!appInstance?.AppDataSource) {
        throw new Error('Database connection not available')
    }

    const dataSource: DataSource = appInstance.AppDataSource
    
    try {
        // Build dynamic query conditions (same logic as searchTime and searchLate)
        const dateConditions: string[] = []
        const queryParams: Record<string, any> = { user_email: request.user_email }

        request.time_query.forEach((dateRange: TimePeriod, index: number) => {
            const startDate = dateRange.start_date
            const endDate = dateRange.end_date

            if (!startDate || !endDate) {
                throw new Error(`Date range ${index} missing start_time or end_time`)
            }

            // Convert YYYY-MM-DD to YYYY-MM-DD HH:MM:SS for precise time filtering
            const startDatetimeISO = `${startDate} 00:00:00`
            const endDatetimeISO = `${endDate} 23:59:59`

            // Create unique parameter names for each range
            const startParam = `start_datetime_${index}`
            const endParam = `end_datetime_${index}`

            queryParams[startParam] = startDatetimeISO
            queryParams[endParam] = endDatetimeISO

            const condition = `(checkin_time >= $${Object.keys(queryParams).length - 1} AND checkin_time <= $${Object.keys(queryParams).length})`
            dateConditions.push(condition)
        })

        // Build the complete SQL query for search_attendance
        const whereClause = dateConditions.join(' OR ')
        const sqlQuery = `
            SELECT 
                DATE(checkin_time) as attendance_date,
                attendance_count
            FROM employee_attendance 
            WHERE 
                user_email = $1
                AND (${whereClause})
            ORDER BY checkin_time ASC
        `

        // Convert queryParams to array in correct order
        const paramValues = [request.user_email]
        request.time_query.forEach((dateRange: TimePeriod, index: number) => {
            const startDatetimeISO = `${dateRange.start_date} 00:00:00`
            const endDatetimeISO = `${dateRange.end_date} 23:59:59`
            paramValues.push(startDatetimeISO, endDatetimeISO)
        })

        logger.info(`Executing search_attendance query for user: ${request.user_email}`)
        logger.debug(`SQL Query: ${sqlQuery}`)
        logger.debug(`Parameters: ${JSON.stringify(paramValues)}`)

        // Execute query using TypeORM DataSource
        const rawRecords = await dataSource.query(sqlQuery, paramValues)

        // Transform results to match API response format
        const attendanceDataList: AttendanceData[] = rawRecords.map((record: any) => {
            // attendance_date is already in YYYY-MM-DD format from PostgreSQL DATE()
            const attendanceDate = record.attendance_date
            const attendanceCount = record.attendance_count

            // Convert date to string format if needed
            let dateString: string
            if (typeof attendanceDate === 'string') {
                dateString = attendanceDate
            } else if (attendanceDate instanceof Date) {
                // Format as YYYY-MM-DD
                dateString = attendanceDate.toISOString().substring(0, 10)
            } else {
                // Fallback formatting
                dateString = new Date(attendanceDate).toISOString().substring(0, 10)
            }

            // Convert attendance_count to number (float as per Python logic)
            const attendanceFloat = parseFloat(attendanceCount) || 0.0

            return {
                date: dateString,
                attendance: attendanceFloat
            }
        })

        logger.info(`Found ${attendanceDataList.length} attendance records for user: ${request.user_email}`)

        return {
            data: attendanceDataList
        }

    } catch (error) {
        logger.error('Error in searchAttendanceService:', error)
        throw error
    }
}

export default {
    searchTimeService,
    searchLateService,
    searchAttendanceService
}
