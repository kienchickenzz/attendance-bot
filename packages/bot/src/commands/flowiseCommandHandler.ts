import { TurnContext } from "botbuilder"
import { 
    TurnState, 
} from '@microsoft/teams-ai'

interface FlowiseResponse {
    text: string;
}

export class FlowiseCommandHandler {
    flowiseEndpoint: string

    constructor() {
        console.log('FLOWISE_URL from env:', process.env.FLOWISE_URL);
        // Cấu hình endpoint Flowise - bạn có thể đưa vào environment variables
        this.flowiseEndpoint = process.env.FLOWISE_URL || 
            "http://localhost:3000/api/v1/prediction/c96a680e-88e6-4698-a4e9-2b4104834abc";
        console.log( this.flowiseEndpoint )
    }

    async handleCommandReceived( context: TurnContext, state: TurnState ) {
        console.log(`Bot received message for Flowise: ${context.activity.text}`);

        const userMessage = context.activity.text;
        
        try {
            // Gửi câu hỏi tới Flowise API
            const flowiseResponse = await this.queryFlowise(userMessage);
            
            // Trả về phản hồi từ Flowise
            return flowiseResponse
            
        } catch (error) {
            console.error("Error calling Flowise API:", error);
            
            // Trả về thông báo lỗi thân thiện với người dùng
            return "Xin lỗi, hiện tại tôi gặp sự cố kỹ thuật. Vui lòng thử lại sau.";
        }
    }

    async queryFlowise( question: string ): Promise< string > {
        // Chuẩn bị data để gửi tới Flowise
        const data = {
            question: question
        };

        // Gọi Flowise API
        const response = await fetch( this.flowiseEndpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        // Kiểm tra xem response có thành công không
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Parse JSON response
        const result: any = await response.json();
        
        console.log("Flowise response:", result);
        
        return result.text;
    }
}
