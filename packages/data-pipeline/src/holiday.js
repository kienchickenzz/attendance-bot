import fs from 'fs'
import path from 'path'

const start = new Date( "2025-03-26" )
const end = new Date( "2025-09-08" )

const filePath = '../sample-data/filtered_nvdat5@cmc.com.vn.json'
const dataPath = path.join( __dirname, filePath )
const rawData = fs.readFileSync( dataPath, 'utf8' ) 
const data = JSON.parse( rawData )

// Lấy tập hợp ngày đã có chấm công
const checkedDates = new Set(
    data.map( r => r.first_in.split( " " )[ 0 ] )
)

let missing = []
for ( let d = new Date( start ); d <= end; d.setDate( d.getDate() + 1 ) ) {
    const dayStr = d.toISOString().slice( 0,10 ) // yyyy-mm-dd
    if ( !checkedDates.has( dayStr ) ) {
        const wd = d.getDay() // 0=CN, 6=T7
        missing.push( {
            date: dayStr,
            name: ( wd === 0 || wd === 6 ) ? "Cuối tuần" : ""
        } )
    }
}

console.log( missing )
