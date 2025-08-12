/* eslint-disable */
import { Entity, PrimaryGeneratedColumn, Column } from "typeorm"

@Entity( { name: "employee_attendance" } )
export class EmployeeAttendance {
    @PrimaryGeneratedColumn()
    id: number

    @Column( { type: "varchar", length: 255 } )
    user_email: string

    @Column( { type: "varchar", length: 255 } )
    user_name: string

    @Column( { type: "timestamp" } )
    checkin_time: Date

    @Column( { type: "timestamp", nullable: true } )
    checkout_time: Date | null

    @Column( { type: "boolean", default: false } )
    is_late: boolean

    @Column( { type: "int" } )
    attendance_count: number
}
