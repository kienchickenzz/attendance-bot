export interface TimePeriod {
    start_time?: string;
    end_time?: string;
}

export interface SessionContext {
    user_name?: string;
    user_email?: string;
    current_time?: string; // Conductify AI
    time_query?: TimePeriod[];
    topic?: string;
    prev_question?: string;
}

export interface UpsertSessionRequest {
    session_id?: string;
    data?: SessionContext;
}
