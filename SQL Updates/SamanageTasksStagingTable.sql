USE [Samanage]
GO

/****** Object:  Table [dbo].[TasksStaging]    Script Date: 4/11/2022 10:50:22 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[TasksStaging](
	[id] [int] NOT NULL,
	[name] [varchar](max) NULL,
	[description] [varchar](max) NULL,
	[requester] [varchar](256) NULL,
	[assigned] [varchar](256) NULL,
	[href] [varchar](max) NULL,
	[due_at] [datetimeoffset](7) NULL,
	[completed_at] [datetimeoffset](4) NULL,
	[completed_by] [int] NULL,
	[created_at] [datetimeoffset](4) NULL,
	[task_type] [varchar](256) NULL,
	[state] [varchar](256) NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO


ALTER TABLE dbo.TasksStaging ADD ParentID INT NULL;
ALTER TABLE dbo.TasksStaging ADD ParentName VARCHAR(max) NULL;
ALTER TABLE dbo.TasksStaging ADD ParentType VARCHAR(256) NULL;