import { MemoryStorage } from "botbuilder"
import { Application } from "@microsoft/teams-ai"

import { FlowiseCommandHandler } from "./commands/flowiseCommandHandler"
import { ConductifyCommandHandler } from "./commands/conductifyCommandHandler"

// Define storage and application
// const storage = new MemoryStorage()
// export const app = new Application( {
//   storage,
// } )

const flowiseCommandHandler = new FlowiseCommandHandler()
const conductifyCommandHandler = new ConductifyCommandHandler()

// app.message( /.*/, async ( context, state ) => {
//     // const reply = await flowiseCommandHandler.handleCommandReceived( context, state )
//     const reply = await conductifyCommandHandler.handleCommandReceived( context )
//     await context.sendActivity( reply )
// } )

import {
  TeamsActivityHandler,
  TurnContext
} from "botbuilder";

export class TeamsBot extends TeamsActivityHandler {
    constructor() {
        super()

        this.onMessage( async ( context: TurnContext, next ) => {
            // const reply = await flowiseCommandHandler.handleCommandReceived( context, state )
            const reply = await conductifyCommandHandler.handleCommandReceived( context )
            await context.sendActivity( reply )

            await next()
        } )

        // Khi có sự kiện membersAdded (người dùng mới bắt đầu chat với bot)
        this.onMembersAdded( async ( context: TurnContext, next ) => {
            const membersAdded = context.activity.membersAdded

            if ( !membersAdded ) {
                return
            }

            const botId = context.activity.recipient.id

            for ( let member of membersAdded ) {
                if ( member.id !== botId ) {
                    await context.sendActivity(
                        `Chào anh/chị 👋 Em là Minh Hiển — trợ lý ảo hỗ trợ tra cứu thông tin chấm công cho công ty.
Em có thể giúp anh/chị tra cứu thời gian check-in/check-out, thông tin vi phạm, v.v.
Ví dụ, anh/chị có thể hỏi:
- thời gian check in, check out của tôi thứ 4 vừa rồi?
- thứ 4 vừa rồi tôi check in lúc nào?
- thứ 4 vừa rồi tôi có vi phạm gì không?
- ngày 25/08 tôi có đi muộn không?
- tổng thời gian vi phạm của tôi hôm nay?
- ngày 25/08 tôi được tính bao nhiêu ngày công?

💡 Để kết quả chính xác nhất, anh/chị nên đặt câu hỏi theo các ví dụ mẫu bên trên.

🔍 Hôm nay anh/chị muốn tra cứu thông tin gì ạ?`
                    )
                }
            }

            // Tiếp tục các middleware khác
            await next()
        } )
    }
}
