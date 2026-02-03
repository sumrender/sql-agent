# Chinook SQLite Database Schema Documentation

## Overview
The Chinook database is a sample database representing a digital media store. It contains information about artists, albums, tracks, customers, employees, invoices, and playlists.

## Database Statistics
- **Total Tables**: 11 (excluding system tables)
- **Total Records**: ~16,000+ records across all tables

## Tables and Row Counts
| Table Name | Row Count |
|------------|-----------|
| artists | 275 |
| albums | 347 |
| tracks | 3,503 |
| customers | 59 |
| invoices | 412 |
| invoice_items | 2,240 |
| employees | 8 |
| genres | 25 |
| media_types | 5 |
| playlists | 18 |
| playlist_track | 8,715 |

---

## Table Schemas

### 1. artists
**Purpose**: Stores artist information

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| ArtistId | INTEGER | PRIMARY KEY, AUTOINCREMENT, NOT NULL | Unique identifier for each artist |
| Name | NVARCHAR(120) | | Artist name |

**Sample Data**:
```
ArtistId | Name
---------|------------------
1        | AC/DC
2        | Accept
3        | Aerosmith
4        | Alanis Morissette
5        | Alice In Chains
```

---

### 2. albums
**Purpose**: Stores album information linked to artists

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| AlbumId | INTEGER | PRIMARY KEY, AUTOINCREMENT, NOT NULL | Unique identifier for each album |
| Title | NVARCHAR(160) | NOT NULL | Album title |
| ArtistId | INTEGER | NOT NULL | Foreign key to artists.ArtistId |

**Sample Data**:
```
AlbumId | Title                                    | ArtistId
--------|------------------------------------------|---------
1       | For Those About To Rock We Salute You   | 1
2       | Balls to the Wall                       | 2
3       | Restless and Wild                       | 2
4       | Let There Be Rock                      | 1
5       | Big Ones                                | 3
```

---

### 3. tracks
**Purpose**: Stores individual track/song information

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| TrackId | INTEGER | PRIMARY KEY, AUTOINCREMENT, NOT NULL | Unique identifier for each track |
| Name | NVARCHAR(200) | NOT NULL | Track name |
| AlbumId | INTEGER | | Foreign key to albums.AlbumId (nullable) |
| MediaTypeId | INTEGER | NOT NULL | Foreign key to media_types.MediaTypeId |
| GenreId | INTEGER | | Foreign key to genres.GenreId (nullable) |
| Composer | NVARCHAR(220) | | Composer name(s) |
| Milliseconds | INTEGER | NOT NULL | Track duration in milliseconds |
| Bytes | INTEGER | | File size in bytes (nullable) |
| UnitPrice | NUMERIC(10,2) | NOT NULL | Price per track |

**Indexes**:
- IFK_TrackAlbumId on AlbumId
- IFK_TrackGenreId on GenreId
- IFK_TrackMediaTypeId on MediaTypeId

**Sample Data**:
```
TrackId | Name                                    | AlbumId | MediaTypeId | GenreId | Composer                                    | Milliseconds | Bytes     | UnitPrice
--------|-----------------------------------------|---------|-------------|---------|---------------------------------------------|--------------|-----------|----------
1       | For Those About To Rock (We Salute You)| 1       | 1           | 1       | Angus Young, Malcolm Young, Brian Johnson   | 343719       | 11170334  | 0.99
2       | Balls to the Wall                      | 2       | 2           | 1       |                                             | 342562       | 5510424   | 0.99
3       | Fast As a Shark                        | 3       | 2           | 1       | F. Baltes, S. Kaufman, U. Dirkscneider...  | 230619       | 3990994   | 0.99
```

---

### 4. genres
**Purpose**: Stores music genre categories

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| GenreId | INTEGER | PRIMARY KEY, AUTOINCREMENT, NOT NULL | Unique identifier for each genre |
| Name | NVARCHAR(120) | | Genre name |

**Sample Data**:
```
GenreId | Name
--------|------------------
1       | Rock
2       | Jazz
3       | Metal
4       | Alternative & Punk
5       | Rock And Roll
6       | Blues
7       | Latin
8       | Reggae
9       | Pop
10      | Soundtrack
```

---

### 5. media_types
**Purpose**: Stores media format types

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| MediaTypeId | INTEGER | PRIMARY KEY, AUTOINCREMENT, NOT NULL | Unique identifier for each media type |
| Name | NVARCHAR(120) | | Media type name |

**Sample Data**:
```
MediaTypeId | Name
------------|--------------------------
1           | MPEG audio file
2           | Protected AAC audio file
3           | Protected MPEG-4 video file
4           | Purchased AAC audio file
5           | AAC audio file
```

---

### 6. customers
**Purpose**: Stores customer information

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| CustomerId | INTEGER | PRIMARY KEY, AUTOINCREMENT, NOT NULL | Unique identifier for each customer |
| FirstName | NVARCHAR(40) | NOT NULL | Customer first name |
| LastName | NVARCHAR(20) | NOT NULL | Customer last name |
| Company | NVARCHAR(80) | | Company name (nullable) |
| Address | NVARCHAR(70) | | Street address (nullable) |
| City | NVARCHAR(40) | | City (nullable) |
| State | NVARCHAR(40) | | State/Province (nullable) |
| Country | NVARCHAR(40) | | Country (nullable) |
| PostalCode | NVARCHAR(10) | | Postal/ZIP code (nullable) |
| Phone | NVARCHAR(24) | | Phone number (nullable) |
| Fax | NVARCHAR(24) | | Fax number (nullable) |
| Email | NVARCHAR(60) | NOT NULL | Email address |
| SupportRepId | INTEGER | | Foreign key to employees.EmployeeId (nullable) |

**Sample Data**:
```
CustomerId | FirstName | LastName    | Company                                    | City              | State | Country | PostalCode | Phone              | Email
-----------|-----------|-------------|--------------------------------------------|-------------------|-------|---------|------------|--------------------|------------------
1          | Luís      | Gonçalves   | Embraer - Empresa Brasileira de Aeronáutica| São José dos Campos| SP    | Brazil  | 12227-000  | +55 (12) 3923-5555 | luisg@embraer.com.br
2          | Leonie    | Köhler      |                                            | Stuttgart         |       | Germany | 70174      | +49 0711 2842222   | leonekohler@surfeu.de
```

---

### 7. employees
**Purpose**: Stores employee information (hierarchical structure)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| EmployeeId | INTEGER | PRIMARY KEY, AUTOINCREMENT, NOT NULL | Unique identifier for each employee |
| LastName | NVARCHAR(20) | NOT NULL | Employee last name |
| FirstName | NVARCHAR(20) | NOT NULL | Employee first name |
| Title | NVARCHAR(30) | | Job title (nullable) |
| ReportsTo | INTEGER | | Foreign key to employees.EmployeeId (self-referencing, nullable) |
| BirthDate | DATETIME | | Date of birth (nullable) |
| HireDate | DATETIME | | Hire date (nullable) |
| Address | NVARCHAR(70) | | Street address (nullable) |
| City | NVARCHAR(40) | | City (nullable) |
| State | NVARCHAR(40) | | State/Province (nullable) |
| Country | NVARCHAR(40) | | Country (nullable) |
| PostalCode | NVARCHAR(10) | | Postal/ZIP code (nullable) |
| Phone | NVARCHAR(24) | | Phone number (nullable) |
| Fax | NVARCHAR(24) | | Fax number (nullable) |
| Email | NVARCHAR(60) | | Email address (nullable) |

**Sample Data**:
```
EmployeeId | LastName | FirstName | Title              | ReportsTo | BirthDate            | HireDate            | City    | State | Country | Email
-----------|----------|-----------|--------------------|-----------|---------------------|---------------------|---------|-------|---------|------------------
1          | Adams    | Andrew    | General Manager    |           | 1962-02-18 00:00:00 | 2002-08-14 00:00:00 | Edmonton | AB    | Canada  | andrew@chinookcorp.com
2          | Edwards  | Nancy     | Sales Manager      | 1         | 1958-12-08 00:00:00 | 2002-05-01 00:00:00 | Calgary | AB    | Canada  | nancy@chinookcorp.com
3          | Peacock  | Jane      | Sales Support Agent| 2         | 1973-08-29 00:00:00 | 2002-04-01 00:00:00 | Calgary | AB    | Canada  | jane@chinookcorp.com
```

---

### 8. invoices
**Purpose**: Stores invoice/order information

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| InvoiceId | INTEGER | PRIMARY KEY, AUTOINCREMENT, NOT NULL | Unique identifier for each invoice |
| CustomerId | INTEGER | NOT NULL | Foreign key to customers.CustomerId |
| InvoiceDate | DATETIME | NOT NULL | Invoice date and time |
| BillingAddress | NVARCHAR(70) | | Billing street address (nullable) |
| BillingCity | NVARCHAR(40) | | Billing city (nullable) |
| BillingState | NVARCHAR(40) | | Billing state/province (nullable) |
| BillingCountry | NVARCHAR(40) | | Billing country (nullable) |
| BillingPostalCode | NVARCHAR(10) | | Billing postal/ZIP code (nullable) |
| Total | NUMERIC(10,2) | NOT NULL | Total invoice amount |

**Sample Data**:
```
InvoiceId | CustomerId | InvoiceDate          | BillingAddress        | BillingCity | BillingState | BillingCountry | BillingPostalCode | Total
----------|------------|---------------------|----------------------|-------------|--------------|----------------|-------------------|-------
1         | 2          | 2009-01-01 00:00:00 | Theodor-Heuss-Straße 34| Stuttgart   |              | Germany        | 70174             | 1.98
2         | 4          | 2009-01-02 00:00:00 | Ullevålsveien 14      | Oslo        |              | Norway         | 0171              | 3.96
```

---

### 9. invoice_items
**Purpose**: Stores line items for each invoice (many-to-many relationship between invoices and tracks)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| InvoiceLineId | INTEGER | PRIMARY KEY, AUTOINCREMENT, NOT NULL | Unique identifier for each invoice line item |
| InvoiceId | INTEGER | NOT NULL | Foreign key to invoices.InvoiceId |
| TrackId | INTEGER | NOT NULL | Foreign key to tracks.TrackId |
| UnitPrice | NUMERIC(10,2) | NOT NULL | Price per unit at time of sale |
| Quantity | INTEGER | NOT NULL | Quantity purchased |

**Sample Data**:
```
InvoiceLineId | InvoiceId | TrackId | UnitPrice | Quantity
--------------|-----------|---------|-----------|----------
1             | 1         | 2       | 0.99      | 1
2             | 1         | 4       | 0.99      | 1
3             | 2         | 6       | 0.99      | 1
```

---

### 10. playlists
**Purpose**: Stores playlist information

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| PlaylistId | INTEGER | PRIMARY KEY, AUTOINCREMENT, NOT NULL | Unique identifier for each playlist |
| Name | NVARCHAR(120) | | Playlist name |

**Sample Data**:
```
PlaylistId | Name
-----------|------------
1          | Music
2          | Movies
3          | TV Shows
4          | Audiobooks
5          | 90's Music
```

---

### 11. playlist_track
**Purpose**: Junction table linking playlists to tracks (many-to-many relationship)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| PlaylistId | INTEGER | NOT NULL, PRIMARY KEY (composite) | Foreign key to playlists.PlaylistId |
| TrackId | INTEGER | NOT NULL, PRIMARY KEY (composite) | Foreign key to tracks.TrackId |

**Note**: Composite primary key on (PlaylistId, TrackId)

**Sample Data**:
```
PlaylistId | TrackId
-----------|--------
1          | 3402
1          | 3389
1          | 3390
```

---

## Entity Relationships

### Relationship Diagram

```
artists (1) ────────< (many) albums
                              │
                              │ (1)
                              │
                              │ (many)
                              ▼
                           tracks
                              │
                    ┌─────────┼─────────┐
                    │         │         │
              (many)│         │(many)   │(many)
                    │         │         │
                    ▼         ▼         ▼
            invoice_items  playlist_track
                    │         │
                    │(many)   │(many)
                    │         │
                    ▼         ▼
              invoices    playlists
                    │
                    │(many)
                    │
                    ▼
              customers
                    │
                    │(many)
                    │
                    ▼
              employees (self-referencing)
```

### Foreign Key Relationships

1. **albums → artists**
   - `albums.ArtistId` → `artists.ArtistId`
   - ON DELETE NO ACTION, ON UPDATE NO ACTION

2. **tracks → albums**
   - `tracks.AlbumId` → `albums.AlbumId`
   - ON DELETE NO ACTION, ON UPDATE NO ACTION
   - Nullable (tracks can exist without albums)

3. **tracks → genres**
   - `tracks.GenreId` → `genres.GenreId`
   - ON DELETE NO ACTION, ON UPDATE NO ACTION
   - Nullable

4. **tracks → media_types**
   - `tracks.MediaTypeId` → `media_types.MediaTypeId`
   - ON DELETE NO ACTION, ON UPDATE NO ACTION
   - Required (NOT NULL)

5. **customers → employees**
   - `customers.SupportRepId` → `employees.EmployeeId`
   - ON DELETE NO ACTION, ON UPDATE NO ACTION
   - Nullable (customers may not have a support rep)

6. **employees → employees** (self-referencing)
   - `employees.ReportsTo` → `employees.EmployeeId`
   - ON DELETE NO ACTION, ON UPDATE NO ACTION
   - Nullable (top-level employees don't report to anyone)
   - Creates hierarchical structure (manager → employee)

7. **invoices → customers**
   - `invoices.CustomerId` → `customers.CustomerId`
   - ON DELETE NO ACTION, ON UPDATE NO ACTION
   - Required (NOT NULL)

8. **invoice_items → invoices**
   - `invoice_items.InvoiceId` → `invoices.InvoiceId`
   - ON DELETE NO ACTION, ON UPDATE NO ACTION
   - Required (NOT NULL)

9. **invoice_items → tracks**
   - `invoice_items.TrackId` → `tracks.TrackId`
   - ON DELETE NO ACTION, ON UPDATE NO ACTION
   - Required (NOT NULL)

10. **playlist_track → playlists**
    - `playlist_track.PlaylistId` → `playlists.PlaylistId`
    - ON DELETE NO ACTION, ON UPDATE NO ACTION
    - Required (NOT NULL)

11. **playlist_track → tracks**
    - `playlist_track.TrackId` → `tracks.TrackId`
    - ON DELETE NO ACTION, ON UPDATE NO ACTION
    - Required (NOT NULL)

---

## Key Business Rules

1. **Music Catalog Hierarchy**:
   - Artists have many Albums
   - Albums have many Tracks
   - Tracks belong to one Genre (optional)
   - Tracks have one MediaType (required)

2. **Sales Structure**:
   - Customers are assigned to Support Representatives (employees)
   - Customers place Invoices
   - Invoices contain multiple InvoiceItems
   - Each InvoiceItem represents one Track purchase

3. **Employee Hierarchy**:
   - Employees can report to other Employees (self-referencing)
   - Creates organizational hierarchy (General Manager → Sales Manager → Sales Support Agents)

4. **Playlists**:
   - Playlists can contain many Tracks
   - Tracks can belong to many Playlists
   - Many-to-many relationship via playlist_track junction table

---

## Common Query Patterns for Testing

### 1. Artist-Album-Track Chain
```sql
SELECT a.Name AS Artist, al.Title AS Album, t.Name AS Track
FROM artists a
JOIN albums al ON a.ArtistId = al.ArtistId
JOIN tracks t ON al.AlbumId = t.AlbumId
WHERE a.Name = 'AC/DC';
```

### 2. Customer Purchase History
```sql
SELECT c.FirstName, c.LastName, i.InvoiceDate, i.Total
FROM customers c
JOIN invoices i ON c.CustomerId = i.CustomerId
ORDER BY i.InvoiceDate DESC;
```

### 3. Invoice Details with Track Information
```sql
SELECT i.InvoiceId, t.Name AS TrackName, ii.UnitPrice, ii.Quantity
FROM invoices i
JOIN invoice_items ii ON i.InvoiceId = ii.InvoiceId
JOIN tracks t ON ii.TrackId = t.TrackId
WHERE i.InvoiceId = 1;
```

### 4. Employee Hierarchy
```sql
SELECT e1.FirstName || ' ' || e1.LastName AS Employee,
       e2.FirstName || ' ' || e2.LastName AS Manager
FROM employees e1
LEFT JOIN employees e2 ON e1.ReportsTo = e2.EmployeeId;
```

### 5. Playlist Contents
```sql
SELECT p.Name AS Playlist, t.Name AS Track, a.Name AS Artist
FROM playlists p
JOIN playlist_track pt ON p.PlaylistId = pt.PlaylistId
JOIN tracks t ON pt.TrackId = t.TrackId
LEFT JOIN albums al ON t.AlbumId = al.AlbumId
LEFT JOIN artists a ON al.ArtistId = a.ArtistId
WHERE p.Name = '90''s Music';
```

---

## Notes for SQL Agent Testing

1. **Complex Joins**: The database has multiple levels of joins (artists → albums → tracks → invoice_items → invoices → customers)

2. **Self-Referencing**: The employees table has a self-referencing foreign key (ReportsTo), useful for testing hierarchical queries

3. **Nullable Foreign Keys**: Some foreign keys are nullable (tracks.AlbumId, tracks.GenreId, customers.SupportRepId), requiring LEFT JOINs in some queries

4. **Composite Primary Key**: playlist_track uses a composite primary key, useful for testing many-to-many relationships

5. **Data Types**: Mix of INTEGER, NVARCHAR, DATETIME, and NUMERIC types for comprehensive type testing

6. **Aggregations**: Good for testing GROUP BY, SUM, COUNT, AVG operations (e.g., total sales per customer, tracks per album)

7. **Date Operations**: InvoiceDate and employee dates (BirthDate, HireDate) allow testing date-based queries

8. **Text Search**: Artist names, track names, album titles provide opportunities for LIKE, pattern matching, and text search testing
