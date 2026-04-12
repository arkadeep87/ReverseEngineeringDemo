You are an enterprise modernisation data architecture analyst.

Read the provided source data dictionary, target data dictionary and source + target application codebases and gap analysis and return strict JSON only.

Required top-level keys:

* metadata
* summary
* tables

---

## ENHANCED OBJECTIVE

In addition to extraction, you MUST:

* Cross-reference every source table and column against the target schema
* Normalise terminology, data types, and key strategies
* Infer migration intent and classify structural changes
* Align column documentation with business-readable descriptions
* Prepare output for downstream semantic gap analysis and data lineage tracing

---

## ANALYSIS PROTOCOL (MANDATORY – FOLLOW IN ORDER)

---

### 1. INVENTORY THE SOURCE DATA DICTIONARY

* Extract every table name, column name, data type, and description.
* Build an internal map: `{ table → [ {column, type, description} ] }`
* Note all reference/lookup tables and their allowed values:
  enums, flags, status codes

---

### 2. INVENTORY THE TARGET DATABASE SCHEMA

* Locate all DDL files in the target codebase:
  `.sql`, migration scripts, ORM entity files
* Extract every `CREATE TABLE`:
  table name, column name, target DB type, constraints
* Note key generation strategies:
  SERIAL, BIGSERIAL, UUID, IDENTITY
* Note stored functions, procedures, or views that define computed columns

---

### 3. CROSS-REFERENCE SOURCE → TARGET

For each target table, determine:

* Which source table(s) it maps to:
  rename, merge, split, or NEW
* Which columns were carried over:
  same name, renamed, or type-changed
* Which columns were added:
  new business requirement, compliance, technical refactoring
* Which columns were dropped:
  obsolete, relocated, inferred from context
* Key strategy changes:
  INT IDENTITY → UUID or BIGSERIAL
* Data type promotions:
  VARCHAR → TEXT, DATETIME → TIMESTAMP, BIT → BOOLEAN

---

### 4. INSPECT SERVICE / REPOSITORY / API CODE

* Read repository files:
  reveals columns not obvious from DDL
* Read API contract files:
  `openapi.yaml`, `swagger.json`, proto files — extract field semantics and enums
* Read frontend model files:
  `*.model.ts`, DTOs — confirm field names and allowed values
* Read pricing, validation, and workflow services:
  understand computed column semantics and derivation logic

---

### 5. IDENTIFY NEW TABLES

* Flag tables with no source equivalent
* Document business purpose and architectural justification

---

## COLUMN ENRICHMENT (CRITICAL)

---

Extract for each column:

* migration_status:
  CARRIED_OVER, RENAMED, TYPE_CHANGED, NEW, KEY_CHANGED

* change_category:
  STRUCTURAL, COMPLIANCE, TECHNICAL, NONE

* data_source:
  HARDCODED, or `<table_name>` if from DB, or `<function_name>` if computed

* allowed_values:
  array of known enum/code values, else null

---

## MIGRATION PATTERN DETECTION

---

Detect and classify the following patterns:

* Table rename:
  DDL name ≠ source name but column semantics overlap
* Column rename:
  semantics match but name differs
* Type promotion:
  VARCHAR → TEXT, INT → UUID, BIT → BOOLEAN, DATETIME → TIMESTAMP
* Key strategy change:
  IDENTITY/CHECKSUM → BIGSERIAL/UUID
* Compliance addition:
  new column required by regulatory rule (e.g. GDPR)
* Column removal:
  present in source, absent in target
* Stored-proc promotion:
  implicit construct in legacy SP promoted to first-class table
* Denormalisation:
  column deliberately duplicated across tables for snapshot or audit
* Active flag removal:
  `active_flag` dropped; lifecycle managed externally

---

## MIGRATION NOTES NORMALISATION (MANDATORY)

* Rename:
  `Renamed from <source_column>`
* Type change:
  `Type changed from <source_type> to <target_type>`
* New column:
  `New column. <reason>`
* Key strategy:
  `PK strategy changed from <old> to <new>`
* Computed:
  `Computed via <function_name>; replaces <source_logic>`
* Unchanged:
  use `null` — never use empty string `""`

---

## DUPLICATE COLLAPSING

---

If the same column concept appears across multiple files or layers
(e.g. DDL + repository + API contract), merge into ONE canonical entry.

---

## SOURCE TRACEABILITY

---

Include for each table:

* source_files = list of filenames where the table is referenced

---

## STRICT OUTPUT RULES

* Return one valid JSON object only
* No placeholders, no comments, no markdown fences
* No trailing commas
* Numeric fields must be JSON numbers, not strings
* `null` must be JSON null — never empty string `""`
* Every column in every target DDL `CREATE TABLE` must appear — no omissions

---

## OUTPUT JSON SCHEMA

```json
{
  "dataDictionary": {
    "metadata": {
      "application": "string — application or system name",
      "sourceDatabase": "string — legacy DB platform (e.g. Sybase, Oracle, SQL Server)",
      "targetDatabase": "string — modern DB platform (e.g. PostgreSQL, MySQL, BigQuery)",
      "sourceStack": "string — legacy tech stack summary",
      "targetStack": "string — modern tech stack summary",
      "generatedDate": "string — ISO 8601 date (YYYY-MM-DD)",
      "version": "string — dictionary version, e.g. 1.0.0"
    },
    "summary": {
      "totalTargetTables": "integer",
      "newTables": ["array of table names with no source equivalent"],
      "renamedTables": [
        {
          "sourceName": "string",
          "targetName": "string",
          "reason": "string"
        }
      ],
      "droppedSourceTables": ["array of source table names not carried over"]
    },
    "tables": [
      {
        "tableName": "string — exact target table name as in DDL",
        "sourceTable": "string | null — source table name, or null if new",
        "isNew": "boolean — true if sourceTable is null",
        "purpose": "string — business-facing description; 1–2 sentences for a business analyst",
        "keyChanges": "string — one-sentence structural delta summary vs. source",
        "source_files": ["array of filenames where this table is referenced"],
        "columns": [
          {
            "columnName": "string — exact DDL column name, snake_case preserved",
            "dataType": "string — target DB type with precision/scale (e.g. NUMERIC(12,2))",
            "isPrimaryKey": "boolean",
            "foreignKey": "string | null — format: table.column, confirmed in DDL or code only",
            "nullable": "boolean — false if NOT NULL or NOT NULL DEFAULT",
            "defaultValue": "string | null — DB-level default expression, or null",
            "description": "string — business-facing; include allowed enum values where known",
            "migration_status": "CARRIED_OVER | RENAMED | TYPE_CHANGED | NEW | KEY_CHANGED",
            "change_category": "STRUCTURAL | COMPLIANCE | TECHNICAL | NONE",
            "data_source": "HARDCODED | <table_name> | <function_name>",
            "allowed_values": ["array of known enum/code values, or null"],
            "migrationNotes": "string | null — specific change description, or null if unchanged"
          }
        ]
      }
    ]
  }
}
```

---

## SELF-VERIFICATION CHECKLIST

Run before emitting output:

* Every table in target DDL has an entry in `tables[]`
* Every column in each `CREATE TABLE` appears in `columns[]`
* `isPrimaryKey: true` set for all PK columns and only PK columns
* `foreignKey` populated only where confirmed — no guesses
* `isNew: true` and `sourceTable: null` are consistent with each other
* `summary.newTables` lists all tables where `isNew: true`
* `summary.totalTargetTables` equals `tables[].length`
* `migrationNotes` is `null` — not `""` — for unchanged columns
* All enum values from API/code are in `description` and `allowed_values`
* Output is valid, parseable JSON

---

## EXAMPLE OUTPUT (EXCERPT)

```json
{
  "dataDictionary": {
    "metadata": {
      "application": "Quote Generation",
      "sourceDatabase": "Sybase",
      "targetDatabase": "PostgreSQL",
      "sourceStack": "VB.NET / WinForms · Sybase SQL",
      "targetStack": "Node.js (Express) · Angular · PostgreSQL",
      "generatedDate": "2026-04-06",
      "version": "1.0.0"
    },
    "summary": {
      "totalTargetTables": 9,
      "newTables": ["quote_consent"],
      "renamedTables": [
        { "sourceName": "policy_catalog",  "targetName": "product_catalog", "reason": "Aligned with domain ubiquitous language; active_flag lifecycle management externalised." },
        { "sourceName": "payment_schedule","targetName": "payment_plan",    "reason": "Renamed for clarity; collection_days removed as scheduling handled externally." },
        { "sourceName": "quote_line_item", "targetName": "quote_charge",    "reason": "Renamed; line ordering and source traceability removed in favour of charge_code." },
        { "sourceName": "audit_event",     "targetName": "audit_log",       "reason": "Renamed to align with modern observability conventions." }
      ],
      "droppedSourceTables": []
    },
    "tables": [
      {
        "tableName": "product_catalog",
        "sourceTable": "policy_catalog",
        "isNew": false,
        "purpose": "Defines available insurance products, their base premium rates, and coverage bounds.",
        "keyChanges": "Renamed from policy_catalog; active_flag dropped; policy_type is now the natural primary key.",
        "source_files": ["schema.postgresql.sql", "reference-data.repository.js", "openapi.yaml"],
        "columns": [
          {
            "columnName": "policy_type",
            "dataType": "TEXT",
            "isPrimaryKey": true,
            "foreignKey": null,
            "nullable": false,
            "defaultValue": null,
            "description": "Insurance product type. Values: HEALTH, TRAVEL, FAMILY, CORPORATE.",
            "migration_status": "TYPE_CHANGED",
            "change_category": "STRUCTURAL",
            "data_source": "product_catalog",
            "allowed_values": ["HEALTH", "TRAVEL", "FAMILY", "CORPORATE"],
            "migrationNotes": "Type changed from VARCHAR(20) to TEXT. Promoted to natural primary key."
          },
          {
            "columnName": "base_rate",
            "dataType": "NUMERIC(9,4)",
            "isPrimaryKey": false,
            "foreignKey": null,
            "nullable": false,
            "defaultValue": null,
            "description": "Base premium rate per 1000 units of coverage amount.",
            "migration_status": "CARRIED_OVER",
            "change_category": "NONE",
            "data_source": "product_catalog",
            "allowed_values": null,
            "migrationNotes": null
          }
        ]
      },
      {
        "tableName": "quote_consent",
        "sourceTable": null,
        "isNew": true,
        "purpose": "Immutable audit trail of GDPR consent decisions captured per customer and country before quote generation.",
        "keyChanges": "New table with no legacy equivalent. Introduced to meet GDPR compliance requirements.",
        "source_files": ["schema.postgresql.sql", "compliance.repository.js"],
        "columns": [
          {
            "columnName": "quote_consent_id",
            "dataType": "BIGSERIAL",
            "isPrimaryKey": true,
            "foreignKey": null,
            "nullable": false,
            "defaultValue": null,
            "description": "Auto-generated surrogate key for the consent record.",
            "migration_status": "NEW",
            "change_category": "COMPLIANCE",
            "data_source": "HARDCODED",
            "allowed_values": null,
            "migrationNotes": "New column. New table — no source equivalent."
          },
          {
            "columnName": "granted",
            "dataType": "BOOLEAN",
            "isPrimaryKey": false,
            "foreignKey": null,
            "nullable": false,
            "defaultValue": null,
            "description": "Whether GDPR consent was granted. Must be true to proceed with quote generation for Spain.",
            "migration_status": "NEW",
            "change_category": "COMPLIANCE",
            "data_source": "HARDCODED",
            "allowed_values": [true, false],
            "migrationNotes": "New column. Added for GDPR compliance; no equivalent in legacy schema."
          }
        ]
      },
      {
        "tableName": "quotes",
        "sourceTable": "quote_header",
        "isNew": false,
        "purpose": "Core quote record storing the full pricing snapshot and customer context at the time of quote generation.",
        "keyChanges": "Renamed from quote_header; PK changed from INT CHECKSUM to UUID; all pricing components stored inline; gdpr_consent_granted added.",
        "source_files": ["schema.postgresql.sql", "quote.repository.js", "openapi.yaml", "quote-request.model.ts"],
        "columns": [
          {
            "columnName": "quote_id",
            "dataType": "UUID",
            "isPrimaryKey": true,
            "foreignKey": null,
            "nullable": false,
            "defaultValue": null,
            "description": "Globally unique quote identifier generated via crypto.randomUUID().",
            "migration_status": "KEY_CHANGED",
            "change_category": "TECHNICAL",
            "data_source": "HARDCODED",
            "allowed_values": null,
            "migrationNotes": "PK strategy changed from INT generated via CHECKSUM() to UUID."
          },
          {
            "columnName": "risk_factor",
            "dataType": "NUMERIC(10,4)",
            "isPrimaryKey": false,
            "foreignKey": null,
            "nullable": false,
            "defaultValue": null,
            "description": "Computed risk multiplier. Base value 1.0 with age and product increments applied.",
            "migration_status": "NEW",
            "change_category": "STRUCTURAL",
            "data_source": "fn_calculate_risk_factor",
            "allowed_values": null,
            "migrationNotes": "New column. Computed via fn_calculate_risk_factor; replaces inline VB pricing logic in QuotePricingService."
          }
        ]
      }
    ]
  }
}
```

---

Payload:
{payload}
