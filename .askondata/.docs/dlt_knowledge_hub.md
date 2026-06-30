# dlt Knowledge Hub

> Condensed reference for **dlt** (data load tool) — an open-source Python library
> that loads data from messy/varied sources into well-structured datasets.
> Built so future agents can quickly get context and jump to the right doc page.
>
> - Docs home: https://dlthub.com/docs/intro
> - Site: https://dlthub.com
> - GitHub: https://github.com/dlt-hub/dlt
> - Source captured: 2026-05-29

---

## 1. What is dlt?

dlt is a lightweight Python library for **EL(T)** — Extract, Load, (Transform). You
write plain Python; dlt handles schema inference, normalization, incremental
loading, schema evolution, and loading into 20+ destinations from 8,000+ sources.

**Install:** `pip install dlt`

**Mental model:** `pipeline` moves data from a `source`/`resource` into a `destination`,
organizing tables inside a `dataset` (schema/namespace).

```python
import dlt

pipeline = dlt.pipeline(
    pipeline_name="github_issues",
    destination="duckdb",
    dataset_name="github_data",
)
load_info = pipeline.run(data, table_name="issues")
print(load_info)
```

---

## 2. Core Concepts (`/docs/general-usage/...`)

| Concept | What it is | Doc |
|---|---|---|
| **Pipeline** | Moves data from Python code → destination; evaluates sources/resources/generators and loads them. | [/general-usage/pipeline](https://dlthub.com/docs/general-usage/pipeline) |
| **Source** | A collection of related resources, grouped with `@dlt.source`. | [/general-usage/source](https://dlthub.com/docs/general-usage/source) |
| **Resource** | An individual data-extraction unit (usually → one table), declared with `@dlt.resource`. | [/general-usage/resource](https://dlthub.com/docs/general-usage/resource) |
| **Destination** | Target system (DuckDB, BigQuery, Snowflake, …). | [/general-usage/destination](https://dlthub.com/docs/general-usage/destination) |
| **Dataset** | Logical group of tables (DB schema or folder of files). | [/general-usage/dataset-access/dataset](https://dlthub.com/docs/general-usage/dataset-access/dataset) |
| **Schema** | Inferred structure; supports evolution and contracts. | [/general-usage/schema](https://dlthub.com/docs/general-usage/schema) |
| **State** | Persisted between runs in the destination (powers incremental). | [/general-usage/state](https://dlthub.com/docs/general-usage/state) |
| **Glossary** | Terminology definitions. | [/general-usage/glossary](https://dlthub.com/docs/general-usage/glossary) |

### Resource & source pattern

```python
@dlt.resource(table_name="issues", write_disposition="merge", primary_key="id")
def get_issues(updated_at=dlt.sources.incremental("updated_at")):
    for page in paginate("https://api.github.com/repos/dlt-hub/dlt/issues"):
        yield page

@dlt.source
def github_source():
    return get_issues  # group multiple resources here
```

Useful pipeline features: working directories & state persistence, **dev mode**,
**refresh modes** (`drop_sources`, `drop_resources`, `drop_data`), and progress
monitoring via `enlighten` / `tqdm` / logging.

---

## 3. Write Dispositions & Incremental Loading

Docs: [/general-usage/incremental-loading](https://dlthub.com/docs/general-usage/incremental-loading)

**Decision rule:** Is the data *stateless* (immutable events → `append`) or
*stateful* (records change → `merge` / `replace`)?

| Disposition | Behavior | Use case |
|---|---|---|
| **append** | Adds new rows, never removes. | Events, logs, immutable data. |
| **replace** | Overwrites the entire table with this run's output. | Full refresh, small dims. |
| **merge** | Upsert via `primary_key` / `merge_key`; dedup + updates. | Stateful records. |

```python
p = dlt.pipeline(destination="bigquery", dataset_name="dataset_name")
p.run(merge_source(), write_disposition="replace")  # one-off full refresh
p.run(merge_source())                               # normal merge run
```

**Advanced:**
- **Cursor-based incremental** — `dlt.sources.incremental("updated_at")` tracks max value, persists in state, filters new data.
- **Lag / attribution windows** — re-pull a trailing time window.
- **SCD2** (Slowly Changing Dimensions) — keep temporal history of changes.

---

## 4. Sources (`/docs/dlt-ecosystem/verified-sources/...`)

**Core sources:** REST API client, 30+ **SQL databases**, **Object store / filesystem**.

Verified sources (slug = `/docs/dlt-ecosystem/verified-sources/<slug>`):

`airtable`, `amazon_kinesis`, `asana`, `chess`, `facebook_ads`, `freshdesk`,
`github`, `google_ads`, `google_analytics`, `google_sheets`, `hubspot`, `inbox`,
`jira`, `kafka`, `matomo`, `mongodb`, `mux`, `notion`, `personio`,
`pg_replication` (Postgres replication), `pipedrive`, `salesforce`, `scrapy`,
`shopify`, `slack`, `strapi`, `stripe`, `workable`, `zendesk`.

Index: [/dlt-ecosystem/verified-sources](https://dlthub.com/docs/dlt-ecosystem/verified-sources/)

---

## 5. Destinations (`/docs/dlt-ecosystem/destinations/...`)

Slug = `/docs/dlt-ecosystem/destinations/<slug>`:

| | | |
|---|---|---|
| `duckdb` | `motherduck` | `ducklake` |
| `bigquery` | `snowflake` | `redshift` |
| `postgres` | `mssql` | `synapse` |
| `athena` | `clickhouse` | `databricks` |
| `dremio` | `fabric` | `sqlalchemy` (any SQLAlchemy DB) |
| `filesystem` (object store) | `delta-iceberg` / `iceberg` | `lance` / `lancedb` |
| `qdrant` (vector) | `weaviate` (vector) | `huggingface` |
| `destination` (Reverse ETL / custom sink) | `community-destinations` | |

Index: [/dlt-ecosystem/destinations](https://dlthub.com/docs/dlt-ecosystem/destinations/)

File formats for filesystem/staging: Parquet, CSV, JSONL.

---

## 6. Configuration & Credentials (`/docs/general-usage/credentials/...`)

Principle: **separate secrets/config from code.** Functions decorated with
`@dlt.source` / `@dlt.resource` / `@dlt.destination` auto-generate config lookups.

Common providers (priority order): env vars → `secrets.toml` / `config.toml`
(`.dlt/` dir) → vaults → in-code defaults.

| Page | Slug |
|---|---|
| Setup (toml files, env vars) | [/general-usage/credentials/setup](https://dlthub.com/docs/general-usage/credentials/setup) |
| Advanced (providers, custom) | [/general-usage/credentials/advanced](https://dlthub.com/docs/general-usage/credentials/advanced) |
| Vaults | [/general-usage/credentials/vaults](https://dlthub.com/docs/general-usage/credentials/vaults) |
| Complex types | [/general-usage/credentials/complex_types](https://dlthub.com/docs/general-usage/credentials/complex_types) |

---

## 7. Transformations (`/docs/dlt-ecosystem/transformations/...`)

- **ETL (before load):** light processing with `add_map()` and `@dlt.transformer`
  — add/derive columns, redact PII, cast types.
  - Overview: [/dlt-ecosystem/transformations](https://dlthub.com/docs/dlt-ecosystem/transformations)
  - Add column / map: `/dlt-ecosystem/transformations/add-map`
- **ELT (after load):** transform in the destination where compute lives.
  - Python / Pandas: `/dlt-ecosystem/transformations/python`
  - SQL & dbt: see transformations index (dbt runner, SQL clients).

---

## 8. Walkthroughs & Production (`/docs/walkthroughs/...`, `/docs/running-in-production/...`)

| Guide | URL |
|---|---|
| Create a pipeline | [/walkthroughs/create-a-pipeline](https://dlthub.com/docs/walkthroughs/create-a-pipeline) |
| Tutorial: load from an API | [/tutorial/load-data-from-an-api](https://dlthub.com/docs/tutorial/load-data-from-an-api) |
| Deploy with GitHub Actions | [/walkthroughs/deploy-a-pipeline/deploy-with-github-actions](https://dlthub.com/docs/walkthroughs/deploy-a-pipeline/deploy-with-github-actions) |
| Running in production | [/running-in-production/running](https://dlthub.com/docs/running-in-production/running) |
| Monitoring | [/running-in-production/monitoring](https://dlthub.com/docs/running-in-production/monitoring) |
| Alerting | [/running-in-production/alerting](https://dlthub.com/docs/running-in-production/alerting) |

Other deploy targets referenced: Airflow, serverless / cloud functions.

---

## 9. Schema Management & Data Quality

- **Schema contracts** — control how schema may evolve (freeze, evolve, discard):
  [/general-usage/schema-contracts](https://dlthub.com/docs/general-usage/schema-contracts)
- **Schema evolution** — dlt auto-adapts to new/changed columns by default.
- **Data quality lifecycle** & enrichments — validation and quality practices
  (see Data Quality section in sidebar).

---

## 10. Performance & Reference

- **Performance / optimization:** [/reference/performance](https://dlthub.com/docs/reference/performance)
  — parallelism, memory, buffer/file rotation, normalization tuning.
- **API Reference** (Pydoc-style): `dlt/__init__`, pipeline, extract, common,
  destinations, dataset access, workspace tooling. Browse from docs sidebar → Reference.
- **Sitemap** (1000+ URLs, authoritative index): https://dlthub.com/docs/sitemap.xml

---

## 11. Quick "where do I look?" cheat sheet

| I need to… | Go to |
|---|---|
| Get started fast | `/intro`, `/tutorial/load-data-from-an-api` |
| Understand pipeline/source/resource | §2 above → `/general-usage/*` |
| Choose append vs merge vs replace | §3 → `/general-usage/incremental-loading` |
| Connect a SaaS/DB source | §4 → `/dlt-ecosystem/verified-sources/<name>` |
| Load to a warehouse/lake | §5 → `/dlt-ecosystem/destinations/<name>` |
| Manage secrets | §6 → `/general-usage/credentials/setup` |
| Transform data | §7 → `/dlt-ecosystem/transformations` |
| Deploy & monitor | §8 → `/walkthroughs`, `/running-in-production` |
| Control schema changes | §9 → `/general-usage/schema-contracts` |
| Tune performance | §10 → `/reference/performance` |
| Find any page | `/docs/sitemap.xml` |

> **Tip for agents:** All doc paths are relative to `https://dlthub.com/docs`.
> When a specific detail isn't captured here, fetch the matching slug above or
> consult the sitemap for the exact page.
