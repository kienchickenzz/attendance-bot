import express, { Router } from 'express'
import sessionRouter from './session'
import searchRouter from './search'
import dayOffRouter from './dayoff'

const router: Router = express.Router()

router.use( '/session', sessionRouter )
router.use( '/search', searchRouter )
router.use( '/day-off', dayOffRouter )

export default router
