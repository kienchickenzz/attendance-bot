export const SHIFTCONFIG = {
    normal: {
        checkInReference: "08:15",
        checkOutReference: "17:30"
    },
    leaveMorning: {
        checkInReference: "13:15", // start day = afternoon
        checkOutReference: "17:30"
    },
    leaveAfternoon: {
        checkInReference: "08:15",
        checkOutReference: "12:00" // end day = morning
    },
    leaveFullDay: {
        checkInReference: null,
        checkOutReference: null
    }
}

export const RULES = [
    // 1 - 15 min
    {
        min: 1,
        max: 15,
        deduct: ( free ) => ( free > 0 ? 0 : 1 ),
    },
    // 15 - 60 min
    {
        min: 16,
        max: 60,
        deduct: () => 1,
    },
    // 1 - 2 hour(s)
    {
        min: 61,
        max: 120,
        deduct: () => 2,
    },
    // 2 - 4 hours
    {
        min: 121,
        max: 240,
        deduct: () => 4,
    },
    // 4 - 6 hours
    {
        min: 241,
        max: 360,
        deduct: () => 6,
    },
    // 6 - 8 hours
    {
        min: 361,
        max: 480,
        deduct: () => 8,
    },
]
