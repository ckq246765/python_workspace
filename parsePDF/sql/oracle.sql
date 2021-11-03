﻿DROP TABLE TMU_TMEDMS.T_PARSER_PDF_DATA;
CREATE TABLE TMU_TMEDMS.T_PARSER_PDF_DATA(
     ID VARCHAR2(32) DEFAULT SYS_GUID(),
     FILE_NAME VARCHAR2(200),
     TITLE_NAME VARCHAR2(300),
     TITLE_DATE VARCHAR2(300),
     REG_NUM VARCHAR2(200),
     PAGE_NUM VARCHAR2(50),
     LAST_PAGE_NUM VARCHAR2(50),
     TOTAL_NUM VARCHAR2(50)
);
DROP TABLE TMU_TMEDMS.T_PARSER_PDF_PAGE_CONTEXT;
CREATE TABLE TMU_TMEDMS.T_PARSER_PDF_PAGE_CONTEXT(
  ID VARCHAR2(32) DEFAULT SYS_GUID(),
  FILE_NAME VARCHAR2(200),
  PAGE_NUM INTEGER,
  PDF_PAGE_CONTEXT BLOB
);