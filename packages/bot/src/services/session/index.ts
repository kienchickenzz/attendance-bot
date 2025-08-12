import { getRunningExpressApp } from '../../utils/getRunningExpressApp'
import { InternalError } from '../../errors/internal_error'
import { StatusCodes } from 'http-status-codes'
import { SessionContext } from '../../Interface'

const upsertSession = async ( sessionId: string, data: SessionContext ) => {
    try {
        const appServer = getRunningExpressApp()
        const redisService = appServer.redisService

        redisService.upsertSession( sessionId, data )
    } catch ( error ) {
        throw new InternalError(
            StatusCodes.INTERNAL_SERVER_ERROR,
            `Error: sessionServices.upsertSession - ${ error }`
        )
    }
}

const getSession = async ( sessionId: string ) => {
    try {
        const appServer = getRunningExpressApp()
        const redisService = appServer.redisService

        return redisService.getSession( sessionId )
    } catch ( error ) {
        throw new InternalError(
            StatusCodes.INTERNAL_SERVER_ERROR,
            `Error: sessionServices.getSession - ${ error }`
        )
    }
}

export default {
    upsertSession,
    getSession,
}
