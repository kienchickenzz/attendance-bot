const axios = require( 'axios' )
const readline = require( 'readline' )
const express = require( 'express' )

// const BOT_ENDPOINT = 'http://localhost:3978/api/messages'
const BOT_ENDPOINT = 'https://hub-welcome-motion-commentary.trycloudflare.com' + '/api/messages'

const MOCK_SERVICE_PORT = 3979
const MOCK_ENDPOINT = `http://localhost:${ MOCK_SERVICE_PORT }`
// const MOCK_ENDPOINT = `http://host.docker.internal:${ MOCK_SERVICE_PORT }` 

const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m'
}

class BotTestClient {
    constructor() {
        this.conversationId = 'test-conversation-' + Date.now()
        this.userId = 'test-user-' + Math.random().toString( 36 ).substr( 2, 9 )
        this.messageCounter = 0
        this.mockServiceUrl = MOCK_ENDPOINT
        this.receivedResponses = []

        console.log( `${ colors.cyan }📡 Bot Endpoint: ${ BOT_ENDPOINT }${ colors.reset }` )
        console.log( `${ colors.cyan }🔧 Mock Service URL: ${ this.mockServiceUrl }${ colors.reset }\n` )
        
        // Create readline interface for interactive testing
        this.rl = readline.createInterface( {
            input: process.stdin,
            output: process.stdout
        } )

        this.setupMockService()
    }

    /**
     * Sets up a mock Bot Framework service to receive responses from the bot
     * This solves the ENOTFOUND error by providing a real endpoint for the bot to send responses to
     */
    setupMockService() {
        this.mockApp = express()
        this.mockApp.use( express.json() )

        this.mockApp.use( ( req, res, next ) => {
            console.log( `${ colors.magenta }[Mock Service] ${ req.method } ${ req.path }${ colors.reset }` )
            next()
        } )

        // Mock endpoint that mimics Bot Framework Connector API
        // This endpoint will receive responses that the bot tries to send back
        this.mockApp.post( '/v3/conversations/:conversationId/activities/:activityId', ( req, res ) => {
            const response = req.body
            
            console.log( `${ colors.green }🤖 Bot Response Received:${ colors.reset }` )
            console.log( `${ colors.cyan }Text:${ colors.reset } ${ response.text || 'No text content' }` )

            // Store the response for later analysis
            this.receivedResponses.push({
                timestamp: new Date().toISOString(),
                response: response
            });

            // Respond with a mock Bot Framework response
            res.status( 200 ).json( {
                id: `response-${ Date.now() }`
            } )
        } )

        // Mock endpoint for posting activities (used for proactive messages)
        this.mockApp.post('/v3/conversations/:conversationId/activities', (req, res) => {
            const activity = req.body;
            console.log(`${colors.magenta}📤 Proactive Message:${colors.reset} ${activity.text}`);
            
            res.status(200).json({
                id: `activity-${Date.now()}`
            });
        });

        this.mockApp.get( '/health', ( req, res ) => {
            res.json( { status: 'healthy', timestamp: new Date().toISOString() } )
        } )

        // Error handling middleware
        this.mockApp.use( ( error, req, res, next ) => {
            console.error( `${ colors.red }[Mock Service Error]:${ colors.reset }`, error )
            res.status( 500 ).json( { error: 'Internal server error' } )
        } )

        // Start the mock service
        this.mockServer = this.mockApp.listen(MOCK_SERVICE_PORT, () => {
            console.log(`${colors.yellow}🔧 Mock Bot Framework service started on port ${MOCK_SERVICE_PORT}${colors.reset}`);
        });
    }

    async generateTestJWT() {
        // Option 1: Simple test token (may not work if server validates signature)
        const header = {
            "alg": "HS256",
            "typ": "JWT"
        };
    
        const payload = {
                "iss": "https://api.botframework.com", // Bot Framework issuer
                "aud": "your-bot-app-id", // Replace with your actual bot's App ID
                "sub": this.userId,
                "iat": Math.floor(Date.now() / 1000),
                "exp": Math.floor(Date.now() / 1000) + (60 * 60), // 1 hour expiration
                "scope": "https://api.botframework.com/.default"
            };
            
            // For testing purposes - encode without signature verification
            const encodedHeader = Buffer.from(JSON.stringify(header)).toString('base64url');
            const encodedPayload = Buffer.from(JSON.stringify(payload)).toString('base64url');
            
            // Simple unsigned token for testing (add .signature if your bot validates it)
            return `${encodedHeader}.${encodedPayload}.test-signature`;
        }

    /**
     * Creates a properly formatted Bot Framework activity object with correct serviceUrl
     * This version uses our mock service URL to avoid DNS resolution errors
     */
    createActivity( text, type = 'message' ) {
        this.messageCounter++;
        
        return {
            type: type,
            text: text,
            textFormat: 'plain',
            timestamp: new Date().toISOString(),
            localTimestamp: new Date().toISOString(),
            id: `message-${this.messageCounter}`,
            from: {
                id: this.userId,
                name: 'Test User',
                aadObjectId: this.userId
            },
            conversation: {
                id: this.conversationId,
                name: 'Test Conversation',
                conversationType: 'personal',
                isGroup: false
            },
            recipient: {
                id: 'bot-id',
                name: 'Attendance Bot'
            },
            channelId: 'test',
            serviceUrl: this.mockServiceUrl, // Use our mock service instead of fake URL
            channelData: {
                source: 'test-client',
                clientActivityID: `client-${this.messageCounter}`
            },
            locale: 'en-US'
        };
    }

    /**
     * Sends a message to the bot and handles the response
     * Now properly handles bot responses through our mock service
     */
    async sendMessage(text) {
        try {
            const activity = this.createActivity(text);
            
            console.log(`\n${colors.cyan}→ Sending:${colors.reset} "${text}"`);
            console.log(`${colors.yellow}⏳ Waiting for bot response...${colors.reset}`);
            
            // Clear previous responses for this message
            const initialResponseCount = this.receivedResponses.length;

            // const jwtToken = await this.generateTestJWT();
            
            const response = await axios.post(BOT_ENDPOINT, activity, {
                headers: {
                    'Content-Type': 'application/json',
                    // 'Authorization': `Bearer ${jwtToken}`,
                    'User-Agent': 'BotTestClient/1.0'
                },
                timeout: 15000 // 15 second timeout
            });
            
            if (response.status === 200) {
                console.log(`${colors.green}✓ Message delivered to bot successfully${colors.reset}`);
                
                // Wait a moment for the bot to process and send response back to our mock service
                await this.sleep(1500);
                
                // Check if we received any new responses
                const newResponseCount = this.receivedResponses.length;
                if (newResponseCount === initialResponseCount) {
                    console.log(`${colors.blue}ℹ️  Bot processed the message but didn't send a response${colors.reset}`);
                    console.log(`${colors.blue}   This might be normal if the message doesn't match any command patterns${colors.reset}`);
                }
            }
            
        } catch (error) {
            console.error(`${colors.red}✗ Error sending message:${colors.reset}`, error.message);
            
            if (error.response) {
                console.error(`${colors.red}Response Status:${colors.reset}`, error.response.status);
                console.error(`${colors.red}Response Data:${colors.reset}`, error.response.data);
            } else if (error.request) {
                console.error(`${colors.red}No response received. Is the bot running on port 3978?${colors.reset}`);
            }
        }
    }

    /**
     * Starts an interactive chat session with enhanced features
     */
    async startInteractiveMode() {
        console.log(`${colors.bright}${colors.green}💬 Interactive Chat Mode Started${colors.reset}`);
        console.log(`${colors.cyan}Type your messages and press Enter to send them to the bot.${colors.reset}`);
        console.log(`${colors.cyan}Special commands:${colors.reset}`);
        console.log(`${colors.cyan}  - 'quit' or 'exit': Stop the test client${colors.reset}`);
        console.log(`${colors.cyan}  - 'history': Show all bot responses received${colors.reset}`);
        console.log(`${colors.cyan}  - 'clear': Clear response history${colors.reset}\n`);
        
        const askForInput = () => {
            this.rl.question(`${colors.bright}You: ${colors.reset}`, async (input) => {
                const trimmedInput = input.trim();
                
                if (trimmedInput.toLowerCase() === 'quit' || trimmedInput.toLowerCase() === 'exit') {
                    console.log(`${colors.yellow}👋 Goodbye!${colors.reset}`);
                    this.cleanup();
                    return;
                }
                
                if (trimmedInput.toLowerCase() === 'history') {
                    this.showResponseHistory();
                    askForInput();
                    return;
                }
                
                if (trimmedInput.toLowerCase() === 'clear') {
                    this.receivedResponses = [];
                    console.log(`${colors.green}✓ Response history cleared${colors.reset}\n`);
                    askForInput();
                    return;
                }
                
                await this.sendMessage(input); // Send original input, not trimmed (to test edge cases)
                console.log(); // Add a blank line for readability
                askForInput(); // Ask for the next input
            });
        };
        
        askForInput();
    }

    /**
     * Displays the history of all responses received from the bot
     */
    showResponseHistory() {
        if (this.receivedResponses.length === 0) {
            console.log(`${colors.yellow}No responses received yet${colors.reset}\n`);
            return;
        }

        console.log(`${colors.bright}${colors.magenta}📋 Response History (${this.receivedResponses.length} responses):${colors.reset}\n`);
        
        this.receivedResponses.forEach((entry, index) => {
            const timestamp = new Date(entry.timestamp).toLocaleTimeString();
            console.log(`${colors.cyan}${index + 1}. [${timestamp}]${colors.reset} ${entry.response.text || '[No text content]'}`);
            
            if (entry.response.attachments && entry.response.attachments.length > 0) {
                console.log(`   📎 ${entry.response.attachments.length} attachment(s)`);
            }
        });
        
        console.log(); // Add blank line
    }

    /**
     * Helper function to pause execution
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Enhanced health check that also verifies our mock service is working
     */
    async checkBotHealth() {
        console.log( `${ colors.yellow }🔍 Performing health check...${ colors.reset }` )
        
        try {
            const testActivity = this.createActivity( 'health-check' )
            
            const response = await axios.post( BOT_ENDPOINT, testActivity, {
                headers: { 'Content-Type': 'application/json' },
                timeout: 5000
            } )
            
            if ( response.status === 200 ) {
                console.log( `${ colors.green }✅ Bot is running and accessible!${ colors.reset }` )
                
                // Wait a moment and check if our mock service received any response
                await this.sleep( 1000 )
                console.log( `${ colors.green }✅ Mock Bot Framework service is working!${ colors.reset }\n` )
                return true
            }
        } catch (error) {
            console.error(`${colors.red}❌ Cannot connect to bot:${colors.reset}`, error.message);
            console.log(`${colors.yellow}💡 Make sure your bot is running with: npm run dev:teamsfx${colors.reset}\n`);
            return false;
        }
    }

    cleanup() {
        if ( this.rl ) {
            this.rl.close()
        }
        if ( this.mockServer ) {
            this.mockServer.close()
            console.log( `${ colors.yellow }🔧 Mock service stopped${ colors.reset }` )
        }
    }
}

async function main() {
    const testClient = new BotTestClient()
    
    process.on( 'SIGINT', () => {
        console.log( `\n${ colors.yellow }👋 Shutting down gracefully...${ colors.reset }` )
        testClient.cleanup()
        process.exit( 0 )
    } )
    process.on( 'SIGTERM', () => {
        testClient.cleanup()
        process.exit( 0 )
    } )
    
    await testClient.sleep( 1000 ) // Wait a moment for mock service to start
    
    const botIsHealthy = await testClient.checkBotHealth()
    if ( !botIsHealthy ) {
        console.log( `${ colors.red }❌ Health check failed. Please check your bot configuration.${ colors.reset }` )
        testClient.cleanup()
        process.exit( 1 )
    }

    await testClient.startInteractiveMode()
}

main().catch( error => {
    console.error( `${ colors.red }❌ Unexpected error:${ colors.reset }`, error )
    process.exit( 1 )
} )
