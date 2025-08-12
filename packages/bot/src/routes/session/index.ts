import express, { Router } from 'express'
import sessionController from '../../controllers/session'

const router: Router = express.Router()

// CREATE
router.post( '/upsert', sessionController.upsert_session )

// READ
router.get( '/:session_id', sessionController.get_session )

export default router
