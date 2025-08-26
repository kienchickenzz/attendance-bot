import { TurnContext } from "botbuilder"

import logger from '../utils/logger'
import { getCurrentMember } from "../utils/index"
import { InternalError } from "../errors/internal_error/index"

export interface UserInfo {
    userId?: string
    userName?: string
    email?: string
}

export class ConductifyCommandHandler {
    backendEndpoint: string
    conductifyEndpoint: string

    constructor() {
        if ( !process.env.BACKEND_URL ) {
            throw new InternalError( 500, 'BACKEND_URL environment variable is required but not set' )
        }
        this.backendEndpoint = process.env.BACKEND_URL 
    }

    async handleCommandReceived( 
        context: TurnContext, 
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
                await this._upsertBasicInfo( userInfo )
                logger.info( `Successfully upserted basic info for user: ${ userInfo.userId }` )

                const conductifyResponse = await this._queryConductify( userMessage, userInfo )
                logger.info( `Successfully received response from Conductify for user: ${ userInfo.userId }` )

                await this._upsertPreviousQA( userInfo, userMessage, conductifyResponse )
                logger.info( `Successfully stored previous Q&A for user: ${ userInfo.userId }` )

                return conductifyResponse
            } catch ( error ) {
                logger.error( `Failed to upsert session context on attempt ${ attempt }: ${ error }` )

                if ( attempt === maxRetries ) {
                    return "Xin lỗi, bên em vừa gặp chút vấn đề với đường truyền mạng. Anh/chị gửi lại thông tin vừa rồi giúp em nhé."
                }
            }
        }

        return "Xin lỗi, bên em vừa gặp chút vấn đề với đường truyền mạng. Anh/chị gửi lại thông tin vừa rồi giúp em nhé."
    }

    async _upsertBasicInfo( userInfo: UserInfo ): Promise< void > {
        const now = new Date()
        const year = now.getFullYear().toString()
        const month = String( now.getMonth() + 1 ).padStart( 2, '0' )
        const day = String( now.getDate() ).padStart( 2, '0' )
        const weekdays = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday"
        ]
        const weekday = weekdays[ now.getDay() ]

        const currentTime = `${ weekday }, ${ year }-${ month }-${ day }`

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

    async _queryConductify( 
        question: string,
        userInfo: UserInfo,
    ): Promise< string > {
        
        const fullPrompt = [
            userInfo.userId ?? "",
            question,
        ].join( "|" )

        logger.debug( `Full prompt sent to Conductify: ${ fullPrompt }` )

        if ( !process.env.CONDUCTIFY_BOT_ID ) {
            throw new InternalError( 500, 'CONDUCTIFY_BOT_ID environment variable is required but not set' )
        }
        if ( !process.env.CONDUCTIFY_API_KEY ) {
            throw new InternalError( 500, 'CONDUCTIFY_API_KEY environment variable is required but not set' )
        }

        const threadId = `teams_${ userInfo.userId }_${ Date.now() }`
        
        const channelId = userInfo.userId
        const requestBody = {
            botUuid: process.env.CONDUCTIFY_BOT_ID,
            prompt: fullPrompt,
            channelId: "037f4fbb-af6b-47ea-bb0b-834ff2b4659e",
            channelType: "web", // Sử dụng "dev" cho Teams bot development, có thể đổi thành "web" sau
            threadId: "web-cc9f96ff-66eb-4434-948f-639ca334e3bc",
        }

        const response = await fetch( 'https://api.conductify.ai/external/v1/chat/completions', {
            method: "POST",
            headers: {
                "accept": "*/*",
                "x-api-key": process.env.CONDUCTIFY_API_KEY,
                "Content-Type": "application/json"
            },
            body: JSON.stringify( requestBody )
        } )

        if ( !response.ok ) {
            const errorText = await response.text()
            logger.error( `Conductify API error: ${response.status} - ${errorText}` )
            throw new InternalError( 
                response.status, 
                `Conductify API error! status: ${ response.status }, body: ${errorText}` 
            )
        }

        const result: any = await response.json()
        const botMsg: string = result.botMsg
        
        logger.debug( `Conductify response: ${ botMsg }` )

        if ( typeof result === "string" && result.startsWith( "Error" ) ) {
            return "Xin lỗi, hệ thống bên em đang gặp chút sự cố. Anh/chị thử lại sau giúp em nhé."
        }
        
        return botMsg
    }

    async _upsertPreviousQA( 
        userInfo: UserInfo, 
        question: string, 
        answer: string 
    ): Promise< void > {
        const upsertRequest = {
            session_id: userInfo.userId,
            data: {
                prev_question: question,
                prev_answer: answer
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
            const errorText = await response.text()
            logger.error( `Failed to upsert previous Q&A: ${ response.status } - ${ errorText }` )
            
            // Note: We don't throw an error here because the main functionality (getting answer) 
            // has already succeeded. We just log the failure to store conversation history.
            logger.warn( `Previous Q&A storage failed for user ${ userInfo.userId }, but continuing with successful response` )
        }
    }
}
