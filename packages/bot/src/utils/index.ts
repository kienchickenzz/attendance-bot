import { TurnContext, TeamsInfo, TeamsPagedMembersResult } from "botbuilder"

export async function getCurrentMember( context: TurnContext ) {
    let continuationToken
    let allMembers = []
    
    do {
        try {
            const pagedMembers: TeamsPagedMembersResult = await TeamsInfo.getPagedMembers( context, 100, continuationToken )
            continuationToken = pagedMembers.continuationToken
            allMembers.push( ...pagedMembers.members )
        } catch ( error ) {
            break
        }
    } while ( continuationToken !== undefined )
    
    return allMembers[ 0 ] // IMPORTANT: Assume this person is talking with the bot alone
}
