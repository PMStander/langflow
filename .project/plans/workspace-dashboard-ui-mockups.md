# Workspace Dashboard & CRM UI Mockups

## Dashboard View

The dashboard will be the central hub for workspace information and quick access to CRM features.

```
+-------------------------------------------------------+
|                     Header                            |
+-------------------------------------------------------+
| Sidebar |                                             |
|         |  +-------------------+  +----------------+  |
| [Home]  |  |                   |  |                |  |
| [Dash]  |  |  Workspace Stats  |  |  Recent        |  |
| [Flows] |  |  - Total Clients  |  |  Activity      |  |
| [CRM]   |  |  - Active Invoices|  |  - User actions|  |
| [Tasks] |  |  - Revenue        |  |  - Updates     |  |
|         |  +-------------------+  +----------------+  |
|         |                                             |
|         |  +-------------------+  +----------------+  |
|         |  |                   |  |                |  |
|         |  |  Client Overview  |  |  Tasks         |  |
|         |  |  - New clients    |  |  - Due today   |  |
|         |  |  - By status      |  |  - Upcoming    |  |
|         |  +-------------------+  +----------------+  |
|         |                                             |
+---------+---------------------------------------------+
```

## Sidebar Navigation

The sidebar will be context-aware, showing different options based on the current view.

### Dashboard/CRM View Sidebar

```
+-------------------+
| Workspace Name ▼  |
+-------------------+
|                   |
| [Dashboard]       |
|                   |
| [Projects/Flows]  |
|                   |
| CRM               |
|  └ [Clients]      |
|  └ [Invoices]     |
|  └ [Opportunities]|
|                   |
| [Tasks]           |
|                   |
| [Settings]        |
|                   |
+-------------------+
```

### Flows View Sidebar (Existing)

```
+-------------------+
| Workspace Name ▼  |
+-------------------+
|                   |
| [Dashboard]       |
|                   |
| Projects          |
|  └ [Project 1]    |
|  └ [Project 2]    |
|  └ [+ New Project]|
|                   |
| [CRM]             |
|                   |
| [Settings]        |
|                   |
+-------------------+
```

## CRM Views

### Clients View

```
+-------------------------------------------------------+
|                     Header                            |
+-------------------------------------------------------+
| Sidebar |  Clients                          [+ New]   |
|         |                                             |
|         |  +-------------------------------------------+
|         |  | Search...                    [Filter ▼]  |
|         |  +-------------------------------------------+
|         |  | Name    | Company  | Status | Created   |
|         |  |-----------------------------------------|
|         |  | Client A | ABC Inc. | Active | 05/20/25 |
|         |  | Client B | XYZ Corp | Lead   | 05/18/25 |
|         |  | Client C | 123 LLC  | Active | 05/15/25 |
|         |  |-----------------------------------------|
|         |  |                                         |
|         |  |       Pagination: < 1 2 3 ... >         |
|         |  |                                         |
|         |  +-------------------------------------------+
|         |                                             |
+---------+---------------------------------------------+
```

### Client Details View

```
+-------------------------------------------------------+
|                     Header                            |
+-------------------------------------------------------+
| Sidebar |  Client: ABC Inc.                [Edit]     |
|         |                                             |
|         |  +-------------------+  +----------------+  |
|         |  |                   |  |                |  |
|         |  |  Client Details   |  |  Contact Info  |  |
|         |  |  - Status: Active |  |  - Email       |  |
|         |  |  - Since: 05/20/25|  |  - Phone       |  |
|         |  |  - Owner: John D. |  |  - Address     |  |
|         |  +-------------------+  +----------------+  |
|         |                                             |
|         |  +-------------------------------------------+
|         |  | Tabs: Overview | Invoices | Opportunities |
|         |  +-------------------------------------------+
|         |  |                                         |
|         |  | [Tab content based on selection]        |
|         |  |                                         |
|         |  +-------------------------------------------+
|         |                                             |
+---------+---------------------------------------------+
```

### Invoices View

```
+-------------------------------------------------------+
|                     Header                            |
+-------------------------------------------------------+
| Sidebar |  Invoices                        [+ New]    |
|         |                                             |
|         |  +-------------------------------------------+
|         |  | Search...                    [Filter ▼]  |
|         |  +-------------------------------------------+
|         |  | Number | Client  | Amount | Status | Due |
|         |  |-----------------------------------------|
|         |  | INV-001 | ABC Inc.| $1,200 | Paid   | -- |
|         |  | INV-002 | XYZ Co. | $3,500 | Sent   | 6/1|
|         |  | INV-003 | 123 LLC | $750   | Draft  | -- |
|         |  |-----------------------------------------|
|         |  |                                         |
|         |  |       Pagination: < 1 2 3 ... >         |
|         |  |                                         |
|         |  +-------------------------------------------+
|         |                                             |
+---------+---------------------------------------------+
```

## Data Visualization Components

### Workspace Stats Card

```
+-------------------------------------------+
|  Workspace Statistics                     |
|                                           |
|  +-------------+  +-------------+         |
|  | 12          |  | $24,500     |         |
|  | Clients     |  | Revenue     |         |
|  +-------------+  +-------------+         |
|                                           |
|  +-------------+  +-------------+         |
|  | 8           |  | 5           |         |
|  | Invoices    |  | Opportunities|         |
|  +-------------+  +-------------+         |
|                                           |
+-------------------------------------------+
```

### Client Status Distribution Chart

```
+-------------------------------------------+
|  Client Status Distribution               |
|                                           |
|  [Pie Chart]                              |
|                                           |
|  Legend:                                  |
|  ● Active (8)                             |
|  ● Lead (3)                               |
|  ● Inactive (1)                           |
|                                           |
+-------------------------------------------+
```

### Revenue Timeline Chart

```
+-------------------------------------------+
|  Revenue Timeline                         |
|                                           |
|  [Line Chart]                             |
|                                           |
|  Jan Feb Mar Apr May Jun Jul Aug Sep Oct  |
|                                           |
|  Y-axis: Revenue                          |
|  X-axis: Months                           |
|                                           |
+-------------------------------------------+
```

### Task Priority Distribution

```
+-------------------------------------------+
|  Task Priority                            |
|                                           |
|  [Horizontal Bar Chart]                   |
|                                           |
|  High   ████████████ 12                   |
|  Medium ██████████████████ 18             |
|  Low    ██████ 6                          |
|                                           |
+-------------------------------------------+
```

## Form Components

### New Client Form

```
+-------------------------------------------+
|  Create New Client                 [X]    |
|                                           |
|  Name*:                                   |
|  [                                    ]   |
|                                           |
|  Company:                                 |
|  [                                    ]   |
|                                           |
|  Email:                                   |
|  [                                    ]   |
|                                           |
|  Phone:                                   |
|  [                                    ]   |
|                                           |
|  Status:                                  |
|  [ Active ▼ ]                             |
|                                           |
|  Description:                             |
|  [                                    ]   |
|  [                                    ]   |
|                                           |
|  [Cancel]                [Create Client]  |
|                                           |
+-------------------------------------------+
```

### New Invoice Form

```
+-------------------------------------------+
|  Create New Invoice                [X]    |
|                                           |
|  Client*:                                 |
|  [ Select Client ▼ ]                      |
|                                           |
|  Invoice Number*:                         |
|  [                                    ]   |
|                                           |
|  Amount*:                                 |
|  [                                    ]   |
|                                           |
|  Issue Date:                              |
|  [ MM/DD/YYYY ]                           |
|                                           |
|  Due Date:                                |
|  [ MM/DD/YYYY ]                           |
|                                           |
|  Status:                                  |
|  [ Draft ▼ ]                              |
|                                           |
|  Description:                             |
|  [                                    ]   |
|  [                                    ]   |
|                                           |
|  [Cancel]                [Create Invoice] |
|                                           |
+-------------------------------------------+
```

## Mobile Responsive Design

The UI will be responsive and adapt to different screen sizes:

### Mobile Dashboard View

```
+----------------------------+
| Header + Workspace Select  |
+----------------------------+
| [☰] Dashboard              |
+----------------------------+
|                            |
| +------------------------+ |
| |                        | |
| |    Workspace Stats     | |
| |                        | |
| +------------------------+ |
|                            |
| +------------------------+ |
| |                        | |
| |    Recent Activity     | |
| |                        | |
| +------------------------+ |
|                            |
| +------------------------+ |
| |                        | |
| |    Tasks               | |
| |                        | |
| +------------------------+ |
|                            |
+----------------------------+
| [Dashboard][CRM][Flows]    |
+----------------------------+
```

These mockups provide a visual guide for implementing the UI components of the Workspace Dashboard and CRM feature.
