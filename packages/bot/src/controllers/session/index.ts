import { Request, Response, NextFunction } from 'express'
import sessionService from '../../services/session'
import { InternalError } from '../../errors/internal_error'
import { StatusCodes } from 'http-status-codes'
import { UpsertSessionRequest, SessionContext } from '../../Interface'

const upsert_session = async ( req: Request, res: Response, next: NextFunction ) => {
    try {
        if ( !req.body ) {
            throw new InternalError(
                StatusCodes.PRECONDITION_FAILED,
                `Error: sessionController.upsert_session - body not provided!`
            )
        }

        const request: UpsertSessionRequest = req.body

        if ( !request.session_id || request.session_id.trim() === "" ) {
            throw new InternalError(
                StatusCodes.BAD_REQUEST,
                "Session ID is required"
            )
        }

        if ( !request.data ) {
            throw new InternalError(
                StatusCodes.BAD_REQUEST,
                "Session data is required"
            )
        }

        const sessionData = Object.fromEntries(
            Object.entries( request.data ).filter( ( [ _, value ] ) => 
                value !== null && value !== undefined && value !== ""
            )
        )

        if ( Object.keys( sessionData ).length === 0 ) {
            throw new InternalError(
                400,
                "At least one data field must be provided"
            )
        }

        await sessionService.upsertSession( request.session_id, request.data )

         res.json( {
            success: true,
            message: "Session upserted successfully"
        } )

    } catch ( error ) {
        next( error )
    }
}

const get_session = async ( req: Request, res: Response, next: NextFunction ) => {
    try {
        const session_id: string = req.params.session_id || req.query.session_id as string

        if ( !session_id || session_id.trim() === "" ) {
            throw new InternalError(
                400,
                "Session ID is required"
            )
        }

        const response = await sessionService.getSession( session_id )
        res.json( response )
    } catch ( error ) {
        next( error )
    }
}

export default {
    upsert_session,
    get_session,
}
