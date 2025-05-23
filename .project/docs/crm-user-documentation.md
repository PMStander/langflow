# Langflow CRM Module User Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Dashboard](#dashboard)
4. [Clients Management](#clients-management)
5. [Invoices Management](#invoices-management)
6. [Opportunities Management](#opportunities-management)
7. [Tasks Management](#tasks-management)
8. [Reports](#reports)
9. [Workspace Integration](#workspace-integration)
10. [API Reference](#api-reference)

## Introduction

The Langflow CRM (Customer Relationship Management) module provides a comprehensive set of tools to manage your client relationships, track sales opportunities, manage invoices, and organize tasks. The CRM module is fully integrated with Langflow's workspace system, allowing you to organize your CRM data by workspace and control access through workspace permissions.

### Key Features

- **Dashboard**: Get an overview of your CRM data with key metrics and visualizations
- **Clients Management**: Manage your client information and track client status
- **Invoices Management**: Create and track invoices for your clients
- **Opportunities Management**: Track sales opportunities and their progress
- **Tasks Management**: Organize and track tasks related to clients, invoices, and opportunities
- **Reports**: Generate reports to analyze your CRM data
- **Workspace Integration**: Organize your CRM data by workspace and control access through workspace permissions

## Getting Started

To access the CRM module, click on the "CRM" icon in the sidebar navigation. This will take you to the CRM dashboard, which provides an overview of your CRM data.

The CRM module is organized into several sections, accessible through the sidebar navigation within the CRM module:

- **Dashboard**: Overview of your CRM data
- **Clients**: Manage your client information
- **Invoices**: Create and track invoices
- **Opportunities**: Track sales opportunities
- **Tasks**: Organize and track tasks
- **Reports**: Generate reports to analyze your CRM data

## Dashboard

The CRM dashboard provides an overview of your CRM data with key metrics and visualizations. The dashboard includes:

- **Client Statistics**: Total number of clients and active clients
- **Invoice Statistics**: Total number of invoices and total revenue
- **Opportunity Statistics**: Total number of opportunities and total value of open opportunities
- **Task Statistics**: Number of open, in-progress, and completed tasks
- **Client Distribution**: Distribution of clients by status (active, inactive, lead)
- **Recent Activity**: Recent activity across all CRM entities

The dashboard data is filtered by the currently selected workspace. You can change the workspace using the workspace selector in the header.

## Clients Management

The Clients section allows you to manage your client information and track client status.

### Viewing Clients

The Clients page displays a list of all clients in the current workspace. You can:

- **Filter** clients by status (active, inactive, lead)
- **Search** for clients by name, email, or company
- **Sort** clients by various fields
- **Paginate** through the client list

### Creating a Client

To create a new client:

1. Click the "Add Client" button
2. Fill in the client details:
   - **Name**: Client name (required)
   - **Email**: Client email address
   - **Phone**: Client phone number
   - **Company**: Client company name
   - **Status**: Client status (active, inactive, lead)
   - **Description**: Additional information about the client
3. Click "Create" to save the client

### Editing a Client

To edit a client:

1. Click on the client in the client list
2. Click the "Edit" button
3. Update the client details
4. Click "Save" to update the client

### Deleting a Client

To delete a client:

1. Click on the client in the client list
2. Click the "Delete" button
3. Confirm the deletion

**Note**: Deleting a client will also delete all associated invoices, opportunities, and tasks.

## Invoices Management

The Invoices section allows you to create and track invoices for your clients.

### Viewing Invoices

The Invoices page displays a list of all invoices in the current workspace. You can:

- **Filter** invoices by status (draft, sent, paid, overdue)
- **Filter** invoices by client
- **Search** for invoices by invoice number
- **Sort** invoices by various fields
- **Paginate** through the invoice list

### Creating an Invoice

To create a new invoice:

1. Click the "Add Invoice" button
2. Fill in the invoice details:
   - **Client**: Select a client (required)
   - **Invoice Number**: Invoice number (required)
   - **Amount**: Invoice amount (required)
   - **Status**: Invoice status (draft, sent, paid, overdue)
   - **Issue Date**: Date the invoice was issued
   - **Due Date**: Date the invoice is due
   - **Description**: Additional information about the invoice
3. Click "Create" to save the invoice

### Editing an Invoice

To edit an invoice:

1. Click on the invoice in the invoice list
2. Click the "Edit" button
3. Update the invoice details
4. Click "Save" to update the invoice

### Deleting an Invoice

To delete an invoice:

1. Click on the invoice in the invoice list
2. Click the "Delete" button
3. Confirm the deletion

## Opportunities Management

The Opportunities section allows you to track sales opportunities and their progress.

### Viewing Opportunities

The Opportunities page displays a list of all opportunities in the current workspace. You can:

- **Filter** opportunities by status (new, qualified, proposal, negotiation, won, lost)
- **Filter** opportunities by client
- **Search** for opportunities by name
- **Sort** opportunities by various fields
- **Paginate** through the opportunity list

### Creating an Opportunity

To create a new opportunity:

1. Click the "Add Opportunity" button
2. Fill in the opportunity details:
   - **Client**: Select a client (required)
   - **Name**: Opportunity name (required)
   - **Value**: Estimated value of the opportunity
   - **Status**: Opportunity status (new, qualified, proposal, negotiation, won, lost)
   - **Expected Close Date**: Expected date to close the opportunity
   - **Description**: Additional information about the opportunity
3. Click "Create" to save the opportunity

### Editing an Opportunity

To edit an opportunity:

1. Click on the opportunity in the opportunity list
2. Click the "Edit" button
3. Update the opportunity details
4. Click "Save" to update the opportunity

### Deleting an Opportunity

To delete an opportunity:

1. Click on the opportunity in the opportunity list
2. Click the "Delete" button
3. Confirm the deletion

## Tasks Management

The Tasks section allows you to organize and track tasks related to clients, invoices, and opportunities.

### Viewing Tasks

The Tasks page displays a list of all tasks in the current workspace. You can:

- **Filter** tasks by status (open, in_progress, completed, cancelled)
- **Filter** tasks by priority (low, medium, high)
- **Filter** tasks by assignee
- **Filter** tasks by client, invoice, or opportunity
- **Search** for tasks by title
- **Sort** tasks by various fields
- **Paginate** through the task list

### Creating a Task

To create a new task:

1. Click the "Add Task" button
2. Fill in the task details:
   - **Title**: Task title (required)
   - **Description**: Task description
   - **Status**: Task status (open, in_progress, completed, cancelled)
   - **Priority**: Task priority (low, medium, high)
   - **Due Date**: Task due date
   - **Assigned To**: User assigned to the task
   - **Client**: Associated client
   - **Invoice**: Associated invoice
   - **Opportunity**: Associated opportunity
3. Click "Create" to save the task

### Editing a Task

To edit a task:

1. Click on the task in the task list
2. Click the "Edit" button
3. Update the task details
4. Click "Save" to update the task

### Deleting a Task

To delete a task:

1. Click on the task in the task list
2. Click the "Delete" button
3. Confirm the deletion

## Reports

The Reports section allows you to generate reports to analyze your CRM data.

### Available Report Types

- **Sales Overview**: Overview of sales performance including revenue, invoices, and opportunities
- **Client Activity**: Analysis of client engagement and activity
- **Opportunity Pipeline**: Analysis of the sales pipeline and opportunity progression
- **Invoice Aging**: Analysis of invoice payment status and aging
- **Task Completion**: Analysis of task completion rates and performance
- **Revenue Forecast**: Forecast of future revenue based on opportunities and invoices

### Generating a Report

To generate a report:

1. Select a report type
2. Configure the report parameters:
   - **Workspace**: Select a workspace
   - **Time Frame**: Select a time frame (last 7 days, last 30 days, last 90 days, last year, custom)
   - **Start Date**: If using a custom time frame, select a start date
   - **End Date**: If using a custom time frame, select an end date
   - **Client**: Optionally filter by a specific client
   - **Export Format**: Optionally select an export format (PDF, CSV, Excel)
3. Click "Generate Report" to view the report

### Exporting a Report

To export a report:

1. Generate the report
2. Click the "Export" button
3. Select an export format (PDF, CSV, Excel)
4. The report will be downloaded in the selected format

## Workspace Integration

The CRM module is fully integrated with Langflow's workspace system, allowing you to organize your CRM data by workspace and control access through workspace permissions.

### Workspace Permissions

- **Owner**: Can perform all actions on CRM data in the workspace
- **Editor**: Can view, create, edit, and delete CRM data in the workspace
- **Viewer**: Can only view CRM data in the workspace

### Switching Workspaces

To switch to a different workspace:

1. Click on the workspace selector in the header
2. Select a workspace from the dropdown menu

All CRM data displayed will be filtered to show only data from the selected workspace.

## API Reference

The CRM module provides a comprehensive API for programmatic access to CRM data. The API endpoints are organized by entity type:

- `/api/v1/clients`: Clients API
- `/api/v1/invoices`: Invoices API
- `/api/v1/opportunities`: Opportunities API
- `/api/v1/tasks`: Tasks API
- `/api/v1/dashboard`: Dashboard API
- `/api/v1/reports`: Reports API

All list endpoints support pagination with the following parameters:

- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100)
- `page`: Page number (1-based, alternative to skip)

The response includes both the requested items and pagination metadata:

```json
{
  "items": [...],
  "metadata": {
    "total": 100,
    "page": 1,
    "size": 10,
    "pages": 10,
    "has_next": true,
    "has_prev": false,
    "next_page": 2,
    "prev_page": null
  }
}
```

For detailed API documentation, refer to the API documentation at `/docs`.
