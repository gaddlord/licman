-- licman.Accounts definition

CREATE TABLE `Accounts` (
  `AccountId` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  PRIMARY KEY (`AccountId`),
  UNIQUE KEY `Name` (`Name`)
) ENGINE=InnoDB AUTO_INCREMENT=6606 DEFAULT CHARSET=utf16;


-- licman.AuditLogs definition

CREATE TABLE `AuditLogs` (
  `AuditLogIds` int NOT NULL AUTO_INCREMENT,
  `Timestamp` datetime DEFAULT NULL,
  `TableName` varchar(100) CHARACTER SET utf16 COLLATE utf16_general_ci NOT NULL,
  `ColumnName` varchar(100) NOT NULL,
  `OldValue` varchar(100) DEFAULT NULL,
  `NewValue` varchar(100) DEFAULT NULL,
  `RecordId` int NOT NULL,
  `UserId` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`AuditLogIds`),
  KEY `idx_auditlogs_table_record` (`TableName`,`RecordId`),
  KEY `idx_auditlogs_timestamp` (`Timestamp`)
) ENGINE=InnoDB AUTO_INCREMENT=154 DEFAULT CHARSET=utf16;


-- licman.Category definition

CREATE TABLE `Category` (
  `CategoryId` varchar(100) NOT NULL,
  `Name` varchar(100) NOT NULL,
  PRIMARY KEY (`CategoryId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf16;


-- licman.`Groups` definition

CREATE TABLE `Groups` (
  `GroupId` varchar(100) NOT NULL,
  `Name` varchar(100) NOT NULL,
  PRIMARY KEY (`GroupId`),
  UNIQUE KEY `Name` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf16;


-- licman.LicenseModel definition

CREATE TABLE `LicenseModel` (
  `LicenseModelId` varchar(100) NOT NULL,
  `Name` varchar(100) NOT NULL,
  PRIMARY KEY (`LicenseModelId`),
  UNIQUE KEY `Name` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf16;


-- licman.Organization definition

CREATE TABLE `Organization` (
  `OrganizationId` varchar(100) NOT NULL,
  `Name` varchar(100) NOT NULL,
  PRIMARY KEY (`OrganizationId`),
  UNIQUE KEY `Name` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf16;


-- licman.Years definition

CREATE TABLE `Years` (
  `YearId` varchar(4) NOT NULL,
  `Name` varchar(100) NOT NULL,
  PRIMARY KEY (`YearId`),
  UNIQUE KEY `Name` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf16;


-- licman.Expense definition

CREATE TABLE `Expense` (
  `ExpenseId` int NOT NULL AUTO_INCREMENT,
  `YearId` varchar(4) NOT NULL,
  `AccountId` int NOT NULL,
  `OrganizationId` varchar(100) NOT NULL,
  `GroupId` varchar(100) NOT NULL,
  `CategoryId` varchar(100) NOT NULL,
  `Vendor` varchar(100) NOT NULL,
  `Product` varchar(100) NOT NULL,
  `LicenseModelId` varchar(100) NOT NULL,
  `CostPerUnit` float DEFAULT NULL,
  `Sunset` tinyint(1) NOT NULL,
  `SunsetPlan` varchar(500) DEFAULT NULL,
  `Notes` varchar(500) DEFAULT NULL,
  `NumberOfUnits` int DEFAULT NULL,
  `ApprovedValue` float NOT NULL,
  `ContractedValue` float DEFAULT NULL,
  `ProcurementUrl` varchar(1000) DEFAULT NULL,
  `EmployeeName` varchar(100) DEFAULT NULL,
  `EmployeeAnnualSalary` float DEFAULT NULL,
  `EmployeeAnnualBonus` float DEFAULT NULL,
  `EmployeeAnnualBenefits` float DEFAULT NULL,
  `EmployeeTargetStartDate` date DEFAULT NULL,
  `TripName` varchar(100) DEFAULT NULL,
  `TripNumberOfPassengers` int DEFAULT NULL,
  `TrainingName` varchar(100) DEFAULT NULL,
  `TrainingNumberOfTrainees` int DEFAULT NULL,
  `WithBreakdown` tinyint(1) DEFAULT '0',
  `ApprovedJan` float DEFAULT NULL,
  `ApprovedFeb` float DEFAULT NULL,
  `ApprovedMar` float DEFAULT NULL,
  `ApprovedApr` float DEFAULT NULL,
  `ApprovedMay` float DEFAULT NULL,
  `ApprovedJun` float DEFAULT NULL,
  `ApprovedJul` float DEFAULT NULL,
  `ApprovedAug` float DEFAULT NULL,
  `ApprovedSep` float DEFAULT NULL,
  `ApprovedOct` float DEFAULT NULL,
  `ApprovedNov` float DEFAULT NULL,
  `ApprovedDec` float DEFAULT NULL,
  `ActualJan` float DEFAULT NULL,
  `ActualFeb` float DEFAULT NULL,
  `ActualMar` float DEFAULT NULL,
  `ActualApr` float DEFAULT NULL,
  `ActualMay` float DEFAULT NULL,
  `ActualJun` float DEFAULT NULL,
  `ActualJul` float DEFAULT NULL,
  `ActualAug` float DEFAULT NULL,
  `ActualSep` float DEFAULT NULL,
  `ActualOct` float DEFAULT NULL,
  `ActualNov` float DEFAULT NULL,
  `ActualDec` float DEFAULT NULL,
  `Renewal` date DEFAULT NULL,
  PRIMARY KEY (`ExpenseId`),
  KEY `YearId` (`YearId`),
  KEY `AccountId` (`AccountId`),
  KEY `OrganizationId` (`OrganizationId`),
  KEY `GroupId` (`GroupId`),
  KEY `CategoryId` (`CategoryId`),
  KEY `LicenseModelId` (`LicenseModelId`),
  CONSTRAINT `Expense_ibfk_1` FOREIGN KEY (`YearId`) REFERENCES `Years` (`YearId`),
  CONSTRAINT `Expense_ibfk_2` FOREIGN KEY (`AccountId`) REFERENCES `Accounts` (`AccountId`),
  CONSTRAINT `Expense_ibfk_3` FOREIGN KEY (`OrganizationId`) REFERENCES `Organization` (`OrganizationId`),
  CONSTRAINT `Expense_ibfk_4` FOREIGN KEY (`GroupId`) REFERENCES `Groups` (`GroupId`),
  CONSTRAINT `Expense_ibfk_5` FOREIGN KEY (`CategoryId`) REFERENCES `Category` (`CategoryId`),
  CONSTRAINT `Expense_ibfk_6` FOREIGN KEY (`LicenseModelId`) REFERENCES `LicenseModel` (`LicenseModelId`)
) ENGINE=InnoDB AUTO_INCREMENT=120 DEFAULT CHARSET=utf16;


-- licman.Licenses definition

CREATE TABLE `Licenses` (
  `LicenseId` int NOT NULL AUTO_INCREMENT,
  `EmployeeEmail` varchar(256) NOT NULL,
  `ExpenseId` int NOT NULL,
  PRIMARY KEY (`LicenseId`),
  KEY `ExpenseId` (`ExpenseId`),
  CONSTRAINT `Licenses_ibfk_1` FOREIGN KEY (`ExpenseId`) REFERENCES `Expense` (`ExpenseId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf16;