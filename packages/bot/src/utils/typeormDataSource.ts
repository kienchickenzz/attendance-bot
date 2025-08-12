import { DataSource } from 'typeorm'
import { getDataSource } from '../DataSource'

import path from 'path'
import dotenv from 'dotenv'
dotenv.config( { path: path.join( __dirname, '..', '..', '.env' ), override: true } )

export const dataSource: DataSource = getDataSource()
