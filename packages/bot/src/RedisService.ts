import Redis from 'ioredis'
import { TimePeriod, SessionContext } from './Interface'
import { InternalError } from './errors/internal_error'

export class RedisService {
    private redisClient: Redis | null = null

    constructor() {
        this.redisClient = new Redis( {
            host: process.env.REDIS_HOST || 'localhost',
            port: parseInt( process.env.REDIS_PORT || '6379' ),
            username: process.env.REDIS_USERNAME || undefined,
            password: process.env.REDIS_PASSWORD || undefined,
            tls:
                process.env.REDIS_TLS === 'true'
                    ? {
                        cert: process.env.REDIS_CERT ? Buffer.from( process.env.REDIS_CERT, 'base64' ) : undefined,
                        key: process.env.REDIS_KEY ? Buffer.from( process.env.REDIS_KEY, 'base64' ) : undefined,
                        ca: process.env.REDIS_CA ? Buffer.from( process.env.REDIS_CA, 'base64' ) : undefined
                    }
                    : undefined,
            keepAlive:
                process.env.REDIS_KEEP_ALIVE && !isNaN( parseInt( process.env.REDIS_KEEP_ALIVE, 10 ) )
                    ? parseInt( process.env.REDIS_KEEP_ALIVE, 10 )
                    : undefined
        } )
    }

    async upsertSession(
        sessionId: string,
        data: SessionContext
    ): Promise< void > {
        try {
            if ( this.redisClient ) {
                const ttl = parseInt( process.env.REDIS_TTL || '3600' )

                // Check if session exists (equivalent to redis.exists in Python)
                const exists = await this.redisClient.exists(sessionId)
                const action = exists ? "updated" : "created"
                
                // Create a copy of data to avoid mutating the original
                const sessionData = { ...data }
                
                // Extract time_query for special handling (just like in Python)
                const timeQuery = sessionData.time_query
                delete sessionData.time_query
                
                const hashData: Record<string, string> = {}
                
                // Convert all fields to strings for hash storage
                // This mirrors your Python logic of converting values to strings
                for (const [field, value] of Object.entries(sessionData)) {
                    if (value !== undefined && value !== null) {
                        hashData[field] = typeof value === 'string' ? value : String(value)
                    }
                }
                
                // Handle time_query specially - serialize to JSON string
                // This exactly matches your Python implementation
                if (timeQuery !== undefined && timeQuery !== null) {
                    hashData['time_query'] = JSON.stringify(timeQuery)
                }
                
                // Use hmset for hash storage and set expiration
                // This mirrors your Python redis.hmset and redis.expire calls
                await this.redisClient.hmset(sessionId, hashData)
                await this.redisClient.expire(sessionId, ttl)
                
                console.log(`Successfully ${action} session '${sessionId}' with TTL ${ttl}s`)
            }
        } catch (error) {
            console.error(`Error upserting session '${sessionId}':`, error)
            throw error
        }
    }

    /**
     * Get session data - equivalent to your Python get_session function
     * Returns formatted session response with TTL information
     */
    async getSession( sessionId: string ) {
        try {
            if ( this.redisClient ) {
                // Get all hash fields for the session
                const sessionData = await this.redisClient.hgetall(sessionId)
                
                // Check if session exists or has expired
                // This mirrors your Python logic for handling missing sessions
                if (!sessionData || Object.keys(sessionData).length === 0) {
                    throw new InternalError(
                        404,
                        `Session '${sessionId}' not found or expired`
                    )
                }
                
                // Get remaining TTL for the session
                const ttl = await this.redisClient.ttl(sessionId)
                
                const processedFields: Partial<SessionContext> = {}
            
                // Process each field carefully, similar to your Python implementation
                // Handle time_query separately due to its special JSON serialization
                if (sessionData['time_query'] && sessionData['time_query'].length > 0) {
                    try {
                        const timeQueryData = JSON.parse(sessionData['time_query'])
                        
                        // Ensure it's an array and convert to TimePeriod objects
                        if (Array.isArray(timeQueryData)) {
                            const timePeriods: TimePeriod[] = timeQueryData.map(periodData => ({
                                start_time: periodData.start_time,
                                end_time: periodData.end_time,
                                description: periodData.description
                            }))
                            
                            processedFields.time_query = timePeriods
                        } else {
                            console.warn(`time_query in session '${sessionId}' is not an array, skipping`)
                        }
                        
                    } catch (jsonError) {
                        console.error(`Invalid JSON in time_query for session '${sessionId}':`, jsonError)
                    }
                }
                
                // Handle other string fields - now TypeScript knows these are only string fields
                const stringFields = ['topic', 'prev_question', 'user_name', 'user_email', 'current_time'] as const
                
                for (const field of stringFields) {
                    if (sessionData[field] && sessionData[field].length > 0) {
                        // TypeScript now knows this is safe because we've excluded time_query
                        processedFields[field] = sessionData[field]
                    }
                }
                
                const sessionContext: SessionContext = processedFields
                
                return {
                    session_id: sessionId,
                    data: sessionContext,
                }
            }
            
        } catch (error) {
            console.error(`Error retrieving session '${sessionId}':`, error)
            throw error
        }
    }
}

let redisServiceInstance: RedisService | undefined

export function getInstance(): RedisService {
    if ( redisServiceInstance === undefined ) {
        redisServiceInstance = new RedisService()
    }

    return redisServiceInstance
}
