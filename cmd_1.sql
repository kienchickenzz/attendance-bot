-- =====================================================
-- APPLICATION-FIRST ARCHITECTURE
-- =====================================================

-- 1. EMPLOYEE
CREATE TABLE employees (
    employee_id VARCHAR( 20 ) PRIMARY KEY,
    email VARCHAR( 100 ) NOT NULL UNIQUE,
    full_name VARCHAR( 100 ) NOT NULL,
    department VARCHAR( 50 ),
    position VARCHAR( 50 ),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE employees IS 'Basic employee information';

-- 2. HOLIDAY
CREATE TABLE holidays (
    date DATE PRIMARY KEY,
    name VARCHAR( 100 ) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE holidays IS 'Holidays, Tet';

-- 3. RAW DATA VỚI CHANGE DETECTION
CREATE TABLE attendance_raw (
    employee_id VARCHAR( 20 ),
    date DATE,
    first_in TIMESTAMP,
    last_out TIMESTAMP,
    
    -- Change detection cho application
    data_version INTEGER DEFAULT 1, -- Tăng mỗi khi update
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Processing status cho application control
    processing_status VARCHAR( 20 ) DEFAULT 'pending', -- pending, processing, completed, failed
    processed_at TIMESTAMP,
    process_attempts INTEGER DEFAULT 0,
    
    PRIMARY KEY ( employee_id, date ),
    FOREIGN KEY ( employee_id ) REFERENCES employees( employee_id )
);
COMMENT ON TABLE attendance_raw IS 'Dữ liệu thô từ máy chấm công - application sẽ xử lý';
COMMENT ON COLUMN attendance_raw.data_version IS 'Version tăng mỗi lần update - application dùng để detect change';
COMMENT ON COLUMN attendance_raw.processing_status IS 'Trạng thái xử lý: pending/processing/completed/failed';
COMMENT ON COLUMN attendance_raw.process_attempts IS 'Số lần thử xử lý (cho retry logic)';

-- 4. LEAVES
CREATE TABLE leaves (
    employee_id VARCHAR( 20 ),
    date DATE,
    time_type VARCHAR( 10 ) DEFAULT 'fullday', -- fullday, morning, afternoon  
    leave_reason VARCHAR( 100 ), -- annual, sick, personal, maternity...
    status VARCHAR( 20 ) DEFAULT 'approved',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Application processing flags
    affects_attendance BOOLEAN DEFAULT TRUE,
    processed_at TIMESTAMP,
    
    PRIMARY KEY ( employee_id, date ),
    FOREIGN KEY ( employee_id ) REFERENCES employees( employee_id )
);
COMMENT ON TABLE leaves IS 'Đăng ký nghỉ phép';
COMMENT ON COLUMN leaves.affects_attendance IS 'Có ảnh hưởng đến tính công hay không';

-- 5. EXPLANATION
CREATE TABLE explanations (
    employee_id VARCHAR( 20 ),
    date DATE,
    reason TEXT NOT NULL,
    penalty_reduction_percent INTEGER DEFAULT 0, -- 0-100%
    status VARCHAR( 20 ) DEFAULT 'approved',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Application processing
    processed_at TIMESTAMP,
    
    PRIMARY KEY ( employee_id, date ), 
    FOREIGN KEY ( employee_id ) REFERENCES employees( employee_id )
);
COMMENT ON TABLE explanations IS 'Giải trình vi phạm chấm công';

-- 6. ATTENDANCE PROCESSED (Application output)
CREATE TABLE attendance (
    employee_id VARCHAR( 20 ),
    date DATE,
    
    -- Input snapshot (for debugging)
    raw_check_in TIMESTAMP,
    raw_check_out TIMESTAMP,
    raw_data_version INTEGER, -- Version của raw data khi process
    
    -- Calculated fields
    shift_start TIME,
    shift_end TIME,
    late_minutes INTEGER DEFAULT 0,
    early_minutes INTEGER DEFAULT 0,
    total_violation_minutes INTEGER DEFAULT 0,
    penalty_hours DECIMAL( 3,1 ) DEFAULT 0,
    
    -- Flags
    is_holiday BOOLEAN DEFAULT FALSE,
    is_leave BOOLEAN DEFAULT FALSE,
    is_free_used BOOLEAN DEFAULT FALSE,
    
    -- Application metadata (QUAN TRỌNG cho debugging)
    calculated_by VARCHAR( 50 ), -- Server/process ID
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    calculation_duration_ms INTEGER, -- Performance tracking
    business_rules_version VARCHAR( 20 ), -- Version của rules khi calculate
    
    PRIMARY KEY ( employee_id, date ),
    FOREIGN KEY ( employee_id ) REFERENCES employees( employee_id )
);
COMMENT ON TABLE attendance IS 'Kết quả xử lý chấm công từ application';
COMMENT ON COLUMN attendance.raw_data_version IS 'Version của raw data khi xử lý - để detect stale data';
COMMENT ON COLUMN attendance.calculated_by IS 'Server/process nào thực hiện calculation';
COMMENT ON COLUMN attendance.business_rules_version IS 'Version của business rules khi calculate';

-- 7. MONTHLY EXEMPT
CREATE TABLE monthly_free_usage (
    employee_id VARCHAR( 20 ),
    year_month DATE, -- YYYY-MM-01
    used_count SMALLINT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY ( employee_id, year_month ),
    FOREIGN KEY ( employee_id ) REFERENCES employees( employee_id )
);
COMMENT ON TABLE monthly_free_usage IS 'Track monthly exemptions';

-- 8. PROCESSING LOG (Application debugging)
CREATE TABLE processing_log (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR( 20 ),
    date DATE,
    event_type VARCHAR( 50 ), -- raw_data_change, leave_added, explanation_added, manual_recalc
    old_penalty DECIMAL( 3,1 ),
    new_penalty DECIMAL( 3,1 ),
    processing_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY ( employee_id ) REFERENCES employees( employee_id )
);
COMMENT ON TABLE processing_log IS 'Processing log for debugging and monitoring';
