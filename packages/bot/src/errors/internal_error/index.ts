export class InternalError extends Error {
    statusCode: number
    constructor( statusCode: number, message: string ) {
        super( message )
        this.statusCode = statusCode
        // Capture stack trace of error from anywhere in the application
        Error.captureStackTrace( this, this.constructor )
    }
}
