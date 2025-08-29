import { Request, Response, NextFunction } from 'express'
import * as fs from 'fs'
import * as path from 'path'
import { InternalError } from '../../errors/internal_error'
import { StatusCodes } from 'http-status-codes'

let currentFileIndex = 0

const getFilteredData = async (req: Request, res: Response, next: NextFunction) => {
    try {
        // const files = ['filtered_2025-08-20.json', 'filtered_2025-08-21.json']
        const files = [ 'data.json' ]
        const currentFile = files[currentFileIndex]
        const filePath = path.join(__dirname, currentFile)
        
        if (!fs.existsSync(filePath)) {
            throw new InternalError(
                StatusCodes.NOT_FOUND,
                `File ${currentFile} not found`
            )
        }

        const rawData = fs.readFileSync(filePath, 'utf8')
        const jsonData = JSON.parse(rawData)

        currentFileIndex = (currentFileIndex + 1) % files.length

        res.json({
            data: jsonData
        })
    } catch (error) {
        next(error)
    }
}

export default {
    getFilteredData,
}
