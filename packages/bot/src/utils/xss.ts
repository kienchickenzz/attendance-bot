export function getAllowedCorsOrigins(): string {
    // Expects FQDN separated by commas, otherwise nothing or * for all.
    return process.env.CORS_ORIGINS ?? '*'
}

export function getCorsOptions(): any {
    const corsOptions = {
        origin: function ( origin: string | undefined, callback: ( err: Error | null, allow?: boolean ) => void ) {
            const allowedOrigins = getAllowedCorsOrigins()
            if ( !origin || allowedOrigins == '*' || allowedOrigins.indexOf( origin ) !== -1 ) {
                callback( null, true )
            } else {
                callback( null, false )
            }
        }
    }
    return corsOptions
}
