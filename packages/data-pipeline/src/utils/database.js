export const createEmployeeInfoTable = async (dataSource) => {
    const queryRunner = dataSource.createQueryRunner()
    
    try {
        
        const createTableQuery = `
            CREATE TABLE IF NOT EXISTS employee_info (
                user_id VARCHAR(255) PRIMARY KEY,
                user_email VARCHAR(255) NOT NULL,
                user_name VARCHAR(255) NOT NULL
            );
        `
        
        const createIndexQueries = [
            'CREATE INDEX IF NOT EXISTS idx_employee_info_email ON employee_info(user_email);',
            'CREATE INDEX IF NOT EXISTS idx_employee_info_name ON employee_info(user_name);'
        ]
        
        console.log('Creating employee_info table...')
        await queryRunner.query(createTableQuery)
        console.log('Table employee_info created successfully')
        
        console.log('Creating indexes...')
        for (const indexQuery of createIndexQueries) {
            await queryRunner.query(indexQuery)
        }
        console.log('Indexes created successfully')
        
    } catch (error) {
        console.error('Error creating table:', error)
        throw error
    } finally {
        await queryRunner.release()
    }
}

export const createEmployeeAttendanceTable = async (dataSource) => {
    const queryRunner = dataSource.createQueryRunner()
    
    try {
        
        const createTableQuery = `
            CREATE TABLE IF NOT EXISTS employee_attendance (
                    user_email VARCHAR(255) NOT NULL,
                    date DATE NOT NULL,
                    leave_morning BOOLEAN DEFAULT FALSE,
                    leave_afternoon BOOLEAN DEFAULT FALSE,
                    checkin_time VARCHAR(5) NULL,     -- HH:MM
                    checkout_time VARCHAR(5) NULL,    -- HH:MM
                    free_allowance INTEGER NOT NULL,
                    checkin_violation INTEGER NULL,
                    checkout_violation INTEGER NULL,
                    total_violation INTEGER NULL,
                    deduction_hours INTEGER NULL,
                    PRIMARY KEY (user_email, date),
                CHECK (checkin_time ~ '^[0-2][0-9]:[0-5][0-9]$' OR checkin_time IS NULL),
                CHECK (checkout_time ~ '^[0-2][0-9]:[0-5][0-9]$' OR checkout_time IS NULL)
            );
        `
        
        const createIndexQueries = [
            'CREATE INDEX IF NOT EXISTS idx_employee_attendance_checkin ON employee_attendance(checkin_time);',
            'CREATE INDEX IF NOT EXISTS idx_employee_attendance_checkout ON employee_attendance(checkout_time);',
        ]
        
        await queryRunner.query(createTableQuery)
        
        for (const indexQuery of createIndexQueries) {
            await queryRunner.query(indexQuery)
        }
        
    } catch (error) {
        console.error('Error creating table:', error)
        throw error
    } finally {
        await queryRunner.release()
    }
}

export const insertAttendanceData = async (dataSource, record, result, userId) => {
    const queryRunner = dataSource.createQueryRunner()
    
    try {
        const insertQuery = `
            INSERT INTO employee_attendance (
                user_email,
                date,
                leave_morning,
                leave_afternoon,
                checkin_time,
                checkout_time,
                free_allowance,
                checkin_violation,
                checkout_violation,
                total_violation,
                deduction_hours
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        `
        
        await queryRunner.query( insertQuery, [
            record.userEmail,
            record.date,
            record.leaveMorning,
            record.leaveAfternoon,
            record.checkinTime,
            record.checkoutTime,
            result.freeAllowance,
            result.morningViolation,
            result.afternoonViolation,
            result.violationMinutes,
            result.deductionHours
        ] )
        
    } catch (error) {
        console.error('Error inserting attendance data:', error)
        throw error
    } finally {
        await queryRunner.release()
    }
}
