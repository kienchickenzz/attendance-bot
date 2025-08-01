import { MemoryStorage } from "botbuilder"
import { Application } from "@microsoft/teams-ai"

// Define storage and application
const storage = new MemoryStorage()
export const app = new Application( {
  storage,
} )
