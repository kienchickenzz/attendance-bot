import express, { Router } from 'express'
import airflowController from '../../controllers/airflow'

const router: Router = express.Router()

// READ
router.post( '/data', airflowController.getFilteredData )

export default router
