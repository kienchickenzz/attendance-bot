import express from 'express'
import path from 'path'
import cors from 'cors'
import http from 'http'
import dotenv from 'dotenv'
import { DataSource } from 'typeorm'
// import cookieParser from 'messagescookie-parser'
import { adapter } from "./internal/initialize"
import apiRouter from './routes'
import { getCorsOptions } from './utils/xss'
import { getInstance as getRedisInstance, RedisService } from './RedisService'
import { TeamsBot } from "./teamsBot" 
import logger, { expressRequestLogger } from './utils/logger'
import { getDataSource } from './DataSource'

dotenv.config( { path: path.join( __dirname, '..', '.env' ), override: true } )

export class App {
    app: express.Application
    redisService: RedisService = getRedisInstance()
    AppDataSource: DataSource = getDataSource()
    teamsBot: TeamsBot
    
    constructor() {
        this.app = express()

        this.teamsBot = new TeamsBot()
    }

    async init() {
        try {
            await this.AppDataSource.initialize()
            logger.info( '📦 [server]: Data Source initialized successfully' )

            this.redisService = new RedisService()
        } catch ( error ) {
            logger.error( '❌ [server]: Error during Data Source initialization:', error )
        }
    }

    async config() {
        // Limit is needed to allow sending/receiving base64 encoded string
        const file_size_limit = process.env.FILE_SIZE_LIMIT || '50mb'
        this.app.use( express.json( { limit: file_size_limit } ) )
        this.app.use( express.urlencoded( { limit: file_size_limit, extended: true } ) )

        // Allow access from specified domains
        this.app.use( cors( getCorsOptions() ) )

        // Add the expressRequestLogger middleware to log all requests
        this.app.use( expressRequestLogger )

        this.app.post( "/api/messages", async ( req, res ) => {
            await adapter.process( req, res, async ( context ) => {
                await this.teamsBot.run( context )
            } )
        } )

        this.app.use( '/api', apiRouter )
    }
}

export default App

let serverApp: App | undefined

export async function start() {
    serverApp = new App()

    const host = process.env.HOST || '0.0.0.0'
    const port = parseInt( process.env.PORT || '', 10 ) || 3978
    const server = http.createServer( serverApp.app )

    await serverApp.init()
    await serverApp.config()

    server.listen( port, host, () => {
        logger.info( `⚡️ [server]: Server is listening at ${ host ? 'http://' + host : '' }:${ port }` )
    } )
}

export function getInstance(): App | undefined {
    return serverApp
}

start()
