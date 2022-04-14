USE [Samanage]
GO

/****** Object:  StoredProcedure [dbo].[spMergeTask]    Script Date: 4/13/2022 7:13:09 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

-- =============================================
-- Author:		Robbie Grantland
-- Create date: 2/1/2022
-- Description:	Used to update and add to TasksStaging table
-- =============================================
ALTER PROCEDURE [dbo].[spMergeTask] 
	-- Add the parameters for the stored procedure here
	@id int,
	@name varchar(max),
	@description varchar(max),
	@requester varchar(256),
	@assigned varchar(256),
	@href varchar(max),
	@due_at datetimeoffset(7),
	@completed_at datetimeoffset(4),
	@completed_by int,
	@created_at datetimeoffset(4),
	@task_type varchar(256),
	@state varchar(256)
AS
BEGIN
	SET NOCOUNT ON;

	MERGE dbo.TasksStaging AS Task
	USING (SELECT  
				@id,
				@name, 
				@description,
				@requester, 
				@assigned,
				@href, 
				@due_at,
				@completed_at,
				@completed_by,
				@created_at,
				@task_type, 
				@state
				  ) AS source(  id,
								name, 
								description, 
								requester,
								assigned,
								href, 
								due_at, 
								completed_at,
								completed_by,
								created_at,
								task_type,
								state)
	ON (Task.id = source.id)
	WHEN MATCHED THEN
		UPDATE SET id = source.id,
				   Name = source.name,
				   description = source.description,
				   requester = source.requester, 
				   assigned = source.assigned, 
				   href = source.href, 
				   due_at = source.due_at, 
				   completed_at = source.completed_at,
				   completed_by = source.completed_by,
				   created_at = source.created_at,
				   task_type = source.task_type,
				   state = source.state
	WHEN NOT MATCHED THEN
		INSERT( id,
				name, 
				description, 
				requester,
				assigned,
				href, 
				due_at, 
				completed_at,
				completed_by,
				created_at,
				task_type,
				state)
		VALUES( source.id,
				source.name, 
				source.description, 
				source.requester,
				source.assigned,
				source.href, 
				source.due_at, 
				source.completed_at,
				source.completed_by,
				source.created_at,
				source.task_type,
				source.state);
END
GO


