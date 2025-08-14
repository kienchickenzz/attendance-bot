import express, { Router } from 'express'
import searchController from '../../controllers/search'

const router: Router = express.Router()

// READ
router.post( '/time', searchController.searchTime )
router.post( '/late', searchController.searchLate )
router.post( '/attendance', searchController.searchAttendance )

export default router
