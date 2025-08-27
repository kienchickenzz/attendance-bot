import fs from 'fs'
import path from 'path'

function filterByDate( date, filePath ) {
    try {
        const dataPath = path.join( __dirname, filePath )
        const rawData = fs.readFileSync( dataPath, 'utf8' ) 
        const data = JSON.parse( rawData )
        
        const filteredData = data.filter( item => {
            if ( item.first_in ) {
                const firstInDate = item.first_in.split( ' ' )[ 0 ]
                return firstInDate === date
            }
            return false
        } )
        
        return filteredData
    } catch ( error ) {
        console.error( 'Error reading or parsing data.json:', error.message )
        return []
    }
}

function saveFilteredData( filteredData, outputFileName ) {
    try {
        const outputPath = path.join( __dirname, `../${ outputFileName }` )
        
        fs.writeFileSync( outputPath, JSON.stringify( filteredData, null, 4 ), 'utf8' )
        console.log( `Saved ${ filteredData.length } records to ${ outputFileName }` )
        
        return true
    } catch ( error ) {
        console.error( 'Error saving filtered data:', error.message )
        return false
    }
}

const filePath = '../data.json'
const targetDate = '2025-08-21' 
const targetFile = `filtered_${ targetDate }.json`

const dailyData = filterByDate( targetDate, filePath )
const result = saveFilteredData( dailyData, targetFile )
console.log( result )
