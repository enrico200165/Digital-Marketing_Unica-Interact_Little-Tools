
Stored procedure source
USE [JLR_Jigsaw]
GO

/****** Object:  StoredProcedure [dbo].[spSetDSSegment]    Script Date: 02/03/2018 19:47:37 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

/*
Purpose	: Updates records in Jigsaw.tblOnlineProfile

Author  : Colin Norris

Date	: 14/02/2018

Modification History
Date  		Initials  	Reason
*/

CREATE PROCEDURE [dbo].[spSetDSSegment]
	 @CookieID NVARCHAR(64)
	,@DSEvent NVARCHAR(10)
AS

SET NOCOUNT ON;

DECLARE  @zSQL NVARCHAR(4000)
		,@lUpdateRowCount TINYINT;

SET @zSQL =
'UPDATE [dbo].[tblOnlineProfile]
SET
	[DateModified] = GETDATE()
	' + IIF(@DSEvent = 'LRDX_INDX'	, ',[LRDX_INDX] += 1', '') + '
	' + IIF(@DSEvent = 'DS_O'		, ',[DS_O]	    += 1', '') + '
	' + IIF(@DSEvent = 'DS_CPB_1'	, ',[DS_CPB_1]  += 1', '') + '
	' + IIF(@DSEvent = 'DS_CPB_2'	, ',[DS_CPB_2]  += 1', '') + '
	' + IIF(@DSEvent = 'DS_CMP_1'	, ',[DS_CMP_1]  += 1', '') + '
	' + IIF(@DSEvent = 'DS_CMP_2'	, ',[DS_CMP_2]  += 1', '') + '
	' + IIF(@DSEvent = 'DS_PRM_1'	, ',[DS_PRM_1]  += 1', '') + '
	' + IIF(@DSEvent = 'DS_PRM_2'	, ',[DS_PRM_2]  += 1', '') + '
	' + IIF(@DSEvent = 'DS_VRS_1'	, ',[DS_VRS_1]  += 1', '') + '
	' + IIF(@DSEvent = 'DS_VRS_2'	, ',[DS_VRS_2]  += 1', '') + '
	' + IIF(@DSEvent IN ('DS_CPB_1', 'DS_CPB_2', 'DS_CMP_1', 'DS_CMP_2', 'DS_PRM_1', 'DS_PRM_2', 'DS_VRS_1', 'DS_VRS_2'),
	',[DS_SEGMENT] = @DSEvent', '') + '
WHERE
	[CookieID] = @CookieID;

SET @lUpdateRowCount = @@ROWCOUNT;'

EXEC sp_executesql @zSQL, N'@CookieID VARCHAR(64), @DSEvent NVARCHAR(10), @lUpdateRowCount INT OUTPUT', @CookieID, @DSEvent, @lUpdateRowCount OUTPUT;

IF @lUpdateRowCount = 0
BEGIN

	SET @zSQL =
	'INSERT INTO [dbo].[tblOnlineProfile]
	(
		 [CookieID]
		,[DateModified]
		' + IIF(@DSEvent = 'LRDX_INDX'	, ',[LRDX_INDX]', '') + '
		' + IIF(@DSEvent = 'DS_O'		, ',[DS_O]', '') + '
		' + IIF(@DSEvent = 'DS_CPB_1'	, ',[DS_CPB_1]', '') + '
		' + IIF(@DSEvent = 'DS_CPB_2'	, ',[DS_CPB_2]', '') + '
		' + IIF(@DSEvent = 'DS_CMP_1'	, ',[DS_CMP_1]', '') + '
		' + IIF(@DSEvent = 'DS_CMP_2'	, ',[DS_CMP_2]', '') + '
		' + IIF(@DSEvent = 'DS_PRM_1'	, ',[DS_PRM_1]', '') + '
		' + IIF(@DSEvent = 'DS_PRM_2'	, ',[DS_PRM_2]', '') + '
		' + IIF(@DSEvent = 'DS_VRS_1'	, ',[DS_VRS_1]', '') + '
		' + IIF(@DSEvent = '		, ',[DS_VRS_2]', '') + '
		' + IIF(@DSEvent IN ('DS_CPB_1', 'DS_CPB_2', 'DS_CMP_1', 'DS_CMP_2', 'DS_PRM_1', 'DS_PRM_2', 'DS_VRS_1', 'DS_VRS_2'), ',[DS_SEGMENT]', '') + '
	)
	SELECT
		 @CookieID
		,GETDATE()
		' + IIF(@DSEvent = 'LRDX_INDX'	, ',1', '') + '
		' + IIF(@DSEvent = 'DS_O'		, ',1', '') + '
		' + IIF(@DSEvent = 'DS_CPB_1'	, ',1', '') + '
		' + IIF(@DSEvent = 'DS_CPB_2'	, ',1', '') + '
		' + IIF(@DSEvent = 'DS_CMP_1'	, ',1', '') + '
		' + IIF(@DSEvent = 'DS_CMP_2'	, ',1', '') + '
		' + IIF(@DSEvent = 'DS_PRM_1'	, ',1', '') + '
		' + IIF(@DSEvent = 'DS_PRM_2'	, ',1', '') + '
		' + IIF(@DSEvent = 'DS_VRS_1'	, ',1', '') + '
		' + IIF(@DSEvent = 'DS_VRS_2'	, ',1', '') + '
		' + IIF(@DSEvent IN ('DS_CPB_1', 'DS_CPB_2', 'DS_CMP_1', 'DS_CMP_2', 'DS_PRM_1', 'DS_PRM_2', 'DS_VRS_1', 'DS_VRS_2'), ', @DSEvent', '') + ';
	'

	EXEC sp_executesql @zSQL, N'@CookieID VARCHAR(64), @DSEvent NVARCHAR(10)', @CookieID, @DSEvent;

END

RETURN 0
GO




DB Structure

REATE TABLE [dbo].[tblOnlineProfile](
	[CookieID] [nvarchar](30) NOT NULL,
	[CTRL] [bit] NULL,
	[LRDX_INDX] [int] NULL,
	[DS_O] [int] NULL,
	[DS_CPB_1] [int] NULL,
	[DS_CPB_2] [int] NULL,
	[DS_CMP_1] [int] NULL,
	[DS_CMP_2] [int] NULL,
	[DS_PRM_1] [int] NULL,
	[DS_PRM_2] [int] NULL,
	[DS_VRS_1] [int] NULL,
	[DS_VRS_2] [int] NULL,
	[DS_SEGMENT] [varchar](10) NULL,
	[DateCreated] [datetime] NULL,
	[DateModified] [datetime] NULL,
	[Session_Start] [datetime] NULL,
	[DEV_Creator] [varchar](16) NULL,
PRIMARY KEY CLUSTERED
( [CookieID] ASC)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 90) ON [PRIMARY]
) ON [PRIMARY]
GO
