export const PIPELINE_MODE_OPTIONS = [
  {
    key: "table",
    label: "Table",
    description:"This migration mode allows to migrate whole table(s) from a source connection to destination connection."
  },
  {
    key: "custom_sql",
    label: "Custom SQL",
    description:"This migration mode allows to provide a custom sql statement that is run on source connection and migrate the fetched data to destination connection."
  },
];

export const QUERY_MODES = [
  {
    label: "Replace",
    value: "replace",
    description: "Replaces the entire table in the destination",
    details: `
**What it does :** Completely overwrites the existing table in your destination. It wipes the old data and replaces it with the fresh data from your source.

**Best for :** Full refreshes or snapshots. Use this when you want to ensure your destination exactly matches your source (e.g., daily product catalogs or currency exchange rates) and you don't need to keep a history of previous migrations.

**Warning :** Any data currently in the destination table that is not in the new source file will be lost.
    `,
  },
  {
    label: "Append",
    value: "append",
    description: "Adds new records to the existing table",
    details: `
**What it does :** Adds new records to the end of your existing destination table without modifying or deleting what is already there.

**Best for :** "Stateless" data like logs, events, or sensor readings. Use this when you are continuously streaming new records and don't need to worry about updating older rows or handling duplicates.
    `,
  },
  {
    label: "Merge",
    value: "merge",
    description: "Merges records based on primary key",
    details: `
**What it does :** Updates existing records and inserts new ones. It uses a "Primary Key" to identify if a record already exists; if it does, it updates the row with new values. If it doesn't, it creates a new row.

**Best for :** "Stateful" data that changes over time, such as customer profiles, inventory levels, or CRM records. Use this to keep your destination up-to-date without creating duplicate entries for the same ID.

**Requirement :** This mode requires you to have a Primary Key defined for your table so the system knows which records to match.
    `,
  },
];
