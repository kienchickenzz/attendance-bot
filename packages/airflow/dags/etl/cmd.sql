-- =====================================================
-- POSTGRESQL CHẤM CÔNG - THIẾT KẾ TỐI ƯU & THỰC TẾ
-- Change Detection + Quality Assurance
-- =====================================================

-- 1. NHÂN VIÊN (Simplified)
CREATE TABLE employees (
    employee_id VARCHAR(20) PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    department VARCHAR(50),
    position VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE employees IS 'Thông tin cơ bản nhân viên';
COMMENT ON COLUMN employees.employee_id IS 'Mã nhân viên duy nhất';
COMMENT ON COLUMN employees.email IS 'Email công ty';
COMMENT ON COLUMN employees.full_name IS 'Họ tên đầy đủ';
COMMENT ON COLUMN employees.department IS 'Tên phòng ban';
COMMENT ON COLUMN employees.position IS 'Chức vụ hiện tại';
COMMENT ON COLUMN employees.is_active IS 'Còn làm việc hay không';

-- 2. NGÀY NGHỈ LỄ
CREATE TABLE holidays (
    date DATE PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

COMMENT ON TABLE holidays IS 'Danh sách ngày nghỉ lễ, Tết, cuối tuần';
COMMENT ON COLUMN holidays.date IS 'Ngày nghỉ';
COMMENT ON COLUMN holidays.name IS 'Tên ngày lễ';

-- 3. DỮ LIỆU CHẤM CÔNG RAW (With Change Detection)
CREATE TABLE attendance_raw (
    employee_id VARCHAR(20),
    date DATE,
    first_in TIMESTAMP,
    last_out TIMESTAMP,
    
    -- Change Detection Fields
    data_hash VARCHAR(64), -- MD5 hash của (first_in + last_out) để detect thay đổi
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_count INTEGER DEFAULT 1, -- Số lần bị update
    
    PRIMARY KEY (employee_id, date),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

COMMENT ON TABLE attendance_raw IS 'Dữ liệu thô từ máy chấm công với change detection';
COMMENT ON COLUMN attendance_raw.employee_id IS 'Mã nhân viên';
COMMENT ON COLUMN attendance_raw.date IS 'Ngày chấm công';
COMMENT ON COLUMN attendance_raw.first_in IS 'Lần chấm vào đầu tiên';
COMMENT ON COLUMN attendance_raw.last_out IS 'Lần chấm ra cuối cùng';
COMMENT ON COLUMN attendance_raw.data_hash IS 'Hash MD5 của dữ liệu để detect thay đổi thật';
COMMENT ON COLUMN attendance_raw.last_updated IS 'Thời điểm cập nhật gần nhất';
COMMENT ON COLUMN attendance_raw.update_count IS 'Số lần record này bị update';

-- 4. NGHỈ PHÉP (Simplified - No separate types table)
CREATE TABLE leaves (
    employee_id VARCHAR(20),
    date DATE,
    time_type VARCHAR(10) DEFAULT 'fullday', -- fullday, morning, afternoon
    leave_reason VARCHAR(100), -- Lý do nghỉ: annual, sick, personal, maternity...
    status VARCHAR(20) DEFAULT 'approved',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (employee_id, date),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

COMMENT ON TABLE leaves IS 'Đăng ký nghỉ phép được duyệt';
COMMENT ON COLUMN leaves.employee_id IS 'Mã nhân viên nghỉ phép';
COMMENT ON COLUMN leaves.date IS 'Ngày nghỉ phép';
COMMENT ON COLUMN leaves.time_type IS 'Thời gian nghỉ: fullday/morning/afternoon';
COMMENT ON COLUMN leaves.leave_reason IS 'Loại nghỉ phép: annual/sick/personal/maternity';
COMMENT ON COLUMN leaves.status IS 'Trạng thái duyệt: approved/pending/rejected';

-- 5. GIẢI TRÌNH VI PHẠM
CREATE TABLE explanations (
    employee_id VARCHAR(20),
    date DATE,
    reason TEXT NOT NULL,
    penalty_reduction_percent INTEGER DEFAULT 0, -- 0-100%
    status VARCHAR(20) DEFAULT 'approved',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (employee_id, date),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

COMMENT ON TABLE explanations IS 'Giải trình vi phạm chấm công';
COMMENT ON COLUMN explanations.employee_id IS 'Mã nhân viên giải trình';
COMMENT ON COLUMN explanations.date IS 'Ngày vi phạm cần giải trình';
COMMENT ON COLUMN explanations.reason IS 'Lý do giải trình chi tiết';
COMMENT ON COLUMN explanations.penalty_reduction_percent IS 'Phần trăm giảm phạt (0-100%)';
COMMENT ON COLUMN explanations.status IS 'Trạng thái duyệt giải trình';

-- 6. CHẤM CÔNG PROCESSED (Main working table)
CREATE TABLE attendance (
    employee_id VARCHAR(20),
    date DATE,
    
    -- Raw data snapshot
    check_in TIMESTAMP,
    check_out TIMESTAMP,
    
    -- Calculated fields  
    shift_start TIME DEFAULT '08:15:00',
    shift_end TIME DEFAULT '17:30:00',
    late_minutes INTEGER DEFAULT 0,
    penalty_hours DECIMAL(3,1) DEFAULT 0,
    
    -- Status flags
    is_holiday BOOLEAN DEFAULT FALSE,
    is_leave BOOLEAN DEFAULT FALSE,
    is_free_used BOOLEAN DEFAULT FALSE,
    
    -- Processing metadata
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_hash VARCHAR(64), -- Hash từ raw data để detect khi raw thay đổi
    
    PRIMARY KEY (employee_id, date),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

COMMENT ON TABLE attendance IS 'Dữ liệu chấm công đã xử lý - bảng chính để query';
COMMENT ON COLUMN attendance.employee_id IS 'Mã nhân viên';
COMMENT ON COLUMN attendance.date IS 'Ngày chấm công';
COMMENT ON COLUMN attendance.check_in IS 'Thời gian check-in (copy từ raw data)';
COMMENT ON COLUMN attendance.check_out IS 'Thời gian check-out (copy từ raw data)';
COMMENT ON COLUMN attendance.shift_start IS 'Giờ bắt đầu ca chuẩn (có thể adjust theo nghỉ phép)';
COMMENT ON COLUMN attendance.shift_end IS 'Giờ kết thúc ca chuẩn (có thể adjust theo nghỉ phép)';
COMMENT ON COLUMN attendance.late_minutes IS 'Số phút đi muộn';
COMMENT ON COLUMN attendance.penalty_hours IS 'Số giờ bị phạt cuối cùng';
COMMENT ON COLUMN attendance.is_holiday IS 'Có phải ngày nghỉ lễ không';
COMMENT ON COLUMN attendance.is_leave IS 'Có nghỉ phép không';
COMMENT ON COLUMN attendance.is_free_used IS 'Đã dùng lượt miễn phạt không';
COMMENT ON COLUMN attendance.calculated_at IS 'Thời điểm tính toán gần nhất';
COMMENT ON COLUMN attendance.source_hash IS 'Hash của raw data để detect thay đổi';

-- 7. MIỄN PHẠT HÀNG THÁNG
CREATE TABLE monthly_free_usage (
    employee_id VARCHAR(20),
    year_month DATE, -- YYYY-MM-01
    used_count SMALLINT DEFAULT 0,
    
    PRIMARY KEY (employee_id, year_month),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

COMMENT ON TABLE monthly_free_usage IS 'Theo dõi lượt miễn phạt đi muộn theo tháng';
COMMENT ON COLUMN monthly_free_usage.employee_id IS 'Mã nhân viên';
COMMENT ON COLUMN monthly_free_usage.year_month IS 'Tháng (lưu ngày đầu tháng YYYY-MM-01)';
COMMENT ON COLUMN monthly_free_usage.used_count IS 'Số lượt miễn phạt đã sử dụng trong tháng (max 5)';

-- =====================================================
-- CHANGE DETECTION SYSTEM (Core Innovation)
-- =====================================================

-- Function tính hash của raw data
CREATE OR REPLACE FUNCTION calculate_raw_hash(emp_id VARCHAR(20), att_date DATE)
RETURNS VARCHAR(64) AS $$
DECLARE
    hash_input TEXT;
BEGIN
    SELECT CONCAT(
        COALESCE(first_in::TEXT, 'NULL'), '|',
        COALESCE(last_out::TEXT, 'NULL')
    ) INTO hash_input
    FROM attendance_raw 
    WHERE employee_id = emp_id AND date = att_date;
    
    RETURN MD5(hash_input);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_raw_hash IS 'Tính hash MD5 của raw data để detect thay đổi';

-- Function kiểm tra raw data có thay đổi không
CREATE OR REPLACE FUNCTION has_raw_data_changed(emp_id VARCHAR(20), att_date DATE)
RETURNS BOOLEAN AS $$
DECLARE
    current_hash VARCHAR(64);
    stored_hash VARCHAR(64);
BEGIN
    -- Get current hash from raw data
    SELECT calculate_raw_hash(emp_id, att_date) INTO current_hash;
    
    -- Get stored hash from processed data
    SELECT source_hash INTO stored_hash
    FROM attendance 
    WHERE employee_id = emp_id AND date = att_date;
    
    -- Return TRUE if different or no processed record exists
    RETURN (stored_hash IS NULL OR stored_hash != current_hash);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION has_raw_data_changed IS 'Kiểm tra raw data có thay đổi so với lần process cuối';

-- =====================================================
-- BUSINESS LOGIC FUNCTIONS
-- =====================================================

-- Function tính penalty theo rules
CREATE OR REPLACE FUNCTION calculate_late_penalty(late_mins INTEGER, has_free BOOLEAN)
RETURNS DECIMAL(3,1) AS $$
BEGIN
    IF late_mins <= 0 THEN 
        RETURN 0;
    END IF;
    
    -- Chỉ áp dụng miễn phạt cho 1-15 phút đi muộn
    IF late_mins BETWEEN 1 AND 15 AND has_free THEN
        RETURN 0;
    END IF;
    
    -- Rules penalty
    RETURN CASE
        WHEN late_mins BETWEEN 1 AND 15 THEN 1.0
        WHEN late_mins BETWEEN 16 AND 60 THEN 1.0
        WHEN late_mins BETWEEN 61 AND 120 THEN 2.0
        WHEN late_mins BETWEEN 121 AND 240 THEN 4.0
        WHEN late_mins BETWEEN 241 AND 360 THEN 6.0
        ELSE 8.0
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION calculate_late_penalty IS 'Tính số giờ phạt dựa theo rules và miễn phạt';

-- Function xử lý 1 attendance record
CREATE OR REPLACE FUNCTION process_attendance_record(emp_id VARCHAR(20), att_date DATE)
RETURNS VOID AS $$
DECLARE
    raw_rec attendance_raw%ROWTYPE;
    shift_start_time TIME := '08:15:00';
    shift_end_time TIME := '17:30:00';
    late_mins INTEGER := 0;
    penalty DECIMAL(3,1) := 0;
    is_holiday_day BOOLEAN := FALSE;
    is_leave_day BOOLEAN := FALSE;
    leave_time_type VARCHAR(10);
    has_free BOOLEAN := FALSE;
    use_free BOOLEAN := FALSE;
    current_month DATE;
    current_free_count INTEGER;
    reduction_percent INTEGER := 0;
    current_hash VARCHAR(64);
BEGIN
    -- Get raw data
    SELECT * INTO raw_rec FROM attendance_raw WHERE employee_id = emp_id AND date = att_date;
    IF NOT FOUND THEN
        RETURN; -- Không có raw data thì không process
    END IF;
    
    -- Calculate current hash
    current_hash := calculate_raw_hash(emp_id, att_date);
    
    -- Check holiday
    SELECT EXISTS(SELECT 1 FROM holidays WHERE date = att_date) INTO is_holiday_day;
    
    -- Check leave và adjust shift
    SELECT 
        EXISTS(SELECT 1 FROM leaves WHERE employee_id = emp_id AND date = att_date AND status = 'approved'),
        COALESCE(time_type, 'fullday')
    INTO is_leave_day, leave_time_type
    FROM leaves WHERE employee_id = emp_id AND date = att_date AND status = 'approved'
    LIMIT 1;
    
    -- Adjust shift times based on leave
    IF is_leave_day THEN
        CASE leave_time_type
            WHEN 'morning' THEN shift_start_time := '13:15:00';
            WHEN 'afternoon' THEN shift_end_time := '12:00:00';
            WHEN 'fullday' THEN 
                shift_start_time := NULL;
                shift_end_time := NULL;
        END CASE;
    END IF;
    
    -- Calculate violations (chỉ khi không holiday và không nghỉ full)
    IF NOT is_holiday_day AND (NOT is_leave_day OR leave_time_type != 'fullday') AND raw_rec.first_in IS NOT NULL THEN
        
        -- Calculate late minutes
        IF shift_start_time IS NOT NULL AND raw_rec.first_in::TIME > shift_start_time THEN
            late_mins := EXTRACT(EPOCH FROM (raw_rec.first_in::TIME - shift_start_time)) / 60;
        END IF;
        
        -- Check free count availability
        current_month := DATE_TRUNC('month', att_date);
        SELECT COALESCE(used_count, 0) INTO current_free_count
        FROM monthly_free_usage 
        WHERE employee_id = emp_id AND year_month = current_month;
        
        has_free := (COALESCE(current_free_count, 0) < 5);
        
        -- Calculate penalty
        penalty := calculate_late_penalty(late_mins, has_free);
        use_free := (late_mins BETWEEN 1 AND 15 AND has_free AND penalty = 0);
        
        -- Apply explanation reduction if exists
        SELECT COALESCE(penalty_reduction_percent, 0) INTO reduction_percent
        FROM explanations 
        WHERE employee_id = emp_id AND date = att_date AND status = 'approved';
        
        penalty := penalty * (100 - reduction_percent) / 100.0;
        
        -- Update free count if used
        IF use_free THEN
            INSERT INTO monthly_free_usage (employee_id, year_month, used_count)
            VALUES (emp_id, current_month, 1)
            ON CONFLICT (employee_id, year_month) 
            DO UPDATE SET used_count = monthly_free_usage.used_count + 1;
        END IF;
    END IF;
    
    -- Upsert attendance record
    INSERT INTO attendance (
        employee_id, date, check_in, check_out, shift_start, shift_end,
        late_minutes, penalty_hours, is_holiday, is_leave, is_free_used,
        calculated_at, source_hash
    ) VALUES (
        emp_id, att_date, raw_rec.first_in, raw_rec.last_out, shift_start_time, shift_end_time,
        late_mins, penalty, is_holiday_day, is_leave_day, use_free,
        CURRENT_TIMESTAMP, current_hash
    ) ON CONFLICT (employee_id, date) DO UPDATE SET
        check_in = EXCLUDED.check_in,
        check_out = EXCLUDED.check_out,
        shift_start = EXCLUDED.shift_start,
        shift_end = EXCLUDED.shift_end,
        late_minutes = EXCLUDED.late_minutes,
        penalty_hours = EXCLUDED.penalty_hours,
        is_holiday = EXCLUDED.is_holiday,
        is_leave = EXCLUDED.is_leave,
        is_free_used = EXCLUDED.is_free_used,
        calculated_at = CURRENT_TIMESTAMP,
        source_hash = EXCLUDED.source_hash;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION process_attendance_record IS 'Xử lý tính toán chấm công cho 1 nhân viên 1 ngày';

-- =====================================================
-- SMART TRIGGERS (Only fire when actual changes)
-- =====================================================

-- Trigger function for attendance_raw changes
CREATE OR REPLACE FUNCTION trigger_attendance_raw_change()
RETURNS TRIGGER AS $$
DECLARE
    old_hash VARCHAR(64);
    new_hash VARCHAR(64);
BEGIN
    -- Calculate hashes
    IF TG_OP = 'INSERT' THEN
        new_hash := MD5(CONCAT(
            COALESCE(NEW.first_in::TEXT, 'NULL'), '|',
            COALESCE(NEW.last_out::TEXT, 'NULL')
        ));
        NEW.data_hash := new_hash;
        NEW.update_count := 1;
        
        -- Process new record
        PERFORM process_attendance_record(NEW.employee_id, NEW.date);
        
    ELSIF TG_OP = 'UPDATE' THEN
        old_hash := MD5(CONCAT(
            COALESCE(OLD.first_in::TEXT, 'NULL'), '|',
            COALESCE(OLD.last_out::TEXT, 'NULL')
        ));
        new_hash := MD5(CONCAT(
            COALESCE(NEW.first_in::TEXT, 'NULL'), '|',
            COALESCE(NEW.last_out::TEXT, 'NULL')
        ));
        
        -- Chỉ process khi có thay đổi thật sự
        IF old_hash != new_hash THEN
            NEW.data_hash := new_hash;
            NEW.last_updated := CURRENT_TIMESTAMP;
            NEW.update_count := OLD.update_count + 1;
            
            -- Process changed record
            PERFORM process_attendance_record(NEW.employee_id, NEW.date);
        ELSE
            -- Không có thay đổi thật sự, giữ nguyên metadata
            NEW.data_hash := OLD.data_hash;
            NEW.last_updated := OLD.last_updated;
            NEW.update_count := OLD.update_count;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER attendance_raw_change_detection
    BEFORE INSERT OR UPDATE ON attendance_raw
    FOR EACH ROW EXECUTE FUNCTION trigger_attendance_raw_change();

COMMENT ON TRIGGER attendance_raw_change_detection ON attendance_raw IS 'Trigger detect thay đổi thật sự và auto-process';

-- Trigger khi có leave/explanation thay đổi
CREATE OR REPLACE FUNCTION trigger_attendance_dependency_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Recalculate affected attendance record
    IF TG_TABLE_NAME = 'leaves' AND (NEW.status = 'approved' OR OLD.status != NEW.status) THEN
        PERFORM process_attendance_record(NEW.employee_id, NEW.date);
    END IF;
    
    IF TG_TABLE_NAME = 'explanations' AND (NEW.status = 'approved' OR OLD.status != NEW.status) THEN
        PERFORM process_attendance_record(NEW.employee_id, NEW.date);
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER leaves_change_trigger
    AFTER INSERT OR UPDATE ON leaves
    FOR EACH ROW EXECUTE FUNCTION trigger_attendance_dependency_change();

CREATE TRIGGER explanations_change_trigger
    AFTER INSERT OR UPDATE ON explanations
    FOR EACH ROW EXECUTE FUNCTION trigger_attendance_dependency_change();

-- =====================================================
-- INDEXES OPTIMIZED
-- =====================================================

CREATE INDEX idx_attendance_date ON attendance (date); -- Monthly reports
CREATE INDEX idx_attendance_penalty ON attendance (penalty_hours) WHERE penalty_hours > 0; -- Violations only
CREATE INDEX idx_raw_last_updated ON attendance_raw (last_updated); -- Find recent changes
CREATE INDEX idx_leaves_status_date ON leaves (status, date); -- Approved leaves

-- =====================================================
-- VIEWS BÁO CÁO (2 views chính theo requirements)
-- =====================================================

-- 1. Monthly Summary Report
CREATE VIEW monthly_summary AS
SELECT 
    TO_CHAR(date, 'YYYY-MM') as month,
    department,
    COUNT(DISTINCT a.employee_id) as total_employees,
    COUNT(*) as working_days,
    COUNT(CASE WHEN late_minutes > 0 THEN 1 END) as violation_days,
    SUM(penalty_hours) as total_penalty_hours,
    COUNT(CASE WHEN is_free_used THEN 1 END) as free_used_count,
    ROUND(AVG(late_minutes), 1) as avg_late_minutes
FROM attendance a
JOIN employees e ON a.employee_id = e.employee_id  
WHERE NOT is_holiday
GROUP BY TO_CHAR(date, 'YYYY-MM'), department
ORDER BY month DESC, department;

COMMENT ON VIEW monthly_summary IS 'Báo cáo tổng hợp vi phạm theo tháng và phòng ban';

-- 2. Individual Violations Report  
CREATE VIEW individual_violations AS
SELECT 
    a.employee_id,
    e.full_name,
    e.department,
    a.date,
    a.late_minutes,
    a.penalty_hours,
    a.is_free_used,
    CASE 
        WHEN a.is_free_used THEN 'Miễn phạt'
        WHEN a.penalty_hours > 0 THEN 'Phạt ' || a.penalty_hours || ' giờ'  
        ELSE 'Không vi phạm'
    END as penalty_status
FROM attendance a
JOIN employees e ON a.employee_id = e.employee_id
WHERE a.late_minutes > 0 AND NOT a.is_holiday
ORDER BY a.date DESC, a.penalty_hours DESC;

COMMENT ON VIEW individual_violations IS 'Báo cáo chi tiết vi phạm từng nhân viên';

-- =====================================================
-- BATCH UTILITIES
-- =====================================================

-- Function xử lý batch tất cả raw data thay đổi
CREATE OR REPLACE FUNCTION process_all_changed_records()
RETURNS TABLE(processed_count INTEGER, skipped_count INTEGER) AS $$
DECLARE
    rec RECORD;
    processed INTEGER := 0;
    skipped INTEGER := 0;
BEGIN
    FOR rec IN 
        SELECT DISTINCT employee_id, date 
        FROM attendance_raw
        ORDER BY date DESC, employee_id
    LOOP
        IF has_raw_data_changed(rec.employee_id, rec.date) THEN
            PERFORM process_attendance_record(rec.employee_id, rec.date);
            processed := processed + 1;
        ELSE
            skipped := skipped + 1;
        END IF;
    END LOOP;
    
    RETURN QUERY SELECT processed, skipped;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION process_all_changed_records IS 'Xử lý batch tất cả records có thay đổi';

-- =====================================================
-- DATA CLEANUP (1 năm)
-- =====================================================

-- Function cleanup data cũ
CREATE OR REPLACE FUNCTION cleanup_old_attendance_data()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    WITH deleted AS (
        DELETE FROM attendance_raw 
        WHERE date < CURRENT_DATE - INTERVAL '1 year'
        RETURNING *
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted;
    
    DELETE FROM attendance WHERE date < CURRENT_DATE - INTERVAL '1 year';
    DELETE FROM monthly_free_usage WHERE year_month < DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 year');
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_old_attendance_data IS 'Xóa dữ liệu chấm công cũ hơn 1 năm';

-- =====================================================
-- SAMPLE DATA
-- =====================================================

INSERT INTO employees VALUES ('EMP001', 'ltthuy4@cmc.com.vn', 'LÊ THỊ THUỶ', 'IT', 'Developer', TRUE);

INSERT INTO holidays VALUES 
('2025-01-01', 'Tết Dương lịch'),
('2025-04-30', 'Giải phóng miền Nam'),
('2025-05-01', 'Quốc tế lao động');

-- =====================================================
-- USAGE EXAMPLES
-- =====================================================

/*
-- Test scenario: Raw data update liên tục
INSERT INTO attendance_raw VALUES ('EMP001', '2025-08-01', '2025-08-01 08:16:00', '2025-08-01 17:30:00');
-- → Auto process, penalty = 1 giờ

UPDATE attendance_raw SET last_out = '2025-08-01 19:24:00' WHERE employee_id = 'EMP001' AND date = '2025-08-01';
-- → Hash changed, auto reprocess (penalty vẫn = 1 giờ vì chỉ last_out đổi)

UPDATE attendance_raw SET first_in = '2025-08-01 08:16:00' WHERE employee_id = 'EMP001' AND date = '2025-08-01';
-- → Hash không đổi, skip processing

-- Test temporal dependencies
INSERT INTO explanations VALUES ('EMP001', '2025-08-01', 'Tắc đường do mưa', 50, 'approved');
-- → Auto recalculate: penalty = 0.5 giờ

-- Manual batch processing nếu cần
SELECT * FROM process_all_changed_records();

-- View reports
SELECT * FROM monthly_summary WHERE month = '2025-08';
SELECT * FROM individual_violations WHERE employee_id = 'EMP001';
*/