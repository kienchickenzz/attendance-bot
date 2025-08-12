import { MigrationInterface, QueryRunner } from "typeorm";

export class InitialMigration1754997051634 implements MigrationInterface {
    name = 'InitialMigration1754997051634'

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`DROP INDEX "public"."employee_attendance_id_idx"`);
        await queryRunner.query(`DROP INDEX "public"."employee_attendance_user_email_idx"`);
        await queryRunner.query(`ALTER TABLE "employee_attendance" ALTER COLUMN "is_late" SET NOT NULL`);
        await queryRunner.query(`ALTER TABLE "employee_attendance" ALTER COLUMN "is_late" SET DEFAULT false`);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`ALTER TABLE "employee_attendance" ALTER COLUMN "is_late" DROP DEFAULT`);
        await queryRunner.query(`ALTER TABLE "employee_attendance" ALTER COLUMN "is_late" DROP NOT NULL`);
        await queryRunner.query(`CREATE INDEX "employee_attendance_user_email_idx" ON "employee_attendance" ("user_email") `);
        await queryRunner.query(`CREATE INDEX "employee_attendance_id_idx" ON "employee_attendance" ("id") `);
    }

}
