import { TurnContext } from "botbuilder"
import { 
    TurnState, 
} from '@microsoft/teams-ai'

import logger from '../utils/logger'
import { getCurrentMember } from "../utils/index"
import { InternalError } from "../errors/internal_error/index"

export interface UserInfo {
    userId?: string
    userName?: string
    email?: string
}

export interface SessionContext {
    user_id?: string
    user_name?: string
    user_email?: string
    current_time?: string
}

export class ConductifyCommandHandler {
    backendEndpoint: string

    constructor() {
        if ( !process.env.BACKEND_URL ) {
            throw new InternalError( 500, 'BACKEND_URL environment variable is required but not set' )
        }
        this.backendEndpoint = process.env.BACKEND_URL 
        logger.info( this.backendEndpoint )
    }

    async handleCommandReceived( 
        context: TurnContext, 
        state: TurnState, 
    ): Promise< string > {
        logger.info( `Bot received message for Conductify: ${ context.activity.text }` )
        const userMessage = context.activity.text

        const member = await getCurrentMember( context )

        // console.log( `${ member.userRole }` )
        // console.log( `${ member.email }` )
        // console.log( `${ member.givenName }` )
        // console.log( `${ member.userPrincipalName }` )

        const [ first, ...rest ] = member.name
            .split( " - " )[ 0 ]
            .replace( ".", "" )
            .split( " " )
        const fullName = [ ...rest, first ].join( " " )

        const userInfo: UserInfo = {
            userId: member.id,
            userName: fullName,
            email: member.email,
        }

        const maxRetries = 3

        for ( let attempt = 1; attempt <= maxRetries; attempt++ ) {
        
            try {
                await this._upsertSessionContext( userInfo )

                logger.info( `Successfully upserted session context for user: ${ userInfo.userId }` )
            } catch ( error ) {
                logger.error( `Failed to upsert session context on attempt ${ attempt }: ${ error }` )

                if ( attempt === maxRetries ) {
                    return "Xin lỗi, bên em vừa gặp chút vấn đề với đường truyền mạng. Anh/chị gửi lại thông tin vừa rồi giúp em nhé."
                }
            }
        }

        // const maxRetries = 3

        // for ( let attempt = 1; attempt <= maxRetries; attempt++ ) {
        
        //     try {
        //         // logger.info( `Attempting to query Flowise (attempt ${ attempt }/${ maxRetries })` )

        //         // return await this._queryFlowise( userMessage, userInfo )
        //     } catch ( error ) {

        //         logger.error( `Flowise query failed on attempt ${ attempt }: ${ error }` )

        //         if ( attempt === maxRetries ) {
        //             logger.error( `All ${ maxRetries } attempts failed for Flowise query` )
        //             return "Xin lỗi, bên em vừa gặp chút vấn đề với đường truyền mạng. Anh/chị gửi lại thông tin vừa rồi giúp em nhé."
        //         }
        //     }
        // }

        return "Xin lỗi, bên em vừa gặp chút vấn đề với đường truyền mạng. Anh/chị gửi lại thông tin vừa rồi giúp em nhé."
    }

    async _upsertSessionContext( userInfo: UserInfo ): Promise< void > {
        const now = new Date()
        const year = now.getFullYear().toString()
        const month = String( now.getMonth() + 1 ).padStart( 2, '0' )
        const day = String( now.getDate() ).padStart( 2, '0' )
        const currentTime = `${ year }-${ month }-${ day }`

        const upsertRequest = {
            session_id: userInfo.userId,
            data: {
                user_name: userInfo.userName,
                user_email: userInfo.email,
                current_time: currentTime
            }
        }

        const response = await fetch( `${ this.backendEndpoint }/api/session/upsert`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify( upsertRequest )
        } )

        if ( !response.ok ) {
            throw new InternalError( 
                response.status, 
                `Failed to upsert session context. HTTP status: ${ response.status }` 
            )
        }
    }

    // async _queryFlowise( 
    //     question: string,
    //     userInfo: UserInfo,
    // ): Promise< string > {
        
    //     const fullQuestion = [
    //         question,
    //         userInfo.userId ?? "",
    //         userInfo.userName ?? "",
    //         userInfo.email ?? ""
    //     ].join( "|" )

    //     logger.debug( `Full question sent to Flowise: ${ fullQuestion }` )

    //     const data = {
    //         question: fullQuestion
    //     }
            
    //     const response = await fetch( this.flowiseEndpoint, {
    //         method: "POST",
    //         headers: {
    //             "Content-Type": "application/json"
    //         },
    //         body: JSON.stringify( data )
    //     } )

    //     if ( !response.ok ) {
    //         throw new InternalError( 500, `HTTP error! status: ${ response.status }` )
    //     }

    //     const result: any = await response.json()
    //     // console.log( "Flowise response:", result )
    //     return result.text
    // }
}
