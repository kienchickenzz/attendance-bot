import express, { Router } from 'express'
import searchController from '../../controllers/search'

const router: Router = express.Router()

// READ
router.post( '/time', searchController.searchTime )

// READ
router.post( '/late', searchController.searchLate )

// READ
router.post( '/attendance', searchController.searchAttendance )

export default router
