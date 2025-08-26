import { getRunningExpressApp } from '../../utils/getRunningExpressApp'
import { InternalError } from '../../errors/internal_error'
import { StatusCodes } from 'http-status-codes'
import { SessionContext, TimePeriod } from '../../Interface'

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

const DEFAULT_FIELDS: ( keyof SessionContext )[] = [
    'topic',
    'prev_question', 
    'prev_answer',
    'user_name',
    'user_email',
    'current_time'
] as const

const _processSessionData = ( data: SessionContext ): SessionContext => {
    const processedData = { ...data }
    
    for ( const field of DEFAULT_FIELDS ) {
        if ( !processedData[ field ] || 
            processedData[ field ] === '' || 
            processedData[ field ] === null || 
            processedData[ field ] === undefined ) {
            
            ( processedData[ field ] as string ) = 'Không có' // Gán giá trị mặc định "Không có" cho trường này
        }
    }
    
    ( processedData as any ).time_query_str = _formatTimeQueryToString( data.time_query )

    return processedData
}

const _formatTimeQueryToString = ( timeQuery: TimePeriod[] | undefined ): string => {
    if ( !timeQuery || timeQuery.length === 0 ) {
        return "Không có"
    }
    
    const lines = timeQuery.map( ( item, index ) => {
        const startDate = item.start_date || 'N/A'
        const endDate = item.end_date || 'N/A'
        
        // Format: "Ngày bắt đầu X: ...\nNgày kết thúc X: ..."
        return `Ngày bắt đầu ${ index + 1 }: ${ startDate }\nNgày kết thúc ${ index + 1 }: ${ endDate }`
    } )
    
    return lines.join( '\n' )
}

const getSession = async ( sessionId: string ) => {
    try {
        const appServer = getRunningExpressApp()
        const redisService = appServer.redisService

        let sessionData: SessionContext

        try {
            const sessionResult = await redisService.getSession( sessionId )
            
            if ( sessionResult && sessionResult.data && typeof sessionResult.data === 'object' ) {
                sessionData = sessionResult.data
            } else {
                sessionData = {
                    topic: undefined,           // Sẽ được điền thành "Không có"
                    prev_question: undefined,   // Sẽ được điền thành "Không có"
                    prev_answer: undefined,     // Sẽ được điền thành "Không có"
                    user_name: undefined,       // Sẽ được điền thành "Không có"
                    user_email: undefined,      // Sẽ được điền thành "Không có"
                    current_time: undefined,    // Sẽ được điền thành "Không có"
                    time_query: undefined       // Sẽ được điền thành "Không có" string
                }
            }
        } catch ( redisError ) {
            console.warn( `Redis error for session '${ sessionId }': ${ redisError }. Using empty session context.` )
            sessionData = sessionData = {
                topic: undefined,           // Sẽ được điền thành "Không có"
                prev_question: undefined,   // Sẽ được điền thành "Không có"
                prev_answer: undefined,     // Sẽ được điền thành "Không có"
                user_name: undefined,       // Sẽ được điền thành "Không có"
                user_email: undefined,      // Sẽ được điền thành "Không có"
                current_time: undefined,    // Sẽ được điền thành "Không có"
                time_query: undefined       // Sẽ được điền thành "Không có" string
            }
        }

        const processedData = _processSessionData( sessionData )

        return {
            session_id: sessionId,
            data: processedData
        }
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
