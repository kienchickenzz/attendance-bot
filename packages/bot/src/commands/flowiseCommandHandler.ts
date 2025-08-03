import { TurnContext } from "botbuilder"
import { 
    TurnState, 
} from '@microsoft/teams-ai'

import logger from '../utils/logger'
import { getCurrentMember } from "../utils/index"

export interface UserInfo {
    userId?: string
    userName?: string
    email?: string
}

export class FlowiseCommandHandler {
    flowiseEndpoint: string

    constructor() {
        logger.info('FLOWISE_URL from env:', process.env.FLOWISE_URL);
        this.flowiseEndpoint = process.env.FLOWISE_URL || 
            "http://localhost:3000/api/v1/prediction/c96a680e-88e6-4698-a4e9-2b4104834abc";
        logger.info( this.flowiseEndpoint )
    }

    async handleCommandReceived( 
        context: TurnContext, 
        state: TurnState, 
    ): Promise< string > {
        logger.info( `Bot received message for Flowise: ${ context.activity.text }` )
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
        
        try {
            return await this._queryFlowise( userMessage, userInfo )
        } catch ( error ) {
            console.error( "Error calling Flowise API:", error )
            return "Xin lỗi, hiện tại tôi gặp sự cố kỹ thuật. Vui lòng thử lại sau."
        }
    }

    async _queryFlowise( 
        question: string,
        userInfo: UserInfo,
     ): Promise< string > {
        
        const fullQuestion = [
            question,
            userInfo.userId ?? "",
            userInfo.userName ?? "",
            userInfo.email ?? ""
        ].join( "|" )

        logger.debug( `Full question sent to Flowise: ${ fullQuestion }` )

        const data = {
            question: fullQuestion
        }
            
        const response = await fetch( this.flowiseEndpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify( data )
        } )

        // TODO: Implement custom Error object
        if ( !response.ok ) {
            throw new Error( `HTTP error! status: ${ response.status }` )
        }

        const result: any = await response.json()
        // console.log( "Flowise response:", result )
        return result.text
    }
}
