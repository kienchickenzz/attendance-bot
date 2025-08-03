import { MemoryStorage } from "botbuilder"
import { Application } from "@microsoft/teams-ai"

import { FlowiseCommandHandler } from "./commands/flowiseCommandHandler"

// Define storage and application
const storage = new MemoryStorage()
export const app = new Application( {
  storage,
} )

const flowiseCommandHandler = new FlowiseCommandHandler()
        
app.message( /.*/, async ( context, state ) => {
    const reply = await flowiseCommandHandler.handleCommandReceived( context, state )
    await context.sendActivity( reply )
} )
