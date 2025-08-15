import { Request, Response, NextFunction } from 'express'
import { StatusCodes } from 'http-status-codes'
import { SearchTimeRequest, SearchLateRequest, SearchAttendanceRequest } from '../../Interface'
import searchService from '../../services/search'
import { InternalError } from '../../errors/internal_error'
import logger from '../../utils/logger'

const searchTime = async ( req: Request, res: Response, next: NextFunction ) => {
    try {
        if ( !req.body ) {
            throw new InternalError(
                StatusCodes.PRECONDITION_FAILED,
                'Error: searchController.searchTime - body not provided!'
            )
        }

        const request: SearchTimeRequest = req.body

        // Validate user_email
        if ( !request.user_email || request.user_email.trim() === '' ) {
            throw new InternalError(
                StatusCodes.BAD_REQUEST,
                'user_email is required and cannot be empty'
            )
        }

        // Validate time_query
        if ( !request.time_query || !Array.isArray( request.time_query ) 
                || request.time_query.length === 0 ) {
            throw new InternalError(
                StatusCodes.BAD_REQUEST,
                'time_query is required and must be a non-empty array'
            )
        }

        // Validate each time period
        for (let i = 0; i < request.time_query.length; i++) {
            const timePeriod = request.time_query[i]

            // Check if start_date and end_date exist
            if (!timePeriod.start_date || timePeriod.start_date.trim() === '') {
                throw new InternalError(
                    StatusCodes.BAD_REQUEST,
                    `time_query[${i}].start_date is required and cannot be empty`
                )
            }

            if (!timePeriod.end_date || timePeriod.end_date.trim() === '') {
                throw new InternalError(
                    StatusCodes.BAD_REQUEST,
                    `time_query[${i}].end_date is required and cannot be empty`
                )
            }

            // Validate date format (YYYY-MM-DD)
            const dateRegex = /^\d{4}-\d{2}-\d{2}$/
            if (!dateRegex.test(timePeriod.start_date)) {
                throw new InternalError(
                    StatusCodes.BAD_REQUEST,
                    `time_query[${i}].start_date must be in format YYYY-MM-DD`
                )
            }

            if (!dateRegex.test(timePeriod.end_date)) {
                throw new InternalError(
                    StatusCodes.BAD_REQUEST,
                    `time_query[${i}].end_date must be in format YYYY-MM-DD`
                )
            }

            // Parse and validate dates
            let startDateObj: Date
            let endDateObj: Date

            try {
                startDateObj = new Date( timePeriod.start_date )
                endDateObj = new Date( timePeriod.end_date )

                if (isNaN(startDateObj.getTime())) {
                    throw new Error('Invalid start_date')
                }
                if (isNaN(endDateObj.getTime())) {
                    throw new Error('Invalid end_date')
                }
            } catch ( error ) {
                throw new InternalError(
                    StatusCodes.BAD_REQUEST,
                    `Invalid date format in time_query[${i}]: ${ error }`
                )
            }

            // Check if start_date <= end_date
            if (startDateObj > endDateObj) {
                throw new InternalError(
                    StatusCodes.BAD_REQUEST,
                    `time_query[${i}]: start_date cannot be later than end_date`
                )
            }
        }

        logger.info(`Processing search_time request for user: ${ request.user_email }` )
        logger.debug(`Time query ranges: ${JSON.stringify(request.time_query)}`)

        // Call service layer
        const response = await searchService.searchTimeService( request )

        res.json( response )

    } catch ( error ) {
        next( error )
    }
}

const searchViolation = async ( req: Request, res: Response, next: NextFunction ) => {
    try {
        if ( !req.body ) {
            throw new InternalError(
                StatusCodes.PRECONDITION_FAILED,
                'Error: searchController.searchLate - body not provided!'
            )
        }

        const request: SearchLateRequest = req.body

        // Validate user_email
        if ( !request.user_email || request.user_email.trim() === '' ) {
            throw new InternalError(
                StatusCodes.BAD_REQUEST,
                'user_email is required and cannot be empty'
            )
        }

        // Validate time_query
        if ( !request.time_query || !Array.isArray( request.time_query ) 
                || request.time_query.length === 0 ) {
            throw new InternalError(
                StatusCodes.BAD_REQUEST,
                'time_query is required and must be a non-empty array'
            )
        }

        // Validate each time period (same validation logic as searchTime)
        for (let i = 0; i < request.time_query.length; i++) {
            const timePeriod = request.time_query[i]

            // Check if start_date and end_date exist
            if (!timePeriod.start_date || timePeriod.start_date.trim() === '') {
                throw new InternalError(
                    StatusCodes.BAD_REQUEST,
                    `time_query[${i}].start_date is required and cannot be empty`
                )
            }

            if (!timePeriod.end_date || timePeriod.end_date.trim() === '') {
                throw new InternalError(
                    StatusCodes.BAD_REQUEST,
                    `time_query[${i}].end_date is required and cannot be empty`
                )
            }

            // Validate date format (YYYY-MM-DD)
            const dateRegex = /^\d{4}-\d{2}-\d{2}$/
            if (!dateRegex.test(timePeriod.start_date)) {
                throw new InternalError(
                    StatusCodes.BAD_REQUEST,
                    `time_query[${i}].start_date must be in format YYYY-MM-DD`
                )
            }

            if (!dateRegex.test(timePeriod.end_date)) {
                throw new InternalError(
                    StatusCodes.BAD_REQUEST,
                    `time_query[${i}].end_date must be in format YYYY-MM-DD`
                )
            }

            // Parse and validate dates
            let startDateObj: Date
            let endDateObj: Date

            try {
                startDateObj = new Date( timePeriod.start_date )
                endDateObj = new Date( timePeriod.end_date )

                if (isNaN(startDateObj.getTime())) {
                    throw new Error('Invalid start_date')
                }
                if (isNaN(endDateObj.getTime())) {
                    throw new Error('Invalid end_date')
                }
            } catch ( error ) {
                throw new InternalError(
                    StatusCodes.BAD_REQUEST,
                    `Invalid date format in time_query[${i}]: ${ error }`
                )
            }

            if ( startDateObj > endDateObj ) {
                throw new InternalError(
                    StatusCodes.BAD_REQUEST,
                    `time_query[${ i }]: start_date cannot be later than end_date`
                )
            }
        }

        logger.info( `Processing search_late request for user: ${ request.user_email }` )
        logger.debug( `Time query ranges: ${ JSON.stringify( request.time_query ) }` )

        const response = await searchService.searchViolationService( request )

        res.json( response )

    } catch ( error ) {
        next( error )
    }
}

const searchAttendance = async ( req: Request, res: Response, next: NextFunction ) => {
    try {
        if ( !req.body ) {
            throw new InternalError(
                StatusCodes.PRECONDITION_FAILED,
                'Error: searchController.searchAttendance - body not provided!'
            )
        }

        const request: SearchAttendanceRequest = req.body

        // Validate user_email
        if (!request.user_email || request.user_email.trim() === '') {
            throw new InternalError(
                StatusCodes.BAD_REQUEST,
                'user_email is required and cannot be empty'
            )
        }

        // Validate time_query
        if ( !request.time_query || !Array.isArray( request.time_query ) || request.time_query.length === 0 ) {
            throw new InternalError(
                StatusCodes.BAD_REQUEST,
                'time_query is required and must be a non-empty array'
            )
        }

        // Validate each time period (same validation logic as searchTime and searchLate)
        for ( let i = 0; i < request.time_query.length; i++) {
            const timePeriod = request.time_query[i]

            // Check if start_date and end_date exist
            if (!timePeriod.start_date || timePeriod.start_date.trim() === '') {
                throw new InternalError(
                    StatusCodes.BAD_REQUEST,
                    `time_query[${i}].start_date is required and cannot be empty`
                )
            }

            if (!timePeriod.end_date || timePeriod.end_date.trim() === '') {
                throw new InternalError(
                    StatusCodes.BAD_REQUEST,
                    `time_query[${i}].end_date is required and cannot be empty`
                )
            }

            // Validate date format (YYYY-MM-DD)
            const dateRegex = /^\d{4}-\d{2}-\d{2}$/
            if (!dateRegex.test(timePeriod.start_date)) {
                throw new InternalError(
                    StatusCodes.BAD_REQUEST,
                    `time_query[${i}].start_date must be in format YYYY-MM-DD`
                )
            }

            if (!dateRegex.test(timePeriod.end_date)) {
                throw new InternalError(
                    StatusCodes.BAD_REQUEST,
                    `time_query[${i}].end_date must be in format YYYY-MM-DD`
                )
            }

            // Parse and validate dates
            let startDateObj: Date
            let endDateObj: Date

            try {
                startDateObj = new Date( timePeriod.start_date )
                endDateObj = new Date( timePeriod.end_date )

                if (isNaN(startDateObj.getTime())) {
                    throw new Error('Invalid start_date')
                }
                if (isNaN(endDateObj.getTime())) {
                    throw new Error('Invalid end_date')
                }
            } catch ( error ) {
                throw new InternalError(
                    StatusCodes.BAD_REQUEST,
                    `Invalid date format in time_query[${i}]: ${ error }`
                )
            }

            // Check if start_date <= end_date
            if (startDateObj > endDateObj) {
                throw new InternalError(
                    StatusCodes.BAD_REQUEST,
                    `time_query[${i}]: start_date cannot be later than end_date`
                )
            }
        }

        logger.info(`Processing search_attendance request for user: ${ request.user_email }` )
        logger.debug(`Time query ranges: ${ JSON.stringify( request.time_query ) }` )

        // Call service layer
        const response = await searchService.searchAttendanceService(request)

        res.status(StatusCodes.OK).json(response)

    } catch ( error ) {
        next( error )
    }
}

export default {
    searchTime,
    searchViolation,
    searchAttendance
}
