export interface TimePeriod {
    start_date?: string
    end_date?: string
}

export interface SessionContext {
    user_name?: string
    user_email?: string
    current_time?: string // Conductify AI
    time_query?: TimePeriod[]
    time_query_str?: string
    topic?: string
    prev_question?: string
    prev_answer?: string
}

export interface UpsertSessionRequest {
    session_id?: string
    data?: SessionContext
}

export interface SearchTimeRequest {
    user_email: string
    time_query: TimePeriod[]
}

export interface SearchTimeResponse {
    data: TimeData[]
}

export interface TimeData {
    date: string           // Format: "YYYY-MM-DD"
    checkin_time: string   // Format: ISO 8601 with UTC "YYYY-MM-DDTHH:MM:SS.fffffZ"
    checkout_time: string  // Format: ISO 8601 with UTC "YYYY-MM-DDTHH:MM:SS.fffffZ"
}

export interface SearchLateRequest {
    user_email: string
    time_query: TimePeriod[]
}

export interface SearchLateResponse {
    data: LateData[]
}

export interface LateData {
    date: string       // Format: "YYYY-MM-DD"
    is_late: boolean   // True if late, false if on time
}

export interface SearchAttendanceRequest {
    user_email: string
    time_query: TimePeriod[]
}

export interface SearchAttendanceResponse {
    data: AttendanceData[]
}

export interface AttendanceData {
    date: string       // Format: "YYYY-MM-DD"
    attendance: number // attendance_count từ database (as float)
}

export interface EmployeeAttendance {
    id: number
    user_email: string
    user_name: string
    checkin_time: Date
    checkout_time: Date | null
    is_late: boolean
    attendance_count: number
}

export interface DayOffRequest {
    time_query: TimePeriod[]
}
