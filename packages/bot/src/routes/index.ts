import express, { Router } from 'express'
import sessionRouter from './session'

const router: Router = express.Router()

router.use( '/session', sessionRouter )

export default router
