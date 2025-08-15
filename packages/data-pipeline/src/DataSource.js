import 'reflect-metadata'
import { DataSource } from 'typeorm'

export const processedDataSource = new DataSource( {
    type: 'postgres',
    host: 'localhost',
    port: 5432,
    username: 'postgres',
    password: 'Pa55w.rd',
    database: 'attendance_processed',
    ssl: false,
    synchronize: false,
    migrationsRun: false,
    extra: {
        idleTimeoutMillis: 120000
    },
    logging: [ 'error', 'warn', 'info', 'log' ],
    logger: 'advanced-console',
    logNotifications: true,
    applicationName: 'Attendance Pipeline - ProcessedDB'
} )
