import { createLogger, transports, format } from 'winston'
import { NextFunction, Request, Response } from 'express'

const { combine, timestamp, printf, errors } = format

console.log( 'Current LOG_LEVEL:', process.env.LOG_LEVEL )

const logger = createLogger( {
    format: combine(
        timestamp( { format: 'YYYY-MM-DD HH:mm:ss' } ),
        format.json(),
        printf( ( { level, message, timestamp, stack } ) => {
            const text = `${ timestamp } [${ level.toUpperCase() }]: ${ message }`
            return stack ? text + '\n' + stack : text
        } ),
        errors( { stack: true } )
    ),
    defaultMeta: {
        package: 'server'
    },
    exitOnError: false,
    transports: [
        new transports.Console( {
            level: process.env.LOG_LEVEL ?? 'info'
        } ),
    ],
    exceptionHandlers: [
        new transports.Console()
    ],
    rejectionHandlers: [
        new transports.Console()
    ]
} )

export function expressRequestLogger( req: Request, res: Response, next: NextFunction ): void {
    const unwantedLogURLs = [ 
        '/api/v1/node-icon/', 
        '/api/v1/components-credentials-icon/',
        '/api/v1/ping',
    ]

    if ( /\/api\//i.test( req.url ) && !unwantedLogURLs.some( ( url ) => new RegExp( url, 'i' ).test( req.url ) ) ) {
        // Create a sanitized copy of the request body
        const sanitizedBody = { ...req.body }
        if ( sanitizedBody.password ) {
            sanitizedBody.password = '********'
        }

        const fileLogger = createLogger( {
            format: combine( timestamp( { format: 'YYYY-MM-DD HH:mm:ss' } ), format.json(), errors( { stack: true } ) ),
            defaultMeta: {
                package: 'server',
                request: {
                    method: req.method,
                    url: req.url,
                    body: sanitizedBody, // Use sanitized body instead of raw body
                    query: req.query,
                    params: req.params,
                    headers: req.headers
                }
            },
            transports: [
                new transports.Console( {
                    level: process.env.LOG_LEVEL ?? 'info'
                } )
            ]
        } )

        const getRequestEmoji = ( method: string ) => {
            const requetsEmojis: Record< string, string > = {
                GET: '⬇️',
                POST: '⬆️',
                PUT: '🖊',
                DELETE: '❌',
                OPTION: '🔗'
            }

            return requetsEmojis[method] || '?'
        }

        if ( req.method !== 'GET' ) {
            fileLogger.info( `${ getRequestEmoji( req.method ) } ${ req.method } ${ req.url }` )
            logger.info( `${ getRequestEmoji( req.method ) } ${ req.method } ${ req.url }` )
        } else {
            fileLogger.http( `${getRequestEmoji( req.method ) } ${ req.method } ${ req.url }` )
        }
    }

    next()
}

export default logger
