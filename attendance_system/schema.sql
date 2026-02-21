-- =====================================================
-- ATTENDANCE SYSTEM - DATABASE SCHEMA (Layer 1)
-- PostgreSQL Schema for 30 Employees
-- Features: October Fiscal Year Start, Saturday Half-Days
-- =====================================================

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS LeaveRequests CASCADE;
DROP TABLE IF EXISTS LeaveBalances CASCADE;
DROP TABLE IF EXISTS Attendance CASCADE;
DROP TABLE IF EXISTS Employees CASCADE;
DROP TABLE IF EXISTS FiscalYears CASCADE;

-- =====================================================
-- 1. FISCAL YEARS TABLE
-- Supports October fiscal year start (Oct 1 - Sep 30)
-- =====================================================
CREATE TABLE FiscalYears (
    FiscalYearID SERIAL PRIMARY KEY,
    FiscalYear INT NOT NULL UNIQUE, -- e.g., 2024, 2025
    StartDate DATE NOT NULL,        -- October 1st
    EndDate DATE NOT NULL,          -- September 30th
    IsActive BOOLEAN DEFAULT TRUE,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 2. EMPLOYEES TABLE
-- =====================================================
CREATE TABLE Employees (
    EmpID SERIAL PRIMARY KEY,
    EmployeeCode VARCHAR(10) UNIQUE NOT NULL, -- e.g., EMP001
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE,
    Phone VARCHAR(20),
    JoinDate DATE NOT NULL,
    Department VARCHAR(50),
    Designation VARCHAR(50),
    IsActive BOOLEAN DEFAULT TRUE,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 3. ATTENDANCE TABLE
-- Tracks daily attendance with day type for Saturday half-days
-- =====================================================
CREATE TABLE Attendance (
    AttendanceID SERIAL PRIMARY KEY,
    EmpID INT NOT NULL,
    WorkDate DATE NOT NULL,
    ClockIn TIME NOT NULL,
    ClockOut TIME,
    DayType VARCHAR(20) DEFAULT 'Full Day' CHECK (DayType IN ('Full Day', 'Half Day', 'Saturday Half Day', 'Holiday', 'Leave')),
    
    -- Ensure ClockOut is later than ClockIn when both are provided
    CONSTRAINT check_clock_times 
        CHECK (ClockOut IS NULL OR ClockIn IS NULL OR ClockOut > ClockIn),

    ExpectedHours INT DEFAULT 8,
    WorkHours DECIMAL(4,2) DEFAULT 0,

    Status VARCHAR(20) DEFAULT 'Present' CHECK (Status IN ('Present', 'Absent', 'On Leave', 'Half Day', 'Holiday')),
    Notes TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key
    CONSTRAINT fk_attendance_employee 
        FOREIGN KEY (EmpID) 
        REFERENCES Employees(EmpID) 
        ON DELETE CASCADE,
    
    -- Ensure one record per employee per day
    CONSTRAINT unique_employee_date 
        UNIQUE (EmpID, WorkDate)
);

-- =====================================================
-- 4. LEAVE BALANCES TABLE
-- Tracks leave balances per fiscal year (October start)
-- =====================================================
CREATE TABLE LeaveBalances (
    BalanceID SERIAL PRIMARY KEY,
    EmpID INT NOT NULL,
    FiscalYear INT NOT NULL,
    AnnualDays DECIMAL(5,2) DEFAULT 0,      -- Annual leave entitlement
    SickDays DECIMAL(5,2) DEFAULT 0,         -- Sick leave entitlement
    AbsentDays DECIMAL(5,2) DEFAULT 0,       -- Absent days (unpaid)
    CasualDays DECIMAL(5,2) DEFAULT 0,       -- Casual leave
    UsedAnnualDays DECIMAL(5,2) DEFAULT 0,    -- Used annual leave
    UsedSickDays DECIMAL(5,2) DEFAULT 0,     -- Used sick leave
    UsedCasualDays DECIMAL(5,2) DEFAULT 0,   -- Used casual leave
    CarryForwardDays DECIMAL(5,2) DEFAULT 0, -- Carry forward from previous year
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    CONSTRAINT fk_leavebalance_employee 
        FOREIGN KEY (EmpID) 
        REFERENCES Employees(EmpID) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_leavebalance_fiscalyear 
        FOREIGN KEY (FiscalYear) 
        REFERENCES FiscalYears(FiscalYear),
    
    -- One balance record per employee per fiscal year
    CONSTRAINT unique_employee_fiscalyear 
        UNIQUE (EmpID, FiscalYear)
);

-- =====================================================
-- 5. LEAVE REQUESTS TABLE
-- Tracks all leave applications
-- =====================================================
CREATE TABLE LeaveRequests (
    RequestID SERIAL PRIMARY KEY,
    EmpID INT NOT NULL,
    LeaveType VARCHAR(20) NOT NULL CHECK (LeaveType IN ('Annual', 'Sick', 'Absent')),

    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    TotalDays DECIMAL(5,2) NOT NULL,
    Reason TEXT,
    Status VARCHAR(20) DEFAULT 'Pending' CHECK (Status IN ('Pending', 'Approved', 'Rejected', 'Cancelled')),
    ApprovedBy INT,
    ApprovedDate TIMESTAMP,
    RequestedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    CONSTRAINT fk_leaverequest_employee 
        FOREIGN KEY (EmpID) 
        REFERENCES Employees(EmpID) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_leaverequest_approver 
        FOREIGN KEY (ApprovedBy) 
        REFERENCES Employees(EmpID),
    
    -- Ensure end date is not before start date
    CONSTRAINT check_date_range 
        CHECK (EndDate >= StartDate)
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================
CREATE INDEX idx_attendance_empid ON Attendance(EmpID);
CREATE INDEX idx_attendance_workdate ON Attendance(WorkDate);
CREATE INDEX idx_attendance_emp_date ON Attendance(EmpID, WorkDate);
CREATE INDEX idx_leavebalance_empid ON LeaveBalances(EmpID);
CREATE INDEX idx_leavebalance_fiscalyear ON LeaveBalances(FiscalYear);
CREATE INDEX idx_leaverequests_empid ON LeaveRequests(EmpID);
CREATE INDEX idx_leaverequests_status ON LeaveRequests(Status);
CREATE INDEX idx_leaverequests_dates ON LeaveRequests(StartDate, EndDate);

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================
COMMENT ON TABLE FiscalYears IS 'Stores fiscal year definitions with October start';
COMMENT ON TABLE Employees IS 'Employee master data';
COMMENT ON TABLE Attendance IS 'Daily attendance records with support for Saturday half-days';
COMMENT ON TABLE LeaveBalances IS 'Leave balances per employee per fiscal year (Oct-Sep)';
COMMENT ON TABLE LeaveRequests IS 'Leave applications and approvals';

COMMENT ON COLUMN Attendance.DayType IS 'Type of day: Full Day, Half Day, Saturday Half Day, Holiday, or Leave';
COMMENT ON COLUMN Attendance.ExpectedHours IS 'Expected hours: 5 for Saturday, 8 for Mon-Fri, 0 for Sunday (set by trigger)';
COMMENT ON COLUMN LeaveBalances.FiscalYear IS 'Fiscal year starting in October (e.g., 2024 = Oct 2024 - Sep 2025)';

-- =====================================================
-- TRIGGER: Set Expected Hours Based on Day of Week
-- Saturday = 5 hours, Mon-Fri = 8 hours, Sunday = error
-- =====================================================
CREATE OR REPLACE FUNCTION trg_set_expected_hours()
RETURNS TRIGGER AS $$
DECLARE
    v_dow INT;
BEGIN
    v_dow := EXTRACT(DOW FROM NEW.WorkDate);
    
    -- 0 = Sunday, 1-5 = Monday-Friday, 6 = Saturday
    IF v_dow = 0 THEN
        -- Sunday - not a working day
        RAISE EXCEPTION 'Cannot insert attendance for Sunday (non-working day). WorkDate: %', NEW.WorkDate;
    ELSIF v_dow = 6 THEN
        -- Saturday = 5 hours
        NEW.ExpectedHours := 5;
    ELSE
        -- Monday-Friday = 8 hours
        NEW.ExpectedHours := 8;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_attendance_set_expected_hours
    BEFORE INSERT ON Attendance
    FOR EACH ROW
    EXECUTE FUNCTION trg_set_expected_hours();

COMMENT ON TRIGGER trg_attendance_set_expected_hours ON Attendance IS 
'Automatically sets ExpectedHours: 5 for Saturday, 8 for Mon-Fri, error for Sunday';
