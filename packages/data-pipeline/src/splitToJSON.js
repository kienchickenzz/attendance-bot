import fs from 'fs'
import path from 'path'

function filterByDate( targetEmail, filePath ) {
    try {
        const dataPath = path.join( __dirname, filePath )
        const rawData = fs.readFileSync( dataPath, 'utf8' ) 
        const data = JSON.parse( rawData )
        
        const filteredData = data.filter( item => {
            if ( item.email ) {
                return item.email === targetEmail
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

const filePath = '../sample-data/data.json'
const targetEmail = 'nvdat5@cmc.com.vn' 
const targetFile = `filtered_${ targetEmail }.json`

const dailyData = filterByDate( targetEmail, filePath )
const result = saveFilteredData( dailyData, targetFile )
console.log( result )
