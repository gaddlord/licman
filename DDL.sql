-- licman.Accounts definition

CREATE TABLE `Accounts` (
  `AccountId` int NOT NULL,
  `Name` varchar(100) NOT NULL,
  PRIMARY KEY (`AccountId`),
  UNIQUE KEY `Accounts_UNIQUE` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf16;


-- licman.Category definition

CREATE TABLE `Category` (
  `CategoryId` varchar(100) NOT NULL,
  `Name` varchar(100) NOT NULL,
  PRIMARY KEY (`CategoryId`),
  UNIQUE KEY `Category_UNIQUE` (`CategoryId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf16;


-- licman.`Groups` definition

CREATE TABLE `Groups` (
  `GroupId` varchar(100) NOT NULL,
  `Name` varchar(100) NOT NULL,
  PRIMARY KEY (`GroupId`),
  UNIQUE KEY `Groups_UNIQUE` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf16;


-- licman.LicenseModel definition

CREATE TABLE `LicenseModel` (
  `LicenseModelId` varchar(100) CHARACTER SET utf16 COLLATE utf16_general_ci NOT NULL,
  `Name` varchar(100) NOT NULL,
  PRIMARY KEY (`LicenseModelId`),
  UNIQUE KEY `LicenseModel_UNIQUE` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf16;


-- licman.Organization definition

CREATE TABLE `Organization` (
  `OrganizationId` varchar(100) NOT NULL,
  `Name` varchar(100) NOT NULL,
  PRIMARY KEY (`OrganizationId`),
  UNIQUE KEY `Organization_UNIQUE` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf16;


-- licman.Periods definition

CREATE TABLE `Periods` (
  `PeriodId` varchar(100) NOT NULL,
  `Name` varchar(100) NOT NULL,
  PRIMARY KEY (`PeriodId`),
  UNIQUE KEY `Periods_UNIQUE` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf16;


-- licman.Units definition

CREATE TABLE `Units` (
  `UnitId` varchar(100) CHARACTER SET utf16 COLLATE utf16_general_ci NOT NULL,
  `Name` varchar(100) NOT NULL,
  PRIMARY KEY (`UnitId`),
  UNIQUE KEY `Units_UNIQUE` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf16;


-- licman.Years definition

CREATE TABLE `Years` (
  `YearId` varchar(4) NOT NULL,
  `Name` varchar(100) NOT NULL,
  PRIMARY KEY (`YearId`),
  UNIQUE KEY `Years_UNIQUE` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf16;


-- licman.Expense definition

CREATE TABLE `Expense` (
  `ExpenseId` int NOT NULL AUTO_INCREMENT,
  `YearId` varchar(4) CHARACTER SET utf16 COLLATE utf16_general_ci NOT NULL,
  `AccountId` int NOT NULL,
  `OrganizationId` varchar(100) CHARACTER SET utf16 COLLATE utf16_general_ci NOT NULL,
  `GroupId` varchar(100) CHARACTER SET utf16 COLLATE utf16_general_ci NOT NULL,
  `CategoryId` varchar(100) NOT NULL,
  `Vendor` varchar(100) CHARACTER SET utf16 COLLATE utf16_general_ci NOT NULL,
  `Product` varchar(100) CHARACTER SET utf16 COLLATE utf16_general_ci NOT NULL,
  `LicenseModelId` varchar(100) CHARACTER SET utf16 COLLATE utf16_general_ci NOT NULL,
  `CostPerUnit` double DEFAULT NULL,
  `Sunset` bit(1) NOT NULL DEFAULT b'0',
  `SunsetPlan` varchar(500) CHARACTER SET utf16 COLLATE utf16_general_ci DEFAULT NULL,
  `Notes` varchar(500) DEFAULT NULL,
  `NumberOfUnits` int DEFAULT NULL,
  `ApprovedValue` double NOT NULL,
  `ContractedValue` double DEFAULT NULL,
  `ProcurementUrl` varchar(1000) CHARACTER SET utf16 COLLATE utf16_general_ci DEFAULT NULL,
  `EmployeeName` varchar(100) CHARACTER SET utf16 COLLATE utf16_general_ci DEFAULT NULL,
  `EmployeeAnnualSalary` double DEFAULT NULL,
  `EmployeeAnnualBonus` double DEFAULT NULL,
  `EmployeeAnnualBenefits` double DEFAULT NULL,
  `EmployeeTargetStartDate` date DEFAULT NULL,
  `TripName` varchar(100) DEFAULT NULL,
  `TripNumberOfPassengers` int DEFAULT NULL,
  `TrainingName` varchar(100) DEFAULT NULL,
  `TrainingNumberOfTrainees` int DEFAULT NULL,
  PRIMARY KEY (`ExpenseId`),
  KEY `Expense_Organization_FK` (`OrganizationId`),
  KEY `Expense_LicenseModel_FK` (`LicenseModelId`),
  KEY `Expense_Groups_FK` (`GroupId`),
  KEY `Expense_Accounts_FK` (`AccountId`),
  KEY `Expense_Years_FK` (`YearId`),
  KEY `Expense_Category_FK` (`CategoryId`),
  CONSTRAINT `Expense_Accounts_FK` FOREIGN KEY (`AccountId`) REFERENCES `Accounts` (`AccountId`),
  CONSTRAINT `Expense_Category_FK` FOREIGN KEY (`CategoryId`) REFERENCES `Category` (`CategoryId`),
  CONSTRAINT `Expense_Groups_FK` FOREIGN KEY (`GroupId`) REFERENCES `Groups` (`GroupId`),
  CONSTRAINT `Expense_Organization_FK` FOREIGN KEY (`OrganizationId`) REFERENCES `Organization` (`OrganizationId`),
  CONSTRAINT `Expense_Years_FK` FOREIGN KEY (`YearId`) REFERENCES `Years` (`YearId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf16;


-- licman.Licenses definition

CREATE TABLE `Licenses` (
  `LicenseId` int NOT NULL,
  `EmployeeEmail` varchar(256) NOT NULL,
  `ExpenseId` int NOT NULL,
  PRIMARY KEY (`LicenseId`),
  UNIQUE KEY `Licenses_UNIQUE` (`LicenseId`,`EmployeeEmail`),
  KEY `Licenses_Expense_FK` (`ExpenseId`),
  CONSTRAINT `Licenses_Expense_FK` FOREIGN KEY (`ExpenseId`) REFERENCES `Expense` (`ExpenseId`),
  CONSTRAINT `Licenses_CHECK` CHECK ((`EmployeeEmail` like _utf16'\0%\0@\0a\0p\0p\0f\0i\0r\0e\0.\0c\0o\0m'))
) ENGINE=InnoDB DEFAULT CHARSET=utf16;