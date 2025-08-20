import express, { Router } from 'express'
import dayOffController from '../../controllers/dayoff'

const router: Router = express.Router()

// READ
router.post( '/check', dayOffController.checkDayOff )

export default router
