import 'reflect-metadata'
import { DataSource } from 'typeorm'
import { entities } from './database/entities'
import { postgresMigrations } from './database/migrations/postgres'
import logger from './utils/logger'

let appDataSource: DataSource

export const init = (): void => {
    switch ( process.env.DATABASE_TYPE ) {
        case 'postgres':
            appDataSource = new DataSource( {
                type: 'postgres',
                host: process.env.DATABASE_HOST,
                port: parseInt( process.env.DATABASE_PORT || '5432' ),
                username: process.env.DATABASE_USER,
                password: process.env.DATABASE_PASSWORD,
                database: process.env.DATABASE_NAME,
                ssl: getDatabaseSSLFromEnv(),
                synchronize: false,
                migrationsRun: false,
                entities: Object.values(entities),
                migrations: postgresMigrations,
                extra: {
                    idleTimeoutMillis: 120000
                },
                logging: ['error', 'warn', 'info', 'log'],
                logger: 'advanced-console',
                logNotifications: true,
                poolErrorHandler: ( err ) => {
                    logger.error(`Database pool error: ${JSON.stringify(err)}`)
                },
                applicationName: 'Attendance Bot'
            } )
            break
    }
}

export function getDataSource(): DataSource {
    if ( appDataSource === undefined ) {
        init()
    }
    return appDataSource
}

const getDatabaseSSLFromEnv = () => {
    if ( process.env.DATABASE_SSL_KEY_BASE64 ) {
        return {
            rejectUnauthorized: false,
            ca: Buffer.from( process.env.DATABASE_SSL_KEY_BASE64, 'base64' )
        }
    } else if ( process.env.DATABASE_SSL === 'true' ) {
        return true
    }
    return undefined
}
