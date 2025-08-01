import express from 'express'
import path from 'path'
// import cors from 'cors'
import http from 'http'
import dotenv from 'dotenv'
// import cookieParser from 'messagescookie-parser'

import { adapter } from "./internal/initialize"
import { TurnContext, TeamsInfo } from "botbuilder"
import { TeamsPagedMembersResult } from "botbuilder";

import { app as teamsApp } from "./teamsBot" 
import { FlowiseCommandHandler } from "./commands/flowiseCommandHandler"
import logger, { expressRequestLogger } from './utils/logger'

dotenv.config( { path: path.join( __dirname, '..', '.env' ), override: true } )

export class App {
    app: express.Application
    
    constructor() {
        this.app = express()
    }

    async config() {
        // Limit is needed to allow sending/receiving base64 encoded string
        const file_size_limit = process.env.FILE_SIZE_LIMIT || '50mb'
        this.app.use( express.json( { limit: file_size_limit } ) )
        this.app.use( express.urlencoded( { limit: file_size_limit, extended: true } ) )

        // Add the expressRequestLogger middleware to log all requests
        this.app.use( expressRequestLogger )

        const flowiseCommandHandler = new FlowiseCommandHandler()
        
        async function getAllMembers( context: TurnContext ) {
            let continuationToken;
            let allMembers = [];
            
            do {
                try {
                    // Lấy thành viên theo từng trang (mỗi trang 100 người)
                    const pagedMembers: TeamsPagedMembersResult = await TeamsInfo.getPagedMembers(context, 100, continuationToken);
                    continuationToken = pagedMembers.continuationToken;
                    allMembers.push(...pagedMembers.members);
                    
                    console.log(`Đã lấy được ${pagedMembers.members.length} thành viên trong trang này`);
                } catch (error) {
                    console.error("Lỗi khi lấy danh sách thành viên:", error);
                    break;
                }
            } while (continuationToken !== undefined);
            
            return allMembers;
        }
        
        teamsApp.message( /.*/, async ( context, state ) => {
            const userMessage = context.activity.text;
        
            const members = await getAllMembers(context);
            
            console.log(`Tổng số thành viên trong cuộc trò chuyện: ${members.length}`);
            
            // In ra thông tin một số thành viên đầu tiên để kiểm tra
            members.slice(0, 3).forEach((member, index) => {
                console.log(`Thành viên ${index + 1}: ${member.name} (ID: ${member.id})`)
                console.log( `${ member.role }` )
                console.log( `${ member.email }` )
                console.log( `${ member.givenName }` )
            });
        
            let reply
            
            reply = await flowiseCommandHandler.handleCommandReceived(context, state);
        
            if ( reply ) {
                await context.sendActivity( reply )
            }
        } )

        this.app.post( "/api/messages", async ( req, res ) => {

            logger.debug( "Hello World" )

            await adapter.process( req, res, async ( context ) => {
                await teamsApp.run( context )
            } )
        } )
    }
}

export default App

let serverApp: App | undefined

export async function start(): Promise<void> {
    serverApp = new App()

    const host = process.env.HOST || '0.0.0.0'
    const port = parseInt( process.env.PORT || '', 10 ) || 3978
    const server = http.createServer( serverApp.app )

    await serverApp.config()

    server.listen( port, host, () => {
        logger.info( `⚡️ [server]: Server is listening at ${ host ? 'http://' + host : '' }:${ port }` )
    } )
}

export function getInstance(): App | undefined {
    return serverApp
}

start()
