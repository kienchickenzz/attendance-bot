import express, { Router } from 'express'
import sessionRouter from './session'
import searchRouter from './search'

const router: Router = express.Router()

router.use( '/session', sessionRouter )
router.use( '/search', searchRouter )

export default router
