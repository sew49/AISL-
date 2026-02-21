-- =====================================================
-- ATTENDANCE SYSTEM - BUSINESS LOGIC (Layer 2)
-- Functions, Triggers, and Views
-- Features: Saturday Half-Days, October Fiscal Year
-- =====================================================

-- =====================================================
-- FUNCTION 1: Get Fiscal Year from Date
-- Fiscal year starts in October (Oct 1 - Sep 30)
-- For example: '2025-10-15' returns 2026, '2025-09-15' returns 2025
-- =====================================================
CREATE OR REPLACE FUNCTION get_fiscal_year(p_date DATE)
RETURNS INT AS $$
BEGIN
    -- If month is October or later, fiscal year is next calendar year
    -- Otherwise, fiscal year is current calendar year
    IF EXTRACT(MONTH FROM p_date) >= 10 THEN
        RETURN EXTRACT(YEAR FROM p_date) + 1;
    ELSE
        RETURN EXTRACT(YEAR FROM p_date);
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION get_fiscal_year(DATE) IS 
'Returns fiscal year for a given date. Fiscal year starts in October. For example, 2025-10-15 returns 2026.';


-- =====================================================
-- FUNCTION 2: Calculate Work Hours
-- Handles Saturday half-days (4 hours instead of 8)
-- =====================================================
CREATE OR REPLACE FUNCTION calculate_work_hours(
    p_clock_in TIME,
    p_clock_out TIME,
    p_work_date DATE
)
RETURNS DECIMAL(4,2) AS $$
DECLARE
    v_hours DECIMAL(4,2);
    v_is_saturday BOOLEAN;
BEGIN
    -- Check if it's Saturday
    v_is_saturday := EXTRACT(DOW FROM p_work_date) = 6; -- 6 = Saturday
    
    -- Calculate total hours
    IF p_clock_in IS NOT NULL AND p_clock_out IS NOT NULL THEN
        v_hours := EXTRACT(EPOCH FROM (p_clock_out - p_clock_in)) / 3600;
        
        -- Cap at standard hours
        IF v_is_saturday THEN
            -- Saturday: cap at 4 hours (half day)
            RETURN LEAST(v_hours, 4.00);
        ELSE
            -- Weekday: cap at 8 hours
            RETURN LEAST(v_hours, 8.00);
        END IF;
    ELSE
        RETURN 0.00;
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION calculate_work_hours(TIME, TIME, DATE) IS 
'Calculates work hours. Saturdays are capped at 4 hours (half-day).';

-- =====================================================
-- FUNCTION 3: Determine Day Type
-- Auto-detects Saturday Half Days and Holidays
-- =====================================================
CREATE OR REPLACE FUNCTION determine_day_type(
    p_work_date DATE,
    p_clock_in TIME,
    p_clock_out TIME
)
RETURNS VARCHAR(20) AS $$
DECLARE
    v_dow INT;
    v_hours DECIMAL(4,2);
BEGIN
    v_dow := EXTRACT(DOW FROM p_work_date);
    
    -- Sunday (0) - typically holiday
    IF v_dow = 0 THEN
        RETURN 'Holiday';
    END IF;
    
    -- Saturday (6) - half day
    IF v_dow = 6 THEN
        IF p_clock_in IS NOT NULL THEN
            RETURN 'Saturday Half Day';
        ELSE
            RETURN 'Holiday'; -- If not working, it's a holiday
        END IF;
    END IF;
    
    -- Weekdays - check if worked
    IF p_clock_in IS NULL THEN
        RETURN 'Absent';
    END IF;
    
    -- Calculate hours to determine full or half day
    v_hours := EXTRACT(EPOCH FROM (p_clock_out - p_clock_in)) / 3600;
    
    IF v_hours >= 6 THEN
        RETURN 'Full Day';
    ELSE
        RETURN 'Half Day';
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- =====================================================
-- FUNCTION 4: Calculate Leave Days Between Dates
-- Excludes Sundays and counts Saturdays as half days
-- =====================================================
CREATE OR REPLACE FUNCTION calculate_leave_days(
    p_start_date DATE,
    p_end_date DATE
)
RETURNS DECIMAL(5,2) AS $$
DECLARE
    v_current_date DATE;
    v_total_days DECIMAL(5,2) := 0;
    v_dow INT;
BEGIN
    v_current_date := p_start_date;
    
    WHILE v_current_date <= p_end_date LOOP
        v_dow := EXTRACT(DOW FROM v_current_date);
        
        -- Sunday = 0, skip
        IF v_dow = 0 THEN
            v_total_days := v_total_days;
        -- Saturday = 6, count as 0.5
        ELSIF v_dow = 6 THEN
            v_total_days := v_total_days + 0.5;
        -- Weekdays, count as 1
        ELSE
            v_total_days := v_total_days + 1;
        END IF;
        
        v_current_date := v_current_date + 1;
    END LOOP;
    
    RETURN v_total_days;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION calculate_leave_days(DATE, DATE) IS 
'Calculates leave days excluding Sundays, Saturdays count as 0.5 days';

-- =====================================================
-- TRIGGER 1: Auto-update Attendance on Insert/Update
-- Automatically sets DayType and WorkHours
-- =====================================================
CREATE OR REPLACE FUNCTION trg_update_attendance()
RETURNS TRIGGER AS $$
BEGIN
    -- Determine day type
    NEW.DayType := determine_day_type(NEW.WorkDate, NEW.ClockIn, NEW.ClockOut);
    
    -- Calculate work hours
    NEW.WorkHours := calculate_work_hours(NEW.ClockIn, NEW.ClockOut, NEW.WorkDate);
    
    -- Update status based on day type
    IF NEW.DayType = 'Absent' THEN
        NEW.Status := 'Absent';
    ELSIF NEW.DayType = 'Saturday Half Day' THEN
        NEW.Status := 'Half Day';
    ELSIF NEW.DayType = 'Holiday' THEN
        NEW.Status := 'Holiday';
    ELSIF NEW.DayType = 'Half Day' THEN
        NEW.Status := 'Half Day';
    ELSE
        NEW.Status := 'Present';
    END IF;
    
    -- Update timestamp
    NEW.UpdatedAt := CURRENT_TIMESTAMP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_attendance_before_insert_update
    BEFORE INSERT OR UPDATE ON Attendance
    FOR EACH ROW
    EXECUTE FUNCTION trg_update_attendance();

COMMENT ON TRIGGER trg_attendance_before_insert_update ON Attendance IS 
'Auto-calculates DayType, WorkHours, and Status based on clock times';

-- =====================================================
-- TRIGGER 2: Update Leave Balance on Approved Leave
-- =====================================================
CREATE OR REPLACE FUNCTION trg_update_leave_balance()
RETURNS TRIGGER AS $$
DECLARE
    v_fiscal_year INT;
    v_column_name VARCHAR(50);
BEGIN
    -- Only process if status changed to Approved
    IF NEW.Status = 'Approved' AND (OLD.Status IS NULL OR OLD.Status != 'Approved') THEN
        -- Get fiscal year for the leave start date
        v_fiscal_year := get_fiscal_year(NEW.StartDate);
        
        -- Determine which balance column to update
        CASE NEW.LeaveType
            WHEN 'Annual' THEN
                UPDATE LeaveBalances 
                SET UsedAnnualDays = UsedAnnualDays + NEW.TotalDays,
                    UpdatedAt = CURRENT_TIMESTAMP
                WHERE EmpID = NEW.EmpID AND FiscalYear = v_fiscal_year;
            WHEN 'Sick' THEN
                UPDATE LeaveBalances 
                SET UsedSickDays = UsedSickDays + NEW.TotalDays,
                    UpdatedAt = CURRENT_TIMESTAMP
                WHERE EmpID = NEW.EmpID AND FiscalYear = v_fiscal_year;
            WHEN 'Absent' THEN
                UPDATE LeaveBalances 
                SET AbsentDays = AbsentDays + NEW.TotalDays,
                    UpdatedAt = CURRENT_TIMESTAMP
                WHERE EmpID = NEW.EmpID AND FiscalYear = v_fiscal_year;
            ELSE
                NULL; -- Do nothing for other types
        END CASE;

    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_leaverequest_after_update
    AFTER UPDATE ON LeaveRequests
    FOR EACH ROW
    EXECUTE FUNCTION trg_update_leave_balance();

COMMENT ON TRIGGER trg_leaverequest_after_update ON LeaveRequests IS 
'Updates leave balance when a leave request is approved';

-- =====================================================
-- TRIGGER 3: Auto-calculate Total Days on Leave Request
-- =====================================================
CREATE OR REPLACE FUNCTION trg_calculate_leave_days()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate total days using business days logic
    NEW.TotalDays := calculate_leave_days(NEW.StartDate, NEW.EndDate);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_leaverequest_before_insert_update
    BEFORE INSERT OR UPDATE ON LeaveRequests
    FOR EACH ROW
    EXECUTE FUNCTION trg_calculate_leave_days();

COMMENT ON TRIGGER trg_leaverequest_before_insert_update ON LeaveRequests IS 
'Auto-calculates TotalDays excluding Sundays, Saturdays as 0.5';

-- =====================================================
-- VIEW 1: Employee Attendance Summary
-- =====================================================
CREATE OR REPLACE VIEW vw_employee_attendance_summary AS
SELECT 
    e.EmpID,
    e.EmployeeCode,
    e.FirstName || ' ' || e.LastName AS FullName,
    a.WorkDate,
    a.ClockIn,
    a.ClockOut,
    a.DayType,
    a.WorkHours,
    a.Status,
    get_fiscal_year(a.WorkDate) AS FiscalYear
FROM Employees e
LEFT JOIN Attendance a ON e.EmpID = a.EmpID
WHERE e.IsActive = TRUE
ORDER BY e.EmpID, a.WorkDate;

COMMENT ON VIEW vw_employee_attendance_summary IS 
'Daily attendance summary with fiscal year information';

-- =====================================================
-- VIEW 2: Leave Balance Summary
-- =====================================================
CREATE OR REPLACE VIEW vw_leave_balance_summary AS
SELECT 
    e.EmpID,
    e.EmployeeCode,
    e.FirstName || ' ' || e.LastName AS FullName,
    lb.FiscalYear,
    fy.StartDate AS FiscalYearStart,
    fy.EndDate AS FiscalYearEnd,
    lb.AnnualDays,
    lb.UsedAnnualDays,
    (lb.AnnualDays - lb.UsedAnnualDays) AS RemainingAnnualDays,
    lb.SickDays,
    lb.UsedSickDays,
    (lb.SickDays - lb.UsedSickDays) AS RemainingSickDays,
    lb.CasualDays,
    lb.UsedCasualDays,
    (lb.CasualDays - lb.UsedCasualDays) AS RemainingCasualDays,
    lb.CarryForwardDays,
    lb.AbsentDays
FROM Employees e
JOIN LeaveBalances lb ON e.EmpID = lb.EmpID
JOIN FiscalYears fy ON lb.FiscalYear = fy.FiscalYear
WHERE e.IsActive = TRUE
ORDER BY e.EmpID, lb.FiscalYear;

COMMENT ON VIEW vw_leave_balance_summary IS 
'Leave balance summary with remaining days calculation';

-- =====================================================
-- VIEW 3: Monthly Attendance Report
-- =====================================================
CREATE OR REPLACE VIEW vw_monthly_attendance_report AS
SELECT 
    e.EmpID,
    e.EmployeeCode,
    e.FirstName || ' ' || e.LastName AS FullName,
    DATE_TRUNC('month', a.WorkDate) AS Month,
    get_fiscal_year(a.WorkDate) AS FiscalYear,
    COUNT(CASE WHEN a.Status = 'Present' THEN 1 END) AS FullDaysPresent,
    COUNT(CASE WHEN a.Status = 'Half Day' OR a.DayType = 'Saturday Half Day' THEN 1 END) AS HalfDays,
    COUNT(CASE WHEN a.Status = 'Absent' THEN 1 END) AS AbsentDays,
    COUNT(CASE WHEN a.Status = 'On Leave' THEN 1 END) AS LeaveDays,
    SUM(a.WorkHours) AS TotalWorkHours,
    COUNT(CASE WHEN a.DayType = 'Saturday Half Day' THEN 1 END) AS SaturdaysWorked
FROM Employees e
LEFT JOIN Attendance a ON e.EmpID = a.EmpID
WHERE e.IsActive = TRUE
GROUP BY e.EmpID, e.EmployeeCode, e.FirstName, e.LastName, 
         DATE_TRUNC('month', a.WorkDate), get_fiscal_year(a.WorkDate)
ORDER BY Month DESC, e.EmpID;

COMMENT ON VIEW vw_monthly_attendance_report IS 
'Monthly attendance statistics including Saturday half-days';

-- =====================================================
-- VIEW 4: Employee Remaining Leave for Current Fiscal Year
-- Calculates remaining leave by subtracting used days from 21-day entitlement
-- =====================================================
CREATE OR REPLACE VIEW vw_EmployeeRemainingLeave AS
SELECT 
    e.EmpID,
    e.EmployeeCode,
    e.FirstName || ' ' || e.LastName AS FullName,
    e.Department,
    get_fiscal_year(CURRENT_DATE) AS CurrentFiscalYear,
    -- Annual Leave
    COALESCE(lb.AnnualDays, 21) AS AnnualEntitlement,
    COALESCE(lb.UsedAnnualDays, 0) AS UsedAnnualDays,
    COALESCE(lb.AnnualDays, 21) - COALESCE(lb.UsedAnnualDays, 0) AS RemainingAnnualDays,
    -- Sick Leave
    COALESCE(lb.SickDays, 10) AS SickEntitlement,
    COALESCE(lb.UsedSickDays, 0) AS UsedSickDays,
    COALESCE(lb.SickDays, 10) - COALESCE(lb.UsedSickDays, 0) AS RemainingSickDays,
    -- Casual Leave
    COALESCE(lb.CasualDays, 5) AS CasualEntitlement,
    COALESCE(lb.UsedCasualDays, 0) AS UsedCasualDays,
    COALESCE(lb.CasualDays, 5) - COALESCE(lb.UsedCasualDays, 0) AS RemainingCasualDays,
    -- Carry Forward
    COALESCE(lb.CarryForwardDays, 0) AS CarryForwardDays,
    -- Total Available (Annual + Carry Forward)
    COALESCE(lb.AnnualDays, 21) - COALESCE(lb.UsedAnnualDays, 0) + COALESCE(lb.CarryForwardDays, 0) AS TotalAvailableAnnual
FROM Employees e
LEFT JOIN LeaveBalances lb ON e.EmpID = lb.EmpID 
    AND lb.FiscalYear = get_fiscal_year(CURRENT_DATE)
WHERE e.IsActive = TRUE
ORDER BY e.EmpID;

COMMENT ON VIEW vw_EmployeeRemainingLeave IS 
'Shows remaining leave days for current fiscal year (21-day annual entitlement minus used days from LeaveRequests)';

-- =====================================================
-- VIEW 5: Monthly Employee Report
-- Shows total hours, leave days, sick/absent days, and underworked flag
-- =====================================================
CREATE OR REPLACE VIEW vw_monthly_employee_report AS
WITH monthly_attendance AS (
    SELECT 
        EmpID,
        DATE_TRUNC('month', WorkDate) AS ReportMonth,
        SUM(WorkHours) AS TotalHoursWorked,
        COUNT(CASE WHEN DayType = 'Saturday Half Day' AND ClockIn IS NOT NULL THEN 1 END) AS SaturdaysWorked,
        COUNT(CASE WHEN Status = 'Absent' THEN 1 END) AS AbsentDays,
        COUNT(CASE WHEN DayType = 'Holiday' THEN 1 END) AS Holidays,
        COUNT(CASE WHEN WorkDate IS NOT NULL THEN 1 END) AS TotalDaysInMonth
    FROM Attendance
    WHERE WorkDate IS NOT NULL
    GROUP BY EmpID, DATE_TRUNC('month', WorkDate)
),
monthly_leave AS (
    SELECT 
        EmpID,
        DATE_TRUNC('month', StartDate) AS ReportMonth,
    SUM(CASE WHEN LeaveType = 'Annual' AND Status = 'Approved' THEN TotalDays ELSE 0 END) AS AnnualLeaveDays,
        SUM(CASE WHEN LeaveType = 'Sick' AND Status = 'Approved' THEN TotalDays ELSE 0 END) AS SickLeaveDays,
        SUM(CASE WHEN LeaveType = 'Absent' AND Status = 'Approved' THEN TotalDays ELSE 0 END) AS AbsentLeaveDays

    FROM LeaveRequests
    WHERE Status = 'Approved'
    GROUP BY EmpID, DATE_TRUNC('month', StartDate)
),
expected_hours AS (
    SELECT 
        a.EmpID,
        DATE_TRUNC('month', a.WorkDate) AS ReportMonth,
        -- Use ExpectedHours from the table (set by trigger: 5 Sat, 8 Mon-Fri)
        SUM(a.ExpectedHours) AS ExpectedHours
    FROM Attendance a
    WHERE a.WorkDate IS NOT NULL
    GROUP BY a.EmpID, DATE_TRUNC('month', a.WorkDate)
)

SELECT 
    e.EmpID,
    e.EmployeeCode,
    e.FirstName || ' ' || e.LastName AS FullName,
    e.Department,
    COALESCE(ma.ReportMonth, ml.ReportMonth, eh.ReportMonth) AS ReportMonth,
    
    -- Total Hours Worked
    ROUND(COALESCE(ma.TotalHoursWorked, 0), 2) AS TotalHoursWorked,
    
    -- Expected Hours for the Month
    ROUND(COALESCE(eh.ExpectedHours, 0), 2) AS ExpectedHours,
    
    -- Leave Days Breakdown
    ROUND(COALESCE(ml.AnnualLeaveDays, 0), 2) AS AnnualLeaveDays,
    ROUND(COALESCE(ml.SickLeaveDays, 0), 2) AS SickLeaveDays,
    ROUND(COALESCE(ml.AbsentLeaveDays, 0), 2) AS AbsentLeaveDays,

    
    -- Total Sick/Absent Days (Sick Leave + Absent days)
    ROUND(COALESCE(ml.SickLeaveDays, 0) + COALESCE(ma.AbsentDays, 0), 2) AS TotalSickOrAbsentDays,
    
    -- Saturdays Worked
    COALESCE(ma.SaturdaysWorked, 0) AS SaturdaysWorked,
    
    -- Underworked Flag (TRUE if worked less than expected hours)
    CASE 
        WHEN COALESCE(ma.TotalHoursWorked, 0) < COALESCE(eh.ExpectedHours, 0) 
        THEN TRUE 
        ELSE FALSE 
    END AS IsUnderworked,
    
    -- Hours Difference (negative means underworked)
    ROUND(COALESCE(ma.TotalHoursWorked, 0) - COALESCE(eh.ExpectedHours, 0), 2) AS HoursDifference

FROM Employees e
LEFT JOIN monthly_attendance ma ON e.EmpID = ma.EmpID
LEFT JOIN monthly_leave ml ON e.EmpID = ml.EmpID AND ma.ReportMonth = ml.ReportMonth
LEFT JOIN expected_hours eh ON e.EmpID = eh.EmpID AND COALESCE(ma.ReportMonth, ml.ReportMonth) = eh.ReportMonth
WHERE e.IsActive = TRUE
ORDER BY COALESCE(ma.ReportMonth, ml.ReportMonth, eh.ReportMonth) DESC, e.EmpID;

COMMENT ON VIEW vw_monthly_employee_report IS 
'Monthly report showing total hours worked, annual leave days, sick/absent days, and underworked flag for all 30 employees';

-- =====================================================
-- STORED PROCEDURE 1: Initialize Fiscal Year


-- Creates fiscal year and default leave balances
-- =====================================================
CREATE OR REPLACE PROCEDURE sp_initialize_fiscal_year(
    p_fiscal_year INT,
    p_annual_days DECIMAL(5,2) DEFAULT 21.00,
    p_sick_days DECIMAL(5,2) DEFAULT 10.00,
    p_casual_days DECIMAL(5,2) DEFAULT 5.00
)
LANGUAGE plpgsql AS $$
DECLARE
    v_start_date DATE;
    v_end_date DATE;
    v_emp RECORD;
    v_previous_fiscal_year INT;
    v_carry_forward DECIMAL(5,2);
BEGIN
    -- Calculate fiscal year dates (Oct 1 - Sep 30)
    v_start_date := make_date(p_fiscal_year, 10, 1);
    v_end_date := make_date(p_fiscal_year + 1, 9, 30);
    v_previous_fiscal_year := p_fiscal_year - 1;
    
    -- Insert fiscal year
    INSERT INTO FiscalYears (FiscalYear, StartDate, EndDate, IsActive)
    VALUES (p_fiscal_year, v_start_date, v_end_date, TRUE)
    ON CONFLICT (FiscalYear) DO NOTHING;
    
    -- Create leave balances for all active employees
    FOR v_emp IN SELECT EmpID FROM Employees WHERE IsActive = TRUE LOOP
        -- Calculate carry forward from previous year (max 5 days)
        SELECT 
            GREATEST(0, LEAST(5.00, (AnnualDays - UsedAnnualDays))) 
        INTO v_carry_forward
        FROM LeaveBalances
        WHERE EmpID = v_emp.EmpID AND FiscalYear = v_previous_fiscal_year;
        
        -- If no previous record, set to 0
        IF v_carry_forward IS NULL THEN
            v_carry_forward := 0;
        END IF;
        
        -- Insert new balance
        INSERT INTO LeaveBalances (
            EmpID, 
            FiscalYear, 
            AnnualDays, 
            SickDays, 
            CasualDays,
            CarryForwardDays,
            UsedAnnualDays,
            UsedSickDays,
            UsedCasualDays,
            AbsentDays
        )
        VALUES (
            v_emp.EmpID, 
            p_fiscal_year, 
            p_annual_days, 
            p_sick_days, 
            p_casual_days,
            v_carry_forward,
            0, 0, 0, 0
        )
        ON CONFLICT (EmpID, FiscalYear) DO NOTHING;
    END LOOP;
    
    RAISE NOTICE 'Fiscal year % initialized successfully', p_fiscal_year;
END;
$$;

COMMENT ON PROCEDURE sp_initialize_fiscal_year IS 
'Initializes a new fiscal year with default leave balances for all employees';

-- =====================================================
-- STORED PROCEDURE 2: Process Monthly Attendance
-- Generates attendance records for weekends/holidays
-- =====================================================
CREATE OR REPLACE PROCEDURE sp_process_monthly_attendance(
    p_year INT,
    p_month INT
)
LANGUAGE plpgsql AS $$
DECLARE
    v_start_date DATE;
    v_end_date DATE;
    v_current_date DATE;
    v_emp RECORD;
    v_dow INT;
BEGIN
    v_start_date := make_date(p_year, p_month, 1);
    v_end_date := (v_start_date + INTERVAL '1 month' - INTERVAL '1 day')::DATE;
    v_current_date := v_start_date;
    
    WHILE v_current_date <= v_end_date LOOP
        v_dow := EXTRACT(DOW FROM v_current_date);
        
        -- For each active employee
        FOR v_emp IN SELECT EmpID FROM Employees WHERE IsActive = TRUE LOOP
            -- Check if attendance record exists
            IF NOT EXISTS (
                SELECT 1 FROM Attendance 
                WHERE EmpID = v_emp.EmpID AND WorkDate = v_current_date
            ) THEN
                -- Auto-create record for Sundays (Holiday)
                IF v_dow = 0 THEN
                    INSERT INTO Attendance (EmpID, WorkDate, DayType, Status)
                    VALUES (v_emp.EmpID, v_current_date, 'Holiday', 'Holiday');
                END IF;
            END IF;
        END LOOP;
        
        v_current_date := v_current_date + 1;
    END LOOP;
    
    RAISE NOTICE 'Monthly attendance processed for %-%', p_year, p_month;
END;
$$;

COMMENT ON PROCEDURE sp_process_monthly_attendance IS 
'Processes monthly attendance and auto-creates holiday records';

-- =====================================================
-- STORED PROCEDURE 3: Employee Clock In/Out
-- Handles clock-in and clock-out with expected hours and late detection
-- =====================================================
CREATE OR REPLACE PROCEDURE sp_employee_clock_in_out(
    p_employee_id INT,
    p_action_type VARCHAR(3)  -- 'IN' or 'OUT'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_today DATE := CURRENT_DATE;
    v_current_time TIME := CURRENT_TIME;
    v_dow INT := EXTRACT(DOW FROM CURRENT_DATE);  -- 0=Sunday, 1=Monday, ..., 6=Saturday
    v_expected_hours INT;
    v_status VARCHAR(20);
    v_existing_record INT;
BEGIN
    -- Determine expected hours based on day of week
    -- Saturday (6): 5 hours (8am to 1pm)
    -- Monday-Friday (1-5): 8 hours
    IF v_dow = 6 THEN
        v_expected_hours := 5;  -- Saturday: 8am to 1pm
    ELSIF v_dow BETWEEN 1 AND 5 THEN
        v_expected_hours := 8;  -- Monday-Friday
    ELSE
        -- Sunday (0) - not a working day
        RAISE EXCEPTION 'Today is Sunday. No clock-in/out allowed.';
    END IF;
    
    -- Check if attendance record exists for today
    SELECT AttendanceID INTO v_existing_record
    FROM Attendance
    WHERE EmpID = p_employee_id AND WorkDate = v_today;
    
    -- Handle CLOCK IN
    IF UPPER(p_action_type) = 'IN' THEN
        -- Check if already clocked in
        IF v_existing_record IS NOT NULL THEN
            -- Check if already has clock in time
            IF EXISTS (SELECT 1 FROM Attendance WHERE AttendanceID = v_existing_record AND ClockIn IS NOT NULL) THEN
                RAISE EXCEPTION 'Employee % has already clocked in today.', p_employee_id;
            END IF;
        END IF;
        
        -- Determine status: Late if after 08:00:00
        IF v_current_time > '08:00:00'::TIME THEN
            v_status := 'Late';
        ELSE
            v_status := 'Present';
        END IF;
        
        -- Insert or update attendance record
        IF v_existing_record IS NULL THEN
            INSERT INTO Attendance (EmpID, WorkDate, ClockIn, Status, Notes)
            VALUES (p_employee_id, v_today, v_current_time, v_status, 
                    'Expected Hours: ' || v_expected_hours);
        ELSE
            UPDATE Attendance 
            SET ClockIn = v_current_time,
                Status = v_status,
                Notes = COALESCE(Notes, '') || ' | Expected Hours: ' || v_expected_hours
            WHERE AttendanceID = v_existing_record;
        END IF;
        
        RAISE NOTICE 'Employee % clocked IN at %. Status: %. Expected Hours: %', 
                     p_employee_id, v_current_time, v_status, v_expected_hours;
    
    -- Handle CLOCK OUT
    ELSIF UPPER(p_action_type) = 'OUT' THEN
        -- Check if employee has clocked in today
        IF v_existing_record IS NULL OR NOT EXISTS (
            SELECT 1 FROM Attendance 
            WHERE AttendanceID = v_existing_record AND ClockIn IS NOT NULL
        ) THEN
            RAISE EXCEPTION 'Employee % has not clocked in today.', p_employee_id;
        END IF;
        
        -- Update clock out time
        UPDATE Attendance 
        SET ClockOut = v_current_time,
            Notes = COALESCE(Notes, '') || ' | Actual Hours: ' || 
                    ROUND(EXTRACT(EPOCH FROM (v_current_time - ClockIn))/3600, 2)::TEXT
        WHERE AttendanceID = v_existing_record;
        
        RAISE NOTICE 'Employee % clocked OUT at %. Work day complete.', 
                     p_employee_id, v_current_time;
    
    ELSE
        RAISE EXCEPTION 'Invalid action type %. Use IN or OUT.', p_action_type;
    END IF;
    
END;
$$;

COMMENT ON PROCEDURE sp_employee_clock_in_out IS 
'Clock-in/out procedure with expected hours: 5 hours on Saturday (8am-1pm), 8 hours on weekdays. Marks Late if clock-in after 08:00:00.';

-- =====================================================
-- STORED PROCEDURE 4: UPSERT Attendance Record
-- If record exists for (EmpID, WorkDate), UPDATE ClockOut
-- If record doesn't exist, INSERT new record with ClockIn
-- =====================================================
CREATE OR REPLACE PROCEDURE sp_upsert_attendance(
    p_employee_id INT,
    p_work_date DATE,
    p_time_in TIME,
    p_time_out TIME
)
LANGUAGE plpgsql AS $$
DECLARE
    v_existing_id INT;
    v_dow INT;
    v_is_sunday BOOLEAN;
BEGIN
    -- Check if it's Sunday (not allowed)
    v_dow := EXTRACT(DOW FROM p_work_date);
    v_is_sunday := (v_dow = 0);
    
    IF v_is_sunday THEN
        RAISE EXCEPTION 'Cannot create attendance record for Sunday (non-working day). WorkDate: %', p_work_date;
    END IF;
    
    -- Check if record already exists for this employee and date
    SELECT AttendanceID INTO v_existing_id
    FROM Attendance
    WHERE EmpID = p_employee_id 
      AND WorkDate = p_work_date;
    
    -- If record exists, UPDATE ClockOut
    IF v_existing_id IS NOT NULL THEN
        -- Validate that time_out is provided for update
        IF p_time_out IS NULL THEN
            RAISE EXCEPTION 'Time out is required when updating existing attendance record';
        END IF;
        
        -- Validate time_out > time_in if both provided
        IF p_time_in IS NOT NULL AND p_time_out <= p_time_in THEN
            RAISE EXCEPTION 'Time out must be later than time in';
        END IF;
        
        UPDATE Attendance 
        SET ClockOut = p_time_out,
            UpdatedAt = CURRENT_TIMESTAMP,
            Notes = COALESCE(Notes, '') || ' | Updated via UPSERT'
        WHERE AttendanceID = v_existing_id;
        
        RAISE NOTICE 'Updated existing attendance record for Employee % on %. ClockOut set to %', 
                     p_employee_id, p_work_date, p_time_out;
    
    -- If record doesn't exist, INSERT new record
    ELSE
        -- Validate that time_in is provided for new record
        IF p_time_in IS NULL THEN
            RAISE EXCEPTION 'Time in is required when creating new attendance record';
        END IF;
        
        -- For new records, time_out is optional (can be NULL for ongoing shift)
        -- If time_out is provided, validate it
        IF p_time_out IS NOT NULL AND p_time_out <= p_time_in THEN
            RAISE EXCEPTION 'Time out must be later than time in';
        END IF;
        
        INSERT INTO Attendance (EmpID, WorkDate, ClockIn, ClockOut, Notes)
        VALUES (p_employee_id, p_work_date, p_time_in, p_time_out, 
                'Created via UPSERT');
        
        RAISE NOTICE 'Inserted new attendance record for Employee % on %. ClockIn set to %', 
                     p_employee_id, p_work_date, p_time_in;
    END IF;
    
END;
$$;

COMMENT ON PROCEDURE sp_upsert_attendance IS 
'UPSERT procedure: If (EmpID, WorkDate) exists, UPDATE ClockOut. If not exists, INSERT new record with ClockIn. Throws error for Sunday records.';

-- =====================================================
-- STORED PROCEDURE 5: Submit Leave Request with Transaction
-- Checks balance, deducts 1 day, inserts LeaveRequest
-- Uses BEGIN/COMMIT/ROLLBACK for data integrity
-- =====================================================
CREATE OR REPLACE PROCEDURE sp_submit_leave_request(
    p_employee_id INT,
    p_leave_type VARCHAR(20),  -- 'Annual', 'Sick', 'Absent'
    p_start_date DATE,
    p_end_date DATE,
    p_reason TEXT
)
LANGUAGE plpgsql AS $$
DECLARE
    v_fiscal_year INT;
    v_balance_column VARCHAR(50);
    v_used_column VARCHAR(50);
    v_current_balance DECIMAL(5,2);
    v_current_used DECIMAL(5,2);
    v_leave_days DECIMAL(5,2);
    v_new_used DECIMAL(5,2);
    v_request_id INT;
BEGIN
    -- Start transaction
    BEGIN
        -- Calculate fiscal year for the leave start date
        v_fiscal_year := get_fiscal_year(p_start_date);
        
        -- Calculate leave days (excludes Sundays, Saturday=0.5)
        v_leave_days := calculate_leave_days(p_start_date, p_end_date);
        
        -- Validate leave type
        IF p_leave_type NOT IN ('Annual', 'Sick', 'Absent') THEN
            RAISE EXCEPTION 'Invalid leave type: %. Must be Annual, Sick, or Absent', p_leave_type;
        END IF;
        
        -- Determine which balance columns to check
        CASE p_leave_type
            WHEN 'Annual' THEN
                v_balance_column := 'AnnualDays';
                v_used_column := 'UsedAnnualDays';
            WHEN 'Sick' THEN
                v_balance_column := 'SickDays';
                v_used_column := 'UsedSickDays';
            WHEN 'Absent' THEN
                -- For Absent, we don't check balance, just record it
                v_balance_column := NULL;
                v_used_column := 'AbsentDays';
            ELSE
                RAISE EXCEPTION 'Invalid leave type: %', p_leave_type;
        END CASE;
        
        -- For Annual and Sick, check if employee has enough balance
        IF p_leave_type IN ('Annual', 'Sick') THEN
            -- Get current balance and used days
            EXECUTE format('SELECT %I, %I FROM LeaveBalances WHERE EmpID = $1 AND FiscalYear = $2', 
                          v_balance_column, v_used_column)
            INTO v_current_balance, v_current_used
            USING p_employee_id, v_fiscal_year;
            
            -- Check if balance record exists
            IF v_current_balance IS NULL THEN
                RAISE EXCEPTION 'No leave balance record found for Employee % in Fiscal Year %', 
                                p_employee_id, v_fiscal_year;
            END IF;
            
            -- Check if employee has enough balance remaining
            IF (v_current_balance - v_current_used) < v_leave_days THEN
                RAISE EXCEPTION 'Insufficient % leave balance for Employee %. Available: % days, Requested: % days', 
                                p_leave_type, p_employee_id, 
                                (v_current_balance - v_current_used), v_leave_days;
            END IF;
            
            -- Calculate new used days
            v_new_used := v_current_used + v_leave_days;
            
            -- Update LeaveBalances (deduct the leave days)
            EXECUTE format('UPDATE LeaveBalances SET %I = $1, UpdatedAt = CURRENT_TIMESTAMP WHERE EmpID = $2 AND FiscalYear = $3',
                          v_used_column)
            USING v_new_used, p_employee_id, v_fiscal_year;
            
            RAISE NOTICE 'Deducted % % days from Employee % balance. New used: %, Remaining: %',
                         v_leave_days, p_leave_type, p_employee_id, v_new_used, 
                         (v_current_balance - v_new_used);
        END IF;
        
        -- For Absent type, just update the AbsentDays counter
        IF p_leave_type = 'Absent' THEN
            UPDATE LeaveBalances 
            SET AbsentDays = AbsentDays + v_leave_days,
                UpdatedAt = CURRENT_TIMESTAMP
            WHERE EmpID = p_employee_id AND FiscalYear = v_fiscal_year;
            
            -- If no record exists, create one
            IF NOT FOUND THEN
                INSERT INTO LeaveBalances (EmpID, FiscalYear, AbsentDays, UsedAnnualDays, UsedSickDays, UsedCasualDays)
                VALUES (p_employee_id, v_fiscal_year, v_leave_days, 0, 0, 0);
            END IF;
        END IF;
        
        -- Insert the leave request
        INSERT INTO LeaveRequests (EmpID, LeaveType, StartDate, EndDate, TotalDays, Reason, Status)
        VALUES (p_employee_id, p_leave_type, p_start_date, p_end_date, v_leave_days, p_reason, 'Pending')
        RETURNING RequestID INTO v_request_id;
        
        -- Commit the transaction
        COMMIT;
        
        RAISE NOTICE 'Leave request submitted successfully. RequestID: %, Employee: %, Type: %, Days: %, Period: % to %',
                     v_request_id, p_employee_id, p_leave_type, v_leave_days, p_start_date, p_end_date;
        
    EXCEPTION
        WHEN OTHERS THEN
            -- Rollback the transaction on any error
            ROLLBACK;
            RAISE EXCEPTION 'Leave request failed: %', SQLERRM;
    END;
    
END;
$$;

COMMENT ON PROCEDURE sp_submit_leave_request IS 
'Transaction-based leave request submission. Checks balance, deducts days, inserts request. Uses BEGIN/COMMIT/ROLLBACK for data integrity.';

-- =====================================================
-- END OF BUSINESS LOGIC
-- =====================================================
